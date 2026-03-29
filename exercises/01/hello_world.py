#!/usr/bin/env python3

# Imports
import csv
import json
import os
from pathlib import Path


# Functions
def load_rows(csv_path: Path) -> list[dict]:
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def mean_income(rows: list[dict]) -> float:
    values = [float(row["income"]) for row in rows]
    return sum(values) / len(values)


def try_langchain_response(rows: list[dict], mean_value: float) -> str:
    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
    except Exception:
        return "LangChain packages not installed. Using local fallback output."

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip() or os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return "OPENROUTER_API_KEY is missing. Using local fallback output."

    base_url = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.environ.get("OPENAI_CHAT_MODEL", os.environ.get("OPENROUTER_DEFAULT_MODEL", "nvidia/nemotron-3-super-120b-a12b:free"))

    llm = ChatOpenAI(api_key=api_key, base_url=base_url, model=model, temperature=0)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a careful data assistant. Return strict JSON with keys task, rows, mean_income, verification_note.",
            ),
            (
                "human",
                "Task: summarize this tiny CSV. Data: {rows}. Precomputed mean_income: {mean_value}.",
            ),
        ]
    )
    chain = prompt | llm
    result = chain.invoke({"rows": json.dumps(rows), "mean_value": mean_value})
    return str(getattr(result, "content", result)).strip()


def main() -> int:
    csv_path = Path(__file__).resolve().parent / "data" / "tiny.csv"
    rows = load_rows(csv_path)
    mean_value = mean_income(rows)

    print(f"rows={len(rows)}")
    print(f"mean_income={mean_value:.2f}")
    print("agent_output=")
    print(try_langchain_response(rows=rows, mean_value=mean_value))
    return 0


# Code
if __name__ == "__main__":
    raise SystemExit(main())
