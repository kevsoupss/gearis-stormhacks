import logging
from typing import List
from langchain_core.tools import tool, BaseTool
from ..utils.connection_manager import manager

logger = logging.getLogger(__name__)


class TauriControlToolkit:
    """Toolkit for Tauri window control."""
    
    @staticmethod
    def get_tools() -> List[BaseTool]:
        """Returns all window control tools."""
        
        @tool
        async def set_window_hidden(value: bool) -> str:
            """
            Sets whether the window is hidden or visible.
            
            Args:
                value: True to hide the window, False to show it
            """
            logger.info(f"🪟 Setting window hidden: {value}")
            try:
                # Send the event to frontend
                await manager.send_event('set_hidden', {'value': value})
                
                # Return success message (this is what the LLM sees)
                status = "hidden" if value else "shown"
                return f"Window {status} successfully"
                
            except Exception as e:
                logger.error(f"❌ Error setting window hidden state: {e}")
                return f"Error setting window hidden state: {str(e)}"
        
        @tool
        async def show_window() -> str:
            """
            Shows the window if it's hidden.
            """
            logger.info("🪟 Showing window")
            try:
                # Send the event to frontend
                await manager.send_event('set_hidden', {'value': False})
                
                # Return success message
                return "Window shown successfully"
                
            except Exception as e:
                logger.error(f"❌ Error showing window: {e}")
                return f"Error showing window: {str(e)}"
        
        return [set_window_hidden, show_window]