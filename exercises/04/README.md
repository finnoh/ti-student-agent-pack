# E04 Tool-Calling Scaffold

Use this folder for Exercise E04.

## Goal

- Define two simple tools.
- Run one question that needs both tools.
- Record trace evidence and one plausibility check.

## Suggested run

```bash
uv run python exercises/04/tool_agent.py
```

## Tool-calling requirement

- This script now uses LangChain tool calling via `bind_tools(...)` with a live LLM.
- Use a model/provider combo that supports tool calls (OpenRouter model varies by support).
- Reference: https://docs.langchain.com/oss/python/langchain/tools

## Notes file

- `exercises/04/tool_trace_notes.md`

## Submission draft

- `exercises/04/E04.md`
