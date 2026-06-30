"""provider 계약(인터페이스) 설명.

각 provider 모듈은 아래 함수를 '같은 이름·같은 입출력'으로 구현하기만 하면 된다.
그러면 config.yaml에서 이름만 바꿔도 서로 갈아끼워진다. (무료↔유료 교체의 핵심 약속)

- text  provider:
    get_keyword()            -> dict   예: {"keyword": "...", "mood": "...", "genre": "..."}
    make_titles(kw)          -> dict   예: {"title_kr": "...", "title_en": "..."}
    make_song_names(kw, n)   -> list[str]
- music provider:
    generate(prompt, seconds, out_path) -> Path   (만들어진 음악 파일 경로)
- image provider:
    generate(prompt, out_path)          -> Path   (만들어진 이미지 파일 경로)
- video provider:
    animate(image_path, seconds, out_path) -> Path (이미지를 움직이게 한 영상 경로)
"""
