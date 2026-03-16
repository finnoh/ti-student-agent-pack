#!/usr/bin/env python3

import json
import shutil
import sys
from pathlib import Path

REQUIRED_FIELD_IDS = [
    "exercise_id",
    "student_name",
    "answer",
]


def root_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def check_python() -> tuple[bool, str]:
    ok = sys.version_info >= (3, 10)
    msg = f"Python {sys.version.split()[0]}"
    return ok, msg


def check_config(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, f"Missing config file: {path}"
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        return False, f"Invalid JSON in config: {exc}"

    form_url = str(config.get("google_form_url", "")).strip()
    if not form_url:
        return False, "google_form_url is empty"

    field_ids = config.get("field_ids", {})
    if not isinstance(field_ids, dict):
        return False, "field_ids must be an object"

    missing = [field for field in REQUIRED_FIELD_IDS if not str(field_ids.get(field, "")).strip()]
    if missing:
        return False, f"Missing required field IDs: {', '.join(missing)}"

    return True, "Form URL + required field IDs configured"


def check_dirs(base: Path) -> tuple[bool, str]:
    for folder in [base / "work", base / "submissions", base / "tools", base / "config"]:
        if not folder.exists():
            return False, f"Missing directory: {folder}"
    return True, "Required directories present"


def check_tools() -> tuple[bool, str]:
    py = shutil.which("python3")
    if not py:
        return False, "python3 not found in PATH"
    return True, f"python3 found at {py}"


def print_result(name: str, ok: bool, detail: str) -> None:
    mark = "[OK]" if ok else "[FAIL]"
    print(f"{mark} {name}: {detail}")


def main() -> int:
    base = root_dir()
    checks = [
        ("Python", *check_python()),
        ("Tools", *check_tools()),
        ("Directories", *check_dirs(base)),
        ("Form config", *check_config(base / "config" / "form_config.json")),
    ]

    all_ok = True
    for name, ok, detail in checks:
        print_result(name, ok, detail)
        all_ok = all_ok and ok

    if all_ok:
        print("\nStartup checks passed.")
        return 0

    print("\nStartup checks failed. Ask the agent to fix what it can, or ask Finn for help.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
