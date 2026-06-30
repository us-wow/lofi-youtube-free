# 무료 오픈소스 로파이 자동화 — 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development (권장) 또는 superpowers:executing-plans 로 task별 구현. 체크박스(`- [ ]`)로 진행 추적.

**Goal:** 유료 API 없이 git clone(또는 Colab)만으로 로파이 영상 1개를 생성하는 파이프라인을 만든다.

**Architecture:** provider 패턴 — 각 단계(text/music/image/video)를 같은 함수 시그니처의 교체 가능한 모듈로 두고, `config.yaml`로 무료↔유료를 전환. `run.py`가 단계를 순서대로 호출, 한 단계가 실패해도 폴백으로 끝까지 간다.

**Tech Stack:** Python 3.10+, audiocraft(MusicGen), diffusers(SD-Turbo), ffmpeg, requests/feedparser, PyYAML, pytest.

설계 근거: `docs/superpowers/specs/2026-06-30-lofi-free-oss-design.md`

---

## 파일 구조 (무엇을 만들고 각 파일의 책임)

```
lofi-youtube-free/
├── README.md              # 빠른시작(로컬/Colab) + 업그레이드 맵 + 라이선스 고지
├── colab.ipynb            # "Open in Colab" 노트북 (clone+install+생성)
├── config.yaml            # provider 선택 + 체험 파라미터 + (빈) 유료 키
├── requirements.txt       # 무료 기본 의존성
├── setup.py               # 의존성/ffmpeg 준비 자동화 + 안내
├── run.py                 # 파이프라인 오케스트레이터 (단계 순서 호출 + 폴백)
├── providers/
│   ├── __init__.py        # config 이름 → provider 모듈 로더 (get_provider)
│   ├── base.py            # 각 provider가 지켜야 할 함수 시그니처(문서/타입)
│   ├── text/rules.py      # 규칙+풀 텍스트 (무료 기본)
│   ├── text/ollama.py     # 업그레이드 스텁 (Ollama)
│   ├── text/claude.py     # 업그레이드 스텁 (Anthropic, 키 필요)
│   ├── music/musicgen.py  # MusicGen-small (무료 기본)
│   ├── music/fal.py       # 업그레이드 스텁 (fal.ai, 키 필요)
│   ├── image/sd_turbo.py  # SD-Turbo (무료 기본)
│   ├── image/flux.py      # 업그레이드 스텁 (FLUX, GPU)
│   ├── image/replicate.py # 업그레이드 스텁 (Replicate, 키 필요)
│   ├── video/ken_burns.py # ffmpeg zoompan (무료 기본)
│   └── video/svd.py       # 업그레이드 스텁 (SVD, GPU)
├── core/
│   ├── keywords.py        # 구글트렌드 RSS + 규칙 필터 + 시드풀 폴백
│   ├── titles.py          # 제목·곡명 템플릿/풀
│   ├── compose.py         # ffmpeg 합성·루프·타임스탬프
│   └── output.py          # 로컬 저장 (+ youtube 옵션 스텁)
├── assets/
│   ├── word_pools.json    # 형용사/명사/장르 풀 (텍스트·곡명용)
│   └── seed_keywords.json # RSS 막힐 때 폴백 키워드 풀
├── examples/              # 샘플 출력 1개 (구현 후 채움)
└── tests/                 # pytest
```

**TDD 적용 원칙:** 순수 로직(keywords 필터·titles·config 로더·ken_burns 명령 생성)은 실패 테스트 → 구현 → 통과. 무거운 모델(musicgen·sd_turbo)은 단위테스트 대신 **smoke test**(작은 입력 1회 실제 실행, 파일 생성 확인)로 검증 — CI 아닌 로컬에서만.

---

## Task 0: 프로젝트 스캐폴딩

**Files:**
- Create: `requirements.txt`, `config.yaml`, `.gitignore`, `providers/__init__.py`, `providers/base.py`, `core/__init__.py`

- [ ] **Step 1: git init + 폴더 생성**

```bash
cd ~/projects/lofi-youtube-free
git init
mkdir -p providers/text providers/music providers/image providers/video core assets examples tests
touch providers/__init__.py providers/text/__init__.py providers/music/__init__.py providers/image/__init__.py providers/video/__init__.py core/__init__.py
```

- [ ] **Step 2: `.gitignore`**

```
__pycache__/
*.pyc
output/
.venv/
models/
*.mp3
*.mp4
*.png
!examples/*
```

- [ ] **Step 3: `requirements.txt` (무료 기본만)**

```
audiocraft==1.3.0
diffusers>=0.27
transformers>=4.40
torch>=2.2
accelerate>=0.29
requests>=2.31
feedparser>=6.0
PyYAML>=6.0
tqdm>=4.66
imageio-ffmpeg>=0.4.9
pytest>=8.0
```

- [ ] **Step 4: `config.yaml`** (설계 8번 그대로)

```yaml
mode: experience
providers:
  text:  rules
  music: musicgen
  image: sd_turbo
  video: ken_burns
output: local
experience:
  songs: 3
  song_seconds: 45
paid_keys:
  fal: ""
  replicate: ""
  anthropic: ""
```

- [ ] **Step 5: `providers/base.py`** — provider 계약 문서화

```python
"""provider 계약 — 각 모듈은 아래 함수를 같은 시그니처로 구현한다.
config.yaml의 이름만 바꾸면 무료↔유료가 교체된다.

text  provider: get_keyword() -> dict, make_titles(kw) -> dict, make_song_names(kw, n) -> list[str]
music provider: generate(prompt, seconds, out_path) -> Path
image provider: generate(prompt, out_path) -> Path
video provider: animate(image_path, seconds, out_path) -> Path
"""
```

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "chore: 프로젝트 스캐폴딩 + provider 계약"
```

---

## Task 1: provider 로더 (config 이름 → 모듈)

**Files:**
- Create: `providers/__init__.py`, `tests/test_loader.py`

- [ ] **Step 1: 실패 테스트** `tests/test_loader.py`

```python
from providers import get_provider

def test_loads_free_defaults():
    text = get_provider("text", "rules")
    assert hasattr(text, "get_keyword")
    music = get_provider("music", "musicgen")
    assert hasattr(music, "generate")

def test_unknown_provider_raises():
    import pytest
    with pytest.raises(ValueError):
        get_provider("text", "nope")
```

- [ ] **Step 2: 실패 확인** — `pytest tests/test_loader.py -v` → FAIL (get_provider 없음)

- [ ] **Step 3: 구현** `providers/__init__.py`

```python
import importlib

def get_provider(kind, name):
    """kind=text/music/image/video, name=config.yaml의 provider 이름."""
    try:
        return importlib.import_module(f"providers.{kind}.{name}")
    except ModuleNotFoundError as e:
        raise ValueError(f"알 수 없는 {kind} provider: '{name}'") from e
```

- [ ] **Step 4: 통과 확인** — `pytest tests/test_loader.py -v` → PASS (rules/musicgen 모듈 생긴 뒤)
- [ ] **Step 5: Commit** — `git commit -am "feat: provider 로더"`

---

## Task 2: 텍스트 provider (rules) + keywords + titles

**Files:**
- Create: `assets/seed_keywords.json`, `assets/word_pools.json`, `core/keywords.py`, `core/titles.py`, `providers/text/rules.py`, `tests/test_text.py`

- [ ] **Step 1: 단어/시드 풀 JSON**

`assets/seed_keywords.json`: 로파이 키워드 폴백 풀 (예: `["rainy night study","late night coding","cozy autumn cafe","winter window","dawn city walk", ...]` 20개)
`assets/word_pools.json`: `{"adj": ["Quiet","Soft","Hazy",...], "noun": ["Hour","Drift","Glow",...], "genre": ["lofi jazz","lofi hiphop","ambient",...]}`

- [ ] **Step 2: 실패 테스트** `tests/test_text.py`

```python
from core import keywords, titles

def test_filter_excludes_bad_topics():
    items = ["jeju travel", "election result", "war news", "autumn cafe"]
    kept = keywords.filter_lofi_friendly(items)
    assert "jeju travel" in kept and "autumn cafe" in kept
    assert "election result" not in kept and "war news" not in kept

def test_seed_fallback_nonempty():
    assert len(keywords.seed_pool()) >= 10

def test_titles_have_kr_and_en():
    t = titles.make_titles({"keyword": "rainy night study", "mood": "calm"})
    assert t["title_kr"] and t["title_en"]

def test_song_names_unique():
    names = titles.make_song_names({"mood": "calm"}, 5)
    assert len(set(names)) == 5
```

- [ ] **Step 3: 실패 확인** — `pytest tests/test_text.py -v` → FAIL

- [ ] **Step 4: 구현**

`core/keywords.py`:
```python
import json, random, requests, feedparser
from pathlib import Path

BAD = {"정치","선거","사건","사고","범죄","재해","전쟁","사망","화재",
       "election","war","crime","disaster","death","politic"}
ASSETS = Path(__file__).parent.parent / "assets"

def seed_pool():
    return json.loads((ASSETS / "seed_keywords.json").read_text(encoding="utf-8"))

def filter_lofi_friendly(items):
    return [x for x in items if not any(b in x.lower() for b in BAD)]

def trending_kr():
    try:
        feed = feedparser.parse("https://trends.google.com/trending/rss?geo=KR")
        return [e.title for e in feed.entries][:20]
    except Exception:
        return []

def get_keyword():
    pool = filter_lofi_friendly(trending_kr()) or seed_pool()
    kw = random.choice(pool)
    return {"keyword": kw, "mood": "calm", "genre": random.choice(
        json.loads((ASSETS / "word_pools.json").read_text(encoding="utf-8"))["genre"])}
```

`core/titles.py`:
```python
import json, random
from pathlib import Path
ASSETS = Path(__file__).parent.parent / "assets"
KR = ["잠 못 드는 밤의 고요","빗소리에 기대는 새벽","창밖이 흐려지는 시간","천천히 가라앉는 하루"]
EN = ["Lofi {g} for late nights","Slow {g} ~ rainy mood","{g} to study & relax","Quiet {g} mix"]

def make_titles(kw):
    g = kw.get("genre", "lofi")
    return {"title_kr": random.choice(KR), "title_en": random.choice(EN).format(g=g) + " 🌙"}

def make_song_names(kw, n):
    pools = json.loads((ASSETS / "word_pools.json").read_text(encoding="utf-8"))
    combos = [f"{a} {b}" for a in pools["adj"] for b in pools["noun"]]
    random.shuffle(combos)
    return combos[:n]
```

`providers/text/rules.py`:
```python
from core import keywords, titles
def get_keyword(): return keywords.get_keyword()
def make_titles(kw): return titles.make_titles(kw)
def make_song_names(kw, n): return titles.make_song_names(kw, n)
```

- [ ] **Step 5: 통과 확인** — `pytest tests/test_text.py -v` → PASS
- [ ] **Step 6: Commit** — `git commit -am "feat: 규칙 기반 텍스트(키워드·제목·곡명)"`

---

## Task 3: 음악 provider (MusicGen) — smoke test

**Files:**
- Create: `providers/music/musicgen.py`, `tests/test_music_smoke.py`

- [ ] **Step 1: 구현** `providers/music/musicgen.py`

```python
from pathlib import Path
_model = None

def _get_model():
    global _model
    if _model is None:
        from audiocraft.models import MusicGen
        _model = MusicGen.get_pretrained("facebook/musicgen-small")  # 첫 호출 시 자동 다운로드
    return _model

def generate(prompt, seconds, out_path):
    import torchaudio
    from audiocraft.data.audio import audio_write
    model = _get_model()
    model.set_generation_params(duration=seconds)
    wav = model.generate([prompt])  # [1, channels, samples]
    out = Path(out_path).with_suffix("")  # audio_write가 .wav 붙임
    audio_write(str(out), wav[0].cpu(), model.sample_rate, strategy="loudness")
    return Path(str(out) + ".wav")
```

- [ ] **Step 2: smoke test** `tests/test_music_smoke.py` (느림 — 로컬에서만, `-m slow`)

```python
import pytest
@pytest.mark.slow
def test_musicgen_makes_file(tmp_path):
    from providers.music import musicgen
    out = musicgen.generate("calm lofi jazz, no vocals", 5, tmp_path / "t")
    assert out.exists() and out.stat().st_size > 0
```

- [ ] **Step 3: 실행** — `pytest tests/test_music_smoke.py -v -m slow` → PASS (첫 실행은 모델 다운로드로 느림). 통과 못 하면 audiocraft 설치/torch 버전 점검.
- [ ] **Step 4: Commit** — `git commit -am "feat: MusicGen 음악 provider"`

---

## Task 4: 이미지 provider (SD-Turbo) — smoke test

**Files:**
- Create: `providers/image/sd_turbo.py`, `tests/test_image_smoke.py`

- [ ] **Step 1: 구현** `providers/image/sd_turbo.py`

```python
from pathlib import Path
_pipe = None
NEG = "text, letters, words, logos, watermark, signature"
SUFFIX = ", lofi illustration, cozy, soft light, extreme bokeh, no text"

def _get_pipe():
    global _pipe
    if _pipe is None:
        import torch
        from diffusers import AutoPipelineForText2Image
        device = "mps" if torch.backends.mps.is_available() else (
                 "cuda" if torch.cuda.is_available() else "cpu")
        _pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sd-turbo")
        _pipe = _pipe.to(device)
    return _pipe

def generate(prompt, out_path):
    pipe = _get_pipe()
    img = pipe(prompt + SUFFIX, negative_prompt=NEG,
               num_inference_steps=1, guidance_scale=0.0).images[0]
    out = Path(out_path)
    img.save(out)
    return out
```

- [ ] **Step 2: smoke test** `tests/test_image_smoke.py`

```python
import pytest
@pytest.mark.slow
def test_sdturbo_makes_png(tmp_path):
    from providers.image import sd_turbo
    out = sd_turbo.generate("rainy night cafe window", tmp_path / "bg.png")
    assert out.exists() and out.stat().st_size > 0
```

- [ ] **Step 3: 실행** — `pytest -m slow tests/test_image_smoke.py -v` → PASS
- [ ] **Step 4: Commit** — `git commit -am "feat: SD-Turbo 이미지 provider"`

---

## Task 5: 영상 provider (Ken Burns / ffmpeg)

**Files:**
- Create: `providers/video/ken_burns.py`, `tests/test_kenburns.py`

- [ ] **Step 1: 실패 테스트** (명령 생성 로직만 단위 테스트) `tests/test_kenburns.py`

```python
from providers.video import ken_burns

def test_build_cmd_has_zoompan_and_duration():
    cmd = ken_burns.build_cmd("in.png", 5, "out.mp4", w=1280, h=720)
    s = " ".join(cmd)
    assert "zoompan" in s and "in.png" in s and "out.mp4" in s
    assert "-t" in cmd and "5" in cmd
```

- [ ] **Step 2: 실패 확인** — `pytest tests/test_kenburns.py -v` → FAIL

- [ ] **Step 3: 구현** `providers/video/ken_burns.py`

```python
import subprocess
from pathlib import Path
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()  # ffmpeg 자동 번들

def build_cmd(image_path, seconds, out_path, w=1280, h=720, fps=25):
    frames = int(seconds * fps)
    # 천천히 줌인하며 약간 팬 — almost-still 느낌
    vf = (f"scale={w*2}:{h*2},zoompan=z='min(zoom+0.0004,1.3)':"
          f"d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps={fps}")
    return [FFMPEG, "-y", "-loop", "1", "-i", str(image_path),
            "-vf", vf, "-t", str(seconds), "-c:v", "libx264",
            "-pix_fmt", "yuv420p", str(out_path)]

def animate(image_path, seconds, out_path):
    subprocess.run(build_cmd(image_path, seconds, out_path), check=True)
    return Path(out_path)
```

- [ ] **Step 4: 통과 확인** — `pytest tests/test_kenburns.py -v` → PASS
- [ ] **Step 5: smoke (선택)** — 실제 png 한 장으로 `animate()` 돌려 mp4 생성 확인
- [ ] **Step 6: Commit** — `git commit -am "feat: Ken Burns 영상 provider(ffmpeg)"`

---

## Task 6: 합성 (core/compose) — ffmpeg

**Files:**
- Create: `core/compose.py`, `tests/test_compose.py`

- [ ] **Step 1: 실패 테스트** (타임스탬프 포맷 로직) `tests/test_compose.py`

```python
from core import compose

def test_timestamps_format():
    ts = compose.format_timestamps([(0,"A"),(125,"B"),(3725,"C")])
    assert "0:00 A" in ts and "2:05 B" in ts and "1:02:05 C" in ts
```

- [ ] **Step 2: 실패 확인** — `pytest tests/test_compose.py -v` → FAIL

- [ ] **Step 3: 구현** `core/compose.py`

```python
import subprocess, tempfile
from pathlib import Path
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FFPROBE = FFMPEG.replace("ffmpeg", "ffprobe")  # 없으면 duration은 mutagen 등으로 대체

def format_timestamps(items):
    lines = []
    for sec, name in items:
        s = int(sec); h, m, s = s//3600, (s%3600)//60, s%60
        stamp = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
        lines.append(f"{stamp} {name}")
    return "\n".join(lines)

def _concat_audio(mp3s, out):
    lst = Path(tempfile.mktemp(suffix=".txt"))
    lst.write_text("".join(f"file '{Path(p).resolve()}'\n" for p in mp3s))
    subprocess.run([FFMPEG,"-y","-f","concat","-safe","0","-i",str(lst),
                    "-c:a","aac","-b:a","192k",str(out)], check=True)

def compose(song_paths, song_names, clip_path, out_path):
    """곡들 이어붙여(2바퀴) + ken_burns 클립 무한루프 → mp4 + 타임스탬프."""
    audio = Path(out_path).with_suffix(".m4a")
    loop = list(song_paths) + list(song_paths)   # 2바퀴
    _concat_audio(loop, audio)
    subprocess.run([FFMPEG,"-y","-stream_loop","-1","-i",str(clip_path),
                    "-i",str(audio),"-map","0:v","-map","1:a","-shortest",
                    "-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",str(out_path)],
                   check=True)
    # 타임스탬프 (곡 길이 누적) — 길이는 ffprobe 또는 곡 메타로
    return Path(out_path)
```

(실제 곡 길이 측정 → 타임스탬프 누적은 구현 시 ffprobe 호출로 채운다. ffprobe 없으면 mutagen로 대체.)

- [ ] **Step 4: 통과 확인** — `pytest tests/test_compose.py -v` → PASS
- [ ] **Step 5: Commit** — `git commit -am "feat: ffmpeg 합성 + 타임스탬프"`

---

## Task 7: 출력 (core/output)

**Files:**
- Create: `core/output.py`

- [ ] **Step 1: 구현** — 로컬 저장(기본) + youtube 스텁

```python
from pathlib import Path
import shutil

def save_local(video_path, timestamps_text, title):
    out_dir = Path("output"); out_dir.mkdir(exist_ok=True)
    safe = "".join(c for c in title if c.isalnum() or c in " _-")[:40].strip() or "lofi"
    final = out_dir / f"{safe}.mp4"
    shutil.move(str(video_path), final)
    (out_dir / f"{safe}_timestamps.txt").write_text(timestamps_text, encoding="utf-8")
    return final

def upload_youtube(*a, **k):
    raise NotImplementedError("YouTube 업로드는 업그레이드: config output: youtube + OAuth 설정")
```

- [ ] **Step 2: Commit** — `git commit -am "feat: 로컬 출력"`

---

## Task 8: 오케스트레이터 (run.py) + end-to-end

**Files:**
- Create: `run.py`

- [ ] **Step 1: 구현** `run.py`

```python
import yaml
from pathlib import Path
from providers import get_provider
from core import compose, output

def main():
    cfg = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8"))
    p = cfg["providers"]; exp = cfg["experience"]
    text  = get_provider("text",  p["text"])
    music = get_provider("music", p["music"])
    image = get_provider("image", p["image"])
    video = get_provider("video", p["video"])

    kw = text.get_keyword();        print("키워드:", kw["keyword"])
    titles = text.make_titles(kw)
    names  = text.make_song_names(kw, exp["songs"])

    tmp = Path("output/_tmp"); tmp.mkdir(parents=True, exist_ok=True)
    songs = []
    for i, name in enumerate(names):
        prompt = f"{kw['genre']}, {kw['mood']}, instrumental, no vocals"
        try:
            songs.append(music.generate(prompt, exp["song_seconds"], tmp / f"song_{i}.mp3"))
        except Exception as e:
            print(f"곡 {i} 실패({e}) — 건너뜀")
    assert songs, "곡 생성 0개 — 음악 provider 점검"

    bg = image.generate(f"{kw['keyword']}, lofi background", tmp / "bg.png")
    clip = video.animate(bg, 5, tmp / "clip.mp4")

    final_tmp = compose.compose(songs, names, clip, tmp / "final.mp4")
    ts = compose.format_timestamps([(0, names[0])])  # 실제 누적은 compose에서 반환하도록 연결
    final = output.save_local(final_tmp, ts, titles["title_en"])
    print("완성:", final)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: end-to-end smoke** — `python run.py` → `output/`에 mp4 1개 생성 확인 (CPU면 느림; `config.yaml`에서 songs:1, song_seconds:15로 줄여 빠르게 검증)
- [ ] **Step 3: Commit** — `git commit -am "feat: run.py 파이프라인 통합"`

---

## Task 9: 업그레이드 provider 스텁 (키 있으면 동작)

**Files:**
- Create: `providers/music/fal.py`, `providers/image/replicate.py`, `providers/image/flux.py`, `providers/text/ollama.py`, `providers/text/claude.py`, `providers/video/svd.py`

- [ ] **Step 1: 각 스텁** — 같은 시그니처, 키/GPU 없으면 친절한 에러. 예 `providers/music/fal.py`:

```python
import os
from pathlib import Path
def generate(prompt, seconds, out_path):
    key = os.getenv("FAL_KEY") or _cfg_key("fal")
    if not key:
        raise RuntimeError("fal 사용하려면 config.yaml paid_keys.fal 에 키를 넣으세요. (무료는 music: musicgen)")
    import fal_client  # 업그레이드 시 pip install fal-client
    ...  # fal.ai 호출 (유료판 minimax_client 참고)
    return Path(out_path)
```

나머지(replicate/flux/ollama/claude/svd)도 동일 패턴: 키/GPU 확인 → 없으면 "무료 기본 쓰세요" 안내.

- [ ] **Step 2: Commit** — `git commit -am "feat: 유료/고품질 업그레이드 provider 스텁"`

---

## Task 10: setup + README + Colab

**Files:**
- Create: `setup.py`, `README.md`, `colab.ipynb`

- [ ] **Step 1: `setup.py`** — `pip install -r requirements.txt` 안내 + ffmpeg(imageio-ffmpeg 번들 확인) + "이제 python run.py" 출력. CPU 감지 시 config를 짧게 자동 조정 안내.

- [ ] **Step 2: `README.md`** — 설계 10번 업그레이드 맵 + 빠른시작 2경로 + **라이선스 고지**(MusicGen 비상업·체험용, 수익화 시 확인 / 코드 자체는 MIT). "Open in Colab" 배지 포함.

- [ ] **Step 3: `colab.ipynb`** — 칸1: `!git clone ... && pip install -r requirements.txt`, 칸2: `!python run.py`, 칸3: 결과 mp4 미리보기. 사용자는 ▶만.

- [ ] **Step 4: 샘플 1개 생성해 `examples/`에 넣기**

- [ ] **Step 5: Commit** — `git commit -am "docs: README(업그레이드 맵·라이선스) + setup + Colab"`

---

## Self-Review

- **Spec 커버리지:** 두 경로(로컬/Colab=Task10) · provider 패턴(Task1·9) · 무료 4종(Task2~5) · 합성/출력(Task6·7) · 첫실행 폴백(Task8 try/except) · 라이선스 고지(Task10) · 업그레이드 맵(Task10) — 모두 task 있음. ✅
- **placeholder:** compose의 타임스탬프 누적과 fal 스텁 본문은 "구현 시 채움"으로 남김 — 핵심 시그니처·검증은 명시했고, 외부 라이브러리 정확 호출은 구현 시점에 문서 확인이 정직. 그 외 TBD 없음.
- **타입 일관성:** provider 시그니처(generate/animate/get_keyword/make_titles/make_song_names)가 base.py·run.py·각 provider에서 동일. ✅
- **알려진 리스크:** compose의 타임스탬프 실제 누적(곡 길이 측정)은 Task6 구현 시 ffprobe로 연결 — run.py Step1의 `format_timestamps([(0, names[0])])`는 임시, compose가 (timestamps) 반환하도록 마무리.
