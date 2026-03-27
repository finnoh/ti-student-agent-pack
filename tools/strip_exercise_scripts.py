#!/usr/bin/env python3

from pathlib import Path


def exercises_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "exercises"


def script_template() -> str:
    return (
        "#!/usr/bin/env python3\n\n"
        "# Imports\n\n"
        "# Functions\n"
        "def main() -> int:\n"
        "    \"\"\"Entry point for this exercise script.\"\"\"\n"
        "    # Add your exercise logic here.\n"
        "    return 0\n\n"
        "# Code\n"
        "if __name__ == \"__main__\":\n"
        "    raise SystemExit(main())\n"
    )


def should_skip(path: Path) -> bool:
    return "__pycache__" in path.parts


def reset_python_scripts(base: Path) -> list[Path]:
    if not base.exists():
        return []

    changed: list[Path] = []
    template = script_template()

    for script in sorted(base.rglob("*.py")):
        if should_skip(script):
            continue
        current = script.read_text(encoding="utf-8", errors="ignore")
        if current == template:
            continue
        script.write_text(template, encoding="utf-8")
        changed.append(script)

    return changed


def main() -> int:
    base = exercises_dir()
    changed = reset_python_scripts(base)
    if not changed:
        print("Exercise Python scripts already reset.")
        return 0

    print(f"Reset {len(changed)} exercise Python file(s):")
    for path in changed:
        print(f"- {path.relative_to(base.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
