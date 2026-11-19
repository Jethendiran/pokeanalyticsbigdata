
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

files = list(RAW_DATA_DIR.glob("*.json"))
sample_file = files[0]

with open(sample_file, "r", encoding="utf-8") as f:
    data = json.load(f)

steps = data.get("steps", [])

print("=" * 60)
print("POKEANALYTICS - BATTLE DATA STRUCTURE INSPECTION")
print("=" * 60)

# Inspect multiple steps
for step_index in [0, 1, 2, 10, len(steps) - 1]:
    if step_index >= len(steps):
        continue

    print(f"\nSTEP {step_index + 1}")
    step = steps[step_index]

    for agent_index, agent in enumerate(step):
        print(f"\nAgent {agent_index}")
        print("Action:", str(agent.get("action"))[:500])
        print("Reward:", agent.get("reward"))
        print("Status:", agent.get("status"))

        observation = agent.get("observation")

        if isinstance(observation, dict):
            print("Observation keys:", list(observation.keys()))

            for key, value in observation.items():
                print(f"  {key}: {type(value).__name__}")

                if isinstance(value, (dict, list)):
                    print("   Preview:", str(value)[:700])
                else:
                    print("   Value:", str(value)[:200])

        visualize = agent.get("visualize")

        if isinstance(visualize, list) and visualize:
            print("\nVisualize first record:")
            print(json.dumps(visualize[0], indent=2)[:1500])

print("\n" + "=" * 60)
print("INSPECTION COMPLETED")
print("=" * 60)

