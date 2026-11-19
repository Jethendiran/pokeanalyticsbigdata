
import json
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "analytics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

files = sorted(RAW_DATA_DIR.glob("*.json"))

card_ids = Counter()
event_types = Counter()
agent_actions = Counter()
turn_numbers = []

processed = 0
failed = 0

print("=" * 60)
print("POKEANALYTICS - FULL BATTLE DATA ANALYSIS")
print("=" * 60)
print(f"JSON files found: {len(files)}")

for index, file_path in enumerate(files, start=1):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        processed += 1

        for step in data.get("steps", []):
            if not isinstance(step, list):
                continue

            for agent in step:
                if not isinstance(agent, dict):
                    continue

                observation = agent.get("observation") or {}

                if not isinstance(observation, dict):
                    continue

                current = observation.get("current")

                if isinstance(current, dict):
                    turn = current.get("turn")
                    if isinstance(turn, int):
                        turn_numbers.append(turn)

                    players = current.get("players", [])

                    if isinstance(players, list):
                        for player in players:
                            if not isinstance(player, dict):
                                continue

                            for area in ["active", "bench", "hand", "discard"]:
                                cards = player.get(area) or []

                                if isinstance(cards, list):
                                    for card in cards:
                                        if isinstance(card, dict) and "id" in card:
                                            card_ids[card["id"]] += 1

                logs = observation.get("logs") or []

                if isinstance(logs, list):
                    for event in logs:
                        if isinstance(event, dict) and "type" in event:
                            event_types[event["type"]] += 1

                action = agent.get("action")
                if isinstance(action, list):
                    agent_actions[len(action)] += 1

    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        failed += 1

    if index % 100 == 0 or index == len(files):
        print(f"Processed {index}/{len(files)} files")

print("\n" + "=" * 60)
print("ANALYSIS RESULTS")
print("=" * 60)

print(f"Total JSON files: {len(files)}")
print(f"Successfully processed: {processed}")
print(f"Failed files: {failed}")
print(f"Unique card IDs: {len(card_ids)}")

print("\nTOP 20 CARD IDS")
for card_id, count in card_ids.most_common(20):
    print(f"Card ID {card_id}: {count} occurrences")

print("\nEVENT TYPE FREQUENCY")
for event_type, count in event_types.most_common():
    print(f"Event type {event_type}: {count}")

print("\nTURN INFORMATION")
if turn_numbers:
    print(f"Minimum turn: {min(turn_numbers)}")
    print(f"Maximum turn: {max(turn_numbers)}")
    print(f"Average turn: {sum(turn_numbers) / len(turn_numbers):.2f}")
else:
    print("No turn information found.")

print("\nACTION LENGTH FREQUENCY")
for length, count in agent_actions.most_common():
    print(f"Action length {length}: {count}")

# Save analysis summary
summary = {
    "total_files": len(files),
    "processed_files": processed,
    "failed_files": failed,
    "unique_card_ids": len(card_ids),
    "top_card_ids": [
        {"card_id": str(card_id), "count": count}
        for card_id, count in card_ids.most_common(20)
    ],
    "event_types": {
        str(event_type): count
        for event_type, count in event_types.items()
    },
    "turn_information": {
        "minimum": min(turn_numbers) if turn_numbers else None,
        "maximum": max(turn_numbers) if turn_numbers else None,
        "average": (
            sum(turn_numbers) / len(turn_numbers)
            if turn_numbers else None
        )
    }
}

output_file = OUTPUT_DIR / "battle_analysis_summary.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=4)

print(f"\nSummary saved to: {output_file}")
print("\nANALYSIS COMPLETED")
print("=" * 60)
