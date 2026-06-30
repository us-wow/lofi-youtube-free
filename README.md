# 🎵 무료 로파이 유튜브 자동화 (오픈소스)

키워드 한 줄만 정하면 **AI가 곡·배경·영상을 만들어 한 편으로 합쳐주는** 로파이 자동 생성 도구.
**API 키도, 가입도, 결제도 없습니다.** 전부 무료 오픈소스 모델로 돌아갑니다.

> 처음 한 번 설치(또는 Colab 클릭)만 하면, 그 뒤로는 공짜로 무한 생성합니다.

---

## 🚀 가장 쉬운 길 — Colab (설치 0, 내 컴퓨터 용량 0)

아래 버튼을 누르고 ▶ 만 차례로 누르면 끝. 곡 만드는 무거운 작업을 구글 서버가 대신 해줍니다.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/us-wow/lofi-youtube-free/blob/main/colab.ipynb)

*(GPU 무료: 메뉴 → 런타임 → 런타임 유형 변경 → GPU 선택하면 더 빠릅니다)*

## 💻 내 컴퓨터에 설치해서 평생 쓰기

용량이 넉넉하면(모델 약 10GB) 로컬에 깔아 무제한으로 쓸 수 있습니다.

```bash
git clone https://github.com/us-wow/lofi-youtube-free.git
cd lofi-youtube-free
python setup.py        # 부품 설치
python run.py          # output/ 폴더에 영상 1개 생성
```

첫 실행 때 곡·그림 AI 모델이 자동으로 내려받아집니다(수 GB, 한 번만).

---

## 🔧 더 좋게 만들기 — 부품 갈아끼우기

`config.yaml`에서 이름만 바꾸면 됩니다. 무료가 기본, 더 좋은 건 선택.

| 바꾸고 싶은 것 | `config.yaml`에서 | 효과 |
|---|---|---|
| 곡 품질 ↑ | `music: musicgen` → `fal` | 더 좋은 곡(유료 키 필요) |
| 그림 품질 ↑ | `image: sd_turbo` → `flux` | 더 예쁜 배경(GPU 필요) |
| 영상에 진짜 움직임 | `video: ken_burns` → `svd` | 정지화면 대신 실제 영상(GPU) |
| 제목 더 똑똑하게 | `text: rules` → `ollama` | 로컬 AI가 제목 작성(무료) |
| 유튜브 자동 업로드 | `output: local` → `youtube` | 영상 자동 업로드(구글 OAuth) |
| 영상 길게/짧게 | `experience: songs / song_seconds` | 곡 수·길이 조절 |

*(유료/GPU provider는 키나 환경을 연결해야 동작합니다. 안 하면 무료 기본으로 돌아갑니다.)*

---

## ⚖️ 라이선스 (꼭 읽어주세요)

- **이 코드 자체**: MIT (자유롭게 쓰고 고치고 배포 OK)
- **⚠️ 무료 음악 모델(MusicGen)의 가중치는 "비상업(CC-BY-NC)"입니다.** 직접 들어보고 **체험·공유**하는 건 괜찮지만, 만든 곡으로 **돈을 벌려면(유튜브 수익화 등) 라이선스를 반드시 확인하거나 유료 음악 provider로 바꾸세요.**
- 그림 모델(SD-Turbo) 등 각 모델의 라이선스도 사용 전 확인하세요.

각 API(fal.ai, Replicate, PiAPI, Anthropic, YouTube)를 쓸 때는 본인 키와 각자의 약관을 따르세요.
