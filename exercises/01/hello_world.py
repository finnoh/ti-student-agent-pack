#!/usr/bin/env python3

import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from live_llm import build_live_model, to_text


def load_incomes(csv_path: Path) -> list[float]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return [float(r["income"]) for r in rows]

def load_names(csv_path: Path) -> list[str]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return [r["group_id"] for r in rows]

def main() -> int:
    incomes = load_incomes(Path(__file__).resolve().parent / "data" / "tiny.csv")
    names = load_names(Path(__file__).resolve().parent / "data" / "tiny.csv")
    mean_income = sum(incomes) / len(incomes)

    model = build_live_model(temperature=0.0)
    # TODO-STUDENT: Add another entry to the json, asking to return female sounding names from tiny.csv
    prompt = (
        "Return only compact JSON with keys task, rows, mean_income, verification_note. Also return a list of female sounding names from tiny.csv"
        f"\nrows={len(incomes)}"
        f"\nmean_income={mean_income:.2f}"
        "\nverification_note: must mention manual cross-check from on whether the number of observations and mean income matches tiny.csv."
        "\n female_names: should be list of all female sounding names in tiny.csv"
    )

    print(f"rows={len(incomes)}")
    print(f"mean_income={mean_income:.2f}")
    print("agent_output=")
    try:
        print(to_text(model.invoke(prompt)))
    except Exception:
        print(
            '{"task":"(fallback) Calculate mean income","rows":%d,"mean_income":%.2f,'
            '"verification_note":"Manual cross-check from tiny.csv"}' % (len(incomes), mean_income)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
