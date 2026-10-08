"""Anime release episode validation.

Only accept an explicitly marked episode number; never infer an episode
from resolution, year, release version, or a bare number in a title.
"""
import re


def anime_episode_matches(title: str, season: int | str | None, episode: int | str | None) -> bool:
    if episode is None:
        return True
    try:
        target = int(episode)
    except (TypeError, ValueError):
        return False
    if target < 0:
        return False
    value = title.lower()
    if season is not None:
        try:
            s = int(season)
        except (TypeError, ValueError):
            return False
        if re.search(rf"(?<![a-z0-9])s0*{s}e0*{target}(?![0-9])|(?<![0-9]){s}x0*{target}(?![0-9])", value):
            return True
    # Anime releases often use '[Group] Title - 12 [1080p]'.
    for pattern in (
        r"(?:^|[^a-z0-9])(?:ep(?:isode)?[ ._-]*)0*([0-9]{1,4})(?![0-9])",
        r"(?:^|\\s)-\\s*0*([0-9]{1,4})(?![0-9])",
    ):
        if any(int(m.group(1)) == target for m in re.finditer(pattern, value)):
            return True
    return False
