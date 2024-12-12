import datetime
from dataclasses import dataclass

from pypresence import ActivityType, Presence

from . import APP_NAME, PROJECT_URL, logger
from .config import Config
from .sources import TrackWithSource
from .utils import is_same_track

DEFAULT_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/CD_icon_test.svg/240px-CD_icon_test.svg.png"

# todo: move this stuff out of here? into sources? idk for api tho
client_ids = {
    "YouTube": "1316777493889286206",
    "Spotify": "1316777610419634180",
    "SoundCloud": "1316777669945458789",
    "Plex": "1316777729508642857",
    "Last.fm": "1316777803768664076",
}

activity_type_overrides = {"YouTube": ActivityType.WATCHING}


@dataclass
class RpcWrapper:
    presence: Presence
    last_progress: float | None = None
    last_track: TrackWithSource | None = None


class DiscordRichPresence:
    def __init__(self, config: Config):
        self.config = config
        self.rpcs = {
            key: RpcWrapper(Presence(client_id))
            for key, client_id in client_ids.items()
        }

    def connect(self):
        for rpc in self.rpcs.values():
            rpc.presence.connect()

        logger.info("Connected to Discord RPC")

    def update(self, tracks: list[TrackWithSource]):
        for source, rpc in self.rpcs.items():
            source_config = self.config.for_source(source)

            track = next(
                (t for t in tracks if t.source == source), None
            )  # todo: dont love this, maybe change input to a dict and stop using lists everywhere

            if not source_config.enabled or not track:
                rpc.presence.clear()
                rpc.last_track = None
                rpc.last_progress = None
                continue

            buttons = []

            start_time = None
            end_time = None

            if self.config.discord.show_urls and track.track.url:
                buttons.append(
                    {
                        "label": f"View track on {track.source}",
                        "url": track.track.url or "",
                    }
                )

            if self.config.discord.show_ad:
                buttons.append(
                    {
                        "label": f"Powered by {APP_NAME}",
                        "url": PROJECT_URL,
                    }
                )

            # handle progress
            if not is_same_track(track, rpc.last_track):
                rpc.last_progress = None

            if (
                track.track.progress_ms is not None
                and track.track.duration_ms is not None
            ):
                if (
                    track.track.progress_ms == rpc.last_progress
                ):  # haven't gotten any progress, don't update - discord will handle it
                    continue

                start_time = (
                    int(datetime.datetime.now().timestamp() * 1000)
                    - track.track.progress_ms
                )
                end_time = start_time + track.track.duration_ms
                rpc.last_progress = track.track.progress_ms

            rpc.presence.update(
                activity_type=ActivityType.LISTENING
                if source not in activity_type_overrides
                else activity_type_overrides[source],
                buttons=buttons,
                details=track.track.name.ljust(
                    2
                )  # "details" length must be at least 2 characters long
                if track.track.name
                else None,
                state=track.track.artist,
                large_image=track.track.image or DEFAULT_IMAGE,
                large_text=track.track.album.ljust(
                    2
                )  # "large_text" length must be at least 2 characters long
                if track.track.album
                else None,
                start=start_time if self.config.discord.show_progress else None,
                end=end_time if self.config.discord.show_progress else None,
                small_image=track.source_image
                if self.config.discord.show_source
                else None,
                small_text=f"Listening on {track.source}"
                if self.config.discord.show_source
                else None,
            )

            rpc.last_track = track

    def close(self):
        try:
            for rpc in self.rpcs.values():
                rpc.presence.clear()
                rpc.presence.close()
        except Exception as e:
            logger.error(e)
