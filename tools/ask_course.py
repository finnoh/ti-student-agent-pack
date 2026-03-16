#!/usr/bin/env python3

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def pack_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_index_path() -> Path:
    return pack_root() / ".index" / "course_index.json"


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "what",
    "when",
    "where",
    "which",
    "with",
    "you",
    "your",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask course questions using the local course index.")
    parser.add_argument("--q", required=True, help="Question to answer")
    parser.add_argument("--index-path", default=str(default_index_path()), help="Path to course index JSON")
    parser.add_argument("--top-k", type=int, default=5, help="How many chunks to retrieve")
    parser.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    parser.add_argument("--chat-model", default=os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini"))
    parser.add_argument("--embedding-model", default="", help="Override embedding model for query vector")
    parser.add_argument("--no-llm", action="store_true", help="Do retrieval only (no answer generation)")
    parser.add_argument("--show-snippets", action="store_true", help="Print retrieved snippets")
    return parser.parse_args()


def tokenize(text: str) -> list[str]:
    return [tok for tok in re.findall(r"[a-z0-9]+", text.lower()) if tok and tok not in STOPWORDS]


def lexical_score(query: str, text: str) -> float:
    query_tokens = tokenize(query)
    if not query_tokens:
        return 0.0
    doc_tokens = set(tokenize(text))
    if not doc_tokens:
        return 0.0
    hits = sum(1 for token in query_tokens if token in doc_tokens)
    return hits / len(query_tokens)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for av, bv in zip(a, b):
        dot += av * bv
        na += av * av
        nb += bv * bv
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def post_json(url: str, payload: dict, headers: dict[str, str], timeout: int = 60) -> dict:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def embed_query(question: str, api_key: str, model: str, base_url: str) -> list[float]:
    url = base_url.rstrip("/") + "/embeddings"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"model": model, "input": question}
    try:
        data = post_json(url=url, payload=payload, headers=headers)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore") if getattr(exc, "fp", None) else ""
        raise RuntimeError(f"Embedding query failed: HTTP {exc.code} {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Embedding query failed: {exc.reason}") from exc

    items = data.get("data", [])
    if not items:
        raise RuntimeError("Embedding query returned no vectors")
    vector = items[0].get("embedding", [])
    if not isinstance(vector, list) or not vector:
        raise RuntimeError("Embedding query returned an empty vector")
    return vector


def rank_entries(question: str, entries: list[dict], query_vector: list[float] | None, top_k: int) -> list[dict]:
    ranked: list[dict] = []
    for entry in entries:
        text = str(entry.get("text", ""))
        lex = lexical_score(question, text)
        vec = 0.0
        if query_vector is not None and isinstance(entry.get("embedding"), list):
            vec = cosine_similarity(query_vector, entry["embedding"])
            vec = max(0.0, (vec + 1.0) / 2.0)
        combined = (0.8 * vec + 0.2 * lex) if query_vector is not None else lex
        ranked.append({"entry": entry, "score": combined, "vector_score": vec, "lexical_score": lex})

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[: max(1, top_k)]


def confidence_label(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def build_context_block(hits: list[dict]) -> str:
    lines: list[str] = []
    for idx, hit in enumerate(hits, start=1):
        entry = hit["entry"]
        source = entry.get("source_path", "unknown")
        text = re.sub(r"\s+", " ", str(entry.get("text", "")).strip())
        snippet = text[:900]
        lines.append(f"[S{idx}] source={source} chunk={entry.get('chunk_index', '?')}")
        lines.append(snippet)
        lines.append("")
    return "\n".join(lines).strip()


def generate_answer_with_llm(
    question: str,
    hits: list[dict],
    api_key: str,
    chat_model: str,
    base_url: str,
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    context = build_context_block(hits)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a course Q&A assistant. Answer only using the provided sources. "
                "If the answer is not in the sources, say that clearly. "
                "Keep it concise (3-6 sentences) and cite sources inline like [S1], [S2]."
            ),
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\nSources:\n{context}",
        },
    ]
    payload = {"model": chat_model, "messages": messages, "temperature": 0.2}

    try:
        data = post_json(url=url, payload=payload, headers=headers)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore") if getattr(exc, "fp", None) else ""
        raise RuntimeError(f"Answer generation failed: HTTP {exc.code} {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Answer generation failed: {exc.reason}") from exc

    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("Answer generation returned no choices")
    message = choices[0].get("message", {})
    content = str(message.get("content", "")).strip()
    if not content:
        raise RuntimeError("Answer generation returned empty content")
    return content


def extractive_fallback(question: str, hits: list[dict]) -> str:
    if not hits:
        return "I could not find relevant material in the current index."

    exercise_match = re.search(r"\bE\d+\b", question, re.IGNORECASE)
    exercise_id = exercise_match.group(0).upper() if exercise_match else ""

    candidates: list[tuple[float, str]] = []
    for hit in hits[:3]:
        text = str(hit["entry"].get("text", "")).strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            clean = re.sub(r"\s+", " ", sentence).strip()
            if len(clean) < 35:
                continue
            score = lexical_score(question, clean)
            if exercise_id and exercise_id in clean.upper():
                score += 0.5
            candidates.append((score, clean))

    if not candidates:
        text = str(hits[0]["entry"].get("text", "")).strip()
        compact = re.sub(r"\s+", " ", text)
        return compact[:450] + ("..." if len(compact) > 450 else "")

    candidates.sort(key=lambda item: item[0], reverse=True)
    top = [sentence for _, sentence in candidates[:2]]
    return " ".join(top)


def main() -> int:
    args = parse_args()
    index_path = Path(args.index_path)
    if not index_path.exists():
        print(f"ERROR: index not found at {index_path}")
        print("Run: python tools/index_course_materials.py")
        return 2

    index_data = json.loads(index_path.read_text(encoding="utf-8"))
    entries = index_data.get("entries", [])
    if not isinstance(entries, list) or not entries:
        print("ERROR: index has no entries.")
        print("Run: python tools/index_course_materials.py")
        return 2

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    has_index_embeddings = bool(index_data.get("has_embeddings", False))
    query_vector = None

    if has_index_embeddings and api_key:
        model = args.embedding_model.strip() or str(index_data.get("embedding_model", "text-embedding-3-small"))
        try:
            query_vector = embed_query(args.q, api_key=api_key, model=model, base_url=args.base_url)
        except Exception as exc:
            print(f"Warning: {exc}")
            print("Falling back to lexical retrieval.")
    elif has_index_embeddings and not api_key:
        print("Warning: OPENAI_API_KEY is not set; using lexical retrieval only.")

    hits = rank_entries(question=args.q, entries=entries, query_vector=query_vector, top_k=max(1, args.top_k))
    if not hits or hits[0]["score"] <= 0.0:
        print("I could not find an answer in the indexed material.")
        return 0

    if args.no_llm or not api_key:
        answer = extractive_fallback(args.q, hits)
    else:
        try:
            answer = generate_answer_with_llm(
                question=args.q,
                hits=hits,
                api_key=api_key,
                chat_model=args.chat_model,
                base_url=args.base_url,
            )
        except Exception as exc:
            print(f"Warning: {exc}")
            print("Falling back to extractive answer.")
            answer = extractive_fallback(args.q, hits)

    top_confidence = confidence_label(hits[0]["score"])
    print(f"Q: {args.q}")
    print("")
    print("Answer:")
    print(answer)
    print("")
    print(f"Confidence: {top_confidence}")
    print("Sources:")
    for idx, hit in enumerate(hits[:4], start=1):
        entry = hit["entry"]
        source = entry.get("source_path", "unknown")
        print(f"- [S{idx}] {source} (chunk {entry.get('chunk_index', '?')})")

    if args.show_snippets:
        print("")
        print("Snippets:")
        for idx, hit in enumerate(hits[:3], start=1):
            snippet = re.sub(r"\s+", " ", str(hit["entry"].get("text", "")).strip())
            print(f"- [S{idx}] {snippet[:280]}{'...' if len(snippet) > 280 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
