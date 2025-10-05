import subprocess
import time
from typing import List
from langchain_core.tools import tool, BaseTool

class SystemControlToolkit:
    """Toolkit for macOS system and application control."""
    
    @staticmethod
    def get_tools() -> List[BaseTool]:
        """Returns all system control tools."""
        
        @tool
        def open_macos_app(app_name: str) -> str:
            """
            Opens a macOS application by name.
            
            Args:
                app_name: Name of the application (e.g., 'Safari', 'Chrome', 'Notion')
            """
            try:
                result = subprocess.run(
                    ['open', '-a', app_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    time.sleep(1)
                    return f"Successfully opened {app_name}"
                else:
                    return f"Failed to open {app_name}. Error: {result.stderr}"
            except Exception as e:
                return f"Error opening {app_name}: {str(e)}"

        @tool
        def close_macos_app(app_name: str) -> str:
            """
            Closes a macOS application by name.
            
            Args:
                app_name: Name of the application to close
            """
            try:
                subprocess.run(['osascript', '-e', f'quit app "{app_name}"'], check=True)
                return f"Successfully closed {app_name}"
            except Exception as e:
                return f"Error closing {app_name}: {str(e)}"

        @tool
        def set_volume(level: int) -> str:
            """
            Sets system volume level.
            
            Args:
                level: Volume level from 0-100
            """
            try:
                level = max(0, min(100, level))
                subprocess.run(['osascript', '-e', f'set volume output volume {level}'], check=True)
                return f"Volume set to {level}%"
            except Exception as e:
                return f"Error setting volume: {str(e)}"

        @tool
        def adjust_volume(change: int) -> str:
            """
            Increases or decreases volume by a relative amount.
            
            Args:
                change: Amount to change (+10 for increase, -10 for decrease)
            """
            try:
                result = subprocess.run(
                    ['osascript', '-e', 'output volume of (get volume settings)'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                current = int(result.stdout.strip())
                new_level = max(0, min(100, current + change))
                
                subprocess.run(['osascript', '-e', f'set volume output volume {new_level}'], check=True)
                return f"Volume adjusted from {current}% to {new_level}%"
            except Exception as e:
                return f"Error adjusting volume: {str(e)}"
        
        return [open_macos_app, close_macos_app, set_volume, adjust_volume]