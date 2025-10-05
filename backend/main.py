from io import BytesIO
from storage.main import ChromaService
from elabs.main import ElevenLabsService
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from agent.graph import create_graph
import logging
from langchain_core.messages import HumanMessage
from agent.utils.connection_manager import manager

app = FastAPI()
logger = logging.getLogger("uvicorn")
elevenlabs = ElevenLabsService()
chroma_service = ChromaService.get_instance()
graph = create_graph()
# save_graph_visualization()
conversation_history = []

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
            data = await websocket.receive_text()
            logger.info(f"Received from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def get_tool_action_text(tool_name: str, args: dict) -> str:
    """Generate human-readable action text for tool calls"""
    tool_messages = {
        "open_app": f"Opening {args.get('app_name', 'application')}",
        "close_app": f"Closing {args.get('app_name', 'application')}",
        "search": f"Searching for '{args.get('query', 'information')}'",
        "open_url": f"Opening {args.get('url', 'URL')}",
        "type_text": f"Typing text",
        "press_key": f"Pressing {args.get('key', 'key')}",
        "set_volume": f"Setting volume to {args.get('level', 'specified level')}",
        "create_note": f"Creating note",
    }
    return tool_messages.get(tool_name, f"Executing {tool_name}")

def get_tool_complete_text(tool_name: str) -> str:
    """Generate completion message for tools"""
    complete_messages = {
        "open_app": "Application opened",
        "close_app": "Application closed",
        "search": "Search completed",
        "open_url": "URL opened",
        "type_text": "Text typed",
        "press_key": "Key pressed",
        "set_volume": "Volume adjusted",
        "create_note": "Note created",
    }
    return complete_messages.get(tool_name, f"{tool_name} completed")

# Audio upload endpoint with WebSocket streaming
@app.post("/api/upload-audio")
async def upload_audio(audio: UploadFile = File(...), toggle_voice: str = ""):
    global conversation_history
    try:
        audio_bytes = await audio.read()
        audio_raw = BytesIO(audio_bytes)
        logger.info("Audio bytes read: %d bytes", len(audio_bytes))
        
        # Notify frontend that STT is starting
        await manager.send_event("status", {"message": "Processing audio..."})
        
        stt_response = elevenlabs.stt(audio_raw)
        logger.info(f"STT response: {stt_response}")
        
        # Send transcript to frontend
        await manager.send_event("status", {"message": f"You said: {stt_response.text}"})
        
        conversation_history.append(HumanMessage(content=stt_response.text))
        
        # Track tools used for summary
        tools_used = []
        
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
                        tool_name = tool_call["name"]
                        args = tool_call["args"]
                        action_text = get_tool_action_text(tool_name, args)
                        
                        tools_used.append({"name": tool_name, "action": action_text})
                        
                        await manager.send_event("status", {
                            "message": action_text
                        })
            
            # When a tool finishes executing
            elif kind == "on_tool_end":
                tool_name = event["name"]
                complete_text = get_tool_complete_text(tool_name)
                
                await manager.send_event("status", {
                    "message": complete_text
                })
            
            # When the entire graph finishes
            elif kind == "on_chain_end" and event["name"] == "LangGraph":
                result = event["data"]["output"]
                conversation_history = result["messages"]
                final_message = result["messages"][-1]
                
                logger.info(f"Final message: {final_message.content}")
                if toggle_voice == 'true':
                    elevenlabs.tts(final_message.content)
                
                # # Create summary of actions
                # if tools_used:
                #     summary = "Task completed. " + ", ".join([t["action"] for t in tools_used])
                # else:
                #     summary = "Task completed"
                
                await manager.send_event("status", {
                    "message": final_message.content 
                })
        
        return {"transcript": stt_response.text, "success": True}
        
    except Exception as e:
        logger.exception("Error during audio upload")
        await manager.send_event("status", {"message": f"Error: {str(e)}"})
        return {"success": False, "error": str(e)}
    finally:
        await audio.close()