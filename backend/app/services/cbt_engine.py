import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "psychology" / "cbt_techniques.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    CBT_RULES = json.load(f)


def select_cbt(intent: str, distress: str) -> dict:
    intent_rules = CBT_RULES.get(intent, CBT_RULES.get("general_support", {}))

    if distress in intent_rules:
        return intent_rules[distress]

    if "medium" in intent_rules:
        return intent_rules["medium"]

    if "low" in intent_rules:
        return intent_rules["low"]

    return {
        "technique": "Gentle pause",
        "category": "grounding",
        "description": "Take a slow breath and notice where you are right now."
    }
