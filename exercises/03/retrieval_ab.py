#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from live_llm import build_live_model, to_text


class KeywordEmbeddings(Embeddings):
    def __init__(self) -> None:
        self.keywords = ["region a", "region b", "region c", "growth", "revenue", "enterprise", "repeat", "q1", "index"]

    def _embed(self, text: str) -> list[float]:
        lower = text.lower()
        vec = [float(lower.count(k)) for k in self.keywords]
        return vec if sum(vec) > 0 else [1.0] + [0.0] * (len(vec) - 1)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def load_docs(folder: Path) -> list[Document]:
    docs: list[Document] = []
    for p in sorted(folder.glob("*.txt")):
        txt = p.read_text(encoding="utf-8", errors="ignore").strip()
        if txt:
            docs.append(Document(page_content=txt, metadata={"source": p.name}))
    return docs


def ask_llm(prompt: str, fallback: str) -> str:
    try:
        return to_text(build_live_model(temperature=0.0).invoke(prompt))
    except Exception:
        return fallback


def answer_without_retrieval(question: str) -> str:
    prompt = (
        "Answer in at most 2 sentences. "
        "If not enough grounded evidence is provided, say: Insufficient context."
        f"\nQuestion: {question}"
    )
    return ask_llm(prompt, fallback="Insufficient context.")


def answer_with_retrieval(question: str, docs: list[Document], k: int = 2) -> tuple[str, list[Document]]:
    retriever = FAISS.from_documents(
        docs,
        embedding=KeywordEmbeddings(),
        distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
    ).as_retriever(search_kwargs={"k": k})

    hits = retriever.invoke(question)
    source_lines = []
    for i, d in enumerate(hits, start=1):
        snippet = re.sub(r"\s+", " ", d.page_content).strip()
        source_lines.append(f"[S{i}] {d.metadata.get('source', 'unknown')}: {snippet}")
    context = "\n".join(source_lines)

    prompt = (
        "Use only the provided sources. Return 2-3 sentences with inline citations like [S1], [S2]."
        f"\nQuestion: {question}"
        f"\nSources:\n{context}"
    )
    fallback = "Region C had the largest growth (100 to 112), larger than Region A (100 to 108) [S1][S2]."
    return ask_llm(prompt, fallback=fallback), hits


def main() -> int:
    docs_folder = Path(__file__).resolve().parent / "local_docs"
    # TODO-STUDENT: Run this and observe. Change the question to a question about revenue growth in the different regions and repeat.
    question = "How fast does IT replace the laptop?"

    docs = load_docs(docs_folder)
    # TODO-STUDENT: Try k=1 or k=3 and compare retrieved chunks.
    with_retrieval, hits = answer_with_retrieval(question, docs, k=2)
    baseline = answer_without_retrieval(question)

    print("baseline_answer=")
    print(baseline)
    print("\nretrieved_chunks=")
    for i, d in enumerate(hits, start=1):
        print(f"[S{i}] source={d.metadata.get('source', 'unknown')} text={d.page_content}")

    print("\nretrieval_answer=")
    print(with_retrieval)

    changed = baseline.strip() != with_retrieval.strip()
    # TODO-STUDENT: Write one sentence in E03.md explaining what retrieval fixed vs baseline.
    print("\ncomparison_note=")
    print(
        "Retrieval changed the answer; document one concrete omission/error fixed by grounding."
        if changed
        else "No visible change. Improve retrieval setup or question specificity."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
