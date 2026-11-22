"""Train an offline text classifier for customer-complaint categories.

The input CSV must contain one text column and one category/label column.
This implementation uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_DATA_PATH = Path("data/complaints.csv")
DEFAULT_MODEL_PATH = Path("models/complaint_classifier.json")
DEFAULT_METRICS_PATH = Path("models/metrics.json")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "has", "have", "i", "in", "is", "it", "me", "my", "of", "on", "or", "our",
    "that", "the", "this", "to", "was", "with", "your",
}
CATEGORY_CUES = {
    "Billing": {
        "balance", "bill", "billed", "billing", "charge", "charged", "coupon",
        "discount", "fee", "invoice", "payment", "receipt", "refund", "tax",
    },
    "Customer Service": {
        "agent", "callback", "contact", "escalate", "feedback", "representative",
        "reply", "response", "supervisor", "support", "update",
    },
    "Technical Support": {
        "app", "application", "browser", "code", "crashes", "device", "error",
        "install", "network", "password", "screen", "server", "software", "website",
    },
    "Account Management": {
        "administrator", "archive", "deactivate", "department", "merge", "nickname",
        "organization", "owner", "preferences", "profile", "rename", "workspace",
    },
    "Security & Fraud": {
        "breach", "compromised", "fraud", "intruder", "phishing", "scam", "security",
        "stolen", "suspicious", "unauthorized",
    },
    "Orders & Delivery": {
        "courier", "delivery", "dispatch", "order", "package", "parcel", "return",
        "shipment", "tracking", "warehouse",
    },
}
CUE_WEIGHT = 1.5


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a customer-complaint text classifier."
    )
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--text-column", default="complaint")
    parser.add_argument("--label-column", default="category")
    parser.add_argument("--model-out", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--metrics-out", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--test-size", type=float, default=0.25)
    return parser.parse_args()


def tokenize(text: str) -> list[str]:
    """Convert complaint text to normalized tokens for the classifier."""
    return [
        token
        for token in TOKEN_PATTERN.findall(text.lower())
        if token not in STOP_WORDS and len(token) > 1
    ]


def load_dataset(data_path: Path, text_column: str, label_column: str) -> list[tuple[str, str]]:
    if not data_path.is_file():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    with data_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("The dataset does not have a header row.")
        missing = {text_column, label_column}.difference(reader.fieldnames)
        if missing:
            available = ", ".join(reader.fieldnames)
            raise ValueError(
                f"Dataset is missing column(s): {', '.join(sorted(missing))}. "
                f"Available columns: {available}"
            )

        rows: list[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for row in reader:
            text = (row.get(text_column) or "").strip()
            label = (row.get(label_column) or "").strip()
            pair = (text, label)
            if text and label and pair not in seen:
                rows.append(pair)
                seen.add(pair)

    if not rows:
        raise ValueError("No valid complaint rows remain after cleaning the dataset.")

    counts = Counter(label for _, label in rows)
    if len(counts) < 2:
        raise ValueError("The dataset needs at least two different categories.")
    too_small = sorted(label for label, count in counts.items() if count < 2)
    if too_small:
        raise ValueError(
            "Each category needs at least two rows for evaluation. Add examples for: "
            + ", ".join(too_small)
        )
    return rows


def stratified_split(
    rows: list[tuple[str, str]], test_size: float
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    grouped: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row[1]].append(row)

    randomizer = random.Random(42)
    train_rows: list[tuple[str, str]] = []
    test_rows: list[tuple[str, str]] = []
    for label, label_rows in grouped.items():
        randomizer.shuffle(label_rows)
        test_count = max(1, round(len(label_rows) * test_size))
        test_count = min(test_count, len(label_rows) - 1)
        test_rows.extend(label_rows[:test_count])
        train_rows.extend(label_rows[test_count:])
    randomizer.shuffle(train_rows)
    randomizer.shuffle(test_rows)
    return train_rows, test_rows


def train_model(rows: list[tuple[str, str]]) -> dict[str, object]:
    class_document_counts: Counter[str] = Counter()
    class_token_counts: dict[str, Counter[str]] = defaultdict(Counter)
    total_token_counts: Counter[str] = Counter()
    vocabulary: set[str] = set()

    for text, label in rows:
        tokens = tokenize(text)
        class_document_counts[label] += 1
        class_token_counts[label].update(tokens)
        total_token_counts[label] += len(tokens)
        vocabulary.update(tokens)

    return {
        "algorithm": "cue_assisted_multinomial_naive_bayes",
        "categories": sorted(class_document_counts),
        "training_examples": len(rows),
        "vocabulary_size": len(vocabulary),
        "class_document_counts": dict(class_document_counts),
        "class_token_counts": {
            label: dict(counts) for label, counts in class_token_counts.items()
        },
        "total_token_counts": dict(total_token_counts),
    }


def predict_probabilities(model: dict[str, object], text: str) -> dict[str, float]:
    categories = list(model["categories"])
    class_document_counts = model["class_document_counts"]
    class_token_counts = model["class_token_counts"]
    total_token_counts = model["total_token_counts"]
    training_examples = int(model["training_examples"])
    vocabulary_size = int(model["vocabulary_size"])
    tokens = tokenize(text)

    log_scores: dict[str, float] = {}
    for category in categories:
        document_count = int(class_document_counts[category])
        token_counts = class_token_counts[category]
        token_total = int(total_token_counts[category])
        score = math.log(document_count / training_examples)
        denominator = token_total + vocabulary_size
        for token in tokens:
            score += math.log((int(token_counts.get(token, 0)) + 1) / denominator)
        score += CUE_WEIGHT * sum(token in CATEGORY_CUES.get(category, set()) for token in tokens)
        log_scores[category] = score

    highest_score = max(log_scores.values())
    unnormalized = {
        category: math.exp(score - highest_score)
        for category, score in log_scores.items()
    }
    normalizer = sum(unnormalized.values())
    return {
        category: value / normalizer for category, value in unnormalized.items()
    }


def classification_report(
    actual: list[str], predicted: list[str], categories: list[str]
) -> dict[str, object]:
    report: dict[str, object] = {}
    weighted_precision = 0.0
    weighted_recall = 0.0
    weighted_f1 = 0.0
    macro_precision = 0.0
    macro_recall = 0.0
    macro_f1 = 0.0

    for category in categories:
        true_positive = sum(
            expected == category and guess == category
            for expected, guess in zip(actual, predicted)
        )
        false_positive = sum(
            expected != category and guess == category
            for expected, guess in zip(actual, predicted)
        )
        false_negative = sum(
            expected == category and guess != category
            for expected, guess in zip(actual, predicted)
        )
        support = actual.count(category)
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        report[category] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "support": support,
        }
        macro_precision += precision
        macro_recall += recall
        macro_f1 += f1
        weighted_precision += precision * support
        weighted_recall += recall * support
        weighted_f1 += f1 * support

    total = len(actual)
    class_count = len(categories)
    report["macro_average"] = {
        "precision": round(macro_precision / class_count, 4),
        "recall": round(macro_recall / class_count, 4),
        "f1_score": round(macro_f1 / class_count, 4),
    }
    report["weighted_average"] = {
        "precision": round(weighted_precision / total, 4),
        "recall": round(weighted_recall / total, 4),
        "f1_score": round(weighted_f1 / total, 4),
    }
    return report


def main() -> None:
    args = parse_arguments()
    if not 0 < args.test_size < 1:
        raise ValueError("--test-size must be greater than 0 and less than 1.")

    rows = load_dataset(args.data, args.text_column, args.label_column)
    train_rows, test_rows = stratified_split(rows, args.test_size)
    model = train_model(train_rows)
    actual = [label for _, label in test_rows]
    predictions = [
        max(predict_probabilities(model, text), key=lambda category: predict_probabilities(model, text)[category])
        for text, _ in test_rows
    ]
    accuracy = sum(expected == guess for expected, guess in zip(actual, predictions)) / len(actual)
    categories = list(model["categories"])
    metrics = {
        "accuracy": round(accuracy, 4),
        "training_examples": len(train_rows),
        "test_examples": len(test_rows),
        "categories": categories,
        "classification_report": classification_report(actual, predictions, categories),
    }

    args.model_out.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_out.parent.mkdir(parents=True, exist_ok=True)
    args.model_out.write_text(json.dumps(model, indent=2), encoding="utf-8")
    args.metrics_out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Trained on {len(train_rows)} complaints; tested on {len(test_rows)} complaints.")
    print(f"Accuracy: {accuracy:.1%}")
    print(f"Model saved to: {args.model_out}")
    print(f"Metrics saved to: {args.metrics_out}")
    print("\nCategory distribution:")
    for category, count in sorted(Counter(label for _, label in rows).items()):
        print(f"{category}: {count}")


if __name__ == "__main__":
    main()
