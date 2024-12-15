import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests

logger = logging.getLogger(__name__)

BASE_URL = "http://ws.audioscrobbler.com/2.0/"


@dataclass
class CoverArtCacheEntry:
    art_url: str | None
    timestamp: datetime


_cover_art_cache: dict[str, CoverArtCacheEntry] = {}


def get_lastfm_cover_art(
    song_title: str, artist: str, album: str | None = None, api_key: str | None = None
) -> str | None:
    key = f"{artist}_{song_title}_{album or ''}"

    # check cache
    if cached_entry := _cover_art_cache.get(key):
        if datetime.now() - cached_entry.timestamp < timedelta(hours=1):
            return cached_entry.art_url

    if not api_key:
        raise ValueError("Last.fm API key is required")

    params = {
        "method": "album.getInfo",
        "api_key": api_key,
        "artist": artist,
        "album": album,
        # "track": song_title,
        "format": "json",
    }

    def fetch_art_url() -> str | None:
        try:
            logger.info(f"Fetching cover art for {artist} - {song_title} from Last.fm")
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if images := data.get("album", {}).get("image"):
                # get highest quality image
                for img in reversed(images):
                    if img["#text"]:
                        return img["#text"]

            return None
        except (requests.RequestException, KeyError) as e:
            logger.error(f"Error fetching cover art: {e}")
            return None

    art_url = fetch_art_url()
    _cover_art_cache[key] = CoverArtCacheEntry(
        art_url=art_url, timestamp=datetime.now()
    )

    return art_url
