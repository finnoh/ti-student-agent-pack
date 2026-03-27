#!/usr/bin/env python3

from pathlib import Path


def startup_path() -> Path:
    return Path(__file__).resolve().parent.parent / "STARTUP.md"


def main() -> int:
    path = startup_path()
    if not path.exists():
        print(f"No STARTUP.md found at {path}")
        return 0

    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    if not lines:
        return 0

    first = lines[0].strip()
    if first != "## STARTUP COMPLETE":
        print("STARTUP.md already clean.")
        return 0

    cleaned = lines[1:]
    if cleaned and cleaned[0].strip() == "":
        cleaned = cleaned[1:]

    path.write_text("\n".join(cleaned).rstrip("\n") + "\n", encoding="utf-8")
    print("Removed '## STARTUP COMPLETE' from STARTUP.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
