# 무료 오픈소스 로파이 자동화 — 설계 문서

- 날짜: 2026-06-30
- 상태: 설계 합의 완료 (구현 계획 대기)
- 원본(유료판): `~/projects/lofi-youtube/` — 이 문서는 그걸 **완전 무료 오픈소스 쌍둥이**로 재현하는 설계다.

---

## 1. 한 줄 목표

유료 API(fal.ai MiniMax · Replicate Flux · PiAPI Kling · Anthropic Claude)를 **전부 무료 로컬 오픈소스로 갈아끼운** 로파이 자동화 도구. 누구나 GitHub에서 받아 **API 키·가입·결제 0으로 곡·영상을 생성**하고, 더 좋게 하고 싶으면 부품(provider)만 갈아끼운다.

## 2. 성공 기준 (가장 중요 — 1순위)

1. **git clone(또는 Colab 버튼) → 명령 하나 → `output/`에 로파이 영상 1개.** 키 입력·로그인 없음.
2. **첫 실행이 막히지 않는다.** 모델은 자동 다운로드, 진행 상황 표시, 에러는 사람이 읽을 수 있는 안내로.
3. **"뭘 바꾸면 뭐가 좋아지나"가 README와 `config.yaml` 주석에 명확.** (유료/고품질 업그레이드 경로)
4. 제작자(유선우)의 키·계정·실명·전화번호·개인 경로가 **일절 들어가지 않는다.**

## 3. 비목표 (YAGNI — 하지 않는 것)

- 유료판과 **동일 품질** 재현 ✗ (체험급이면 충분)
- YouTube 자동 업로드를 기본값으로 ✗ → 기본은 **로컬 mp4 출력**, 업로드는 옵션
- 운영 전용 기능 제외: iMessage 알림, SSD 아카이브, preflight 7항목, 쇼츠 생성, 월간 플래너
- **새 기능 추가 ✗** — 유료판 흐름을 무료로 재현만 한다

## 4. 두 가지 실행 경로 (둘 다 GitHub 레포 하나에)

| | Colab판 | 로컬판 |
|---|---|---|
| 설치 | 0 (브라우저) | 한 번(수 GB) |
| 속도 | 빠름(무료 GPU) | 느림(보통 CPU) |
| 필요 | 구글 계정 | 파이썬 + ffmpeg |
| 지속성 | 세션 종료 시 초기화 | 평생 보관·무한 |
| 용도 | "지금 당장 구경" | "평생 쓰기" |

- Colab판: README 상단 **"Open in Colab" 배지** → 노트북 첫 칸이 `git clone` + 의존성 설치 자동 → 다음 칸 ▶ 로 생성.
- 로컬판: `setup` 스크립트가 의존성·ffmpeg 준비 → `python run.py`.

## 5. 핵심 구조 — provider 패턴

각 단계를 **인터페이스**로 분리하고, **무료 구현이 기본 / 유료·고품질은 끼우기**. `config.yaml` 한 줄로 전환.

| 단계 | 무료 기본 (clone하면 동작) | 업그레이드 (원하면) | 라이선스 메모 |
|---|---|---|---|
| 텍스트(키워드·제목·곡명) | **규칙 + 단어풀** (LLM·설치 0) | Ollama(무료 로컬) → Claude(유료) | 자유 |
| 음악 | **MusicGen-small** | MusicGen-medium / fal.ai(유료) | ⚠️ 가중치 CC-BY-NC(비상업) |
| 이미지 | **SD-Turbo** 또는 SD 1.5 | FLUX.1-schnell(GPU) / Replicate(유료) | SD1.5=OpenRAIL(상업OK), FLUX-schnell=Apache2 |
| 영상 | **Ken Burns** (ffmpeg 줌/팬, 모델 0) | SVD·AnimateDiff(GPU) / Kling(유료) | ffmpeg 자유 |
| 합성 | ffmpeg (고정) | — | LGPL/GPL |
| 출력 | **로컬 mp4** | YouTube 업로드(OAuth) | — |

**인터페이스 계약(provider가 지켜야 할 함수):**
- `text`: `get_keyword()` · `make_titles(kw)` · `make_song_names(n)`
- `music`: `generate(prompt, seconds) -> mp3_path`
- `image`: `generate(prompt) -> png_path`
- `video`: `animate(image_path, seconds) -> mp4_path`

무료 구현이든 유료 구현이든 **같은 함수 시그니처**만 지키면 `config.yaml`에서 이름만 바꿔 교체된다.

## 6. 단계별 무료 기본 구현

- **텍스트**: 키워드는 구글 트렌드 RSS(무료) + 규칙 필터(정치·사건·재해 제외). RSS가 막히면 **내장 시드 단어풀**로 폴백. 제목·곡명은 템플릿 + 형용사·명사 풀 조합(유료판에 이미 있는 폴백 로직을 기본으로 승격).
- **음악**: MusicGen-small. 체험 기본값 **곡 2~3개 · 각 30~60초** (CPU에서도 몇 분 내). `is_instrumental` 보컬 없음.
- **이미지**: SD-Turbo(1-step, 가장 빠름) 배경 1장. 글자 깨짐 방지 프롬프트("no text… extreme bokeh") 유지.
- **영상**: Ken Burns — 이미지 1장을 ffmpeg `zoompan`으로 천천히 줌/팬해 5초 클립. 모델 0. (로파이 배경은 거의 정지화면이라 충분)
- **합성**: ffmpeg — 곡 무음 제거 → 이어붙이기 → Ken Burns 클립 `-stream_loop -1` 루프 → `-shortest` → 새벽빛 컬러그레이딩 + 페이드 → mp4 + 타임스탬프(.txt).
- **출력**: `output/`에 mp4 + 타임스탬프 저장. 끝.

## 7. 레포 구조

```
lofi-youtube-free/
├── README.md              # 빠른시작(로컬/Colab) + 업그레이드 맵 + 라이선스 고지
├── colab.ipynb            # "Open in Colab" 노트북
├── config.yaml            # provider 선택 (free ↔ paid)
├── requirements.txt       # 무료 기본 의존성
├── setup.py               # 의존성 + ffmpeg 준비 자동화(또는 setup.sh)
├── run.py                 # python run.py → 끝까지 한 방
├── providers/
│   ├── text/   rules.py     ( ollama.py · claude.py )
│   ├── music/  musicgen.py  ( fal.py )
│   ├── image/  sd_turbo.py  ( flux.py · replicate.py )
│   └── video/  ken_burns.py ( svd.py · kling.py )
├── core/
│   ├── keywords.py        # 구글트렌드 RSS + 규칙 필터 + 시드풀 폴백
│   ├── titles.py          # 제목·곡명 템플릿/풀
│   ├── compose.py         # ffmpeg 합성·루프·타임스탬프
│   └── output.py          # 로컬 저장 / youtube 옵션
├── assets/                # 폰트, 단어풀 json
└── examples/              # 샘플 영상 1개(안 돌려봐도 결과 감 잡게)
```

## 8. `config.yaml` 예시

```yaml
mode: experience        # experience(가벼움) | full(고품질)
providers:
  text:  rules          # rules | ollama | claude
  music: musicgen       # musicgen | fal
  image: sd_turbo       # sd_turbo | flux | replicate
  video: ken_burns      # ken_burns | svd | kling
output: local           # local | youtube
experience:
  songs: 3
  song_seconds: 45
paid_keys:              # 비워두면 무료 provider만 동작
  fal: ""
  replicate: ""
  anthropic: ""
```

## 9. 실행 흐름 (`run.py`)

1. `config.yaml` 로드 → provider 선택
2. `keywords.get_keyword()` — 오늘 키워드 1개
3. `titles` — 제목·곡명 생성
4. `music.generate()` × N — 곡 N개
5. `image.generate()` — 배경 이미지 1장
6. `video.animate()` — 이미지 → 움직이는 5초 클립(Ken Burns)
7. `compose` — 곡들 + 클립 루프 → mp4 + 타임스탬프
8. `output` — `output/`에 저장 (또는 YouTube)

## 10. README 업그레이드 맵 (스레드에 그대로 인용 가능하게)

- 음악 더 좋게 → `config.yaml`의 `music: musicgen` → `fal`(유료 키) 또는 `mode: full`
- 그림 더 좋게 → `image: sd_turbo` → `flux`(GPU) 또는 `replicate`(유료)
- 영상 진짜 움직임 → `video: ken_burns` → `svd`(GPU) 또는 `kling`(유료)
- 제목 더 똑똑하게 → `text: rules` → `ollama`(무료 로컬) 또는 `claude`(유료)
- 유튜브 자동 업로드 → `output: local` → `youtube` (구글 OAuth 1회)

## 11. 첫 실행 경험(First-run) 설계

- 의존성·모델 자동 다운로드 + 진행바(tqdm). "지금 1.5GB 받는 중…" 식 안내.
- ffmpeg 없으면: 설치 안내 출력(또는 `imageio-ffmpeg` 번들로 우회).
- CPU 감지 시 자동으로 `mode: experience`(짧게) + 예상 소요시간 안내("CPU라 곡 1개에 ~3분 걸려요").
- 어느 단계가 실패해도 **유료판처럼 폴백**(곡 실패→기존 샘플, 텍스트 실패→풀)으로 끝까지 가서 영상 1개는 나오게.

## 12. 리스크 / 트레이드오프 (정직하게)

- **CPU 음악 생성이 느리다** — 그래서 기본 "짧게" + Colab(무료 GPU) 병행 권장.
- **모델 용량이 크다**(수 GB) — 첫 다운로드 한 번. README에 명시.
- **MusicGen 가중치는 CC-BY-NC(비상업)** — 체험·공유는 OK, 만든 곡으로 **수익화하려면 라이선스 확인/유료 전환 필요.**
  - **결정(2026-06-30): MusicGen으로 가고 README에 "체험용·비상업, 수익화 시 라이선스 확인"을 굵게 고지한다.** 상업이 필요해지면 음악 provider만 교체(별도 과제).
- 이미지·영상 모델 라이선스는 상업 가능한 것 우선(SD1.5 OpenRAIL / FLUX-schnell Apache2).

## 13. 다음 단계

이 설계 승인 후 → 구현 계획(writing-plans)으로 단계 분해 → provider 한 개씩 구현·검증.
