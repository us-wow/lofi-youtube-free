"""합성 — 곡들을 이어 붙이고(2바퀴), 짧은 배경 클립을 무한 반복해 한 영상으로 굽는다.
타임스탬프(유튜브 챕터)는 곡 길이가 일정하다고 보고 순서대로 누적해 만든다.
무거운 모델 없음. ffmpeg만 쓴다.
"""
import subprocess
import tempfile
from pathlib import Path


def _ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def format_timestamps(items):
    """[(시작초, 곡이름), ...] → 유튜브 챕터 텍스트. 1시간 넘으면 H:MM:SS."""
    lines = []
    for sec, name in items:
        s = int(sec)
        h, m, s = s // 3600, (s % 3600) // 60, s % 60
        stamp = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
        lines.append(f"{stamp} {name}")
    return "\n".join(lines)


def _concat_audio(audio_paths, out_path, ffmpeg):
    # ffmpeg concat demuxer로 여러 곡을 한 오디오로 이어붙임
    lst = Path(tempfile.mktemp(suffix=".txt"))
    lst.write_text("".join(f"file '{Path(p).resolve()}'\n" for p in audio_paths))
    subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c:a", "aac", "-b:a", "192k", str(out_path)], check=True)
    lst.unlink(missing_ok=True)


def compose(song_paths, song_names, song_seconds, clip_path, out_path):
    """곡들(2바퀴) + 배경 클립 루프 → mp4. (영상경로, 타임스탬프텍스트) 반환."""
    ffmpeg = _ffmpeg()
    loop_paths = list(song_paths) + list(song_paths)   # 2바퀴
    loop_names = list(song_names) + list(song_names)

    audio = Path(out_path).with_suffix(".m4a")
    _concat_audio(loop_paths, audio, ffmpeg)

    # 5초 배경 클립을 무한 반복하고 오디오 길이에 맞춰 자른다(-shortest)
    subprocess.run([ffmpeg, "-y", "-stream_loop", "-1", "-i", str(clip_path),
                    "-i", str(audio), "-map", "0:v", "-map", "1:a", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    str(out_path)], check=True)

    items = [(i * song_seconds, n) for i, n in enumerate(loop_names)]
    return Path(out_path), format_timestamps(items)
