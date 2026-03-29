#!/usr/bin/env python3

import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from live_llm import build_live_model


def extract_final_text(result: dict) -> str:
    messages = result.get("messages", [])
    if not messages:
        return ""
    last = messages[-1]
    content = getattr(last, "content", "")
    if isinstance(content, str):
        return content.strip()
    return str(content).strip()


def count_tool_messages(result: dict) -> int:
    messages = result.get("messages", [])
    return sum(1 for msg in messages if getattr(msg, "type", "") == "tool")


async def run() -> int:
    try:
        from langchain.agents import create_agent
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError:
        print("missing_dependency=Install langchain and langchain-mcp-adapters first.")
        print("hint=uv sync --project student-agent-pack")
        return 1

    client = MultiServerMCPClient(
        {
            "time": {
                "transport": "stdio",
                "command": "uvx",
                "args": ["mcp-server-time"],
            }
        }
    )

    tools = await client.get_tools()
    model = build_live_model(temperature=0.0)
    agent = create_agent(model, tools)

    # TODO-STUDENT: Change timezone pairs and compare outputs.
    q_success = "When it is 16:30 in Europe/Amsterdam, what time is it in Asia/Tokyo?"
    # TODO-STUDENT: Try a different failure case (e.g., malformed time 25:99).
    q_error = "Convert 16:30 from Mars/Phobos to Europe/London."

    success_result = await agent.ainvoke({"messages": [{"role": "user", "content": q_success}]})
    success_answer = extract_final_text(success_result)
    success_tools = count_tool_messages(success_result)

    try:
        error_result = await agent.ainvoke({"messages": [{"role": "user", "content": q_error}]})
        error_answer = extract_final_text(error_result)
        error_tools = count_tool_messages(error_result)
    except Exception as exc:
        error_answer = f"tool_error={type(exc).__name__}: {exc}"
        error_tools = 1

    sanity_ok = ("tokyo" in success_answer.lower()) and (success_tools >= 1)
    handled_error = ("error" in error_answer.lower()) or ("invalid" in error_answer.lower()) or ("not" in error_answer.lower())

    print(f"success_question={q_success}")
    print(f"success_tool_calls={success_tools}")
    print(f"success_answer={success_answer}")
    print(f"sanity_check={'pass' if sanity_ok else 'fail'}")

    print(f"error_question={q_error}")
    print(f"error_tool_calls={error_tools}")
    print(f"error_answer={error_answer}")
    # TODO-STUDENT: Tighten this criterion after observing your model/provider behavior.
    print(f"error_path_check={'pass' if handled_error else 'needs_review'}")
    return 0


#TODO-STUDENT: Implement another run() function for a MCP server of your choice: https://github.com/modelcontextprotocol/servers

def main() -> int:
    try:
        return asyncio.run(run())
    except Exception as exc:
        print(f"runtime_error={type(exc).__name__}: {exc}")
        print("hint=Ensure uvx is available and mcp-server-time can start.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
