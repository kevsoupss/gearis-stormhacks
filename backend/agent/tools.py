from langchain_core.tools import tool
import subprocess
import pyautogui
import time

# ============================================================================
# Application Name Mappings (macOS display name -> actual app name)
# ============================================================================
APP_NAME_MAPPING = {
    # Browsers
    'chrome': 'Google Chrome',
    'google chrome': 'Google Chrome',
    'firefox': 'Firefox',
    'safari': 'Safari',
    'arc': 'Arc',
    'brave': 'Brave Browser',
    'edge': 'Microsoft Edge',
    'opera': 'Opera',
    
    # Common apps
    'vscode': 'Visual Studio Code',
    'vs code': 'Visual Studio Code',
    'code': 'Visual Studio Code',
    'notion': 'Notion',
    'slack': 'Slack',
    'discord': 'Discord',
    'spotify': 'Spotify',
    'notes': 'Notes',
    'calendar': 'Calendar',
    'mail': 'Mail',
    'messages': 'Messages',
    'facetime': 'FaceTime',
    'calculator': 'Calculator',
    'terminal': 'Terminal',
    'iterm': 'iTerm',
    'iterm2': 'iTerm',
    'finder': 'Finder',
    'music': 'Music',
    'photos': 'Photos',
    'preview': 'Preview',
    'textedit': 'TextEdit',
    'pages': 'Pages',
    'keynote': 'Keynote',
    'numbers': 'Numbers',
    'zoom': 'zoom.us',
    'obs': 'OBS',
    'vlc': 'VLC',
    'photoshop': 'Adobe Photoshop 2024',
    'illustrator': 'Adobe Illustrator 2024',
}

def normalize_app_name(app_name: str) -> str:
    """
    Normalizes application names to their actual macOS names.
    
    Args:
        app_name: User-provided app name (e.g., 'chrome', 'Chrome')
    
    Returns:
        Actual macOS application name (e.g., 'Google Chrome')
    """
    # Convert to lowercase for matching
    app_lower = app_name.lower().strip()
    
    # Check if it's in our mapping
    if app_lower in APP_NAME_MAPPING:
        return APP_NAME_MAPPING[app_lower]
    
    # If not in mapping, return original with proper capitalization
    return app_name.title()

# ============================================================================
# CATEGORY 1: System/Desktop Control Tools
# ============================================================================

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
            time.sleep(1)  # Give app time to open
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
        level = max(0, min(100, level))  # Clamp between 0-100
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
        # Get current volume
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


# ============================================================================
# CATEGORY 2: Browser/Application-Specific Tools
# ============================================================================

@tool
def browser_search(query: str, browser: str = "Chrome") -> str:
    """
    Opens a browser and performs a web search.
    Requires browser to be already open or will open it.
    
    Args:
        query: Search query text
        browser: Browser name (Chrome, Safari, Firefox, Arc, Brave, Edge)
    """
    try:
        # Normalize browser name
        actual_browser = normalize_app_name(browser)
        
        # URL encode the query
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        # Open URL in browser
        subprocess.run(['open', '-a', actual_browser, search_url], check=True)
        time.sleep(2)  # Wait for page to load
        
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
    Useful for filling forms, writing notes, etc.
    
    Args:
        text: Text to type
    """
    try:
        time.sleep(0.5)  # Brief delay to ensure focus
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
            # Handle key combinations
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
        # Open Notes app
        subprocess.run(['open', '-a', 'Notes'], check=True)
        time.sleep(1)
        
        # Create new note (Cmd+N)
        pyautogui.hotkey('command', 'n')
        time.sleep(0.5)
        
        # Type content
        pyautogui.write(f"{title}\n{content}", interval=0.05)
        
        return f"Created note: {title}"
    except Exception as e:
        return f"Error creating note: {str(e)}"


# ============================================================================
# CATEGORY 3: Spotify Control Tools
# ============================================================================

@tool
def spotify_play_track(query: str) -> str:
    """
    Searches for and directly plays a track, album, or artist on Spotify.
    This will start playing immediately without manual selection.
    
    Args:
        query: Song name, artist, or album (e.g., "Bohemian Rhapsody Queen", "Drake", "Abbey Road")
    """
    try:
        # Open Spotify if not already open
        subprocess.run(['open', '-a', 'Spotify'], check=True)
        time.sleep(1.5)
        
        # Use AppleScript to search and play
        # This will play the first result automatically
        applescript = f'''
        tell application "Spotify"
            activate
            play track "spotify:search:{query}"
        end tell
        '''
        
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True
        )
        
        time.sleep(2)  # Wait for playback to start
        
        # Get what's actually playing
        track_info = _get_spotify_current_track()
        return f"▶️ Now playing: {track_info}"
        
    except Exception as e:
        # Fallback to search if direct play fails
        return f"Searched for '{query}' in Spotify. You may need to select the track manually. Error: {str(e)}"


@tool
def spotify_search(query: str) -> str:
    """
    Searches for a song, artist, album, or playlist on Spotify and shows results.
    Use spotify_play_track() instead if you want to play immediately.
    
    Args:
        query: What to search for (e.g., "Bohemian Rhapsody", "The Beatles", "Chill Vibes playlist")
    """
    try:
        # Open Spotify
        subprocess.run(['open', '-a', 'Spotify'], check=True)
        time.sleep(2)  # Wait for Spotify to open
        
        # Use Spotify URL scheme to search
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        search_url = f"spotify:search:{encoded_query}"
        
        subprocess.run(['open', search_url], check=True)
        time.sleep(1)
        
        return f"🔍 Opened Spotify and searched for: {query}. Results are displayed - you can select what to play."
    except Exception as e:
        return f"Error searching Spotify: {str(e)}"


@tool
def spotify_play() -> str:
    """
    Plays or resumes the current track in Spotify.
    """
    try:
        applescript = 'tell application "Spotify" to play'
        subprocess.run(['osascript', '-e', applescript], check=True)
        
        # Get current track info
        track_info = _get_spotify_current_track()
        return f"▶️ Playing: {track_info}"
    except Exception as e:
        return f"Error playing Spotify: {str(e)}"


@tool
def spotify_pause() -> str:
    """
    Pauses the current track in Spotify.
    """
    try:
        applescript = 'tell application "Spotify" to pause'
        subprocess.run(['osascript', '-e', applescript], check=True)
        
        track_info = _get_spotify_current_track()
        return f"⏸️ Paused: {track_info}"
    except Exception as e:
        return f"Error pausing Spotify: {str(e)}"


@tool
def spotify_next() -> str:
    """
    Skips to the next track in Spotify.
    """
    try:
        applescript = 'tell application "Spotify" to next track'
        subprocess.run(['osascript', '-e', applescript], check=True)
        time.sleep(0.5)  # Wait for track to change
        
        track_info = _get_spotify_current_track()
        return f"⏭️ Skipped to next track: {track_info}"
    except Exception as e:
        return f"Error skipping to next track: {str(e)}"


@tool
def spotify_previous() -> str:
    """
    Goes back to the previous track in Spotify.
    """
    try:
        applescript = 'tell application "Spotify" to previous track'
        subprocess.run(['osascript', '-e', applescript], check=True)
        time.sleep(0.5)  # Wait for track to change
        
        track_info = _get_spotify_current_track()
        return f"⏮️ Playing previous track: {track_info}"
    except Exception as e:
        return f"Error going to previous track: {str(e)}"


@tool
def spotify_current_track() -> str:
    """
    Gets information about the currently playing track in Spotify.
    """
    try:
        track_info = _get_spotify_current_track()
        return f"🎵 Currently playing: {track_info}"
    except Exception as e:
        return f"Error getting current track: {str(e)}"


@tool
def spotify_set_volume(volume: int) -> str:
    """
    Sets Spotify volume (separate from system volume).
    
    Args:
        volume: Volume level from 0-100
    """
    try:
        volume = max(0, min(100, volume))  # Clamp between 0-100
        applescript = f'tell application "Spotify" to set sound volume to {volume}'
        subprocess.run(['osascript', '-e', applescript], check=True)
        return f"🔊 Set Spotify volume to {volume}%"
    except Exception as e:
        return f"Error setting Spotify volume: {str(e)}"


@tool
def spotify_play_playlist(playlist_name: str) -> str:
    """
    Plays a specific playlist by name in Spotify.
    Note: This searches for the playlist and opens it.
    
    Args:
        playlist_name: Name of the playlist to play
    """
    try:
        # Use Spotify URI to search for playlist
        import urllib.parse
        encoded_name = urllib.parse.quote(playlist_name)
        
        # Open Spotify
        subprocess.run(['open', '-a', 'Spotify'], check=True)
        time.sleep(1)
        
        # Search for playlist
        search_url = f"spotify:search:playlist:{encoded_name}"
        subprocess.run(['open', search_url], check=True)
        
        return f"🎵 Searching for playlist: {playlist_name}. Select it from the results to play."
    except Exception as e:
        return f"Error playing playlist: {str(e)}"


def _get_spotify_current_track() -> str:
    """
    Helper function to get current Spotify track information.
    """
    try:
        # Get track name
        applescript_track = 'tell application "Spotify" to name of current track'
        track_result = subprocess.run(
            ['osascript', '-e', applescript_track],
            capture_output=True,
            text=True,
            check=True
        )
        track_name = track_result.stdout.strip()
        
        # Get artist
        applescript_artist = 'tell application "Spotify" to artist of current track'
        artist_result = subprocess.run(
            ['osascript', '-e', applescript_artist],
            capture_output=True,
            text=True,
            check=True
        )
        artist_name = artist_result.stdout.strip()
        
        return f"{track_name} by {artist_name}"
    except:
        return "Unknown track"


# ============================================================================
# CATEGORY 4: YouTube Control Tools
# ============================================================================

@tool
def youtube_search(query: str, browser: str = "Chrome") -> str:
    """
    Searches YouTube and opens the search results page.
    
    Args:
        query: What to search for (e.g., "python tutorial", "music video")
        browser: Browser to use (Chrome, Safari, Firefox, Arc, Brave, Edge)
    """
    try:
        actual_browser = normalize_app_name(browser)
        
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        subprocess.run(['open', '-a', actual_browser, search_url], check=True)
        time.sleep(2)
        
        return f"🔍 Opened YouTube search results for: {query}"
    except Exception as e:
        return f"Error searching YouTube: {str(e)}"


@tool
def youtube_play_video(query: str, browser: str = "Chrome") -> str:
    """
    Searches YouTube and plays the first/top result automatically.
    
    Args:
        query: Video to search and play (e.g., "Bohemian Rhapsody", "How to code")
        browser: Browser to use (Chrome, Safari, Firefox, Arc, Brave, Edge)
    """
    try:
        actual_browser = normalize_app_name(browser)
        
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        
        # Use YouTube's feeling lucky-style direct search
        # This often redirects to the first result
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        subprocess.run(['open', '-a', actual_browser, search_url], check=True)
        time.sleep(2)
        
        # Simulate pressing Enter on first result (keyboard automation)
        # Wait for page load, then press Tab (to focus first result) and Enter
        time.sleep(1)
        pyautogui.press('tab')  # Focus on first result
        time.sleep(0.3)
        pyautogui.press('return')  # Click/play
        
        return f"▶️ Playing YouTube video: {query}"
    except Exception as e:
        return f"Searched YouTube for '{query}'. You may need to select the video manually. Error: {str(e)}"


@tool
def youtube_open_channel(channel_name: str, browser: str = "Chrome") -> str:
    """
    Opens a YouTube channel by name.
    
    Args:
        channel_name: Channel name or handle (e.g., "mkbhd", "@mkbhd")
        browser: Browser to use (Chrome, Safari, Firefox, Arc, Brave, Edge)
    """
    try:
        actual_browser = normalize_app_name(browser)
        
        import urllib.parse
        
        # Clean up channel name
        if not channel_name.startswith('@'):
            channel_name = f"@{channel_name}"
        
        encoded_channel = urllib.parse.quote(channel_name)
        channel_url = f"https://www.youtube.com/{encoded_channel}"
        
        subprocess.run(['open', '-a', actual_browser, channel_url], check=True)
        
        return f"📺 Opened YouTube channel: {channel_name}"
    except Exception as e:
        return f"Error opening YouTube channel: {str(e)}"


@tool
def youtube_open_url(video_url: str, browser: str = "Chrome") -> str:
    """
    Opens a specific YouTube video URL.
    
    Args:
        video_url: Full YouTube URL or video ID
        browser: Browser to use (Chrome, Safari, Firefox, Arc, Brave, Edge)
    """
    try:
        actual_browser = normalize_app_name(browser)
        
        # Handle both full URLs and video IDs
        if not video_url.startswith('http'):
            video_url = f"https://www.youtube.com/watch?v={video_url}"
        
        subprocess.run(['open', '-a', actual_browser, video_url], check=True)
        
        return f"▶️ Opened YouTube video"
    except Exception as e:
        return f"Error opening YouTube video: {str(e)}"


@tool
def youtube_play_playlist(playlist_name: str, browser: str = "Chrome") -> str:
    """
    Searches for and plays a YouTube playlist.
    
    Args:
        playlist_name: Name of the playlist to search for
        browser: Browser to use (Chrome, Safari, Firefox, Arc, Brave, Edge)
    """
    try:
        actual_browser = normalize_app_name(browser)
        
        import urllib.parse
        encoded_query = urllib.parse.quote(f"{playlist_name} playlist")
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=EgIQAw%253D%253D"
        
        subprocess.run(['open', '-a', actual_browser, search_url], check=True)
        
        return f"🎵 Searched for YouTube playlist: {playlist_name}"
    except Exception as e:
        return f"Error searching for playlist: {str(e)}"


@tool
def youtube_control_playback(action: str) -> str:
    """
    Controls YouTube video playback using keyboard shortcuts.
    Works when YouTube is the active tab.
    
    Args:
        action: One of: 'play_pause', 'next', 'previous', 'fullscreen', 'mute', 
                'increase_volume', 'decrease_volume', 'skip_forward', 'skip_backward'
    """
    try:
        action_map = {
            'play_pause': 'k',           # or 'space'
            'next': 'shift+n',           # Next video in playlist
            'previous': 'shift+p',       # Previous video
            'fullscreen': 'f',           # Toggle fullscreen
            'mute': 'm',                 # Toggle mute
            'increase_volume': 'up',     # Volume up
            'decrease_volume': 'down',   # Volume down
            'skip_forward': 'l',         # Skip 10s forward
            'skip_backward': 'j',        # Skip 10s backward
            'captions': 'c',             # Toggle captions
        }
        
        if action not in action_map:
            return f"Unknown action: {action}. Available: {', '.join(action_map.keys())}"
        
        key = action_map[action]
        
        # Press the key
        if '+' in key:
            keys = key.split('+')
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(key)
        
        action_labels = {
            'play_pause': '⏯️ Toggled play/pause',
            'next': '⏭️ Next video',
            'previous': '⏮️ Previous video',
            'fullscreen': '🖥️ Toggled fullscreen',
            'mute': '🔇 Toggled mute',
            'increase_volume': '🔊 Increased volume',
            'decrease_volume': '🔉 Decreased volume',
            'skip_forward': '⏩ Skipped 10s forward',
            'skip_backward': '⏪ Skipped 10s backward',
            'captions': '💬 Toggled captions',
        }
        
        return action_labels.get(action, f"Executed: {action}")
        
    except Exception as e:
        return f"Error controlling playback: {str(e)}"


# All available tools
tools = [
    # System control
    open_macos_app,
    close_macos_app,
    set_volume,
    adjust_volume,
    
    # Browser/app-specific
    browser_search,
    open_url,
    type_text,
    press_key,
    create_note,
    
    # Spotify control
    spotify_play_track,
    spotify_search,
    spotify_play,
    spotify_pause,
    spotify_next,
    spotify_previous,
    spotify_current_track,
    spotify_set_volume,
    spotify_play_playlist,
    
    # YouTube control
    youtube_search,
    youtube_play_video,
    youtube_open_channel,
    youtube_open_url,
    youtube_play_playlist,
    youtube_control_playback,
]