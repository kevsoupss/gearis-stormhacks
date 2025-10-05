
from io import BytesIO
from elabs.main import ElevenLabsService
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
from agent.graph import create_graph
import logging
from langchain_core.messages import HumanMessage

app = FastAPI()
logger = logging.getLogger("uvicorn")
elevenlabs = ElevenLabsService()
graph = create_graph()
conversation_history = []


# CORS middleware to allow requests from Tauri app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Tauri app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Example data
fake_users_db = {
    1: {"id": 1, "name": "Alice"},
    2: {"id": 2, "name": "Bob"},
}

# Health check endpoint
@app.get("/ping")
def ping():
    return {"message": "pong"}

# User model
class User(BaseModel):
    id: int
    name: str

# Get user by ID
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    user = fake_users_db.get(user_id)
    if not user:
        return {"error": "User not found"}
    return user

# Example POST endpoint
@app.post("/users", response_model=User)
def create_user(user: User):
    fake_users_db[user.id] = user.dict()
    return user

# Audio upload endpoint
@app.post("/api/upload-audio")
async def upload_audio(audio: UploadFile = File(...)):
    global conversation_history
    try:
        audio_bytes = await audio.read()
        audio_raw = BytesIO(audio_bytes)
        logger.info("Audio bytes read: %d bytes", len(audio_bytes))
        
        stt_response = elevenlabs.stt(audio_raw)
        logger.info(f"STT response: {stt_response}")
        
        conversation_history.append(HumanMessage(content=stt_response.text))
        
        # Run the agent - it will loop through tools as needed
        result = graph.invoke({"messages": conversation_history})
        
        # Update history with all messages (including tool calls/results)
        conversation_history = result["messages"]
        
        # Print the final response
        final_message = result["messages"][-1]
        logger.info(f"Final message: {final_message.content}")
        
        return {"transcript": stt_response.text}
    except Exception as e:
        logger.exception("Error during audio upload")
        return {"success": False, "error": str(e)}
    finally:
        await audio.close()
