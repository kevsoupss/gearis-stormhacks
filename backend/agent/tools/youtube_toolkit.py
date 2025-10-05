import subprocess
import time
from typing import List
from langchain_core.tools import tool, BaseTool
import urllib.parse

from ..utils.mapping import normalize_app_name

class YouTubeToolkit:
    """Toolkit for YouTube video control using AppleScript and JavaScript."""
    
    @staticmethod
    def _execute_js_in_browser(js_code: str, browser: str) -> str:
        """Execute JavaScript in the active browser tab using AppleScript."""
        actual_browser = normalize_app_name(browser)
        
        # Escape quotes in JavaScript code
        js_escaped = js_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
        
        # Different AppleScript syntax for different browsers
        if actual_browser in ["Google Chrome", "Brave Browser", "Microsoft Edge"]:
            applescript = f'''
            tell application "{actual_browser}"
                tell active tab of window 1
                    execute javascript "{js_escaped}"
                end tell
            end tell
            '''
        elif actual_browser == "Safari":
            applescript = f'''
            tell application "Safari"
                tell current tab of window 1
                    do JavaScript "{js_escaped}"
                end tell
            end tell
            '''
        elif actual_browser == "Arc":
            # Arc uses Chrome-like AppleScript
            applescript = f'''
            tell application "Arc"
                tell active tab of window 1
                    execute javascript "{js_escaped}"
                end tell
            end tell
            '''
        else:
            return "Browser not supported for JavaScript execution"
        
        try:
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else result.stderr
        except Exception as e:
            return str(e)
    
    @staticmethod
    def get_tools() -> List[BaseTool]:
        """Returns all YouTube control tools."""
        
        @tool
        def youtube_search(query: str, browser: str) -> str:
            """
            Searches YouTube and opens the search results page.
            
            Args:
                query: What to search for
                browser: Browser to use (Chrome, Safari, Firefox, Arc, Brave, Edge)
            """
            try:
                actual_browser = normalize_app_name(browser)
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
                
                subprocess.run(['open', '-a', actual_browser, search_url], check=True)
                time.sleep(2)
                
                return f"Opened YouTube search results for: {query}"
            except Exception as e:
                return f"Error searching YouTube: {str(e)}"

        @tool
        def youtube_play_video(query: str, browser: str) -> str:
            """
            Searches YouTube and plays the first/top result automatically.
            
            Args:
                query: Video to search and play
                browser: Browser to use (Chrome, Safari, Firefox, Arc, Brave, Edge)
            """
            try:
                actual_browser = normalize_app_name(browser)
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
                
                # Open search results
                subprocess.run(['open', '-a', actual_browser, search_url], check=True)
                time.sleep(3)  # Wait for page to load
                
                # JavaScript to click the first video
                js_code = """
                (function() {
                    const videos = document.querySelectorAll('a#video-title');
                    if (videos && videos.length > 0) {
                        const title = videos[0].getAttribute('title') || 'video';
                        videos[0].click();
                        return title;
                    }
                    return 'No videos found';
                })();
                """
                
                result = YouTubeToolkit._execute_js_in_browser(js_code, actual_browser)
                
                if result and "No videos found" not in result:
                    return f"Playing: {result}"
                else:
                    return f"Opened YouTube search for: {query}. Click a video to play."
                    
            except Exception as e:
                return f"Error playing video '{query}': {str(e)}"
        
        @tool
        def youtube_fullscreen(browser: str) -> str:
            """
            Toggles fullscreen mode for the currently playing YouTube video.
            Call this after a video has started playing.
            
            Args:
                browser: Browser to use (Chrome, Safari, Firefox, Arc, Brave, Edge)
            """
            try:
                actual_browser = normalize_app_name(browser)
                
                # JavaScript to click YouTube's fullscreen button
                fullscreen_js = """
                (function() {
                    const fullscreenBtn = document.querySelector('.ytp-fullscreen-button');
                    if (fullscreenBtn) {
                        fullscreenBtn.click();
                        if (document.fullscreenElement) {
                            return 'Exited fullscreen';
                        } else {
                            return 'Entered fullscreen';
                        }
                    }
                    return 'Fullscreen button not found - make sure a video is playing';
                })();
                """
                
                result = YouTubeToolkit._execute_js_in_browser(fullscreen_js, actual_browser)
                return result or "Toggled fullscreen"
                    
            except Exception as e:
                return f"Error toggling fullscreen: {str(e)}"

        @tool
        def youtube_open_channel(channel_name: str, browser: str) -> str:
            """
            Opens a YouTube channel by name.
            
            Args:
                channel_name: Channel name or handle (e.g., "mkbhd", "@mkbhd")
                browser: Browser to use
            """
            try:
                actual_browser = normalize_app_name(browser)
                
                if not channel_name.startswith('@'):
                    channel_name = f"@{channel_name}"
                
                encoded_channel = urllib.parse.quote(channel_name)
                channel_url = f"https://www.youtube.com/{encoded_channel}"
                
                subprocess.run(['open', '-a', actual_browser, channel_url], check=True)
                
                return f"Opened YouTube channel: {channel_name}"
            except Exception as e:
                return f"Error opening YouTube channel: {str(e)}"

        @tool
        def youtube_open_url(video_url: str, browser: str) -> str:
            """
            Opens a specific YouTube video URL.
            
            Args:
                video_url: Full YouTube URL or video ID
                browser: Browser to use
            """
            try:
                actual_browser = normalize_app_name(browser)
                
                if not video_url.startswith('http'):
                    video_url = f"https://www.youtube.com/watch?v={video_url}"
                
                subprocess.run(['open', '-a', actual_browser, video_url], check=True)
                
                return f"Opened YouTube video"
            except Exception as e:
                return f"Error opening YouTube video: {str(e)}"

        @tool
        def youtube_play_playlist(playlist_name: str, browser: str) -> str:
            """
            Searches for and opens a YouTube playlist.
            
            Args:
                playlist_name: Name of the playlist to search for
                browser: Browser to use
            """
            try:
                actual_browser = normalize_app_name(browser)
                encoded_query = urllib.parse.quote(f"{playlist_name} playlist")
                search_url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=EgIQAw%253D%253D"
                
                subprocess.run(['open', '-a', actual_browser, search_url], check=True)
                time.sleep(3)
                
                # JavaScript to click first playlist
                js_code = """
                (function() {
                    const playlist = document.querySelector('ytd-playlist-renderer a');
                    if (playlist) {
                        const title = playlist.getAttribute('title') || 'playlist';
                        playlist.click();
                        return title;
                    }
                    return 'No playlist found';
                })();
                """
                
                result = YouTubeToolkit._execute_js_in_browser(js_code, actual_browser)
                
                if result and "No playlist found" not in result:
                    return f"Opened playlist: {result}"
                else:
                    return f"Searched for YouTube playlist: {playlist_name}"
                    
            except Exception as e:
                return f"Error searching for playlist: {str(e)}"

        @tool
        def youtube_control_playback(action: str, browser: str) -> str:
            """
            Controls YouTube video playback using JavaScript.
            Works when a YouTube video is playing in the browser.
            
            Args:
                action: One of: 'play_pause', 'next', 'previous', 'fullscreen', 'mute', 
                        'increase_volume', 'decrease_volume', 'skip_forward', 'skip_backward'
                browser: Browser to use
            """
            try:
                actual_browser = normalize_app_name(browser)
                
                # JavaScript commands for different actions
                js_commands = {
                    'play_pause': """
                        const video = document.querySelector('video');
                        if (video) {
                            if (video.paused) {
                                video.play();
                                'Playing';
                            } else {
                                video.pause();
                                'Paused';
                            }
                        }
                    """,
                    'mute': """
                        const video = document.querySelector('video');
                        if (video) {
                            video.muted = !video.muted;
                            video.muted ? 'Muted' : 'Unmuted';
                        }
                    """,
                    'skip_forward': """
                        const video = document.querySelector('video');
                        if (video) {
                            video.currentTime += 10;
                            'Skipped forward 10s';
                        }
                    """,
                    'skip_backward': """
                        const video = document.querySelector('video');
                        if (video) {
                            video.currentTime -= 10;
                            'Skipped backward 10s';
                        }
                    """,
                    'increase_volume': """
                        const video = document.querySelector('video');
                        if (video) {
                            video.volume = Math.min(1, video.volume + 0.1);
                            'Volume increased';
                        }
                    """,
                    'decrease_volume': """
                        const video = document.querySelector('video');
                        if (video) {
                            video.volume = Math.max(0, video.volume - 0.1);
                            'Volume decreased';
                        }
                    """,
                    'next': """
                        const nextBtn = document.querySelector('.ytp-next-button');
                        if (nextBtn) {
                            nextBtn.click();
                            'Next video';
                        }
                    """,
                    'previous': """
                        const prevBtn = document.querySelector('.ytp-prev-button');
                        if (prevBtn) {
                            prevBtn.click();
                            'Previous video';
                        }
                    """,
                    'fullscreen': """
                        const video = document.querySelector('video');
                        if (video) {
                            if (document.fullscreenElement) {
                                document.exitFullscreen();
                                'Exited fullscreen';
                            } else {
                                video.requestFullscreen();
                                'Entered fullscreen';
                            }
                        }
                    """,
                }
                
                if action not in js_commands:
                    available = ', '.join(js_commands.keys())
                    return f"Unknown action: {action}. Available: {available}"
                
                result = YouTubeToolkit._execute_js_in_browser(js_commands[action], actual_browser)
                
                return result or f"Executed: {action}"
                
            except Exception as e:
                return f"Error controlling playback: {str(e)}"
        
        return [
            youtube_search,
            youtube_play_video,
            youtube_fullscreen,
            youtube_open_channel,
            youtube_open_url,
            youtube_play_playlist,
            youtube_control_playback,
        ]