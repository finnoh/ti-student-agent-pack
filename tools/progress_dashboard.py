#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path

EXERCISE_TITLES = {
    "E1": "Setup Jan + OpenRouter + hello world",
    "E2": "Prompt anatomy in LangChain code",
    "E3": "Context pipeline with retrieval",
    "E4": "Tool-calling mini-agent",
    "E5": "Build + connect tiny MCP tool",
    "E6": "Memory behavior: session + retrieval",
    "E7": "Ideation project + idea napkin",
    "E8": "AI data-collection design memo",
    "E9": "Evidence paragraph + claim ledger",
    "E10": "Reproducible analysis loop",
    "E11": "Issue -> agent -> PR workflow",
    "E12": "Writing + syndication sprint",
}

EXERCISES = [f"E{i}" for i in range(1, 13)]
WIDTH = 74


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show exercise progress dashboard (not started / started / submitted).")
    parser.add_argument("--exercise", default="", help="Show only one exercise (e.g., E3)")
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


def _receipt_success_for_exercise(receipt_path: Path, exercise_id: str) -> bool:
    try:
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    submission = data.get("submission", {})
    if str(submission.get("exercise_id", "")).upper() != exercise_id:
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


def render_dashboard(base_dir: Path, selected: str | None = None) -> None:
    work_dir = base_dir / "work"
    exercises = [selected] if selected else EXERCISES

    states: dict[str, tuple[bool, bool]] = {}
    for ex in exercises:
        started = has_started(work_dir / f"{ex}.md")
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
    selected = args.exercise.strip().upper()
    if selected and selected not in EXERCISES:
        print("ERROR: --exercise must be E1..E12")
        return 2

    base = Path(__file__).resolve().parent.parent
    render_dashboard(base_dir=base, selected=selected or None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
