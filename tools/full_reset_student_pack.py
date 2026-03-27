#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def pack_root() -> Path:
    return Path(__file__).resolve().parent.parent


def repo_root() -> Path:
    return pack_root().parent


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), text=True, capture_output=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hard reset student-agent-pack folder to a fresh git state from remote."
    )
    parser.add_argument("--ref", default="origin/main", help="Git reference to reset from (default: origin/main)")
    parser.add_argument("--yes", action="store_true", help="Skip interactive confirmation")
    return parser.parse_args()


def confirm_or_exit(force_yes: bool, target_ref: str) -> None:
    if force_yes:
        return
    if not sys.stdin.isatty():
        print("ERROR: interactive confirmation required. Re-run with --yes to force reset.")
        raise SystemExit(2)

    print("WARNING: This will hard reset the entire student-agent-pack folder.")
    print(f"Source ref: {target_ref}")
    print("All local changes in student-agent-pack/ will be discarded.")
    typed = input("Type RESET to continue: ").strip()
    if typed != "RESET":
        print("Cancelled. No changes made.")
        raise SystemExit(0)


def ensure_git_available() -> None:
    if shutil.which("git") is None:
        print("ERROR: git is not available in PATH.")
        raise SystemExit(2)


def main() -> int:
    args = parse_args()
    ensure_git_available()

    root = repo_root()
    module_rel = "student-agent-pack"

    confirm_or_exit(force_yes=args.yes, target_ref=args.ref)

    fetch = run_git(["fetch", "origin"], cwd=root)
    if fetch.returncode != 0:
        print("ERROR: git fetch failed")
        print(fetch.stderr.strip() or fetch.stdout.strip())
        return 2

    restore = run_git(
        ["restore", "--source", args.ref, "--staged", "--worktree", module_rel],
        cwd=root,
    )
    if restore.returncode != 0:
        print("ERROR: git restore failed")
        print(restore.stderr.strip() or restore.stdout.strip())
        return 2

    clean = run_git(["clean", "-fd", module_rel], cwd=root)
    if clean.returncode != 0:
        print("ERROR: git clean failed")
        print(clean.stderr.strip() or clean.stdout.strip())
        return 2

    print("student-agent-pack reset complete.")
    print(f"Refreshed from {args.ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
