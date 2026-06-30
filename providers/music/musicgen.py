"""무료 곡 생성 — MusicGen-small (Meta).
첫 호출 때 '작곡 AI 두뇌'를 자동으로 내려받는다(~수 GB, 한 번만).
※ 무거움: 용량/속도 때문에 Colab이나 GPU PC 권장. CPU도 되지만 느리다.
※ 무거운 import(audiocraft)는 함수 안에 둬서, 이 파일을 불러오는 것만으론 아무것도 안 받는다.
"""
from pathlib import Path

_model = None  # 모델은 한 번만 로드해서 재사용(매번 다시 받으면 느림)


def _get_model():
    global _model
    if _model is None:
        from audiocraft.models import MusicGen  # 무거운 import — 실제 생성할 때만
        _model = MusicGen.get_pretrained("facebook/musicgen-small")
    return _model


def generate(prompt, seconds, out_path):
    """prompt(분위기 글)로 seconds초짜리 곡을 만들어 out_path에 저장하고 경로를 돌려준다."""
    from audiocraft.data.audio import audio_write
    model = _get_model()
    model.set_generation_params(duration=seconds)
    wav = model.generate([prompt])  # [곡개수, 채널, 샘플]
    out = Path(out_path).with_suffix("")          # audio_write가 .wav를 알아서 붙임
    audio_write(str(out), wav[0].cpu(), model.sample_rate, strategy="loudness")
    return Path(str(out) + ".wav")
