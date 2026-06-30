"""타임스탬프(유튜브 챕터) 글자 포맷 검사 — 순수 로직이라 가볍다."""
from core import compose


def test_timestamps_format():
    ts = compose.format_timestamps([(0, "A"), (125, "B"), (3725, "C")])
    assert "0:00 A" in ts      # 0초
    assert "2:05 B" in ts      # 125초 = 2분 5초
    assert "1:02:05 C" in ts   # 3725초 = 1시간 2분 5초
