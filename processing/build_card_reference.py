
import json
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

files = sorted(RAW_DATA_DIR.glob("*.json"))

card_names = {}
conflicts = []

def find_cards(obj):
    """Find card objects containing both an ID and a name."""
    if isinstance(obj, dict):
        card_id = obj.get("id")
        card_name = obj.get("name")

        if (
            isinstance(card_id, int)
            and isinstance(card_name, str)
            and card_name.strip()
        ):
            if card_id not in card_names:
                card_names[card_id] = card_name
            elif card_names[card_id] != card_name:
                conflicts.append({
                    "id": card_id,
                    "existing_name": card_names[card_id],
                    "new_name": card_name
                })

        for value in obj.values():
            find_cards(value)

    elif isinstance(obj, list):
        for item in obj:
            find_cards(item)


print("=" * 60)
print("POKEANALYTICS - COMPLETE CARD REFERENCE BUILDER")
print("=" * 60)

print(f"\nJSON files found: {len(files)}")

for index, file_path in enumerate(files, start=1):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for step in data.get("steps", []):
            for agent in step:
                visualize = agent.get("visualize")
                if visualize is not None:
                    find_cards(visualize)

                observation = agent.get("observation") or {}
                current = observation.get("current")

                if current is not None:
                    find_cards(current)

    except Exception as error:
        print(f"\nError in {file_path.name}: {error}")

    if index % 100 == 0 or index == len(files):
        print(
            f"Processed {index}/{len(files)} files | "
            f"Unique cards: {len(card_names)}"
        )

# Save JSON reference
json_output = OUTPUT_DIR / "card_reference.json"

with open(json_output, "w", encoding="utf-8") as f:
    json.dump(
        [
            {"id": card_id, "name": name}
            for card_id, name in sorted(card_names.items())
        ],
        f,
        indent=2,
        ensure_ascii=False
    )

# Save CSV reference
csv_output = OUTPUT_DIR / "card_reference.csv"

with open(csv_output, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name"])
    writer.writeheader()

    for card_id, name in sorted(card_names.items()):
        writer.writerow({"id": card_id, "name": name})

# Save conflicting names for review
conflict_output = OUTPUT_DIR / "card_name_conflicts.json"

with open(conflict_output, "w", encoding="utf-8") as f:
    json.dump(conflicts, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print("CARD REFERENCE BUILD COMPLETED")
print("=" * 60)

print(f"Files processed: {len(files)}")
print(f"Unique card IDs: {len(card_names)}")
print(f"Name conflicts found: {len(conflicts)}")
print(f"\nJSON: {json_output}")
print(f"CSV: {csv_output}")
print(f"Conflicts: {conflict_output}")
