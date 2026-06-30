"""로컬 설치 도우미 — `python setup.py` 하면 부품을 한 번에 깔아준다."""
import subprocess
import sys


def main():
    print("🎵 무료 로파이 자동화 — 설치를 시작합니다.\n")
    print("부품(라이브러리)을 내려받는 중... (몇 분 걸릴 수 있어요)\n")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("\n✅ 설치 끝!")
    print("이제  python run.py  를 실행하면 output/ 폴더에 영상이 만들어집니다.")
    print("⚠️ 첫 실행 때 곡·그림 AI 모델이 자동으로 내려받아집니다(수 GB, 한 번만).")


if __name__ == "__main__":
    main()
