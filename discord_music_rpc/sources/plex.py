from plexapi.audio import Album, Artist
from plexapi.audio import Track as PlexTrack
from plexapi.server import PlexServer

from .. import logger
from . import BaseSource, Track


class PlexSource(BaseSource):
    @property
    def source_name(self):
        return "Plex"

    @property
    def source_image(self):
        return "https://www.plex.tv/wp-content/uploads/2022/09/plexamp-app-icon.png"

    def initialize_client(self):
        self.client = None

        if not self.config.plex.server_url or not self.config.plex.token:
            logger.debug(f"{self.source_name} credentials not configured.")
        else:
            try:
                self.client = PlexServer(
                    self.config.plex.server_url, self.config.plex.token
                )
            except Exception as e:
                logger.warning(f"Failed to initialise {self.source_name}: {e}")

    def get_current_track(self) -> Track | None:
        if not self.client:
            logger.debug(f"{self.source_name} credentials not configured.")
            return None

        for session in self.client.sessions():
            if session.type != "track":
                continue

            track: PlexTrack = session
            artist: Artist = track.artist()
            album: Album = track.album()

            return Track(
                name=track.title,
                artist=artist.title,
                album=album.title,
                url=None,
                image=None,  # Placeholder for thumbnail logic
                progress_ms=track.viewOffset,
                duration_ms=track.duration,
            )

        return None
