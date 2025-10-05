import subprocess
import time
import pyautogui
from typing import List
from langchain_core.tools import tool, BaseTool

from ..utils.mapping import normalize_app_name

class DiscordToolkit:
    """Toolkit for Discord application control on macOS."""
    
    @staticmethod
    def get_tools() -> List[BaseTool]:
        """Returns all Discord control tools."""
        
        @tool
        def discord_open() -> str:
            """Opens the Discord application."""
            try:
                subprocess.run(['open', '-a', 'Discord'], check=True)
                time.sleep(2)
                return "Opened Discord"
            except Exception as e:
                return f"Error opening Discord: {str(e)}"
        
        @tool
        def discord_close() -> str:
            """Closes the Discord application."""
            try:
                subprocess.run(['osascript', '-e', 'quit app "Discord"'], check=True)
                return "Closed Discord"
            except Exception as e:
                return f"Error closing Discord: {str(e)}"
        
        @tool
        def discord_toggle_mute() -> str:
            """Toggles microphone mute/unmute in Discord."""
            try:
                # Discord keyboard shortcut: Cmd+Shift+M
                pyautogui.hotkey('command', 'shift', 'm')
                return "Toggled Discord microphone mute"
            except Exception as e:
                return f"Error toggling mute: {str(e)}"
        
        @tool
        def discord_toggle_deafen() -> str:
            """Toggles deafen on/off in Discord."""
            try:
                # Discord keyboard shortcut: Cmd+Shift+D
                pyautogui.hotkey('command', 'shift', 'd')
                return "Toggled Discord deafen"
            except Exception as e:
                return f"Error toggling deafen: {str(e)}"
        
        @tool
        def discord_answer_call() -> str:
            """Answers an incoming Discord call."""
            try:
                # Discord keyboard shortcut: Cmd+Enter (when call notification is visible)
                pyautogui.hotkey('command', 'return')
                return "Answered Discord call"
            except Exception as e:
                return f"Error answering call: {str(e)}"
        
        @tool
        def discord_decline_call() -> str:
            """Declines an incoming Discord call."""
            try:
                # Discord keyboard shortcut: Escape
                pyautogui.press('escape')
                return "Declined Discord call"
            except Exception as e:
                return f"Error declining call: {str(e)}"
        
        @tool
        def discord_search() -> str:
            """Opens Discord search (Cmd+K)."""
            try:
                # First, activate Discord
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Cmd+K
                pyautogui.hotkey('command', 'k')
                return "Opened Discord search"
            except Exception as e:
                return f"Error opening search: {str(e)}"
        
        @tool
        def discord_navigate_to_server(server_number: int) -> str:
            """
            Navigates to a Discord server by position (1-9).
            
            Args:
                server_number: Server position number (1-9, where 1 is the first server)
            """
            try:
                if not 1 <= server_number <= 9:
                    return "Server number must be between 1 and 9"
                
                # Activate Discord first
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Cmd+Number
                pyautogui.hotkey('command', str(server_number))
                return f"Navigated to server #{server_number}"
            except Exception as e:
                return f"Error navigating to server: {str(e)}"
        
        @tool
        def discord_toggle_pins() -> str:
            """Toggles the pinned messages panel."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Cmd+P
                pyautogui.hotkey('command', 'p')
                return "Toggled Discord pins panel"
            except Exception as e:
                return f"Error toggling pins: {str(e)}"
        
        @tool
        def discord_toggle_inbox() -> str:
            """Toggles the inbox (notifications) panel."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Cmd+I
                pyautogui.hotkey('command', 'i')
                return "Toggled Discord inbox"
            except Exception as e:
                return f"Error toggling inbox: {str(e)}"
        
        @tool
        def discord_mark_server_read() -> str:
            """Marks the current server as read."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Shift+Escape
                pyautogui.hotkey('shift', 'escape')
                return "Marked current server as read"
            except Exception as e:
                return f"Error marking as read: {str(e)}"
        
        @tool
        def discord_mark_channel_read() -> str:
            """Marks the current channel as read."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Escape
                pyautogui.press('escape')
                return "Marked current channel as read"
            except Exception as e:
                return f"Error marking channel as read: {str(e)}"
        
        @tool
        def discord_upload_file() -> str:
            """Opens the file upload dialog."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Cmd+Shift+U
                pyautogui.hotkey('command', 'shift', 'u')
                return "Opened file upload dialog"
            except Exception as e:
                return f"Error opening upload dialog: {str(e)}"
        
        @tool
        def discord_create_dm() -> str:
            """Opens dialog to create a new DM or group DM."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Cmd+K, then type username
                pyautogui.hotkey('command', 'k')
                return "Opened DM creation (search for a user to message)"
            except Exception as e:
                return f"Error creating DM: {str(e)}"
        
        @tool
        def discord_scroll_chat_up() -> str:
            """Scrolls up in the current chat."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                pyautogui.press('pageup')
                return "Scrolled chat up"
            except Exception as e:
                return f"Error scrolling: {str(e)}"
        
        @tool
        def discord_scroll_chat_down() -> str:
            """Scrolls down in the current chat."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                pyautogui.press('pagedown')
                return "Scrolled chat down"
            except Exception as e:
                return f"Error scrolling: {str(e)}"
        
        @tool
        def discord_focus_text_input() -> str:
            """Focuses the message text input field."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Click in the text area or use Tab to navigate
                pyautogui.press('tab')
                return "Focused text input"
            except Exception as e:
                return f"Error focusing input: {str(e)}"
        
        @tool
        def discord_send_message(message: str) -> str:
            """
            Types and sends a message in the current Discord channel.
            Make sure you're in the correct channel first.
            
            Args:
                message: The message text to send
            """
            try:
                # Activate Discord
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Focus text input
                pyautogui.press('tab')
                time.sleep(0.3)
                
                # Type the message
                pyautogui.write(message, interval=0.02)
                time.sleep(0.2)
                
                # Send with Enter
                pyautogui.press('return')
                
                return f"Sent message: {message}"
            except Exception as e:
                return f"Error sending message: {str(e)}"
        
        @tool
        def discord_toggle_emoji_picker() -> str:
            """Opens the emoji picker."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Cmd+E
                pyautogui.hotkey('command', 'e')
                return "Opened emoji picker"
            except Exception as e:
                return f"Error opening emoji picker: {str(e)}"
        
        @tool
        def discord_navigate_to_dms() -> str:
            """Navigates to the DMs/Home section (leaves any server)."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Use Cmd+K to open quick switcher, then go home
                pyautogui.hotkey('command', 'k')
                time.sleep(0.3)
                
                # Type "home" or "friends" to navigate to DM section
                pyautogui.write('home', interval=0.05)
                time.sleep(0.3)
                
                pyautogui.press('return')
                return "Navigated to DMs/Home"
            except Exception as e:
                return f"Error navigating to DMs: {str(e)}"
        
        @tool
        def discord_next_channel() -> str:
            """Moves to the next channel or DM in the list."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Alt+Down Arrow (macOS: Option+Down)
                pyautogui.hotkey('alt', 'down')
                return "Moved to next channel/DM"
            except Exception as e:
                return f"Error navigating: {str(e)}"
        
        @tool
        def discord_previous_channel() -> str:
            """Moves to the previous channel or DM in the list."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Alt+Up Arrow (macOS: Option+Up)
                pyautogui.hotkey('alt', 'up')
                return "Moved to previous channel/DM"
            except Exception as e:
                return f"Error navigating: {str(e)}"
        
        @tool
        def discord_next_unread_channel() -> str:
            """Jumps to the next unread channel or DM."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Alt+Shift+Down (macOS: Option+Shift+Down)
                pyautogui.hotkey('alt', 'shift', 'down')
                return "Jumped to next unread channel/DM"
            except Exception as e:
                return f"Error navigating: {str(e)}"
        
        @tool
        def discord_previous_unread_channel() -> str:
            """Jumps to the previous unread channel or DM."""
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Discord keyboard shortcut: Alt+Shift+Up (macOS: Option+Shift+Up)
                pyautogui.hotkey('alt', 'shift', 'up')
                return "Jumped to previous unread channel/DM"
            except Exception as e:
                return f"Error navigating: {str(e)}"
        
        @tool
        def discord_search_dm(username: str) -> str:
            """
            Opens search and searches for a specific user to open their DM.
            
            Args:
                username: Discord username to search for
            """
            try:
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Open quick switcher (Cmd+K)
                pyautogui.hotkey('command', 'k')
                time.sleep(0.5)
                
                # Type the username
                pyautogui.write(username, interval=0.05)
                time.sleep(0.5)
                
                # Press Enter to select first result
                pyautogui.press('return')
                
                return f"Searched for DM with: {username}"
            except Exception as e:
                return f"Error searching DM: {str(e)}"
        
        @tool
        def discord_click_dm_by_position(position: int) -> str:
            """
            Clicks on a DM by its position in the DM list (visual clicking method).
            Position 1 is the first DM, 2 is second, etc.
            Make sure you're in the DM/Home view first.
            
            Args:
                position: Position of the DM in the list (1-10)
            """
            try:
                if not 1 <= position <= 10:
                    return "Position must be between 1 and 10"
                
                subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
                time.sleep(0.5)
                
                # Click on the left sidebar where DMs are
                # These are approximate coordinates - may need adjustment
                base_y = 150  # Starting Y position for first DM
                dm_height = 44  # Height between each DM item
                click_x = 150  # X position in left sidebar
                
                click_y = base_y + (dm_height * (position - 1))
                
                pyautogui.click(click_x, click_y)
                
                return f"Clicked DM at position {position}"
            except Exception as e:
                return f"Error clicking DM: {str(e)}"
        
        return [
            discord_open,
            discord_close,
            discord_toggle_mute,
            discord_toggle_deafen,
            discord_answer_call,
            discord_decline_call,
            discord_search,
            discord_navigate_to_server,
            discord_toggle_pins,
            discord_toggle_inbox,
            discord_mark_server_read,
            discord_mark_channel_read,
            discord_upload_file,
            discord_create_dm,
            discord_scroll_chat_up,
            discord_scroll_chat_down,
            discord_focus_text_input,
            discord_send_message,
            discord_toggle_emoji_picker,
            # DM Navigation
            discord_navigate_to_dms,
            discord_next_channel,
            discord_previous_channel,
            discord_next_unread_channel,
            discord_previous_unread_channel,
            discord_search_dm,
            discord_click_dm_by_position,
        ]