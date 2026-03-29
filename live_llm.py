#!/usr/bin/env python3

from __future__ import annotations

import os
from pathlib import Path

from langchain_openai import ChatOpenAI


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_FREE_CHAT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


def pack_root() -> Path:
    return Path(__file__).resolve().parent


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


def resolve_api_key() -> str:
    return os.environ.get("OPENROUTER_API_KEY", "").strip() or os.environ.get("OPENAI_API_KEY", "").strip()


def build_live_model(temperature: float = 0.0) -> ChatOpenAI:
    apply_dotenv_defaults()
    api_key = resolve_api_key()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY (or OPENAI_API_KEY) is not set.")

    base_url = os.environ.get("OPENAI_BASE_URL", OPENROUTER_BASE_URL).strip() or OPENROUTER_BASE_URL
    model = (
        os.environ.get("OPENAI_CHAT_MODEL", "").strip()
        or os.environ.get("OPENROUTER_DEFAULT_MODEL", "").strip()
        or DEFAULT_FREE_CHAT_MODEL
    )
    return ChatOpenAI(model=model, api_key=api_key, base_url=base_url, temperature=temperature)


def to_text(response: object) -> str:
    return str(getattr(response, "content", response)).strip()
