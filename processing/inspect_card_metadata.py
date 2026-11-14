
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

files = sorted(RAW_DATA_DIR.glob("*.json"))

if not files:
    raise FileNotFoundError("No JSON files found in data/raw")

with open(files[0], "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 60)
print("POKEANALYTICS - CARD NAME EXTRACTION")
print("=" * 60)

card_names = {}

def find_cards(obj):
    """Recursively find card objects containing both id and name."""
    if isinstance(obj, dict):
        if "id" in obj and "name" in obj:
            card_id = obj["id"]
            card_name = obj["name"]

            if isinstance(card_id, int) and isinstance(card_name, str):
                card_names[card_id] = card_name

        for value in obj.values():
            find_cards(value)

    elif isinstance(obj, list):
        for item in obj:
            find_cards(item)

# Search visualization data from every step and agent
for step in data.get("steps", []):
    for agent in step:
        visualize = agent.get("visualize")
        if visualize is not None:
            find_cards(visualize)

# Also search observations for card objects
for step in data.get("steps", []):
    for agent in step:
        observation = agent.get("observation") or {}
        find_cards(observation.get("current"))

print(f"\nUnique card IDs with names found: {len(card_names)}")

print("\nCARD ID -> CARD NAME")
print("-" * 60)

for card_id, card_name in sorted(card_names.items()):
    print(f"{card_id}: {card_name}")

output_file = PROJECT_ROOT / "data" / "processed" / "card_reference.json"
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(
        [{"id": card_id, "name": name}
         for card_id, name in sorted(card_names.items())],
        f,
        indent=2,
        ensure_ascii=False
    )

print("\nSaved card reference to:")
print(output_file)
print("\nEXTRACTION COMPLETED")
