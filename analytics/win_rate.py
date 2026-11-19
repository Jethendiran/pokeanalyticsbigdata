import json
import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "analytics"
OUTPUT.mkdir(parents=True, exist_ok=True)

files = sorted(RAW.glob("*.json"))

decisive_wins = 0
decisive_losses = 0
draws = 0
incomplete = 0
failed = 0
status_counts = Counter()
rows = []

for index, path in enumerate(files, 1):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        rewards = data.get("rewards")
        statuses = data.get("statuses") or []

        if isinstance(statuses, list):
            status_counts.update(str(s) for s in statuses)

        if not isinstance(rewards, list) or len(rewards) != 2:
            incomplete += 1
            outcome = "Incomplete"
            rewards = [None, None]
        elif rewards == [1, -1]:
            decisive_wins += 1
            decisive_losses += 1
            outcome = "Decisive"
        elif rewards == [-1, 1]:
            decisive_wins += 1
            decisive_losses += 1
            outcome = "Decisive"
        elif rewards == [0, 0]:
            draws += 1
            outcome = "Draw"
        else:
            incomplete += 1
            outcome = "Incomplete"

        rows.append({
            "episode_id": data.get("id", path.stem),
            "agent_0_reward": rewards[0],
            "agent_1_reward": rewards[1],
            "agent_0_status": statuses[0] if len(statuses) > 0 else "",
            "agent_1_status": statuses[1] if len(statuses) > 1 else "",
            "battle_outcome": outcome
        })

    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        failed += 1

    if index % 500 == 0 or index == len(files):
        print(f"Processed {index}/{len(files)} episodes")

total_decisive = decisive_wins + decisive_losses
win_rate = (
    decisive_wins / total_decisive * 100
    if total_decisive else 0
)
loss_rate = (
    decisive_losses / total_decisive * 100
    if total_decisive else 0
)

summary = {
    "total_episodes": len(files),
    "decisive_battles": decisive_wins,
    "agent_wins_in_decisive_battles": decisive_wins,
    "agent_losses_in_decisive_battles": decisive_losses,
    "decisive_win_rate_percent": round(win_rate, 2),
    "decisive_loss_rate_percent": round(loss_rate, 2),
    "draw_battles": draws,
    "incomplete_episodes": incomplete,
    "failed_files": failed,
    "agent_status_counts": dict(status_counts)
}

with open(OUTPUT / "win_rate_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=4)

with open(OUTPUT / "episode_outcomes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\n" + "=" * 60)
print("POKEANALYTICS - CORRECTED WIN/LOSS ANALYSIS")
print("=" * 60)
print("Total episodes:", len(files))
print("Decisive battles:", decisive_wins)
print("Agent wins:", decisive_wins)
print("Agent losses:", decisive_losses)
print("Decisive win rate:", f"{win_rate:.2f}%")
print("Decisive loss rate:", f"{loss_rate:.2f}%")
print("Draw battles:", draws)
print("Incomplete episodes:", incomplete)
print("Failed files:", failed)
print("Agent statuses:", dict(status_counts))
print("\nResults saved in:", OUTPUT)
print("ANALYSIS COMPLETED")
