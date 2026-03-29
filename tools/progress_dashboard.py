#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path

EXERCISE_TITLES = {
    "E01": "Setup Jan + OpenRouter + hello world",
    "E02": "Prompt anatomy in LangChain code",
    "E03": "Context pipeline with retrieval",
    "E04": "Tool-calling mini-agent",
    "E05": "Build + connect tiny MCP tool",
    "E06": "Memory behavior: session + retrieval",
    "E07": "Ideation project + idea napkin",
    "E08": "AI data-collection design memo",
    "E09": "Evidence paragraph + claim ledger",
    "E10": "Reproducible analysis loop",
    "E11": "Issue -> agent -> PR workflow",
    "E12": "Writing + syndication sprint",
}

EXERCISES = [f"E{i:02d}" for i in range(1, 13)]
WIDTH = 74


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show exercise progress dashboard (not started / started / submitted).")
    parser.add_argument("--exercise", default="", help="Show only one exercise (e.g., E03)")
    return parser.parse_args()


def bar() -> str:
    return "+" + ("-" * WIDTH) + "+"


def row(text: str) -> str:
    clipped = text[:WIDTH]
    return "|" + clipped.ljust(WIDTH) + "|"


def _extract_section(text: str, section_name: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(section_name)}\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    rest = text[start:]
    next_header = re.search(r"^##\s+", rest, flags=re.MULTILINE)
    if next_header:
        rest = rest[: next_header.start()]
    return rest.strip()


def _is_effectively_empty(value: str) -> bool:
    if not value.strip():
        return True
    placeholders = {
        "- [ ] subtask 1",
        "- [ ] subtask 2",
        "- [ ] subtask 3",
    }
    lines = [line.strip().lower() for line in value.splitlines() if line.strip()]
    if lines and all(line in placeholders for line in lines):
        return True
    return False


def has_started(work_file: Path) -> bool:
    if not work_file.exists():
        return False

    text = work_file.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"-\s*\[[xX]\]", text):
        return True

    final_response = _extract_section(text, "Final response")
    iteration_notes = _extract_section(text, "Iteration notes")
    for section in [final_response, iteration_notes]:
        if not _is_effectively_empty(section):
            return True

    return False


def normalize_exercise_id(value: str) -> str:
    ex = value.strip().upper()
    if not ex.startswith("E"):
        raise ValueError("exercise id must start with E")
    number = ex[1:]
    if not number.isdigit():
        raise ValueError("exercise id must end with a number")
    numeric = int(number)
    if numeric < 1 or numeric > 12:
        raise ValueError("exercise id must be between E01 and E12")
    return f"E{numeric:02d}"


def _receipt_success_for_exercise(receipt_path: Path, exercise_id: str) -> bool:
    try:
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    submission = data.get("submission", {})
    raw_exercise = str(submission.get("exercise_id", "")).upper()
    try:
        saved_exercise = normalize_exercise_id(raw_exercise)
    except ValueError:
        return False
    if saved_exercise != exercise_id:
        return False
    return bool(data.get("success", False))


def has_submitted(base_dir: Path, exercise_id: str) -> bool:
    receipts_dir = base_dir / "submissions" / "receipts"
    if not receipts_dir.exists():
        return False
    for path in sorted(receipts_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        if _receipt_success_for_exercise(path, exercise_id):
            return True
    return False


def symbol(started: bool, submitted: bool) -> str:
    if submitted:
        return "[X]"
    if started:
        return "[ ]"
    return ""


def exercise_folder(exercise_id: str) -> str:
    number = int(exercise_id[1:])
    return f"{number:02d}"


def exercise_markdown_path(exercises_dir: Path, exercise_id: str) -> Path:
    return exercises_dir / exercise_folder(exercise_id) / f"{exercise_id}.md"


def render_dashboard(base_dir: Path, selected: str | None = None) -> None:
    exercises_dir = base_dir / "exercises"
    exercises = [selected] if selected else EXERCISES

    states: dict[str, tuple[bool, bool]] = {}
    for ex in exercises:
        started = has_started(exercise_markdown_path(exercises_dir, ex))
        submitted = has_submitted(base_dir, ex)
        states[ex] = (started, submitted)

    started_count = sum(1 for started, _ in states.values() if started)
    submitted_count = sum(1 for _, submitted in states.values() if submitted)
    total = len(exercises)

    print(bar())
    print(row(" Jan Exercise Progress"))
    print(bar())
    print(row(" Legend: blank = not started, [ ] = started, [X] = submitted"))
    print(row(f" Started: {started_count}/{total} | Submitted: {submitted_count}/{total}"))
    print(bar())

    for ex in exercises:
        title = EXERCISE_TITLES.get(ex, "")
        state_symbol = symbol(*states[ex])
        label = f" {ex.ljust(4)} {title}"
        if state_symbol:
            label = f"{label} {state_symbol}"
        print(row(label))

    print(bar())


def main() -> int:
    args = parse_args()
    selected = args.exercise.strip()
    if selected:
        try:
            selected = normalize_exercise_id(selected)
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 2

    base = Path(__file__).resolve().parent.parent
    render_dashboard(base_dir=base, selected=selected or None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
