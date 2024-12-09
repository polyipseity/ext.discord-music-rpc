import os
import requests
from dataclasses import dataclass, field
from typing import Any, Optional, Literal, List
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import Config


@dataclass
class Track:
    name: str
    artist: str
    source: Literal["spotify", "lastfm"]
    album: Optional[str] = None
    url: Optional[str] = None
    image: Optional[str] = None
    progress_ms: Optional[int] = None
    duration_ms: Optional[int] = None


class SpotifySource:
    def __init__(self, config: Config):
        if (
            not config.SPOTIFY_CLIENT_ID
            or not config.SPOTIFY_CLIENT_SECRET
            or not config.SPOTIFY_REDIRECT_URI
        ):
            print("Spotify credentials not configured.")
            self.client = None
            return

        self.client = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=config.SPOTIFY_CLIENT_ID,
                client_secret=config.SPOTIFY_CLIENT_SECRET,
                redirect_uri=config.SPOTIFY_REDIRECT_URI,
                scope="user-read-currently-playing user-read-playback-state",
            )
        )

    def get_current_track(self) -> Optional[Track]:
        if not self.client:
            print("Spotify credentials not configured.")
            return

        try:
            current_track = self.client.current_playback()

            if not current_track or not current_track["is_playing"]:
                return None

            # Extract track information
            track = current_track["item"]
            return Track(
                name=track["name"],
                artist=track["artists"][0]["name"],
                album=track["album"]["name"],
                url=track["external_urls"]["spotify"],
                image=(
                    track["album"]["images"][0]["url"]
                    if track["album"]["images"]
                    else None
                ),
                progress_ms=current_track["progress_ms"],
                duration_ms=track["duration_ms"],
                source="spotify",
            )
        except Exception as e:
            print(f"Error fetching Spotify track: {e}")
            return None


class LastFmSource:
    def __init__(self, config: Config):
        self.username = config.LASTFM_USERNAME
        self.api_key = config.LASTFM_API_KEY

        if not self.username or not self.api_key:
            print("Last.fm credentials not configured.")

    def get_current_track(self) -> Optional[Track]:
        if not self.username or not self.api_key:
            print("Last.fm username or API key not configured.")
            return None

        params = {
            "method": "user.getrecenttracks",
            "api_key": self.api_key,
            "user": self.username,
            "limit": "1",
            "format": "json",
        }

        try:
            response = requests.get("https://ws.audioscrobbler.com/2.0/", params=params)
            data = response.json()

            # Check if a track is currently playing
            track = data["recenttracks"]["track"][0]
            if "@attr" in track and track["@attr"].get("nowplaying") == "true":
                return Track(
                    name=track["name"],
                    artist=track["artist"]["#text"],
                    album=track["album"]["#text"],
                    url=track["url"],
                    image=next(
                        (
                            img["#text"]
                            for img in track["image"]
                            if img["size"] == "large"
                        ),
                        None,
                    ),
                    source="lastfm",
                )
            return None

        except Exception as e:
            print(f"Error fetching Last.fm track: {e}")
            return None


class MusicSourceManager:
    def __init__(self, config: Config):
        self.sources: List[Any] = [  # also works as priority highest -> lowest
            SpotifySource(config),  # highest priority because it has progress info
            LastFmSource(config),  # fallback
        ]

    def get_current_track(self) -> Optional[Track]:
        for source in self.sources:
            track = source.get_current_track()
            if track:
                return track
        return None
