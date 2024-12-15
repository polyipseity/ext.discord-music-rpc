import logging
from datetime import datetime, timedelta
from typing import TypedDict

import requests

logger = logging.getLogger(__name__)

BASE_URL = "http://ws.audioscrobbler.com/2.0/"


class CoverArtCacheEntry(TypedDict):
    url: str | None
    timestamp: datetime


_cover_art_cache: dict[str, CoverArtCacheEntry] = {}


def get_lastfm_cover_art(song_title, artist, album=None, api_key=None):
    key = f"{artist}_{song_title}_{album or ''}"

    # check cache
    if key in _cover_art_cache:
        cached_item = _cover_art_cache[key]
        if datetime.now() - cached_item["timestamp"] < timedelta(hours=1):
            return cached_item["url"]

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

    def get_image_url():
        try:
            logger.info(f"Fetching cover art for {artist} - {song_title} from Last.fm")

            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()

            data = response.json()

            if "album" in data and "image" in data["album"]:
                images = data["album"]["image"]

                # get highest quality image
                largest_image = None
                for img in reversed(images):
                    if img["#text"]:
                        largest_image = img["#text"]
                        break

                return largest_image

            return None

        except (requests.RequestException, KeyError, IndexError) as e:
            logger.error(f"Error fetching cover art: {e}")
            return None

    image = get_image_url()

    _cover_art_cache[key] = {
        "url": image,
        "timestamp": datetime.now(),
    }

    return image
