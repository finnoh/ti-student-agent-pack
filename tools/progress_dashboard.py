#!/usr/bin/env python3

from pathlib import Path

EXERCISES = [f"E{i}" for i in range(1, 9)]
WIDTH = 50


def bar() -> str:
    return "+" + ("-" * WIDTH) + "+"


def row(text: str) -> str:
    clipped = text[:WIDTH]
    return "|" + clipped.ljust(WIDTH) + "|"


def parse_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    data: dict[str, str] = {}
    if not lines or lines[0].strip() != "---":
        return data
    for idx in range(1, len(lines)):
        line = lines[idx]
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def find_latest_work_files(work_dir: Path) -> dict[str, Path]:
    latest: dict[str, Path] = {}
    for path in sorted(work_dir.glob("E*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        ex = path.stem
        if ex not in EXERCISES:
            continue
        if ex not in latest:
            latest[ex] = path
    return latest


def main() -> int:
    base = Path(__file__).resolve().parent.parent
    work_dir = base / "work"
    submissions_dir = base / "submissions"
    insights_path = base / "INSIGHTS.md"

    latest = find_latest_work_files(work_dir)
    submitted_count = len(list(submissions_dir.glob("*.json")))

    print(bar())
    print(row(" TI Student Tutor Progress Dashboard"))
    print(bar())
    print(row(f" Exercises drafted: {len(latest)}"))
    print(row(f" Submission records: {submitted_count}"))
    print(row(f" Insights file: {'yes' if insights_path.exists() else 'no'}"))
    print(bar())
    print(row(" Exercise status"))
    print(bar())

    for ex in EXERCISES:
        path = latest.get(ex)
        if path:
            print(row(f" {ex}: draft ready"))
        else:
            print(row(f" {ex}: not started"))

    print(bar())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
