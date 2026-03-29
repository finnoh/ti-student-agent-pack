#!/usr/bin/env python3

# Imports
from pathlib import Path


# Functions
def read_local_documents(folder: Path) -> list[str]:
    documents: list[str] = []
    for path in sorted(folder.glob("*.txt")):
        documents.append(path.read_text(encoding="utf-8", errors="ignore"))
    return documents


def baseline_answer(question: str) -> str:
    return (
        "[Baseline placeholder] "
        f"Question: {question}. "
        "No retrieval context was used."
    )


def retrieval_answer(question: str, documents: list[str]) -> str:
    snippet = " ".join(documents)[:240]
    return (
        "[Retrieval placeholder] "
        f"Question: {question}. "
        f"Context snippet: {snippet}"
    )


def compare_answers(baseline: str, with_retrieval: str) -> str:
    if baseline == with_retrieval:
        return "No visible difference. Improve prompt or context setup."
    return "Difference observed. Document one baseline failure that retrieval fixes."


# Code
def main() -> int:
    docs_folder = Path(__file__).resolve().parent / "local_docs"
    question = "Which market had the largest quarter-over-quarter growth in this mini corpus?"

    documents = read_local_documents(docs_folder)
    baseline = baseline_answer(question)
    with_retrieval = retrieval_answer(question, documents)
    verdict = compare_answers(baseline, with_retrieval)

    print("baseline_answer=")
    print(baseline)
    print("\nretrieval_answer=")
    print(with_retrieval)
    print("\ncomparison_note=")
    print(verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
