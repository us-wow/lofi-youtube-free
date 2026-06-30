"""결과물 저장 — 기본은 로컬 파일. (YouTube 자동 업로드는 업그레이드 옵션)"""
import shutil
from pathlib import Path


def save_local(video_path, timestamps_text, title):
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    # 파일명에 못 쓰는 글자 제거
    safe = "".join(c for c in title if c.isalnum() or c in " _-").strip()[:40] or "lofi"
    final = out_dir / f"{safe}.mp4"
    shutil.move(str(video_path), final)
    (out_dir / f"{safe}_timestamps.txt").write_text(timestamps_text, encoding="utf-8")
    return final


def upload_youtube(*args, **kwargs):
    raise NotImplementedError(
        "YouTube 자동 업로드는 업그레이드 기능입니다. "
        "config.yaml의 output을 youtube로 바꾸고 구글 OAuth를 설정하세요."
    )
