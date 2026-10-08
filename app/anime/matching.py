"""Conservative anime episode matching, including absolute episode releases."""
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
        if re.search(rf"(?<![a-z0-9])s0*{s}e0*{target}(?!\\d)|(?<!\\d){s}x0*{target}(?!\\d)", value):
            return True
    # Do not confuse 1080p, 2026, or release-group version numbers with episodes.
    for pattern in (
        r"(?:^|[\\s._\\-])(?:ep(?:isode)?[\\s._\\-]*)0*(\\d{1,4})(?!\\d)",
        r"(?:[\\s._\\-]+-+[\\s._\\-]*)0*(\\d{1,4})(?!\\d)",
    ):
        for match in re.finditer(pattern, value):
            if int(match.group(1)) == target:
                return True
    return False
