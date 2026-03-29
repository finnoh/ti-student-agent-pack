#!/usr/bin/env python3

import json
from pathlib import Path
import sys

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from live_llm import build_live_model, to_text

# TODO-STUDENT: What is this?
SESSION_STATE: dict[str, str] = {}
# TODO-STUDENT: You can also look at long_term_store.json directly, and you can edit it, ...
STORE_PATH = Path(__file__).with_name("long_term_store.json")

# TODO-STUDENT: What does this do? How does it compare to SESSION_STATE?
def _read_store() -> dict[str, str]:
    if not STORE_PATH.exists():
        return {}
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def _write_store(data: dict[str, str]) -> None:
    STORE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


@tool
def remember_chart_style(chart_style: str) -> str:
    # TODO-STUDENT: Notice this comment / docstring. Does it matter? What happens when you change it to something ridiculous? What if you change the function name?
    """Save chart style in short-term session memory."""
    SESSION_STATE["chart_style"] = chart_style
    return f"saved_short_term={chart_style}"


@tool
def recall_chart_style() -> str:
    """Read chart style from short-term session memory."""
    return SESSION_STATE.get("chart_style", "no_short_term_chart_style")


@tool
def save_project_deadline(project: str, deadline: str) -> str:
    """Save a project deadline in long-term file memory."""
    store = _read_store()
    store[project] = deadline
    _write_store(store)
    return f"saved_long_term={project}:{deadline}"


@tool
def load_project_deadline(project: str) -> str:
    """Load a project deadline from long-term file memory."""
    store = _read_store()
    return store.get(project, f"no_long_term_deadline_for={project}")


TOOLS = [remember_chart_style, recall_chart_style, save_project_deadline, load_project_deadline]
TOOL_BY_NAME = {t.name: t for t in TOOLS}


def run_turn(user_text: str) -> str:
    model = build_live_model(temperature=0.0).bind_tools(TOOLS)
    messages = [
        SystemMessage(
            content=(
                "You are demonstrating memory behavior. "
                "Use tools to save/load chart preferences and deadlines. "
                "Respond in one short sentence."
            )
        ),
        HumanMessage(content=user_text),
    ]

    for _ in range(3):
        try:
            ai = model.invoke(messages)
        except Exception as exc:
            return f"llm_error={type(exc).__name__}: run again in 30-60s or switch model"
        messages.append(ai)
        if not ai.tool_calls:
            return to_text(ai)
        for call in ai.tool_calls:
            out = TOOL_BY_NAME[call["name"]].invoke(call.get("args", {}))
            messages.append(ToolMessage(tool_call_id=call.get("id", "call_1"), content=str(out)))

    return "tool_loop_limit_reached"


def main() -> int:
    # TODO-STUDENT: Try a different preference key (e.g., color palette) and compare short vs long memory behavior.
    print("SHORT-TERM MEMORY")
    print(run_turn("Remember my chart style is line charts."))
    print(run_turn("What chart style do I prefer?"))

    print("\nNew session starts (short-term reset)")
    SESSION_STATE.clear()
    print(run_turn("What chart style do I prefer?"))

    print("\nLONG-TERM MEMORY")
    print(run_turn("Save this deadline: E06 report is due on 2026-05-15."))
    print(run_turn("What is the deadline for E06 report?"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
