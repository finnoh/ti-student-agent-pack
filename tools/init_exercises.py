#!/usr/bin/env python3

import argparse
from pathlib import Path

EXERCISE_META = {
    "E1": {
        "title": "Prompt anatomy lab",
        "objective": "Diagnose a weak prompt and produce an improved version.",
        "deliverable": "Before/after prompt rewrite with short rationale.",
        "failure_risk": "Constraints stay too vague to reproduce output quality.",
    },
    "E2": {
        "title": "Prompt rewrite challenge",
        "objective": "Run an A/B prompt comparison with clear evidence.",
        "deliverable": "Scored A/B note and final chosen prompt.",
        "failure_risk": "Too many variables changed between A and B.",
    },
    "E3": {
        "title": "IDE coding sprint",
        "objective": "Complete one bugfix or refactor with verification.",
        "deliverable": "Patch summary and verification trace.",
        "failure_risk": "No executable check of the final code path.",
    },
    "E4": {
        "title": "Draft and verify paragraph",
        "objective": "Write one claim-evidence paragraph with source checks.",
        "deliverable": "Paragraph plus citation verification note.",
        "failure_risk": "Claims exceed what sources support.",
    },
    "E5": {
        "title": "Design agent workflow",
        "objective": "Design a reliability-aware agent workflow.",
        "deliverable": "Architecture sketch with fallback and escalation path.",
        "failure_risk": "Missing human handoff for high-risk steps.",
    },
    "E6": {
        "title": "Build mini pipeline",
        "objective": "Draft a mini research pipeline with explicit limits.",
        "deliverable": "Protocol note and sample artifacts.",
        "failure_risk": "Overstating confidence from synthetic outputs.",
    },
    "E7": {
        "title": "Evaluate two outputs",
        "objective": "Compare two outputs with the workshop rubric.",
        "deliverable": "Scored table and short adoption memo.",
        "failure_risk": "Scores are not justified with evidence.",
    },
    "E8": {
        "title": "Resilience protocol plan",
        "objective": "Create a personal verification protocol.",
        "deliverable": "One-page protocol with trigger rules.",
        "failure_risk": "Protocol stays generic and non-actionable.",
    },
}


def build_file_content(exercise_id: str, student_name: str) -> str:
    meta = EXERCISE_META[exercise_id]
    return (
        "---\n"
        f"exercise_id: {exercise_id}\n"
        f"student_name: {student_name}\n"
        "---\n\n"
        "# Exercise Submission Draft\n\n"
        f"## Exercise\n{exercise_id} - {meta['title']}\n\n"
        f"## Objective\n{meta['objective']}\n\n"
        f"## Deliverable target\n{meta['deliverable']}\n\n"
        "## Final response\n\n"
        "## Iteration notes\n\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize prefilled markdown files for E1-E8")
    parser.add_argument("--student-name", default="", help="Student name used in front matter")
    parser.add_argument(
        "--work-dir",
        default=str(Path(__file__).resolve().parent.parent / "work"),
        help="Work directory for exercise markdown files",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0

    student_name = args.student_name.strip() or ""

    for exercise_id in [f"E{i}" for i in range(1, 9)]:
        file_path = work_dir / f"{exercise_id}.md"
        if file_path.exists() and not args.overwrite:
            skipped += 1
            continue
        file_path.write_text(build_file_content(exercise_id, student_name), encoding="utf-8")
        created += 1

    print("Initialized exercise files E1-E8.")
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print(f"Location: {work_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
