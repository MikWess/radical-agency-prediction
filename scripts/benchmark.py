"""Local-only benchmark templates and strict choice/probability scoring."""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_records(path):
    records = {}
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        key = item.get("id")
        if not isinstance(key, str) or not key or key in records:
            raise ValueError("Each record needs a unique, nonempty string id")
        records[key] = item
    if not records:
        raise ValueError("No records supplied")
    return records


def score(answers, predictions):
    if not answers or set(answers) != set(predictions):
        raise ValueError("Answer and prediction IDs must match exactly and be nonempty")
    correct, brier = 0, 0.0
    for key, answer in answers.items():
        options = answer.get("options")
        if (not isinstance(options, list) or len(options) < 2
                or any(not isinstance(x, str) or not x for x in options)
                or len(set(options)) != len(options)
                or answer.get("choice") not in options):
            raise ValueError(f"{key}: invalid options or missing actual choice")
        probs = predictions[key].get("probabilities")
        if not isinstance(probs, dict) or set(probs) != set(options):
            raise ValueError(f"{key}: probabilities must cover exactly the answer options")
        if any(type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1
               for p in probs.values()):
            raise ValueError(f"{key}: probabilities must be finite numbers between 0 and 1")
        if not math.isclose(sum(probs.values()), 1.0, abs_tol=1e-6, rel_tol=0):
            raise ValueError(f"{key}: probabilities must sum to 1")
        best = max(probs.values())
        winners = [option for option in options if probs[option] == best]
        choice = predictions[key].get("choice")
        if choice is None and len(winners) == 1:
            choice = winners[0]
        if choice not in winners:
            raise ValueError(f"{key}: supply a choice among the top-probability options (required for ties)")
        correct += choice == answer["choice"]
        brier += sum((probs[option] - int(option == answer["choice"])) ** 2
                     for option in options)
    n = len(answers)
    # Wilson 95% interval: describes one accuracy estimate, not a paired model difference.
    accuracy, z = correct / n, 1.959963984540054
    denom = 1 + z*z/n
    center = (accuracy + z*z/(2*n)) / denom
    half = z * math.sqrt(accuracy*(1-accuracy)/n + z*z/(4*n*n)) / denom
    return {"n": n, "correct": correct, "choice_accuracy": accuracy,
            "accuracy_wilson_95": [max(0, center-half), min(1, center+half)],
            "multiclass_brier_sum": brier/n}


def initialize(destination):
    scenarios = json.loads((ROOT / "experiments/starter-scenarios.json").read_text())
    destination.mkdir(parents=True, exist_ok=True)
    files = {
        "scenarios.json": json.dumps(scenarios, indent=2) + "\n",
        "answers.jsonl": "".join(json.dumps({"id": s["id"], "options": list(s["options"]),
                                             "choice": None, "reason": ""}) + "\n" for s in scenarios),
        "predictions-template.jsonl": "".join(json.dumps({"id": s["id"],
            "probabilities": {k: None for k in s["options"]}}) + "\n" for s in scenarios),
    }
    if any((destination / name).exists() for name in files):
        raise ValueError("Templates already exist; refusing to overwrite local evidence")
    for name, content in files.items():
        with (destination / name).open("x") as file:
            file.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Create private synthetic workflow templates")
    scoring = commands.add_parser("score", help="Score one condition's predictions")
    scoring.add_argument("answers")
    scoring.add_argument("predictions")
    args = parser.parse_args()
    try:
        if args.command == "init":
            initialize(ROOT / "private")
            print("Created private templates. Synthetic examples only; no model has run.")
        else:
            print(json.dumps(score(load_records(args.answers), load_records(args.predictions)), indent=2))
    except (ValueError, OSError, TypeError, AttributeError) as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
