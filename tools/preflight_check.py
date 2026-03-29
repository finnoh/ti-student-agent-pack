#!/usr/bin/env python3

from __future__ import annotations

import os
import shutil
import socket
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def pack_root() -> Path:
    return Path(__file__).resolve().parent.parent


def apply_dotenv_defaults() -> None:
    env_path = pack_root() / ".env"
    if not env_path.exists():
        return

    try:
        lines = env_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


def check_python() -> Check:
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (3, 10)
    return Check("python", ok, f"{major}.{minor}")


def check_uv() -> Check:
    uv = shutil.which("uv")
    return Check("uv", uv is not None, uv or "not found")


def check_env_key() -> Check:
    key = (os.getenv("OPENROUTER_API_KEY") or "").strip()
    return Check("OPENROUTER_API_KEY", bool(key), "set" if key else "missing")


def check_base_url() -> Check:
    base = (os.getenv("OPENAI_BASE_URL") or "").strip()
    ok = base == "https://openrouter.ai/api/v1"
    detail = base if base else "missing"
    return Check("OPENAI_BASE_URL", ok, detail)


def check_dns() -> Check:
    try:
        socket.gethostbyname("openrouter.ai")
        return Check("network_dns", True, "openrouter.ai resolved")
    except OSError as exc:
        return Check("network_dns", False, str(exc))


def main() -> int:
    apply_dotenv_defaults()
    checks = [
        check_python(),
        check_uv(),
        check_env_key(),
        check_base_url(),
        check_dns(),
    ]

    failed = [c for c in checks if not c.ok]
    for check in checks:
        status = "PASS" if check.ok else "FAIL"
        print(f"{status:4} | {check.name:20} | {check.detail}")

    if failed:
        print("\nPreflight incomplete. Fix failed checks before class start.")
        return 1

    print("\nPreflight passed. You are ready to start exercises.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
