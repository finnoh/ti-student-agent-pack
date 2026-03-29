#!/usr/bin/env python3

# Imports
import csv
from pathlib import Path


# Functions
def load_values(csv_path: Path) -> list[float]:
    values: list[float] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            values.append(float(row["value"]))
    return values


def compute_mean(values: list[float]) -> float:
    return sum(values) / len(values)


# Code
def main() -> int:
    data_path = Path(__file__).resolve().parent / "data" / "sample.csv"
    values = load_values(data_path)
    mean_value = compute_mean(values)
    print(f"mean_value={mean_value:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
