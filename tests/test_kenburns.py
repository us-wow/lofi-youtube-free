"""Ken Burns 영상 명령이 제대로 만들어지는지 (ffmpeg 실제 실행/다운로드 없이 명령만 검사)."""
from providers.video import ken_burns


def test_build_cmd_has_zoompan_and_duration():
    cmd = ken_burns.build_cmd("in.png", 5, "out.mp4", w=1280, h=720)
    s = " ".join(cmd)
    assert "zoompan" in s
    assert "in.png" in s
    assert "out.mp4" in s
    assert "-t" in cmd and "5" in cmd
