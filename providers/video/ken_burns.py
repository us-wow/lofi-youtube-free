"""무료 영상 만들기 — Ken Burns 기법.
AI 영상 모델 없이, 이미지 1장을 ffmpeg로 천천히 줌인/팬해서 '움직이는 배경'처럼 만든다.
모델 다운로드 0. 로파이 배경은 거의 정지화면이라 이걸로 충분하다.
"""
import subprocess
from pathlib import Path


def _ffmpeg():
    # ffmpeg 실행파일 경로 (imageio-ffmpeg가 번들로 제공 → 시스템에 ffmpeg 없어도 됨)
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def build_cmd(image_path, seconds, out_path, w=1280, h=720, fps=25, ffmpeg="ffmpeg"):
    """ffmpeg 명령을 만들어서 돌려준다(테스트하기 쉽게 명령 생성과 실행을 분리)."""
    frames = int(seconds * fps)
    # 2배로 키운 뒤 zoompan으로 아주 천천히 줌인 — almost-still 느낌
    vf = (f"scale={w*2}:{h*2},zoompan=z='min(zoom+0.0004,1.3)':"
          f"d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps={fps}")
    return [ffmpeg, "-y", "-loop", "1", "-i", str(image_path),
            "-vf", vf, "-t", str(seconds), "-c:v", "libx264",
            "-pix_fmt", "yuv420p", str(out_path)]


def animate(image_path, seconds, out_path):
    """이미지 1장 → seconds초 움직이는 영상 클립."""
    subprocess.run(build_cmd(image_path, seconds, out_path, ffmpeg=_ffmpeg()), check=True)
    return Path(out_path)
