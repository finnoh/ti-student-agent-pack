from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(relative_path: str, module_name: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


e01 = load_module("exercises/01/hello_world.py", "e01_hello_world")
e02 = load_module("exercises/02/prompt_lab.py", "e02_prompt_lab")
e03 = load_module("exercises/03/retrieval_ab.py", "e03_retrieval_ab")
e04 = load_module("exercises/04/tool_agent.py", "e04_tool_agent")
e05 = load_module("exercises/05/mcp_tool.py", "e05_mcp_tool")
e06 = load_module("exercises/06/memory_demo.py", "e06_memory_demo")


def test_e01_mean_income_and_agent_payload() -> None:
    csv_path = ROOT / "exercises/01/data/tiny.csv"
    rows = e01.load_rows(csv_path)
    mean = e01.mean_income(rows)
    payload = json.loads(e01.try_langchain_response(rows, mean))

    assert len(rows) == 4
    assert mean == 175.0
    assert payload["rows"] == 4
    assert payload["mean_income"] == 175.0


def test_e02_extraction_and_verification() -> None:
    model = e02.build_language_model()
    raw = e02.run_country_extraction(model, e02.NOISY_PARAGRAPH)
    parsed = e02.parse_python_list(raw)
    structured = e02.run_structured_extraction(model, e02.NOISY_PARAGRAPH)

    assert "Italy" in parsed
    assert "Canada" in parsed
    assert "Wakanda" not in parsed
    assert e02.verify_countries(structured) is True


def test_e03_retrieval_identifies_best_region() -> None:
    docs = e03.read_local_documents(ROOT / "exercises/03/local_docs")
    question = "Which market had the largest quarter-over-quarter growth in this mini corpus?"
    retriever = e03.build_retriever(docs, k=2)
    hits = retriever.invoke(question)
    sources = [doc.metadata.get("source", "") for doc in hits]
    combined = " ".join([doc.page_content for doc in hits])

    assert len(docs) >= 5
    assert len(hits) == 2
    assert "market_note_3.txt" in sources
    assert "Region C" in combined


def test_e04_tool_agent_success_and_missing_values_path() -> None:
    results, trace, final = e04.run_tool_agent("region_code=C; values=12,15,18")
    assert len(results) == 2
    assert results[0].name == "lookup_label"
    assert results[1].name == "calc_average"
    assert any(step.action.startswith("plausibility_check") for step in trace)
    assert "15.00" in final
    assert "region" in final.lower()

    results2, trace2, final2 = e04.run_tool_agent("region_code=B; values=")
    assert len(results2) >= 1
    assert any("cannot compute average" in step.observation.lower() for step in trace2)
    assert "average" in final2.lower()


def test_e05_helpers_for_mcp_output() -> None:
    mock = {"messages": [type("M", (), {"type": "tool", "content": "ok"})(), type("M", (), {"type": "ai", "content": "Done"})()]}
    assert e05.count_tool_messages(mock) == 1
    assert e05.extract_final_text(mock) == "Done"


def test_e06_memory_trace_and_retrieval_fact() -> None:
    e06.SESSION_STATE.clear()
    short_set = e06.remember_chart_style.invoke({"chart_style": "line charts"})
    short_get = e06.recall_chart_style.invoke({})

    assert "line charts" in short_set.lower()
    assert "line charts" in short_get.lower()

    save_msg = e06.save_project_deadline.invoke({"project": "E06 test", "deadline": "2026-05-15"})
    load_msg = e06.load_project_deadline.invoke({"project": "E06 test"})
    assert "saved" in save_msg.lower()
    assert "2026-05-15" in load_msg
