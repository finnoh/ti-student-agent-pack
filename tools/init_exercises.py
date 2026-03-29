#!/usr/bin/env python3

import argparse
from pathlib import Path

EXERCISE_META = {
    "E01": {
        "title": "Setup Jan + OpenRouter + hello world",
        "objective": "Complete minimum setup evidence first, then run one verified LangChain hello-world task if time allows.",
        "deliverable": "Minimum startup evidence + Jan response; full submission adds hello-world run, manual verification, and customization note.",
        "failure_risk": "API key or base URL mismatch in .env.",
    },
    "E02": {
        "title": "Prompt anatomy in LangChain code",
        "objective": "Run a first LangChain prompt, solve country extraction, and return structured Python output.",
        "deliverable": "Runnable snippet returning a cleaned Python list plus short orientation note (minimum one takeaway, optional blackjack extension).",
        "failure_risk": "Output format drifts away from strict Python list requirements.",
    },
    "E03": {
        "title": "Context pipeline with retrieval",
        "objective": "Build a small local corpus and compare baseline no-context answer with retrieval-assisted answer.",
        "deliverable": "A/B note with one failure fixed by retrieval, one quoted source chunk, and one boundary disclosure.",
        "failure_risk": "A/B comparison is not fair because prompts differ across runs.",
    },
    "E04": {
        "title": "Tool-calling mini-agent",
        "objective": "Integrate at least one existing tool with a no-auth fallback and run an agent that uses two tools in one workflow.",
        "deliverable": "Tool trace + one output plausibility check + one failure-mode note.",
        "failure_risk": "Agent answers directly without actually using both tools.",
    },
    "E05": {
        "title": "Connect LangChain agent to MCP time server",
        "objective": "Connect a LangChain agent to mcp-server-time, run one successful call, and capture one handled error path.",
        "deliverable": "MCP call demo (success + error path) plus one sanity check and one TODO-STUDENT experiment note.",
        "failure_risk": "MCP server runtime is unavailable or error-path evidence is missing.",
    },
    "E06": {
        "title": "Memory behavior: session + retrieval",
        "objective": "Define memory policy and demonstrate short-term and retriever-backed memory behavior.",
        "deliverable": "Trace with remembered preference, retrieved project fact, and risk note.",
        "failure_risk": "Memory claims are not supported by clear run evidence.",
    },
    "E07": {
        "title": "Ideation project + idea napkin",
        "objective": "Run the ideation pipeline with researcher context and produce at least two idea napkins.",
        "deliverable": "Selected lead idea napkin + domain scorecard comparison + IP/HARKING caution.",
        "failure_risk": "Idea remains too broad to test within available data constraints.",
    },
    "E08": {
        "title": "AI data-collection design memo",
        "objective": "Choose exactly one mode (A/B/C) and design a credible collection protocol with one prototype artifact.",
        "deliverable": "One-page memo with mode choice, threat model, verification plan, and prototype artifact reference.",
        "failure_risk": "Mode choice is not linked to a clear validity-risk mitigation plan.",
    },
    "E09": {
        "title": "Evidence paragraph + claim ledger",
        "objective": "Produce one evidence-backed paragraph with traceable claims and a journal-policy note.",
        "deliverable": "Paragraph plus claim/source/snippet/confidence/gap ledger (minimum two claims) and one unresolved gap.",
        "failure_risk": "Claims are not clearly linked to source snippets.",
    },
    "E10": {
        "title": "Reproducible analysis loop in VS Code",
        "objective": "Compare direct prompting to prompt -> code -> run -> test -> fix with a keep/reject decision.",
        "deliverable": "Minimal code, executable check output, verification note, and AI provenance note.",
        "failure_risk": "No executable test evidence.",
    },
    "E11": {
        "title": "Issue -> agent -> PR workflow drill",
        "objective": "Practice safe issue-to-agent-to-PR collaboration with explicit acceptance criteria.",
        "deliverable": "Issue text, handoff prompt, review verdict, and PR link or simulated PR record.",
        "failure_risk": "No explicit human checkpoint.",
    },
    "E12": {
        "title": "Writing + syndication sprint",
        "objective": "Convert notes into a short brief and syndication plan.",
        "deliverable": "300-500 word brief, 3-channel plan, and disclosure note (optional web-ready draft).",
        "failure_risk": "Output is generic and not audience-specific.",
    },
}


def exercise_folder(exercise_id: str) -> str:
    number = int(exercise_id[1:])
    return f"{number:02d}"


def exercise_code(number: int) -> str:
    return f"E{number:02d}"


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
        "## Verification method\n\n"
        "## Final response\n\n"
        "## Iteration notes\n\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize prefilled markdown files for E01-E12")
    parser.add_argument("--student-name", default="", help="Student name used in front matter")
    parser.add_argument(
        "--exercises-dir",
        default=str(Path(__file__).resolve().parent.parent / "exercises"),
        help="Exercises directory for exercise markdown files",
    )
    parser.add_argument("--work-dir", default="", help="Deprecated alias for --exercises-dir")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    target_dir = Path(args.work_dir) if args.work_dir else Path(args.exercises_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0

    student_name = args.student_name.strip() or ""

    for i in range(1, 13):
        exercise_id = exercise_code(i)
        exercise_dir = target_dir / exercise_folder(exercise_id)
        exercise_dir.mkdir(parents=True, exist_ok=True)
        file_path = exercise_dir / f"{exercise_id}.md"
        if file_path.exists() and not args.overwrite:
            skipped += 1
            continue
        file_path.write_text(build_file_content(exercise_id, student_name), encoding="utf-8")
        created += 1

    print("Initialized exercise files E01-E12.")
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print(f"Location: {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
