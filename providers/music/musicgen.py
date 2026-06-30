"""무료 곡 생성 — MusicGen (Meta), 허깅페이스 transformers로 실행.
모델 크기는 config.yaml의 experience.music_model로 고른다(기본 medium).
  - small : 빠르지만 거침(데모급)
  - medium: 권장 — 곡다운 곡
  - large : 최고 품질·가장 무거움
첫 호출 때 모델을 자동 다운로드(medium ~6GB). 무거운 import는 함수 안에 둔다.
"""
from pathlib import Path

_model = None
_processor = None
_device = None


def _model_name():
    # config.yaml에서 모델 크기를 읽는다. 없거나 실패하면 medium.
    import yaml
    root = Path(__file__).parent.parent.parent
    try:
        cfg = yaml.safe_load((root / "config.yaml").read_text(encoding="utf-8"))
        size = (cfg.get("experience") or {}).get("music_model", "medium")
    except Exception:
        size = "medium"
    return f"facebook/musicgen-{size}"


def _load():
    global _model, _processor, _device
    if _model is None:
        import torch
        from transformers import AutoProcessor, MusicgenForConditionalGeneration
        name = _model_name()
        _processor = AutoProcessor.from_pretrained(name)
        _model = MusicgenForConditionalGeneration.from_pretrained(name)
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        _model.to(_device)
    return _model, _processor, _device


def generate(prompt, seconds, out_path):
    """prompt(분위기 글)로 seconds초짜리 곡을 만들어 out_path(.wav)에 저장하고 경로를 돌려준다."""
    import scipy.io.wavfile
    model, processor, device = _load()

    inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
    # musicgen-small은 ~30초(1500토큰)가 한계 → 초과하면 잘라 'index out of range' 방지
    tokens = min(int(seconds * 50), 1500)
    # do_sample=True + guidance_scale=3 은 MusicGen 공식 권장값(안 주면 음악이 단조·왜곡)
    audio = model.generate(**inputs, do_sample=True, guidance_scale=3.0, max_new_tokens=tokens)

    sr = model.config.audio_encoder.sampling_rate
    data = audio[0, 0].cpu().numpy()
    out = Path(out_path).with_suffix(".wav")
    scipy.io.wavfile.write(str(out), rate=sr, data=data)
    return out
