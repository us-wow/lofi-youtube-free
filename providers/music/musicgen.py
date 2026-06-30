"""무료 곡 생성 — MusicGen-small (Meta), 허깅페이스 transformers로 실행.
audiocraft는 설치가 까다로워서, 같은 모델을 더 안정적인 transformers로 돌린다.
첫 호출 때 '작곡 AI 두뇌'를 자동으로 내려받는다(~수 GB, 한 번만).
※ 무거운 import(transformers/torch)는 함수 안에 둬서, 이 파일을 불러오는 것만으론 아무것도 안 받는다.
"""
from pathlib import Path

_model = None
_processor = None
_device = None


def _load():
    global _model, _processor, _device
    if _model is None:
        import torch
        from transformers import AutoProcessor, MusicgenForConditionalGeneration
        _processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        _model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
        # GPU 있으면 GPU로(빠름), 없으면 CPU
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        _model.to(_device)
    return _model, _processor, _device


def generate(prompt, seconds, out_path):
    """prompt(분위기 글)로 seconds초짜리 곡을 만들어 out_path(.wav)에 저장하고 경로를 돌려준다."""
    import scipy.io.wavfile
    model, processor, device = _load()

    inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
    # MusicGen은 1초에 약 50토큰 → 원하는 길이를 토큰 수로 환산
    tokens = int(seconds * 50)
    audio = model.generate(**inputs, max_new_tokens=tokens)

    sr = model.config.audio_encoder.sampling_rate
    data = audio[0, 0].cpu().numpy()
    out = Path(out_path).with_suffix(".wav")
    scipy.io.wavfile.write(str(out), rate=sr, data=data)
    return out
