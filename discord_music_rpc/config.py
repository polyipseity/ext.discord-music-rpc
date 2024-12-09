import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    # Spotify Configuration
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    SPOTIFY_REDIRECT_URI: str = os.getenv(
        "SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"
    )

    # Last.fm Configuration
    LASTFM_USERNAME: str = os.getenv("LASTFM_USERNAME", "")
    LASTFM_API_KEY: str = os.getenv("LASTFM_API_KEY", "")

    # SoundCloud Configuration
    SOUNDCLOUD_AUTH_TOKEN: str = os.getenv("SOUNDCLOUD_AUTH_TOKEN", "")

    # Discord RPC Configuration
    DISCORD_CLIENT_ID: str = os.getenv("DISCORD_CLIENT_ID", "")

    @classmethod
    def validate(cls) -> list[str]:
        # Spotify configuration checks
        if not cls.SPOTIFY_CLIENT_ID:
            print(
                "Note: SPOTIFY_CLIENT_ID not configured. Spotify support will be disabled."
            )
        if not cls.SPOTIFY_CLIENT_SECRET:
            print(
                "Note: SPOTIFY_CLIENT_SECRET not configured. Spotify support will be disabled."
            )

        # Last.fm configuration checks
        if not cls.LASTFM_USERNAME:
            print(
                "Note: LASTFM_USERNAME not configured. Spotify support will be disabled."
            )
        if not cls.LASTFM_API_KEY:
            print(
                "Note: LASTFM_API_KEY not configured. Spotify support will be disabled."
            )

        if not cls.SOUNDCLOUD_AUTH_TOKEN:
            print(
                "Note: SOUNDCLOUD_AUTH_TOKEN not configured. SoundCloud support will be disabled."
            )
