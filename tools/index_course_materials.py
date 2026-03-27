#!/usr/bin/env python3

import argparse
import html
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


def pack_root() -> Path:
    return Path(__file__).resolve().parent.parent


def repo_root() -> Path:
    return pack_root().parent


def default_index_path() -> Path:
    return pack_root() / ".index" / "course_index.json"


def default_site_url() -> str:
    return os.environ.get("COURSE_WEBSITE_URL", "https://finnoh.github.io/ws_genai_eb/").strip()


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


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def resolve_api_key() -> str:
    return os.environ.get("OPENROUTER_API_KEY", "").strip() or os.environ.get("OPENAI_API_KEY", "").strip()


def default_sources() -> list[Path]:
    root = repo_root()
    candidates = [
        pack_root() / "context" / "course_context.md",
        root / "exercises" / "drafts.md",
        root / "exercises" / "rubrics.md",
        root / "slides" / "day1_foundations.qmd",
        root / "slides" / "day2_advanced.qmd",
    ]
    return [path for path in candidates if path.exists()]


def parse_args() -> argparse.Namespace:
    apply_dotenv_defaults()
    parser = argparse.ArgumentParser(description="Build a lightweight local course index for question mode.")
    parser.add_argument(
        "--source-mode",
        choices=["website", "local", "hybrid"],
        default="website",
        help="Where to load source material from",
    )
    parser.add_argument("--source", action="append", default=[], help="Source file path (repeatable)")
    parser.add_argument("--site-url", default=default_site_url(), help="Published course website base URL")
    parser.add_argument("--max-site-pages", type=int, default=40, help="Maximum docs pages to fetch from sitemap")
    parser.add_argument("--index-path", default=str(default_index_path()), help="Output index JSON path")
    parser.add_argument("--chunk-size", type=int, default=900, help="Chunk size in characters")
    parser.add_argument("--chunk-overlap", type=int, default=120, help="Chunk overlap in characters")
    parser.add_argument("--embedding-model", default="text-embedding-3-small", help="OpenAI embedding model")
    parser.add_argument("--batch-size", type=int, default=32, help="Embedding batch size")
    parser.add_argument("--no-embeddings", action="store_true", help="Build lexical-only index")
    parser.add_argument(
        "--require-embeddings",
        action="store_true",
        help="Fail if embeddings cannot be generated",
    )
    parser.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", OPENROUTER_BASE_URL))
    return parser.parse_args()


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.strip()


def split_long_paragraph(paragraph: str, chunk_size: int, overlap: int) -> list[str]:
    if len(paragraph) <= chunk_size:
        return [paragraph]
    out: list[str] = []
    step = max(1, chunk_size - max(0, overlap))
    for start in range(0, len(paragraph), step):
        out.append(paragraph[start : start + chunk_size].strip())
        if start + chunk_size >= len(paragraph):
            break
    return [part for part in out if part]


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    expanded: list[str] = []
    for paragraph in paragraphs:
        expanded.extend(split_long_paragraph(paragraph, chunk_size, overlap))

    chunks: list[str] = []
    current = ""
    for paragraph in expanded:
        if not current:
            current = paragraph
            continue
        candidate = current + "\n\n" + paragraph
        if len(candidate) <= chunk_size:
            current = candidate
            continue
        chunks.append(current)
        tail = current[-overlap:] if overlap > 0 else ""
        current = (tail + "\n\n" + paragraph).strip() if tail else paragraph

    if current:
        chunks.append(current)
    return chunks


def to_repo_relative(path: Path) -> str:
    root = repo_root()
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)


def fetch_text(url: str, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": "TI-Student-Agent-Pack/1.2"}, method="GET")
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="ignore")


def html_to_text(raw_html: str) -> str:
    no_script = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw_html, flags=re.IGNORECASE | re.DOTALL)
    no_style = re.sub(r"<style\b[^>]*>.*?</style>", " ", no_script, flags=re.IGNORECASE | re.DOTALL)
    main_match = re.search(r"<main\b[^>]*>(.*?)</main>", no_style, flags=re.IGNORECASE | re.DOTALL)
    body = main_match.group(1) if main_match else no_style
    no_tags = re.sub(r"<[^>]+>", " ", body)
    decoded = html.unescape(no_tags)
    return normalize_whitespace(re.sub(r"\s+", " ", decoded))


def discover_docs_urls(site_url: str, max_pages: int) -> list[str]:
    base = site_url if site_url.endswith("/") else site_url + "/"
    candidates = [urljoin(base, "sitemap.xml")]
    parsed = urlparse(base)
    if parsed.path and parsed.path != "/":
        trimmed = parsed.path.strip("/").split("/")[0]
        rootish = f"{parsed.scheme}://{parsed.netloc}/{trimmed}/sitemap.xml"
        if rootish not in candidates:
            candidates.append(rootish)

    sitemap_xml = ""
    last_error = ""
    for sitemap_url in candidates:
        try:
            sitemap_xml = fetch_text(sitemap_url)
            break
        except Exception as exc:
            last_error = str(exc)

    if not sitemap_xml:
        raise RuntimeError(f"Could not fetch sitemap.xml from {base}: {last_error}")

    urls = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sitemap_xml)
    docs_urls = [u for u in urls if "/docs/" in u and not u.endswith(".xml")]
    seen = set()
    unique: list[str] = []
    for url in docs_urls:
        if url in seen:
            continue
        seen.add(url)
        unique.append(url)
        if len(unique) >= max(1, max_pages):
            break
    return unique


def fetch_website_docs(site_url: str, max_pages: int) -> list[dict]:
    urls = discover_docs_urls(site_url=site_url, max_pages=max_pages)
    docs: list[dict] = []
    for idx, url in enumerate(urls, start=1):
        try:
            raw_html = fetch_text(url)
            text = html_to_text(raw_html)
            if not text:
                continue
            docs.append({"source_path": url, "text": text})
            print(f"Fetched {idx}/{len(urls)} docs pages")
        except Exception as exc:
            print(f"Warning: failed to fetch {url}: {exc}")
    return docs


def build_entries_from_documents(documents: list[dict], chunk_size: int, overlap: int) -> list[dict]:
    entries: list[dict] = []
    running_id = 1
    for doc in documents:
        source_path = str(doc.get("source_path", "unknown"))
        normalized = normalize_whitespace(str(doc.get("text", "")))
        if not normalized:
            continue

        for idx, chunk in enumerate(chunk_text(normalized, chunk_size=chunk_size, overlap=overlap), start=1):
            entries.append(
                {
                    "id": f"C{running_id}",
                    "source_path": source_path,
                    "chunk_index": idx,
                    "text": chunk,
                    "char_count": len(chunk),
                }
            )
            running_id += 1
    return entries


def collect_local_documents(source_paths: list[Path]) -> list[dict]:
    docs: list[dict] = []
    for source in source_paths:
        try:
            text = source.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            print(f"Warning: could not read {source}: {exc}")
            continue
        docs.append({"source_path": to_repo_relative(source), "text": text})
    return docs


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


def embed_texts(
    texts: list[str],
    api_key: str,
    model: str,
    base_url: str,
    batch_size: int,
) -> list[list[float]]:
    url = base_url.rstrip("/") + "/embeddings"
    all_vectors: list[list[float]] = []
    headers = {"Authorization": f"Bearer {api_key}"}

    total = len(texts)
    for start in range(0, total, max(1, batch_size)):
        end = min(total, start + max(1, batch_size))
        batch = texts[start:end]
        payload = {"model": model, "input": batch}
        try:
            data = post_json(url=url, payload=payload, headers=headers)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore") if getattr(exc, "fp", None) else ""
            raise RuntimeError(f"Embedding request failed: HTTP {exc.code} {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"Embedding request failed: {exc.reason}") from exc

        items = data.get("data", [])
        if len(items) != len(batch):
            raise RuntimeError("Embedding response size mismatch")
        vectors = [item.get("embedding", []) for item in items]
        if any(not isinstance(vec, list) or not vec for vec in vectors):
            raise RuntimeError("Embedding response contained empty vectors")
        all_vectors.extend(vectors)
        print(f"Embedded {end}/{total} chunks")

    return all_vectors


def main() -> int:
    args = parse_args()
    index_path = Path(args.index_path)
    source_paths = [Path(value).resolve() for value in args.source] if args.source else default_sources()
    local_docs: list[dict] = []
    remote_docs: list[dict] = []

    if args.source_mode in {"local", "hybrid"}:
        missing = [path for path in source_paths if not path.exists()]
        if missing:
            for path in missing:
                print(f"Warning: source file not found: {path}")
        source_paths = [path for path in source_paths if path.exists()]
        local_docs = collect_local_documents(source_paths)

    if args.source_mode in {"website", "hybrid"}:
        try:
            remote_docs = fetch_website_docs(site_url=args.site_url, max_pages=max(1, args.max_site_pages))
        except Exception as exc:
            if args.source_mode == "website":
                print(f"ERROR: {exc}")
                return 2
            print(f"Warning: website indexing failed: {exc}")

    documents = remote_docs + local_docs
    if not documents:
        print("ERROR: no source material found to index.")
        return 2

    entries = build_entries_from_documents(
        documents,
        chunk_size=max(200, args.chunk_size),
        overlap=max(0, args.chunk_overlap),
    )
    if not entries:
        print("ERROR: no index entries were generated.")
        return 2

    use_embeddings = not args.no_embeddings
    has_embeddings = False
    api_key = resolve_api_key()

    if use_embeddings:
        if not api_key:
            msg = "OPENROUTER_API_KEY (or OPENAI_API_KEY) is not set; building lexical-only index."
            if args.require_embeddings:
                print(f"ERROR: {msg}")
                return 2
            print(f"Warning: {msg}")
        else:
            print(f"Generating embeddings with model {args.embedding_model}...")
            try:
                vectors = embed_texts(
                    texts=[entry["text"] for entry in entries],
                    api_key=api_key,
                    model=args.embedding_model,
                    base_url=args.base_url,
                    batch_size=max(1, args.batch_size),
                )
            except Exception as exc:
                if args.require_embeddings:
                    print(f"ERROR: {exc}")
                    return 2
                print(f"Warning: {exc}")
                print("Continuing with lexical-only index.")
            else:
                for entry, vector in zip(entries, vectors):
                    entry["embedding"] = vector
                has_embeddings = True

    payload = {
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "repo_root": str(repo_root()),
        "source_mode": args.source_mode,
        "site_url": args.site_url,
        "embedding_model": args.embedding_model,
        "has_embeddings": has_embeddings,
        "chunk_size": max(200, args.chunk_size),
        "chunk_overlap": max(0, args.chunk_overlap),
        "sources": [doc["source_path"] for doc in documents],
        "entries": entries,
    }

    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(payload, ensure_ascii=True) + "\n", encoding="utf-8")

    mode = "vector + lexical" if has_embeddings else "lexical-only"
    print(f"Wrote index: {index_path}")
    print(f"Indexed chunks: {len(entries)} ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
