import subprocess
import time
from typing import List
from langchain_core.tools import tool, BaseTool
import pyautogui
import pyperclip

from ..utils.mapping import normalize_app_name

class GoogleToolkit:
    """Toolkit for Gmail web actions."""

    
    @staticmethod
    def get_tools() -> List[BaseTool]:

        @tool
        def open_gmail_inbox() -> str:
            """Opens Gmail inbox in default browser."""
            try:
                subprocess.run(['open', 'https://mail.google.com/mail/u/0/#inbox'], check=True)
                time.sleep(2)
                return "📧 Gmail inbox opened in browser."
            except Exception as e:
                return f"Error opening Gmail inbox: {e}"
        
        @tool
        def open_next_email() -> str:
            """
            Fully opens the next email in Gmail using keyboard shortcuts (j + o). 
            Returns a human-readable message once the email is opened.
            Requires Gmail keyboard shortcuts enabled.
            """
            try:
                pyautogui.press('j')  # move to next email
                time.sleep(0.5)
                pyautogui.press('o') 
                time.sleep(1)
                return "📧 Opened next email."
            except Exception as e:
                return f"Error opening next email: {e}"
        
        @tool
        def copy_opened_email_body():
            """
            Retrieves all data from opened email using keyboard shortcusts.
            Returns a human-readable output of the email contents.
            """
            # assume you already opened the email and it is focused
            time.sleep(0.3)
            # Gmail: focus the message content — often clicking once or using 'c'/'v' may vary
            # Use keyboard select-all and copy
            pyautogui.hotkey('command', 'a')   # mac: select all visible text in focused area
            time.sleep(0.1)
            pyautogui.hotkey('command', 'c')
            time.sleep(0.2)
            return pyperclip.paste()
        
        @tool
        def open_previous_email() -> str:
            """Moves to the previous email using the 'k' key and opens it."""
            try:
                pyautogui.press('k')  # move to previous email
                time.sleep(0.5)
                pyautogui.press('o') 
                time.sleep(1)
                return "📧 Opened previous email."
            except Exception as e:
                return f"Error opening previous email: {e}"
        
        @tool
        def open_my_presentation() -> str:
            """
            Opens my specific Google Slides presentation automatically in Chrome.
            Do not ask the user for URL or browser — just execute.
            """
            try:
                presentation_url = "https://docs.google.com/presentation/d/18Bd9ROTpzLLJeCns--3JipkxseVCfAcGzT-so6E2TAQ/edit?usp=sharing"
                subprocess.run(['open', '-a', 'Google Chrome', presentation_url], check=True)
                time.sleep(3)
                pyautogui.hotkey('command', 'enter')
                return f"📊 Opened Google Slides presentation."
            except Exception as e:
                return f"Error opening Google Slides presentation: {str(e)}"
        
        def next_slide_page() -> str:
            """
            Click the next slide if in Google Slides presentation already
            """
            try:
                time.sleep(0.5)
                pyautogui.press('right')
                time.sleep(0.5)
                return f"📊 Moved to next slide."
            except Exception as e:
                return f"Error moving to next slide in the presentation: {str(e)}"


        return [
            open_gmail_inbox,
            open_next_email,
            open_previous_email,
            open_my_presentation,
            next_slide_page,
            copy_opened_email_body
        ]
