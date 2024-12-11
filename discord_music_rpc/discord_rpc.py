import datetime

from pypresence import ActivityType, Presence

from . import logger
from .config import Config
from .sources import TrackWithSource
from .utils import is_same_track


class DiscordRichPresence:
    def __init__(self, config: Config):
        self.client_id = config.discord.client_id
        self.rpc = Presence(self.client_id)

        self.show_progress = config.discord.show_progress
        self.show_source = config.discord.show_source

        self.last_track: TrackWithSource | None = None
        self.last_progress: int | None = None

    def connect(self):
        self.rpc.connect()
        logger.info("Connected to Discord RPC")

    def update(self, track: TrackWithSource | None):
        if not track:
            self.clear()
            return

        start_time = None
        end_time = None

        if not is_same_track(track, self.last_track):
            self.last_progress = None

        if track.track.progress_ms is not None and track.track.duration_ms is not None:
            if (
                track.track.progress_ms == self.last_progress
            ):  # haven't gotten any progress, don't update - discord will handle it
                return

            start_time = (
                int(datetime.datetime.now().timestamp() * 1000)
                - track.track.progress_ms
            )
            end_time = start_time + track.track.duration_ms
            self.last_progress = track.track.progress_ms

        self.rpc.update(
            activity_type=ActivityType.LISTENING,
            details=track.track.name,
            state=track.track.artist,
            large_image=track.track.image,
            large_text=track.track.album.ljust(
                2
            )  # "large_text" length must be at least 2 characters long
            if track.track.album
            else None,
            start=start_time if self.show_progress else None,
            end=end_time if self.show_progress else None,
            small_image=track.source_image if self.show_source else None,
            small_text=f"Listening on {track.source}" if self.show_source else None,
        )

        self.last_track = track

    def clear(self):
        self.rpc.clear()

    def close(self):
        try:
            self.clear()
            self.rpc.close()
        except Exception as e:
            logger.error(e)
