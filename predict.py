"""Predict the category of one new customer complaint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from train import predict_probabilities


DEFAULT_MODEL_PATH = Path("models/complaint_classifier.json")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Predict a category for a customer complaint."
    )
    parser.add_argument("complaint", help="The complaint text to classify.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if not args.model.is_file():
        raise FileNotFoundError(
            f"Model not found: {args.model}. Train it first with: py train.py"
        )

    model = json.loads(args.model.read_text(encoding="utf-8"))
    probabilities = predict_probabilities(model, args.complaint)
    category, confidence = max(probabilities.items(), key=lambda item: item[1])

    print(f"Predicted category: {category}")
    print(f"Confidence: {confidence:.1%}")
    print("\nAll category probabilities:")
    for name, probability in sorted(
        probabilities.items(), key=lambda item: item[1], reverse=True
    ):
        print(f"- {name}: {probability:.1%}")


if __name__ == "__main__":
    main()
