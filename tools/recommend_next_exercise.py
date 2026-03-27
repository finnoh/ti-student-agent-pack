#!/usr/bin/env python3

import json
import re
from pathlib import Path

EXERCISES = [f"E{i}" for i in range(1, 13)]
WIDTH = 74


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
    return bool(lines) and all(line in placeholders for line in lines)


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


def main() -> int:
    base = Path(__file__).resolve().parent.parent
    work_dir = base / "work"

    started_not_submitted = []
    unstarted = []

    for ex in EXERCISES:
        started = has_started(work_dir / f"{ex}.md")
        submitted = has_submitted(base, ex)
        if submitted:
            continue
        if started:
            started_not_submitted.append(ex)
        else:
            unstarted.append(ex)

    suggested_continue = started_not_submitted[0] if started_not_submitted else ""
    suggested_start = unstarted[0] if unstarted else ""
    suggested_latest_unstarted = unstarted[-1] if unstarted else ""

    print(bar())
    print(row(" Jan Sequential Exercise Recommendation"))
    print(bar())

    if suggested_continue:
        print(row(f" Primary recommendation: continue {suggested_continue} and submit it first."))
    elif suggested_start:
        print(row(f" Primary recommendation: start {suggested_start}."))
    else:
        print(row(" All exercises appear submitted. Great work."))

    print(bar())
    print(row(" Suggested prompt to student:"))

    if suggested_continue:
        print(row(f" Continue {suggested_continue}, or start {suggested_start or 'E1'}?"))
    elif suggested_start:
        print(row(f" Start with E1, or jump to {suggested_latest_unstarted}?"))
    else:
        print(row(" You can review any exercise or start an extension task."))

    print(bar())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
