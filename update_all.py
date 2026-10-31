"""Run the complete data refresh pipeline in dependency order."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    "src/fetch_historical_weather.py",
    "src/store_historical_weather.py",
    "src/fetch_weather.py",
    "src/clean_and_store.py",
    "src/fetch_air_quality.py",
    "src/store_air_quality.py",
]


def main():
    for relative in SCRIPTS:
        script = ROOT / relative
        print(f"\n{'=' * 65}\nRunning {relative}\n{'=' * 65}", flush=True)
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT)
        if result.returncode:
            raise SystemExit(f"Pipeline stopped: {relative} failed with exit code {result.returncode}")
    print("\nAll data refresh steps completed successfully.")


if __name__ == "__main__":
    main()
