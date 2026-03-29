#!/usr/bin/env python3

# Imports
import ast
import json
import os
from typing import Any

from pydantic import BaseModel


# Functions
NOISY_PARAGRAPH = (
    "Luca's dream itinerary included visits to Itally, Argentina, and New Zeland. "
    "He skipped over Egypt because of the heat. Meanwhile, his cousin flew to Caneda and "
    "then backpacked through Vietnaam and Australa. They briefly discussed going to Wakanda, "
    "but decided it wasn't real."
)


class CountryList(BaseModel):
    countries: list[str]


def build_language_model():
    from langchain_openai import ChatOpenAI

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip() or os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY (or OPENAI_API_KEY).")

    base_url = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.environ.get("OPENAI_CHAT_MODEL", os.environ.get("OPENROUTER_DEFAULT_MODEL", "nvidia/nemotron-3-super-120b-a12b:free"))

    return ChatOpenAI(api_key=api_key, base_url=base_url, model=model, temperature=0)


def run_first_prompt(model: Any) -> str:
    response = model.invoke("Say hello in one short sentence to economics students learning LangChain.")
    return str(getattr(response, "content", response)).strip()


def extraction_prompt_text() -> str:
    return (
        "Extract all country names from the paragraph. "
        "Fix country typos. Ignore fictional places. "
        "Return only a Python list of country names and nothing else."
    )


def run_country_extraction(model: Any, text: str) -> str:
    response = model.invoke(f"{extraction_prompt_text()}\n\nParagraph:\n{text}")
    return str(getattr(response, "content", response)).strip()


def parse_python_list(raw: str) -> list[str]:
    parsed = ast.literal_eval(raw)
    if not isinstance(parsed, list):
        raise ValueError("Output is not a Python list.")
    if not all(isinstance(x, str) for x in parsed):
        raise ValueError("List contains non-string values.")
    return parsed


def run_structured_extraction(model: Any, text: str) -> list[str]:
    from langchain_core.prompts import ChatPromptTemplate

    structured_llm = model.with_structured_output(CountryList)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Extract real country names from noisy text."
                " Fix country typos. Ignore fictional places."
                " Return only the schema fields.",
            ),
            ("human", "Paragraph: {paragraph}"),
        ]
    )
    chain = prompt | structured_llm
    result = chain.invoke({"paragraph": text})
    return result.countries


def verify_countries(countries: list[str]) -> bool:
    lowered = {x.strip().lower() for x in countries}
    expected = {
        "italy",
        "argentina",
        "new zealand",
        "egypt",
        "canada",
        "vietnam",
        "australia",
    }
    if not expected.issubset(lowered):
        return False
    if "wakanda" in lowered:
        return False
    if len(countries) < 7:
        return False
    return True


# Code
def main() -> int:
    model = build_language_model()

    hello = run_first_prompt(model)
    print("step1_first_prompt_output=")
    print(hello)

    raw_list_text = run_country_extraction(model, NOISY_PARAGRAPH)
    print("step2_raw_extraction_output=")
    print(raw_list_text)

    parsed_list = parse_python_list(raw_list_text)
    print("step2_parsed_python_list=")
    print(json.dumps(parsed_list, ensure_ascii=True))

    structured_list = run_structured_extraction(model, NOISY_PARAGRAPH)
    print("step3_structured_python_list=")
    print(json.dumps(structured_list, ensure_ascii=True))

    verified = verify_countries(structured_list)
    print(f"verification_ok={verified}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
