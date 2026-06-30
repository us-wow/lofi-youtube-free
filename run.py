"""전체 파이프라인 — python run.py 하면 키워드부터 영상까지 한 방에.
한 단계가 실패해도 가능한 데까진 진행한다(곡 일부 실패해도 나머지로 영상 생성).
"""
import yaml
from pathlib import Path

from providers import get_provider
from core import compose, output


def main():
    cfg = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8"))
    p, exp = cfg["providers"], cfg["experience"]

    # config가 고른 부품 4개 불러오기
    text = get_provider("text", p["text"])
    music = get_provider("music", p["music"])
    image = get_provider("image", p["image"])
    video = get_provider("video", p["video"])

    # 1) 키워드 → 제목 → 곡 이름
    kw = text.get_keyword()
    print("🎯 키워드:", kw["keyword"], "/", kw["genre"])
    titles = text.make_titles(kw)
    names = text.make_song_names(kw, exp["songs"])

    tmp = Path("output/_tmp")
    tmp.mkdir(parents=True, exist_ok=True)

    # 2) 곡 생성 (실패한 곡은 건너뛰고 계속)
    songs = []
    for i in range(exp["songs"]):
        prompt = f"{kw['genre']}, {kw['mood']}, instrumental, no vocals"
        try:
            print(f"🎵 곡 {i+1}/{exp['songs']} 생성 중...")
            songs.append(music.generate(prompt, exp["song_seconds"], tmp / f"song_{i}"))
        except Exception as e:
            print(f"   ⚠️ 곡 {i+1} 실패({e}) — 건너뜀")
    assert songs, "곡이 하나도 안 만들어졌어요 — 음악 provider/설치를 확인하세요."

    # 3) 배경 이미지 → 움직이는 클립
    print("🖼️  배경 그림 생성 중...")
    bg = image.generate(f"{kw['keyword']}, lofi background", tmp / "bg.png")
    print("🎞️  배경 움직이는 중(Ken Burns)...")
    clip = video.animate(bg, 5, tmp / "clip.mp4")

    # 4) 합성 → 저장
    print("🧩 합성 중...")
    video_tmp, ts = compose.compose(
        songs, names[:len(songs)], exp["song_seconds"], clip, tmp / "final.mp4")
    final = output.save_local(video_tmp, ts, titles["title_en"])
    print("✅ 완성:", final)
    print("📝 제목:", titles["title_kr"], "/", titles["title_en"])


if __name__ == "__main__":
    main()
