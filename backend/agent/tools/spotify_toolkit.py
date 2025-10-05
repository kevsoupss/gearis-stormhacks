import logging
import subprocess
import time
from typing import List
from langchain_core.tools import tool, BaseTool

class SpotifyToolkit:
    """Toolkit for Spotify music control."""
    
    @staticmethod
    def _get_current_track() -> str:
        """Helper function to get current Spotify track information."""
        try:
            applescript_track = 'tell application "Spotify" to name of current track'
            track_result = subprocess.run(
                ['osascript', '-e', applescript_track],
                capture_output=True,
                text=True,
                check=True
            )
            track_name = track_result.stdout.strip()
            
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
    
    @staticmethod
    def get_tools() -> List[BaseTool]:
        """Returns all Spotify control tools."""
        
        @tool
        def spotify_play_track(query: str) -> str:
            """
            Searches for and directly plays a track, album, or artist on Spotify.
            
            Args:
                query: Song name, artist, or album (e.g., "Bohemian Rhapsody Queen")
            """
            logging.info("calling play spotify track tool")
            try:
                subprocess.run(['open', '-a', 'Spotify'], check=True)
                time.sleep(1.5)
                
                applescript = f'''
                tell application "Spotify"
                    activate
                    play track "spotify:search:{query}"
                end tell
                '''
                
                subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
                time.sleep(2)
                
                track_info = SpotifyToolkit._get_current_track()
                return f"▶️ Now playing: {track_info}"
                
            except Exception as e:
                return f"Searched for '{query}' in Spotify. Error: {str(e)}"

        @tool
        def spotify_search(query: str) -> str:
            """
            Searches for a song, artist, album, or playlist on Spotify.
            
            Args:
                query: What to search for
            """
            logging.info("calling spotify search tool")
            try:
                subprocess.run(['open', '-a', 'Spotify'], check=True)
                time.sleep(2)
                
                import urllib.parse
                encoded_query = urllib.parse.quote(query)
                search_url = f"spotify:search:{encoded_query}"
                
                subprocess.run(['open', search_url], check=True)
                time.sleep(1)
                
                return f"🔍 Opened Spotify and searched for: {query}"
            except Exception as e:
                return f"Error searching Spotify: {str(e)}"

        @tool
        def spotify_play() -> str:
            """Plays or resumes the current track in Spotify."""
            logging.info("calling spotify play track tool")
            try:
                applescript = 'tell application "Spotify" to play'
                subprocess.run(['osascript', '-e', applescript], check=True)
                
                track_info = SpotifyToolkit._get_current_track()
                return f"▶️ Playing: {track_info}"
            except Exception as e:
                return f"Error playing Spotify: {str(e)}"

        @tool
        def spotify_pause() -> str:
            """Pauses the current track in Spotify."""
            logging.info("calling spotify pause track tool")
            try:
                applescript = 'tell application "Spotify" to pause'
                subprocess.run(['osascript', '-e', applescript], check=True)
                
                track_info = SpotifyToolkit._get_current_track()
                return f"⏸️ Paused: {track_info}"
            except Exception as e:
                return f"Error pausing Spotify: {str(e)}"

        @tool
        def spotify_next() -> str:
            """Skips to the next track in Spotify."""
            logging.info("calling spotify skip track tool")
            try:
                applescript = 'tell application "Spotify" to next track'
                subprocess.run(['osascript', '-e', applescript], check=True)
                time.sleep(0.5)
                
                track_info = SpotifyToolkit._get_current_track()
                return f"⏭️ Skipped to next track: {track_info}"
            except Exception as e:
                return f"Error skipping to next track: {str(e)}"

        @tool
        def spotify_previous() -> str:
            """Goes back to the previous track in Spotify."""
            logging.info("calling spotify previous track tool")
            try:
                applescript = 'tell application "Spotify" to previous track'
                subprocess.run(['osascript', '-e', applescript], check=True)
                time.sleep(0.5)
                
                track_info = SpotifyToolkit._get_current_track()
                return f"⏮️ Playing previous track: {track_info}"
            except Exception as e:
                return f"Error going to previous track: {str(e)}"

        @tool
        def spotify_current_track() -> str:
            """Gets information about the currently playing track in Spotify."""
            logging.info("calling spotify current track tool")
            try:
                track_info = SpotifyToolkit._get_current_track()
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
            logging.info("calling spotify set volume tool")
            try:
                volume = max(0, min(100, volume))
                applescript = f'tell application "Spotify" to set sound volume to {volume}'
                subprocess.run(['osascript', '-e', applescript], check=True)
                return f"🔊 Set Spotify volume to {volume}%"
            except Exception as e:
                return f"Error setting Spotify volume: {str(e)}"

        @tool
        def spotify_play_playlist(playlist_name: str) -> str:
            """
            Plays a specific playlist by name in Spotify.
            
            Args:
                playlist_name: Name of the playlist to play
            """
            logging.info("calling spotify play playlist tool")
            try:
                import urllib.parse
                encoded_name = urllib.parse.quote(playlist_name)
                
                subprocess.run(['open', '-a', 'Spotify'], check=True)
                time.sleep(1)
                
                search_url = f"spotify:search:playlist:{encoded_name}"
                subprocess.run(['open', search_url], check=True)
                
                return f"🎵 Searching for playlist: {playlist_name}"
            except Exception as e:
                return f"Error playing playlist: {str(e)}"
        
        return [
            spotify_play_track,
            spotify_search,
            spotify_play,
            spotify_pause,
            spotify_next,
            spotify_previous,
            spotify_current_track,
            spotify_set_volume,
            spotify_play_playlist,
        ]
