#!/usr/bin/env python3

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve exercise file/folder paths for E01-E12.")
    parser.add_argument("exercise_id", help="Exercise ID like E01, E02, ...")
    parser.add_argument(
        "--kind",
        choices=["md", "dir"],
        default="md",
        help="Return markdown file path (md) or exercise folder path (dir)",
    )
    return parser.parse_args()


def normalize_exercise_id(value: str) -> str:
    exercise_id = value.strip().upper()
    if not exercise_id.startswith("E"):
        raise ValueError("exercise_id must start with E (for example E02)")
    number = exercise_id[1:]
    if not number.isdigit():
        raise ValueError("exercise_id must end with a number (for example E02)")
    numeric = int(number)
    if numeric < 1 or numeric > 12:
        raise ValueError("exercise_id must be between E01 and E12")
    return f"E{numeric:02d}"


def exercise_folder(exercise_id: str) -> str:
    number = int(exercise_id[1:])
    return f"{number:02d}"


def exercise_dir(base_dir: Path, exercise_id: str) -> Path:
    return base_dir / "exercises" / exercise_folder(exercise_id)


def exercise_md(base_dir: Path, exercise_id: str) -> Path:
    return exercise_dir(base_dir, exercise_id) / f"{exercise_id}.md"


def main() -> int:
    args = parse_args()
    try:
        exercise_id = normalize_exercise_id(args.exercise_id)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    base = Path(__file__).resolve().parent.parent
    target = exercise_md(base, exercise_id) if args.kind == "md" else exercise_dir(base, exercise_id)
    print(str(target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
