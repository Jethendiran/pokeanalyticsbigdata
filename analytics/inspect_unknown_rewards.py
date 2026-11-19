import json
import csv
from pathlib import Path

root = Path("data/raw")

with open("data/analytics/episode_outcomes.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

unknown_ids = {
    row["episode_id"]
    for row in rows
    if row["battle_outcome"] == "Unknown"
}

print("UNKNOWN EPISODE REWARDS")
print("=" * 60)

found = set()

for path in root.glob("*.json"):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        episode_id = data.get("id")

        if episode_id in unknown_ids:
            print("Episode:", episode_id)
            print("Rewards:", data.get("rewards"))
            print("Statuses:", data.get("statuses"))
            print("-" * 60)
            found.add(episode_id)

    except (json.JSONDecodeError, OSError):
        continue

print("Unknown episodes found:", len(found))
