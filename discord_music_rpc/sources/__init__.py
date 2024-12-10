from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


@dataclass
class Track:
    name: str
    artist: str
    source: Literal["spotify", "lastfm", "soundcloud", "plex"]
    album: str | None = None
    url: str | None = None
    image: str | None = None
    progress_ms: int | None = None
    duration_ms: int | None = None


class BaseSource(ABC):
    def __init__(self, config):
        self.client = None
        self.config = config
        self.initialize_client()

    @abstractmethod
    def initialize_client(self):
        """
        Initialize the client for the specific source.
        Should be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_current_track(self):
        """
        Retrieve the currently playing track.
        Should return a Track object or None if no track is playing.
        Should be implemented by subclasses.
        """
        pass


class MusicSourceManager:
    def __init__(self, config):
        from .lastfm import LastFmSource
        from .plex import PlexSource
        from .soundcloud import SoundCloudSource
        from .spotify import SpotifySource

        # Sources ordered by priority (highest to lowest)
        self.sources = [
            SpotifySource(config),  # highest priority (has progress info)
            PlexSource(config),
            LastFmSource(config),
            SoundCloudSource(config),  # lowest priority
        ]

    def get_current_track(self) -> Track | None:
        for source in self.sources:
            track = source.get_current_track()
            if track:
                return track
        return None
