"""키워드 만들기 — 두 갈래.
1) 구글 트렌드(한국) 실시간 검색어 RSS에서 긁어와 '로파이에 어울리는 것만' 거른다.
2) RSS가 막히거나 비면, 내장 시드 풀(assets/seed_keywords.json)에서 고른다.
둘 다 무료, 키 불필요.
"""
import json
import random
from pathlib import Path

ASSETS = Path(__file__).parent.parent / "assets"

# 로파이 분위기를 깨는 주제는 제외 (슬픈 뉴스가 로파이 제목 되는 사고 방지)
BAD = {
    "정치", "선거", "사건", "사고", "범죄", "재해", "전쟁", "사망", "화재", "참사",
    "election", "war", "crime", "disaster", "death", "politic", "kill", "attack",
}


def seed_pool():
    # RSS가 안 될 때 쓰는 비상용 키워드 풀
    return json.loads((ASSETS / "seed_keywords.json").read_text(encoding="utf-8"))


def filter_lofi_friendly(items):
    # 나쁜 단어가 하나라도 들어간 항목은 버린다
    return [x for x in items if not any(b in x.lower() for b in BAD)]


def trending_kr():
    # 구글 트렌드 한국 실시간 검색어 (네트워크 실패해도 죽지 않게 try)
    try:
        import feedparser  # 함수 안에서 import → 테스트 가볍게
        feed = feedparser.parse("https://trends.google.com/trending/rss?geo=KR")
        return [e.title for e in feed.entries][:20]
    except Exception:
        return []


def get_keyword():
    # 트렌드에서 거른 것 → 비면 시드 풀
    pool = filter_lofi_friendly(trending_kr()) or seed_pool()
    kw = random.choice(pool)
    genres = json.loads((ASSETS / "word_pools.json").read_text(encoding="utf-8"))["genre"]
    return {"keyword": kw, "mood": "calm", "genre": random.choice(genres)}
