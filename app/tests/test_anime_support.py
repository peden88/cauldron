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
