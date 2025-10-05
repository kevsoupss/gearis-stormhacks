from langchain_core.tools import BaseTool
from typing import List

from .system_toolkit import SystemControlToolkit
from .browser_toolkit import BrowserToolkit
from .spotify_toolkit import SpotifyToolkit
from .youtube_toolkit import YouTubeToolkit
from .discord_toolkit import DiscordToolkit
from .cool_toolkit import CoolToolkit
from .rag import RagTool
from .tauri_toolkit import TauriControlToolkit

# Get all tools from all toolkits
def get_all_tools() -> List[BaseTool]:
    """Returns all tools from all toolkits."""
    return (
        SystemControlToolkit.get_tools() +
        BrowserToolkit.get_tools() +
        SpotifyToolkit.get_tools() +
        YouTubeToolkit.get_tools() +
        DiscordToolkit.get_tools() +
        CoolToolkit.get_tools() + 
        RagTool.get_tool() +
        TauriControlToolkit.get_tools()
    )

# # Or get specific toolkits
# def get_media_tools() -> List[BaseTool]:
#     """Returns only media-related tools (Spotify + YouTube)."""
#     return SpotifyToolkit.get_tools() + YouTubeToolkit.get_tools()

# def get_system_tools() -> List[BaseTool]:
#     """Returns only system control tools."""
#     return SystemControlToolkit.get_tools() + BrowserToolkit.get_tools()


# Main tools list for your agent
tools = get_all_tools()