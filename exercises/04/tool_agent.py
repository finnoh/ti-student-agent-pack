#!/usr/bin/env python3

from pathlib import Path
import re
import sys

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from live_llm import build_live_model, to_text


REGION_LABELS = {"A": "North region", "B": "South region", "C": "West region"}


@tool
def lookup_label_tool(code: str) -> str:
    """Return a human-readable region label from a short region code."""
    # TODO-STUDENT: Add your own region codes (for example D/E) and rerun.
    return REGION_LABELS.get(code.upper(), "Unknown region")

# TODO-STUDENT: Can you write a tool that looks up the label for a region? Try to wire it into the LLM below...

@tool
def calc_average_tool(values: list[float]) -> str:
    """Compute arithmetic mean for a non-empty list of numbers."""
    if not values:
        return "No numeric values provided; cannot compute average."
    return f"{sum(values) / len(values):.2f}"


def parse_values(question: str) -> list[float]:
    match = re.search(r"values\s*=\s*([0-9,\.\-\s]+)", question)
    if not match:
        return []
    return [float(x.strip()) for x in match.group(1).split(",") if x.strip()]


def run(question: str) -> tuple[str, list[str], str]:
    model = build_live_model(temperature=0.0).bind_tools([lookup_label_tool, calc_average_tool])
    system = SystemMessage(
        content=(
            "You are a research assistant. Call BOTH tools exactly once before answering. "
            "Pass region code and numeric list from the user question."
        )
    )
    user = HumanMessage(content=question)
    try:
        first = model.invoke([system, user])
    except Exception:
        code_match = re.search(r"region_code\s*=\s*([A-Za-z])", question)
        code = code_match.group(1).upper() if code_match else ""
        region = lookup_label_tool.invoke({"code": code})
        values = parse_values(question)
        average = calc_average_tool.invoke({"values": values})
        trace = [
            f"tool_call_1 -> lookup_label_tool(args={{'code': '{code}'}}) => {region}",
            f"tool_call_2 -> calc_average_tool(args={{'values': {values}}}) => {average}",
        ]
        if values and average.replace(".", "", 1).isdigit():
            manual = sum(values) / len(values)
            ok = abs(float(average) - manual) < 0.01
            trace.append(f"plausibility_check -> {'pass' if ok else 'fail'} (manual={manual:.2f})")
        else:
            trace.append("plausibility_check -> skipped")
        return region, trace, f"Region={region}; average={average}."

    if not first.tool_calls:
        trace = ["llm_tool_call_check -> no tool calls returned"]
        return "Unknown region", trace, "Answer unavailable because no tool calls were returned."

    trace: list[str] = []
    region = "Unknown region"
    average = "unavailable"
    tool_messages: list[ToolMessage] = []

    for idx, call in enumerate(first.tool_calls, start=1):
        name = call.get("name", "")
        args = call.get("args", {})
        if name == "lookup_label_tool":
            out = lookup_label_tool.invoke(args)
            region = out
        elif name == "calc_average_tool":
            out = calc_average_tool.invoke(args)
            average = out
        else:
            out = f"Unsupported tool call: {name}"
        trace.append(f"tool_call_{idx} -> {name}(args={args}) => {out}")
        tool_messages.append(ToolMessage(tool_call_id=call.get("id", f"call_{idx}"), content=out))

    try:
        second = model.invoke([system, user, first, *tool_messages])
        final_answer = to_text(second)
    except Exception:
        final_answer = f"Region={region}; average={average}."

    values = parse_values(question)
    if values and average.replace(".", "", 1).isdigit():
        manual = sum(values) / len(values)
        ok = abs(float(average) - manual) < 0.01
        trace.append(f"plausibility_check -> {'pass' if ok else 'fail'} (manual={manual:.2f})")
    else:
        trace.append("plausibility_check -> skipped")

    return region, trace, final_answer


def main() -> int:
    # TODO-STUDENT: Try changing this question format and see if tool use still works.
    question = "For region_code=C and values=12,15,18, identify the region and compute the average."
    region, trace, final = run(question)

    print(f"question={question}")
    print(f"region={region}")
    print("trace=")
    for line in trace:
        print(line)
    print(f"final_answer={final}")
    print("failure_mode_note=If a model does not support tool calls, no tool_calls will be returned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
