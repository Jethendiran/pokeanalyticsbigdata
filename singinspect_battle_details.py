[1mdiff --git a/ingestion/download_data.py b/ingestion/download_data.py[m
[1mindex e69de29..7aa3b24 100644[m
[1m--- a/ingestion/download_data.py[m
[1m+++ b/ingestion/download_data.py[m
[36m@@ -0,0 +1,35 @@[m
[32m+[m
[32m+[m[32mfrom pathlib import Path[m
[32m+[m[32mimport kagglehub[m
[32m+[m[32mimport shutil[m
[32m+[m
[32m+[m[32m# Project directories[m
[32m+[m[32mPROJECT_ROOT = Path(__file__).resolve().parents[1][m
[32m+[m[32mRAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"[m
[32m+[m
[32m+[m[32m# Create raw data directory[m
[32m+[m[32mRAW_DATA_DIR.mkdir(parents=True, exist_ok=True)[m
[32m+[m
[32m+[m[32m# Download Pokémon TCG dataset[m
[32m+[m[32mprint("Downloading Pokémon TCG dataset...")[m
[32m+[m
[32m+[m[32mdownload_path = kagglehub.dataset_download([m
[32m+[m[32m    "kaggle/pokemon-tcg-ai-battle-episodes-2026-07-15"[m
[32m+[m[32m)[m
[32m+[m
[32m+[m[32mprint(f"Dataset downloaded to: {download_path}")[m
[32m+[m
[32m+[m[32m# Copy downloaded files into our project[m
[32m+[m[32msource = Path(download_path)[m
[32m+[m
[32m+[m[32mfor item in source.iterdir():[m
[32m+[m[32m    destination = RAW_DATA_DIR / item.name[m
[32m+[m
[32m+[m[32m    if item.is_dir():[m
[32m+[m[32m        if destination.exists():[m
[32m+[m[32m            shutil.rmtree(destination)[m
[32m+[m[32m        shutil.copytree(item, destination)[m
[32m+[m[32m    else:[m
[32m+[m[32m        shutil.copy2(item, destination)[m
[32m+[m
[32m+[m[32mprint(f"Dataset copied successfully to: {RAW_DATA_DIR}")[m
