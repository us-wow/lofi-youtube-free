"""글(키워드·제목·곡명) 로직 테스트 — 무겁지 않아 어디서나 돈다."""
from core import keywords, titles


def test_filter_excludes_bad_topics():
    items = ["jeju travel", "election result", "war news", "autumn cafe"]
    kept = keywords.filter_lofi_friendly(items)
    assert "jeju travel" in kept
    assert "autumn cafe" in kept
    assert "election result" not in kept
    assert "war news" not in kept


def test_seed_fallback_nonempty():
    assert len(keywords.seed_pool()) >= 10


def test_get_keyword_shape():
    kw = keywords.get_keyword()
    assert kw["keyword"] and kw["genre"]


def test_titles_have_kr_and_en():
    t = titles.make_titles({"keyword": "rainy night study", "genre": "lofi jazz"})
    assert t["title_kr"]
    assert t["title_en"]


def test_song_names_unique():
    names = titles.make_song_names({"mood": "calm"}, 5)
    assert len(names) == 5
    assert len(set(names)) == 5
