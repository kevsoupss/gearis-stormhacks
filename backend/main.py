from io import BytesIO
from storage.main import ChromaService
from elabs.main import ElevenLabsService
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
from agent.graph import create_graph
import logging
from langchain_core.messages import HumanMessage
from typing import List

app = FastAPI()
logger = logging.getLogger("uvicorn")
elevenlabs = ElevenLabsService()
chroma_service = ChromaService.get_instance()
graph = create_graph()
conversation_history = []

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")

    async def send_event(self, event_type: str, data: dict):
        """Send event to all connected clients"""
        message = {"type": event_type, "data": data}
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                logger.info(f"Sent event: {event_type}")
            except Exception as e:
                logger.error(f"Error sending to client: {e}")

manager = ConnectionManager()

# CORS middleware to allow requests from Tauri app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Tauri app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    chroma_service.start()
    logger.info("✅ File watcher started in background.")

@app.on_event("shutdown")
def on_shutdown():
    chroma_service.stop()

# Health check endpoint
@app.get("/ping")
def ping():
    return {"message": "pong"}

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for any client messages
            data = await websocket.receive_text()
            logger.info(f"Received from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Audio upload endpoint with WebSocket streaming
@app.post("/api/upload-audio")
async def upload_audio(audio: UploadFile = File(...)):
    global conversation_history
    try:
        audio_bytes = await audio.read()
        audio_raw = BytesIO(audio_bytes)
        logger.info("Audio bytes read: %d bytes", len(audio_bytes))
        
        # Notify frontend that STT is starting
        await manager.send_event("stt_start", {})
        
        stt_response = elevenlabs.stt(audio_raw)
        logger.info(f"STT response: {stt_response}")
        
        # Send transcript to frontend
        await manager.send_event("transcript", {"text": stt_response.text})
        
        conversation_history.append(HumanMessage(content=stt_response.text))
        
        # Notify that agent is starting
        await manager.send_event("agent_start", {"query": stt_response.text})
        
        # Stream events from the graph
        async for event in graph.astream_events(
            {"messages": conversation_history},
            version="v2"
        ):
            kind = event["event"]
            
            # When agent decides to call a tool
            if kind == "on_chat_model_end":
                output = event["data"]["output"]
                if hasattr(output, 'tool_calls') and output.tool_calls:
                    for tool_call in output.tool_calls:
                        await manager.send_event("tool_call_start", {
                            "tool": tool_call["name"],
                            "args": tool_call["args"],
                            "id": tool_call.get("id", "")
                        })
            
            # When a tool finishes executing
            elif kind == "on_tool_end":
                await manager.send_event("tool_call_end", {
                    "tool": event["name"],
                    "output": str(event["data"].get("output", ""))
                })
            
            # When the entire graph finishes
            elif kind == "on_chain_end" and event["name"] == "LangGraph":
                result = event["data"]["output"]
                conversation_history = result["messages"]
                final_message = result["messages"][-1]
                
                logger.info(f"Final message: {final_message.content}")
                
                await manager.send_event("agent_complete", {
                    "response": final_message.content
                })
        
        return {"transcript": stt_response.text, "success": True}
        
    except Exception as e:
        logger.exception("Error during audio upload")
        await manager.send_event("error", {"message": str(e)})
        return {"success": False, "error": str(e)}
    finally:
        await audio.close()