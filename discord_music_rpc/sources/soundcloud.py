import datetime

from soundcloud import SoundCloud

from .. import logger
from . import BaseSource, Track


class SoundCloudSource(BaseSource):
    @property
    def source_name(self):
        return "SoundCloud"

    @property
    def source_image(self):
        return "https://d21buns5ku92am.cloudfront.net/26628/images/419679-1x1_SoundCloudLogo_cloudmark-f5912b-large-1645807040.jpg"

    def initialize_client(self):
        self.client = None

        if not self.config.soundcloud.auth_token:
            logger.debug(f"{self.source_name} credentials not configured.")
        else:
            try:
                self.client = SoundCloud(auth_token=self.config.soundcloud.auth_token)
            except Exception as e:
                logger.warning(f"Failed to initialise {self.source_name}: {e}")

    def get_current_track(self) -> Track | None:
        if not self.client:
            logger.debug(f"{self.source_name} credentials not configured.")
            return None

        song = next(self.client.get_my_history())
        if not song:
            return None

        now = int(datetime.datetime.now().timestamp() * 1000)

        if now > song.played_at and now <= song.played_at + song.track.duration:
            return Track(
                name=song.track.title,
                artist=song.track.user.username,
                url=song.track.permalink_url,
                image=song.track.artwork_url,
            )

        return None
