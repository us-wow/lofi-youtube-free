"""제목·곡명 만들기 — 템플릿 + 단어풀 조합. AI 없이 그럴듯한 이름이 나온다.
유료판의 'AI 실패 시 폴백' 로직을 여기선 기본으로 승격한 것.
"""
import json
import random
from pathlib import Path

ASSETS = Path(__file__).parent.parent / "assets"

# 한국어 감성 제목 후보 (명사구 풍경, 1인칭 고독 톤은 일부러 배제)
KR_TITLES = [
    "잠 못 드는 밤의 고요",
    "빗소리에 기대는 새벽",
    "창밖이 흐려지는 시간",
    "천천히 가라앉는 하루",
    "불 꺼진 방의 온기",
    "느린 새벽의 결",
]

# 영어 제목 템플릿 ({g}에 장르가 들어감)
EN_TEMPLATES = [
    "Lofi {g} for late nights",
    "Slow {g} ~ rainy mood",
    "{g} to study & relax",
    "Quiet {g} mix",
    "Late night {g} session",
]


def make_titles(kw):
    g = kw.get("genre", "lofi")
    return {
        "title_kr": random.choice(KR_TITLES),
        "title_en": random.choice(EN_TEMPLATES).format(g=g) + " 🌙",
    }


def make_song_names(kw, n):
    # 형용사 + 명사를 섞어 중복 없이 n개 (예: "Hazy Window", "Soft Drift")
    pools = json.loads((ASSETS / "word_pools.json").read_text(encoding="utf-8"))
    combos = [f"{a} {b}" for a in pools["adj"] for b in pools["noun"]]
    random.shuffle(combos)
    unique = list(dict.fromkeys(combos))  # 혹시 모를 중복 제거
    return unique[:n]
