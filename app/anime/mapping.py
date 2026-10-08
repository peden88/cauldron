"""Anime identity mapping sourced from the same Fribb dataset as Comet.

A bounded, shared in-memory index is refreshed at most once every 24 hours.
If mapping is unavailable, callers continue with Kitsu metadata.
"""
import asyncio
import logging
import time

import httpx

log = logging.getLogger(__name__)
URL = "https://raw.githubusercontent.com/Fribb/anime-lists/refs/heads/master/anime-list-full.json"
_index = {}
_last_attempt = 0.0
_lock = asyncio.Lock()
PROVIDERS = {"kitsu": "kitsu_id", "mal": "mal_id", "myanimelist": "mal_id", "anilist": "anilist_id", "anidb": "anidb_id", "imdb": "imdb_id"}


async def lookup(provider: str, identifier: str) -> dict:
    global _index, _last_attempt
    if provider not in PROVIDERS or not identifier:
        return {}
    if time.monotonic() - _last_attempt > 86400:
        async with _lock:
            if time.monotonic() - _last_attempt > 86400:
                _last_attempt = time.monotonic()
                try:
                    async with httpx.AsyncClient(timeout=35) as client:
                        response = await client.get(URL)
                        response.raise_for_status()
                        entries = response.json()
                    if not isinstance(entries, list):
                        raise ValueError("Invalid anime mapping payload")
                    fresh = {}
                    for item in entries:
                        if not isinstance(item, dict):
                            continue
                        for key, field in PROVIDERS.items():
                            value = item.get(field)
                            for identity in value if isinstance(value, list) else [value]:
                                if identity is not None:
                                    fresh[(key, str(identity))] = item
                    if fresh:
                        _index = fresh
                except (httpx.HTTPError, ValueError, TypeError) as exc:
                    log.warning("Anime mapping refresh failed: %s", exc)
    return _index.get((provider, str(identifier)), {})


def titles_for(entry: dict) -> list[str]:
    values = []
    for field in ("title", "title_english", "title_romaji", "title_native"):
        value = entry.get(field)
        if isinstance(value, str) and value.strip():
            values.append(value.strip())
    for field in ("synonyms", "titles"):
        value = entry.get(field)
        if isinstance(value, list):
            values.extend(v for v in value if isinstance(v, str) and v.strip())
    return list(dict.fromkeys(values))


_KITSU_EPISODES_URL = "https://raw.githubusercontent.com/TheBeastLT/stremio-kitsu-anime/master/static/data/imdb_mapping.json"
_episode_index = {}
_episode_attempt = 0.0
_episode_lock = asyncio.Lock()


async def kitsu_episode_mapping(kitsu_id: str) -> dict:
    """Return Comet-compatible Kitsu-to-IMDb season and episode offsets."""
    global _episode_index, _episode_attempt
    if time.monotonic() - _episode_attempt > 86400:
        async with _episode_lock:
            if time.monotonic() - _episode_attempt > 86400:
                _episode_attempt = time.monotonic()
                try:
                    async with httpx.AsyncClient(timeout=35) as client:
                        response = await client.get(_KITSU_EPISODES_URL)
                        response.raise_for_status()
                        rows = response.json()
                    if not isinstance(rows, list):
                        raise ValueError("Invalid Kitsu episode mapping")
                    _episode_index = {str(v["kitsu_id"]): v for v in rows if isinstance(v, dict) and v.get("kitsu_id") is not None}
                except (httpx.HTTPError, ValueError, TypeError) as exc:
                    log.warning("Kitsu episode mapping unavailable: %s", exc)
    return _episode_index.get(str(kitsu_id), {})
