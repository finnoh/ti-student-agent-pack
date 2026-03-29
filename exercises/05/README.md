# E05 MCP Time Server Scaffold

Use this folder for Exercise E05.

## Goal

- Connect a LangChain agent to a real MCP server (`mcp-server-time`).
- Run one successful time conversion call.
- Run one error-path call and verify graceful handling.

## Suggested run

```bash
uv run python exercises/05/mcp_tool.py
```

## Tool-calling requirement

- This script uses `langchain-mcp-adapters` + `create_agent(...)` with MCP tools.
- MCP server is launched over stdio via `uvx mcp-server-time`.
- References:
  - https://docs.langchain.com/oss/python/langchain/mcp#quickstart
  - https://github.com/modelcontextprotocol/servers/tree/main/src/time

## Notes file

- `exercises/05/sanity_notes.md`

## Submission draft

- `exercises/05/E05.md`
