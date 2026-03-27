#!/usr/bin/env python3

import json
import os
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


def check_optional_tools() -> tuple[bool, str]:
    git_ok = shutil.which("git") is not None
    gh_ok = shutil.which("gh") is not None
    uv_ok = shutil.which("uv") is not None

    details = [
        f"git: {'yes' if git_ok else 'no'}",
        f"gh: {'yes' if gh_ok else 'no (optional for Track A)'}",
        f"uv: {'yes' if uv_ok else 'no (optional)'}",
    ]
    return True, ", ".join(details)


def check_openrouter_env(base: Path) -> tuple[bool, str]:
    env_path = base / ".env"
    env_key = os.environ.get("OPENROUTER_API_KEY", "").strip()

    if env_key:
        return True, "OPENROUTER_API_KEY loaded in environment"

    if not env_path.exists():
        return False, "Missing .env with OPENROUTER_API_KEY"

    try:
        lines = env_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError as exc:
        return False, f"Could not read .env: {exc}"

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not stripped.startswith("OPENROUTER_API_KEY="):
            continue
        value = stripped.split("=", 1)[1].strip()
        if value:
            return True, "OPENROUTER_API_KEY present in .env"
        return False, "OPENROUTER_API_KEY is empty in .env"

    return False, "OPENROUTER_API_KEY not found in .env"


def check_teacher_mode(base: Path) -> tuple[bool, str]:
    config_path = base / "opencode.json"
    if not config_path.exists():
        return False, "Missing opencode.json"

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"Invalid opencode.json: {exc}"

    agents = config.get("agent", {})
    if not isinstance(agents, dict):
        return False, "opencode.json: agent section is missing or invalid"

    build = agents.get("build", {})
    teacher = agents.get("teacher", {})
    if not isinstance(build, dict) or not isinstance(teacher, dict):
        return False, "opencode.json: build/teacher agent config missing"

    teacher_prompt = "{file:./context/teacher_mode_prompt.md}"
    build_prompt = str(build.get("prompt", "")).strip()
    teacher_agent_prompt = str(teacher.get("prompt", "")).strip()

    if build_prompt != teacher_prompt:
        return (
            False,
            "OpenCode build agent is not in teacher mode. Switch to teacher mode (Tab) or update opencode.json.",
        )

    if teacher_agent_prompt != teacher_prompt:
        return False, "Teacher agent prompt is not configured to context/teacher_mode_prompt.md"

    return True, "OpenCode starts in teacher mode by default"


def print_result(name: str, ok: bool, detail: str) -> None:
    mark = "[OK]" if ok else "[FAIL]"
    print(f"{mark} {name}: {detail}")


def main() -> int:
    base = root_dir()
    checks = [
        ("Python", *check_python()),
        ("Tools", *check_tools()),
        ("Optional tools", *check_optional_tools()),
        ("Teacher mode", *check_teacher_mode(base)),
        ("OpenRouter key", *check_openrouter_env(base)),
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
