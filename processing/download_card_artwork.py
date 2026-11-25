import json
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CATALOG_FILE = ROOT / "data" / "processed" / "card_catalog.json"
ARTWORK_DIR = ROOT / "dashboard" / "assets" / "cards"

ARTWORK_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.trust_env = False
session.headers.update({"User-Agent": "PokeAnalytics/1.0"})

def normalize(name):
    name = name.lower().replace("’", "'")
    return re.sub(r"\s+", " ", name).strip()

def safe_filename(card_id, name):
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    return f"{card_id}_{slug}.png"

with CATALOG_FILE.open("r", encoding="utf-8") as file:
    cards = json.load(file)

pokemon_cards = [c for c in cards if c.get("category") == "Pokemon"]

downloaded = 0
not_found = []

print(f"Starting artwork download for {len(pokemon_cards)} Pokémon cards...")

for index, card in enumerate(pokemon_cards, start=1):
    name = card["name"]
    print(f"[{index}/{len(pokemon_cards)}] Searching: {name}")

    try:
        response = session.get(
            "https://api.tcgdex.net/v2/en/cards",
            params={"name": name},
            timeout=30
        )
        response.raise_for_status()
        results = response.json()

        exact_matches = [
            item for item in results
            if normalize(item.get("name", "")) == normalize(name)
            and item.get("image")
        ]

        if not exact_matches:
            card["artwork"] = None
            not_found.append(name)
            print("  No exact artwork match found.")
            continue

        image_base = exact_matches[0]["image"]
        image_url = image_base + "/high.png"

        image_response = session.get(image_url, timeout=30)

        if not image_response.ok:
            image_response = session.get(image_base + "/low.png", timeout=30)

        image_response.raise_for_status()

        filename = safe_filename(card["id"], name)
        image_path = ARTWORK_DIR / filename
        image_path.write_bytes(image_response.content)

        card["artwork"] = f"dashboard/assets/cards/{filename}"
        downloaded += 1
        print("  Downloaded successfully.")

    except Exception as error:
        card["artwork"] = None
        not_found.append(name)
        print(f"  Error: {error}")

    time.sleep(0.2)

with CATALOG_FILE.open("w", encoding="utf-8") as file:
    json.dump(cards, file, indent=2, ensure_ascii=False)

print("\nArtwork download completed!")
print(f"Pokémon cards: {len(pokemon_cards)}")
print(f"Images downloaded: {downloaded}")
print(f"Images not matched: {len(not_found)}")

if not_found:
    print("\nCards without artwork:")
    for name in not_found:
        print("-", name)
