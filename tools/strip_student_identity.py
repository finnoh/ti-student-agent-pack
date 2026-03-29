#!/usr/bin/env python3

from pathlib import Path


def exercises_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "exercises"


def strip_student_name(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    if not lines:
        return markdown_text

    in_frontmatter = False
    frontmatter_delims = 0
    out: list[str] = []

    for line in lines:
        if line.strip() == "---":
            frontmatter_delims += 1
            if frontmatter_delims == 1:
                in_frontmatter = True
            elif frontmatter_delims == 2:
                in_frontmatter = False
            out.append(line)
            continue

        if in_frontmatter and line.lower().startswith("student_name:"):
            out.append("student_name:")
            continue

        out.append(line)

    return "\n".join(out).rstrip("\n") + "\n"


def main() -> int:
    base = exercises_dir()
    if not base.exists():
        print("No exercises directory found.")
        return 0

    changed: list[Path] = []
    for path in sorted(base.glob("[0-9][0-9]/E*.md")):
        original = path.read_text(encoding="utf-8", errors="ignore")
        updated = strip_student_name(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(path)

    if not changed:
        print("No student identity fields needed cleanup.")
        return 0

    print(f"Cleared student_name in {len(changed)} submission draft file(s):")
    for path in changed:
        print(f"- {path.relative_to(base.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
