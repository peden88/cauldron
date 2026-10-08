"""SeaDex curated anime torrent hashes (AniList-indexed)."""
import logging
import re

import httpx

from app.models import TorrentResult

log = logging.getLogger(__name__)


async def search_seadex(anilist_id: str | int | None) -> list[TorrentResult]:
    if not anilist_id or not str(anilist_id).isdigit():
        return []
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            response = await client.get(
                "https://releases.moe/api/collections/entries/records",
                params={"expand": "trs", "filter": f"alID={anilist_id}"},
            )
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("SeaDex lookup failed: %s", exc)
        return []
    results = []
    for entry in payload.get("items", []) if isinstance(payload, dict) else []:
        if not isinstance(entry, dict):
            continue
        for torrent in (entry.get("expand") or {}).get("trs", []):
            if not isinstance(torrent, dict):
                continue
            info_hash = str(torrent.get("infoHash") or "").lower()
            if not re.fullmatch("[0-9a-f]{40}", info_hash):
                continue
            for file in torrent.get("files") or []:
                if not isinstance(file, dict) or not isinstance(file.get("name"), str):
                    continue
                results.append(TorrentResult(
                    title=file["name"],
                    info_hash=info_hash,
                    magnet=f"magnet:?xt=urn:btih:{info_hash}",
                    size_bytes=file.get("length") if isinstance(file.get("length"), int) else None,
                    source="seadex",
                    indexer="SeaDex",
                ))
    return results
