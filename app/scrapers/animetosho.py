"""AnimeTosho Torznab-compatible anime torrent search."""
import logging
import re
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

import httpx

from app.models import TorrentResult
from app.scrapers.base import Scraper

logger = logging.getLogger(__name__)
ATTR_NS = "{http://torznab.com/schemas/2015/feed}"


class AnimeToshoScraper(Scraper):
    name = "animetosho"

    async def search(self, query: str, *, imdb_id=None, season=None, episode=None, media_type=None):
        if media_type != "anime":
            return []
        try:
            async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
                response = await client.get(
                    "https://feed.animetosho.org/api",
                    params={"t": "search", "q": query, "offset": 0, "limit": 100},
                )
                response.raise_for_status()
            root = ET.fromstring(response.content)
        except (httpx.HTTPError, ET.ParseError) as exc:
            logger.warning("AnimeTosho search failed: %s", exc)
            return []

        results = []
        for item in root.findall(".//item"):
            title = item.findtext("title")
            attributes = {
                node.get("name"): node.get("value")
                for node in item.findall(f".//{ATTR_NS}attr")
            }
            info_hash = (attributes.get("infohash") or "").lower()
            if not title or not re.fullmatch(r"[0-9a-f]{40}", info_hash):
                continue
            magnet = attributes.get("magneturl") or f"magnet:?xt=urn:btih:{info_hash}"
            try:
                size = int(attributes["size"]) if attributes.get("size") else None
                seeds = int(attributes["seeders"]) if attributes.get("seeders") else None
            except (TypeError, ValueError):
                size = seeds = None
            results.append(TorrentResult(
                title=title,
                info_hash=info_hash,
                magnet=magnet,
                size_bytes=size,
                seeders=seeds,
                source="animetosho",
                indexer="AnimeTosho",
            ))
        return results
