
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import os

app = FastAPI(title="Tauri + FastAPI Example")

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
    try:
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save original file temporarily
        temp_filename = f"temp_{timestamp}.webm"
        temp_path = UPLOAD_DIR / temp_filename
        
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # Convert to MP3 using ffmpeg
        mp3_filename = f"recording_{timestamp}.mp3"
        mp3_path = UPLOAD_DIR / mp3_filename
        
        # Run ffmpeg conversion
        result = subprocess.run([
            "ffmpeg", "-i", str(temp_path),
            "-vn",  # No video
            "-ar", "44100",  # Audio sample rate
            "-ac", "2",  # Audio channels
            "-b:a", "192k",  # Audio bitrate
            str(mp3_path)
        ], capture_output=True, text=True)
        
        # Remove temporary file
        if temp_path.exists():
            os.remove(temp_path)
        
        if result.returncode == 0:
            return {
                "success": True,
                "filename": mp3_filename,
                "size": mp3_path.stat().st_size,
                "path": str(mp3_path)
            }
        else:
            return {
                "success": False,
                "error": f"FFmpeg conversion failed: {result.stderr}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        audio.file.close()