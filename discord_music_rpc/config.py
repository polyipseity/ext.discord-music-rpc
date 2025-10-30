import logging
from pathlib import Path

import yaml
from pydantic import BaseModel

from . import CONFIG_DIR, utils

logger = logging.getLogger(__name__)

CFG_PATH = CONFIG_DIR / "config.yaml"


class DiscordConfig(BaseModel):
    show_progress: bool = True
    show_source_logo: bool = True
    show_urls: bool = True
    show_ad: bool = True


class SpotifyConfig(BaseModel):
    enabled: bool = False
    client_id: str | None = None
    client_secret: str | None = None
    redirect_uri: str = "http://localhost:8888/callback"


class LastFmConfig(BaseModel):
    enabled: bool = False
    username: str | None = None
    api_key: str | None = None
    # todo: skip if already showing in rpc? tricky though because titles might be slightly different


class PlexConfig(BaseModel):
    enabled: bool = False
    server_url: str | None = None
    token: str | None = None
    libraries: list[str] = []


class SoundCloudConfig(BaseModel):
    enabled: bool = False


class YouTubeConfig(BaseModel):
    enabled: bool = False


class Config(BaseModel):
    discord: DiscordConfig = DiscordConfig()
    spotify: SpotifyConfig = SpotifyConfig()
    lastfm: LastFmConfig = LastFmConfig()
    plex: PlexConfig = PlexConfig()
    soundcloud: SoundCloudConfig = SoundCloudConfig()
    youtube: YouTubeConfig = YouTubeConfig()

    def validate(self):
        # Spotify configuration checks
        if not self.spotify.client_id:
            logger.info(
                "Note: spotify.client_id not configured. Spotify support will be disabled."
            )
        if not self.spotify.client_secret:
            logger.info(
                "Note: spotify.client_secret not configured. Spotify support will be disabled."
            )

        # Last.fm configuration checks
        if not self.lastfm.username:
            logger.info(
                "Note: lastfm.username not configured. Last.fm support will be disabled."
            )
        if not self.lastfm.api_key:
            logger.info(
                "Note: lastfm.api_key not configured. Last.fm support will be disabled."
            )

        # Plex configuration checks
        if not self.plex.server_url:
            logger.info(
                "Note: plex.server_url not configured. Plex support will be disabled."
            )
        if not self.plex.token:
            logger.info(
                "Note: plex.token not configured. Plex support will be disabled."
            )

        # todo return false if nothings enabled? idk
        return True

    def for_source(self, source: str):
        return getattr(
            self,
            source.lower().replace(".", ""),  # todo: hacky and gross but whatever
            None,
        )

    def dump(self):
        return self.model_dump()

    def save(self, path: Path = CFG_PATH):
        with path.open("w") as f:
            yaml.dump(self.dump(), f, Dumper=utils.PrettyDumper, sort_keys=False)

    @staticmethod
    def load(path: Path = CFG_PATH):
        if not path.exists() or path.stat().st_size == 0:
            Config().save()

        with path.open("r") as f:
            yaml_data = yaml.safe_load(f)

            if not isinstance(yaml_data, dict):
                raise ValueError("YAML data is not a dictionary")

            return Config(**yaml_data)


def load_config():
    config = Config.load()

    try:
        # config might be missing or have extra variables, save after validating
        # todo: i know if you just created a config for the first time this will save pointlessly but idc
        config.save()
    except:
        logger.info("Failed to save config")
        pass

    return config
