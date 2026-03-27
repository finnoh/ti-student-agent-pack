#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def pack_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_config_path() -> Path:
    return pack_root() / "config" / "form_config.json"


def default_work_path(exercise_id: str) -> Path:
    return pack_root() / "work" / f"{exercise_id}.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print an exercise packet and manual Google Form submission link."
    )
    parser.add_argument("--exercise-id", required=True, help="Exercise ID like E1, E2, ...")
    parser.add_argument("--config", default=str(default_config_path()), help="Path to form config JSON")
    parser.add_argument("--work-file", default="", help="Path to exercise markdown file")
    parser.add_argument("--include-answer", action="store_true", help="Also print current answer draft")
    return parser.parse_args()


def load_config(path: Path) -> dict:
    if not path.exists():
        return {"google_form_url": "", "field_ids": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {"google_form_url": "", "field_ids": {}}
    field_ids = data.get("field_ids", {})
    if not isinstance(field_ids, dict):
        field_ids = {}
    return {
        "google_form_url": str(data.get("google_form_url", "")).strip(),
        "field_ids": field_ids,
    }


def apply_env_overrides(config: dict) -> dict:
    form_url = os.environ.get("GOOGLE_FORM_URL", "").strip()
    exercise_field = os.environ.get("GOOGLE_FORM_EXERCISE_FIELD", "").strip()
    merged = {
        "google_form_url": form_url or config.get("google_form_url", ""),
        "field_ids": dict(config.get("field_ids", {})),
    }
    if exercise_field:
        merged["field_ids"]["exercise_id"] = exercise_field
    return merged


def parse_sections(markdown_text: str) -> dict:
    sections: dict[str, list[str]] = {}
    current = "_preamble"
    sections[current] = []

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip("\n")
        if line.startswith("## "):
            current = line[3:].strip().lower().replace(" ", "_")
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def build_prefilled_url(form_url: str, exercise_field_id: str, exercise_id: str) -> str:
    if not form_url:
        return ""
    if not exercise_field_id:
        return form_url

    parsed = urlparse(form_url)
    params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    params[f"entry.{exercise_field_id}"] = exercise_id
    updated = parsed._replace(query=urlencode(params))
    return urlunparse(updated)


def main() -> int:
    args = parse_args()
    exercise_id = args.exercise_id.strip().upper()
    if not exercise_id.startswith("E"):
        print("ERROR: --exercise-id must look like E1, E2, ...")
        return 2

    work_file = Path(args.work_file).resolve() if args.work_file else default_work_path(exercise_id)
    if not work_file.exists():
        print(f"ERROR: exercise file not found: {work_file}")
        return 2

    markdown_text = work_file.read_text(encoding="utf-8")
    sections = parse_sections(markdown_text)

    config = apply_env_overrides(load_config(Path(args.config)))
    form_url = str(config.get("google_form_url", "")).strip()
    exercise_field_id = str(config.get("field_ids", {}).get("exercise_id", "")).strip()
    prefilled_url = build_prefilled_url(form_url=form_url, exercise_field_id=exercise_field_id, exercise_id=exercise_id)

    print("+--------------------------------------------------+")
    print(f"| Backup Mode Packet - {exercise_id:<28}|")
    print("+--------------------------------------------------+")
    print(f"Exercise file: {work_file}")
    print("")

    objective = sections.get("objective", "")
    deliverable = sections.get("deliverable_target", "")
    print("Objective:")
    print(objective or "(not specified)")
    print("")
    print("Deliverable target:")
    print(deliverable or "(not specified)")
    print("")

    if args.include_answer:
        print("Current draft answer:")
        print(sections.get("final_response", "(empty)"))
        print("")

    print("Manual submit link:")
    if prefilled_url:
        print(prefilled_url)
    elif form_url:
        print(form_url)
        print("(exercise_id prefill unavailable: missing field ID)")
    else:
        print("(missing google_form_url; set config/form_config.json or GOOGLE_FORM_URL)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
