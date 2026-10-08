from app.anime.matching import anime_episode_matches


def test_absolute_episode_matches():
    assert anime_episode_matches("[SubsPlease] Frieren - 12 [1080p]", 1, 12)
    assert anime_episode_matches("Frieren Episode 012 WEB-DL", 1, 12)
    assert anime_episode_matches("Frieren S01E12", 1, 12)


def test_wrong_episode_and_resolution_rejected():
    assert not anime_episode_matches("Frieren - 13 [1080p]", 1, 12)
    assert not anime_episode_matches("Frieren [1080p]", 1, 12)
    assert not anime_episode_matches("Frieren - 120 [1080p]", 1, 12)


def test_wrong_season_rejected():
    assert not anime_episode_matches("Frieren S02E12", 1, 12)


from app.scrapers.aggregator import _title_matches_anime


def test_fansub_group_and_colon_title():
    assert _title_matches_anime("Cyberpunk: Edgerunners", "[SubsPlease] Cyberpunk Edgerunners - 04 [1080p]")
    assert _title_matches_anime("Cyberpunk: Edgerunners", "Cyberpunk.Edgerunners.S01E04.1080p")
    assert not _title_matches_anime("Monster", "[Group] Monsters - 04 [1080p]")
    assert not _title_matches_anime("Cyberpunk: Edgerunners", "[Group] Cyberpunk 2077 - 04")


def test_dash_episode():
    assert anime_episode_matches("[SubsPlease] Cyberpunk Edgerunners - 04 [1080p]", 1, 4)
    assert not anime_episode_matches("[SubsPlease] Cyberpunk Edgerunners - 05 [1080p]", 1, 4)
