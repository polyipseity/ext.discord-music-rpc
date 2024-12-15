import datetime
import logging
import threading
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from pydantic.dataclasses import dataclass

logger = logging.getLogger(__name__)

ERROR_GAP = 5


@dataclass
class Track:
    name: str
    artist: str
    album: str | None = None
    url: str | None = None
    image: str | None = None
    progress_ms: float | None = None
    duration_ms: float | None = None


@dataclass
class TrackWithSource:
    track: Track
    source: str
    source_image: str


class BaseSource(ABC):
    from discord_music_rpc.config import Config

    config: Config
    alive: bool = True
    track: Track | None = None
    track_time: datetime.datetime | None = None

    def __init__(self, config, update_gap=1):
        self.update_gap = update_gap
        self.update_config(config)

    def update_config(self, config):
        self.config = config
        self.initialize_client()

    @property
    @abstractmethod
    def source_name(self) -> str:
        """
        Name of the source.
        """
        pass

    @property
    @abstractmethod
    def source_image(self) -> str:
        """
        Image URL of the source's logo.
        """
        pass

    @abstractmethod
    def initialize_client(self):
        """
        Initialize the client for the specific source.
        """
        pass

    @abstractmethod
    def get_current_track(self) -> Track | None:
        """
        Retrieve the currently playing track.
        Returns a Track object or None if no track is playing.
        """
        pass

    def update_loop(self):
        while self.alive:
            try:
                self.track = self.get_current_track()
                self.track_time = datetime.datetime.now()

                time.sleep(self.update_gap)
            except Exception as e:
                logger.warning(
                    f"Source {self.source_name} failed to update:\n"
                    f"{type(e).__name__}: {e}"
                )
                time.sleep(ERROR_GAP)


class MusicSourceManager:
    def __init__(self, config):
        from .lastfm import LastFmSource
        from .plex import PlexSource
        from .spotify import SpotifySource

        # Sources ordered by priority (highest to lowest)
        self.sources: list[BaseSource] = []

        if config.spotify.enabled:
            self.sources.append(
                SpotifySource(config)
            )  # highest priority (has progress info)

        if config.plex.enabled:
            self.sources.append(PlexSource(config))

        if config.lastfm.enabled:
            self.sources.append(LastFmSource(config))

        for source in self.sources:
            threading.Thread(target=source.update_loop, daemon=True).start()

    def stop(self):
        for source in self.sources:
            source.alive = False

    def get_current_tracks(self) -> list[TrackWithSource]:
        tracks: list[TrackWithSource] = []

        for source in self.sources:
            if not source.track or not source.track_time:
                continue

            update_gap_timedelta = datetime.timedelta(
                seconds=source.update_gap * 3
            )  # *3 cause idk something might happen. i dont even know if checking update time really matters
            time_diff = datetime.datetime.now() - source.track_time

            if time_diff <= update_gap_timedelta:
                tracks.append(
                    TrackWithSource(
                        source.track, source.source_name, source.source_image
                    )
                )

        return tracks
