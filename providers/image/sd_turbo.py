"""무료 배경 그림 생성 — SD-Turbo (Stability).
1-step이라 그림 생성 모델 중에선 빠른 편. 첫 호출 때 '그림 AI 두뇌' 자동 다운로드(~수 GB).
※ 무거운 import(torch/diffusers)는 함수 안에 둔다.
"""
from pathlib import Path

_pipe = None

# 글자 깨짐 방지: 글자·로고 빼고, 배경을 흐리게(bokeh) → 로파이 감성
NEG = "text, letters, words, logos, watermark, signature"
SUFFIX = ", lofi illustration, cozy, soft light, extreme bokeh, no text"


def _get_pipe():
    global _pipe
    if _pipe is None:
        import torch
        from diffusers import AutoPipelineForText2Image
        # 가능한 가속기 자동 선택: 애플실리콘(mps) → 엔비디아(cuda) → 일반(cpu)
        device = "mps" if torch.backends.mps.is_available() else (
                 "cuda" if torch.cuda.is_available() else "cpu")
        _pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sd-turbo").to(device)
    return _pipe


def generate(prompt, out_path):
    """prompt(장면 글)로 배경 이미지 1장을 만들어 out_path에 저장."""
    pipe = _get_pipe()
    # SD-Turbo는 step이 적어 빠르지만 거칠다. 2~3 step이면 형태가 좀 더 안정적.
    img = pipe(prompt + SUFFIX, negative_prompt=NEG,
               num_inference_steps=3, guidance_scale=0.0).images[0]
    out = Path(out_path)
    img.save(out)
    return out
