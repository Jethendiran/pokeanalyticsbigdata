import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SUMMARY_FILE = PROJECT_ROOT / "data" / "analytics" / "battle_analysis_summary.json"
REFERENCE_FILE = PROJECT_ROOT / "data" / "processed" / "card_reference.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "analytics" / "card_frequency.csv"

with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
    summary = json.load(f)

reference = pd.read_csv(REFERENCE_FILE, dtype={"id": str})

cards = pd.DataFrame(summary["top_card_ids"])
cards["card_id"] = cards["card_id"].astype(str)

cards = cards.merge(
    reference,
    left_on="card_id",
    right_on="id",
    how="left"
)

cards = cards[["card_id", "name", "count"]]
cards = cards.sort_values("count", ascending=False)

cards.to_csv(OUTPUT_FILE, index=False)

print("=" * 60)
print("POKEANALYTICS - CARD FREQUENCY ANALYSIS")
print("=" * 60)

print("\nTOP 20 MOST FREQUENT CARDS")
print(cards.to_string(index=False))

print(f"\nResults saved to: {OUTPUT_FILE}")
