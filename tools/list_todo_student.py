#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List TODO-STUDENT comments with line numbers.")
    parser.add_argument("--exercise", help="Exercise ID like E01, E02, ...")
    parser.add_argument("--path", help="Optional file or folder path to scan")
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


def resolve_scan_root(base_dir: Path, args: argparse.Namespace) -> Path:
    if args.path:
        return Path(args.path).expanduser().resolve()
    if args.exercise:
        exercise_id = normalize_exercise_id(args.exercise)
        folder = f"{int(exercise_id[1:]):02d}"
        return (base_dir / "exercises" / folder).resolve()
    return (base_dir / "exercises").resolve()


def iter_python_files(scan_root: Path) -> list[Path]:
    if scan_root.is_file():
        return [scan_root] if scan_root.suffix == ".py" else []
    return sorted(p for p in scan_root.rglob("*.py") if p.is_file())


def collect_todos(files: list[Path], base_dir: Path) -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    for file_path in files:
        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        rel = str(file_path.relative_to(base_dir)) if file_path.is_relative_to(base_dir) else str(file_path)
        for line_no, line in enumerate(lines, start=1):
            if "TODO-STUDENT" in line:
                rows.append((rel, line_no, line.strip()))
    return rows


def main() -> int:
    args = parse_args()
    base_dir = Path(__file__).resolve().parent.parent

    try:
        scan_root = resolve_scan_root(base_dir, args)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    files = iter_python_files(scan_root)
    todos = collect_todos(files, base_dir)

    print("GREAT!! WE HAVE SOME HANDS-ON STUFF NOW!")
    print(f"scan_root={scan_root}")
    print(f"python_files_scanned={len(files)}")

    if not todos:
        print("todo_student_count=0")
        print("No TODO-STUDENT comments found.")
        return 0

    print(f"todo_student_count={len(todos)}")
    print("sub_subtasks=")
    for idx, (path, line_no, text) in enumerate(todos, start=1):
        print(f"{idx}. [{path}:{line_no}] {text}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
