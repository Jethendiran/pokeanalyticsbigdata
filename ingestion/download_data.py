
from pathlib import Path
import shutil
import kagglehub

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

DATASET = "kaggle/pokemon-tcg-ai-battle-episodes-2026-07-15"

print("Downloading Pokémon TCG dataset...")

download_path = kagglehub.dataset_download(DATASET)
source = Path(download_path)

print(f"Dataset downloaded to: {source}")

copied = 0
skipped = 0

for item in source.iterdir():
    destination = RAW_DATA_DIR / item.name

    if destination.exists():
        skipped += 1
        continue

    if item.is_dir():
        shutil.copytree(item, destination)
    else:
        shutil.copy2(item, destination)

    copied += 1

print("\nDataset copy completed!")
print(f"New items copied: {copied}")
print(f"Existing items skipped: {skipped}")
print(f"Destination: {RAW_DATA_DIR}")
