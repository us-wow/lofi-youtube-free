"""무료 기본 텍스트 provider — AI(LLM) 없이 '규칙 + 단어풀'로만 동작.
설치할 것도, API 키도 없다. 그래서 누구나 clone하면 바로 돈다.
나중에 더 똑똑한 제목을 원하면 config에서 text: ollama(무료 로컬) 또는 claude(유료)로 교체.
"""
from core import keywords, titles


def get_keyword():
    # 오늘의 키워드 1개 (트렌드 RSS → 실패하면 내장 풀)
    return keywords.get_keyword()


def make_titles(kw):
    # 한국어/영어 제목
    return titles.make_titles(kw)


def make_song_names(kw, n):
    # 곡 이름 n개
    return titles.make_song_names(kw, n)
