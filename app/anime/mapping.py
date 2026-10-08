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
                            if value is not None:
                                fresh[(key, str(value))] = item
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
