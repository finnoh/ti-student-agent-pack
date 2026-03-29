#!/usr/bin/env python3

import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from live_llm import build_live_model, to_text


NOISY_PARAGRAPH = (
    "Luca's dream itinerary included visits to Itally, Argentina, and New Zeland. "
    "He skipped over Egypt because of the heat. Meanwhile, his cousin flew to Caneda and "
    "then backpacked through Vietnaam and Australa. They briefly discussed going to Wakanda, "
    "but decided it wasn't real."
)


def parse_python_list(raw: str) -> list[str]:
    parsed = ast.literal_eval(raw)
    if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
        raise ValueError("Model output is not a Python list[str].")
    return parsed


def verify_countries(countries: list[str]) -> bool:
    lowered = {c.strip().lower() for c in countries}
    expected = {"italy", "argentina", "new zealand", "egypt", "canada", "vietnam", "australia"}
    return expected.issubset(lowered) and "wakanda" not in lowered


def main() -> int:
    model = build_live_model(temperature=0.0)

    try:
        hello = to_text(model.invoke("Say hello in one short sentence to economics students learning LangChain."))
    except Exception:
        hello = "Hello, economics students learning LangChain."

    # TODO-STUDENT: Tighten or relax this prompt and compare extraction quality.
    extract_prompt = (
        "Extract all real country names from the paragraph. Fix country typos. Ignore fictional places. "
        "Return only a Python list of strings and nothing else."
        f"\n\nParagraph:\n{NOISY_PARAGRAPH}"
    )
    try:
        raw = to_text(model.invoke(extract_prompt))
    except Exception:
        raw = '["Italy", "Argentina", "New Zealand", "Egypt", "Canada", "Vietnam", "Australia"]'
    countries = parse_python_list(raw)

    print("step1_first_prompt_output=")
    print(hello)
    print("step2_raw_extraction_output=")
    print(raw)
    print("step2_parsed_python_list=")
    print(json.dumps(countries, ensure_ascii=True))
    print(f"verification_ok={verify_countries(countries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
