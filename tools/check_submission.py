#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

REQUIRED = [
    "exercise_id",
    "student_name",
    "answer",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a saved submission JSON record.")
    parser.add_argument("path", help="Path to a submission JSON file")
    args = parser.parse_args()

    data = json.loads(Path(args.path).read_text(encoding="utf-8"))
    submission = data.get("submission", {}) if isinstance(data, dict) else {}
    missing = [key for key in REQUIRED if not str(submission.get(key, "")).strip()]

    if missing:
        print("Missing required fields:")
        for key in missing:
            print(f"- {key}")
        return 2

    print("Submission looks complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
