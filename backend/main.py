# backend/main.py

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
        file_extension = audio.filename.split(".")[-1]
        filename = f"recording_{timestamp}.{file_extension}"
        file_path = UPLOAD_DIR / filename
        
        # Save the file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        return {
            "success": True,
            "filename": filename,
            "size": file_path.stat().st_size,
            "path": str(file_path)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        audio.file.close()