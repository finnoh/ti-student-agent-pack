#!/usr/bin/env python3

import argparse
from pathlib import Path

EXERCISE_META = {
    "E1": {
        "title": "OpenRouter + deep-agent setup",
        "objective": "Configure OpenRouter defaults and run one verified deep-agent test.",
        "deliverable": "Setup note with selected default model and successful run output.",
        "failure_risk": "API key or base URL mismatch in .env.",
    },
    "E2": {
        "title": "Deep-agent prompt design",
        "objective": "Draft a deep-agent prompt and tool-routing rules for one task.",
        "deliverable": "Prompt spec and a concise routing decision table.",
        "failure_risk": "Prompt leaves tool-choice policy ambiguous.",
    },
    "E3": {
        "title": "LangChain deep-agent coding sprint",
        "objective": "Implement one deep-agent component with docs-backed API usage.",
        "deliverable": "Patch summary and verification trace.",
        "failure_risk": "API mismatch from skipping docs lookup.",
    },
    "E4": {
        "title": "Structured output and verification",
        "objective": "Create one verifiable structured output for a deep-agent step.",
        "deliverable": "Schema plus validated sample output.",
        "failure_risk": "Schema does not constrain risky model behavior.",
    },
    "E5": {
        "title": "Design deep-agent workflow",
        "objective": "Design a reliability-aware agent workflow.",
        "deliverable": "Architecture sketch with fallback and escalation path.",
        "failure_risk": "Missing human handoff for high-risk steps.",
    },
    "E6": {
        "title": "Memory-enabled deep-agent pipeline",
        "objective": "Draft a mini deep-agent pipeline with memory and explicit limits.",
        "deliverable": "Protocol note and sample artifacts.",
        "failure_risk": "Overstating confidence from synthetic outputs.",
    },
    "E7": {
        "title": "Compare free OpenRouter models",
        "objective": "Compare two free-model outputs with a controlled protocol.",
        "deliverable": "Scored table and short adoption memo.",
        "failure_risk": "Settings drift between model runs.",
    },
    "E8": {
        "title": "Deep-agent resilience protocol",
        "objective": "Create a personal verification protocol for deep-agent use.",
        "deliverable": "One-page protocol with trigger rules.",
        "failure_risk": "Protocol stays generic and non-actionable.",
    },
    "E9": {
        "title": "Evidence paragraph + claim ledger",
        "objective": "Produce one evidence-backed paragraph with traceable claims.",
        "deliverable": "Paragraph plus claim-evidence ledger.",
        "failure_risk": "Claims are not traceable to sources.",
    },
    "E10": {
        "title": "Reproducible analysis loop",
        "objective": "Run prompt -> code -> run -> test -> fix with a keep/reject decision.",
        "deliverable": "Minimal code, executable check output, and verification note.",
        "failure_risk": "No executable test evidence.",
    },
    "E11": {
        "title": "Issue -> agent -> PR workflow",
        "objective": "Practice safe issue-to-agent-to-PR collaboration.",
        "deliverable": "Issue text, handoff prompt, and PR review verdict.",
        "failure_risk": "No explicit human checkpoint.",
    },
    "E12": {
        "title": "Writing + syndication sprint",
        "objective": "Convert notes into a short brief and syndication plan.",
        "deliverable": "300-500 word brief, 3-channel plan, and disclosure note.",
        "failure_risk": "Output is generic and not audience-specific.",
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
        "## Subtasks\n"
        "- [ ] Subtask 1\n"
        "- [ ] Subtask 2\n"
        "- [ ] Subtask 3\n\n"
        "## Final response\n\n"
        "## Iteration notes\n\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize prefilled markdown files for E1-E12")
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

    for exercise_id in [f"E{i}" for i in range(1, 13)]:
        file_path = work_dir / f"{exercise_id}.md"
        if file_path.exists() and not args.overwrite:
            skipped += 1
            continue
        file_path.write_text(build_file_content(exercise_id, student_name), encoding="utf-8")
        created += 1

    print("Initialized exercise files E1-E12.")
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print(f"Location: {work_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
