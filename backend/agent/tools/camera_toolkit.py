import subprocess
import os
import time

from langchain_core.tools import tool

DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
os.makedirs(DESKTOP_DIR, exist_ok=True) 

class CameraToolkit:
    """Toolkit for controlling the Mac camera and taking pictures."""

    @staticmethod
    @tool
    def take_picture(save_path: str = "./photo.jpg") -> str:
        """
        Takes a picture using the Mac's built-in camera.
        
        """
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"
            filepath = os.path.join(DESKTOP_DIR, filename)
            subprocess.run(["imagesnap", "-q", filepath], check=True, timeout=10)
            return f"📸 Photo saved to: {filename}"
        except Exception as e:
            return f"⚠️ Unexpected error: {str(e)}"

    @staticmethod
    def get_tools():
        return [CameraToolkit.take_picture]
