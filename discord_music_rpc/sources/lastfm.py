import requests

from .. import logger
from . import BaseSource, Track


class LastFmSource(BaseSource):
    @property
    def source_name(self):
        return "Last.fm"

    @property
    def source_image(self):
        return (
            "https://www.last.fm/static/images/lastfm_avatar_twitter.52a5d69a85ac.png"
        )

    def initialize_client(self):
        self.username = self.config.lastfm.username
        self.api_key = self.config.lastfm.api_key

        if not self.username or not self.api_key:
            logger.debug("Last.fm credentials not configured.")
            self.client = None
        else:
            self.client = True  # Placeholder to signify initialization success

    def get_current_track(self) -> Track | None:
        if not self.client:
            logger.debug("Last.fm credentials not configured.")
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
                )
            return None
        except Exception as e:
            logger.error(f"Error fetching Last.fm track: {e}")
            return None
