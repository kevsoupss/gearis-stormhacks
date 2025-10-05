import subprocess
import time
from typing import List
from langchain_core.tools import tool, BaseTool
import pyautogui

from ..utils.mapping import normalize_app_name

class BrowserToolkit:
    """Toolkit for browser and general application interaction."""
    
    @staticmethod
    def get_tools() -> List[BaseTool]:
        """Returns all browser and interaction tools."""
        
        @tool
        def browser_search(query: str, browser: str = "Chrome") -> str:
            """
            Opens a browser and performs a web search.
            
            Args:
                query: Search query text
                browser: Browser name (Chrome, Safari, Firefox, Arc, Brave, Edge)
            """
            try:
                actual_browser = normalize_app_name(browser)
                import urllib.parse
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://www.google.com/search?q={encoded_query}"
                
                subprocess.run(['open', '-a', actual_browser, search_url], check=True)
                time.sleep(2)
                
                return f"Opened {actual_browser} and searched for: {query}"
            except Exception as e:
                return f"Error performing search: {str(e)}"

        @tool
        def open_url(url: str, browser: str = "Chrome") -> str:
            """
            Opens a specific URL in a browser.
            
            Args:
                url: Full URL to open
                browser: Browser name (Chrome, Safari, Firefox, Arc, Brave, Edge)
            """
            try:
                actual_browser = normalize_app_name(browser)
                subprocess.run(['open', '-a', actual_browser, url], check=True)
                return f"Opened {url} in {actual_browser}"
            except Exception as e:
                return f"Error opening URL: {str(e)}"

        @tool
        def type_text(text: str) -> str:
            """
            Types text into the currently focused application.
            
            Args:
                text: Text to type
            """
            try:
                time.sleep(0.5)
                pyautogui.write(text, interval=0.05)
                return f"Typed text into active application"
            except Exception as e:
                return f"Error typing text: {str(e)}"

        @tool
        def press_key(key: str) -> str:
            """
            Presses a keyboard key or key combination.
            
            Args:
                key: Key to press (e.g., 'enter', 'command+s', 'tab')
            """
            try:
                if '+' in key:
                    keys = key.split('+')
                    pyautogui.hotkey(*keys)
                else:
                    pyautogui.press(key)
                return f"Pressed key: {key}"
            except Exception as e:
                return f"Error pressing key: {str(e)}"

        @tool
        def create_note(title: str, content: str) -> str:
            """
            Creates a new note in Notes app.
            
            Args:
                title: Note title
                content: Note content
            """
            try:
                subprocess.run(['open', '-a', 'Notes'], check=True)
                time.sleep(1)
                
                pyautogui.hotkey('command', 'n')
                time.sleep(0.5)
                
                pyautogui.write(f"{title}\n{content}", interval=0.05)
                
                return f"Created note: {title}"
            except Exception as e:
                return f"Error creating note: {str(e)}"
        
        return [browser_search, open_url, type_text, press_key, create_note]