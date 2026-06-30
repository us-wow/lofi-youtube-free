"""provider 로더가 이름을 모듈로 잘 바꾸는지 + 잘못된 이름은 막는지."""
import pytest
from providers import get_provider


def test_loads_text_default():
    text = get_provider("text", "rules")
    assert hasattr(text, "get_keyword")
    assert hasattr(text, "make_titles")
    assert hasattr(text, "make_song_names")


def test_unknown_provider_raises():
    with pytest.raises(ValueError):
        get_provider("text", "nope")
