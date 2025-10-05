import subprocess
import time
from typing import List
from langchain_core.tools import tool, BaseTool
import pyautogui

from ..utils.mapping import normalize_app_name

class CoolToolkit:
    """Toolkit for cool interactions."""
    
    @staticmethod
    def get_tools() -> List[BaseTool]:
        """Returns all cool tools."""
        
        @tool
        def surgin_it() -> str:
            """
            Runs the surgin it function

            Args:
                None
            """
            try:
                subprocess.run(['open', '-a', 'Spotify'], check=True)
                time.sleep(1.5)
                
                applescript = f'''
                tell application "Spotify"
                    activate
                    play track "spotify:search:timeless the weeknd"
                end tell
                '''
                
                subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)

                time.sleep(2)

                actual_browser = normalize_app_name("Chrome")
                search_url = f"https://www.stormhacks.com/"
                
                subprocess.run(['open', '-a', actual_browser, search_url], check=True)
                
                return f"▶️ Im Surgin it gng"
                
            except Exception as e:
                return f"Searched for Timeless in Spotify. Error: {str(e)}"
    
        return [surgin_it]
    