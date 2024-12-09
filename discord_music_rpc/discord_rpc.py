import datetime
from typing import Optional
from pypresence import Presence, ActivityType
from .music_sources import Track, Config


class DiscordRichPresence:
    def __init__(self, config: Config):
        self.client_id = config.DISCORD_CLIENT_ID
        self.rpc = Presence(self.client_id)
        self.last_track: Optional[Track] = None

    def connect(self):
        self.rpc.connect()
        print("Connected to Discord RPC")

    def update(self, track: Optional[Track]):
        if not track:
            self.clear()
            return

        try:
            # buttons = []
            # buttons.append(
            #     {
            #         "label": f"View {track.source.capitalize()} Track",
            #         "url": track.url or "",
            #     }
            # )

            start_time = None
            end_time = None

            if track.progress_ms is not None and track.duration_ms is not None:
                start_time = (
                    int(datetime.datetime.now().timestamp() * 1000) - track.progress_ms
                )
                end_time = start_time + track.duration_ms

            self.rpc.update(
                activity_type=ActivityType.LISTENING,
                details=track.name,
                state=track.artist,
                large_image=track.image or "placeholder",
                large_text=track.album or "Unknown Album",
                # buttons=buttons,
                start=start_time,
                end=end_time,
            )

            self.last_track = track
        except Exception as e:
            print(f"Error updating Discord presence: {e}")

    def clear(self):
        self.rpc.clear()

    def close(self):
        self.clear()
        self.rpc.close()
