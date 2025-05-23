import logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from . import BaseSource, Track

logger = logging.getLogger(__name__)


class SpotifySource(BaseSource):
    @property
    def source_name(self):
        return "Spotify"

    @property
    def source_image(self):
        return "https://storage.googleapis.com/pr-newsroom-wp/1/2023/05/Spotify_Primary_Logo_RGB_Green.png"

    def initialize_client(self):
        if (
            not self.config.spotify.client_id
            or not self.config.spotify.client_secret
            or not self.config.spotify.redirect_uri
        ):
            logger.debug("Spotify credentials not configured.")
            return

        try:
            self.client = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=self.config.spotify.client_id,
                    client_secret=self.config.spotify.client_secret,
                    redirect_uri=self.config.spotify.redirect_uri,
                    scope="user-read-currently-playing user-read-playback-state",
                )
            )
        except Exception as e:
            logger.warning(f"Failed to initialise {self.source_name}: {e}")

    def get_current_track(self):
        if not self.client:
            logger.debug("Spotify credentials not configured.")
            return None

        try:
            current_track = self.client.current_playback()

            if not current_track or not current_track["is_playing"]:
                return None

            # Extract track information
            track = current_track["item"]
            return Track(
                name=track["name"],
                artist=", ".join([artist["name"] for artist in track["artists"]]),
                album=track["album"]["name"],
                url=track["external_urls"]["spotify"],
                image=(
                    track["album"]["images"][0]["url"]
                    if track["album"]["images"]
                    else None
                ),
                progress_ms=current_track["progress_ms"],
                duration_ms=track["duration_ms"],
            )
        except Exception as e:
            logger.error(f"Error fetching Spotify track: {e}")
            return None
