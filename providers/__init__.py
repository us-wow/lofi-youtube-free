"""provider 로더.
config.yaml에서 고른 이름(rules/musicgen 등)을 실제 파이썬 모듈로 바꿔준다.
'이름만 바꾸면 무료↔유료가 갈리는' 마법이 사실 이 한 함수 덕분이다.
"""
import importlib


def get_provider(kind, name):
    # kind = "text"/"music"/"image"/"video", name = config.yaml에 적은 provider 이름
    try:
        return importlib.import_module(f"providers.{kind}.{name}")
    except ModuleNotFoundError as e:
        # 오타거나 없는 provider면 조용히 죽지 말고 친절히 알려준다
        raise ValueError(f"알 수 없는 {kind} provider: '{name}'") from e
