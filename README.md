# TI Student Agent Pack

Portable, self-contained workspace for Tinbergen Institute workshop exercises.

## Workflow Track

Default mode is **Track A (local-first, no GitHub workflow required)**.

- Do exercises in `exercises/E1.md` ... `exercises/E12.md`
- Submit with `uv run python tools/submit_exercise.py --from-markdown exercises/<EXERCISE_ID>.md`
- Keep all progress local in this folder

GitHub issues and PRs are optional and only needed for advanced collaboration drills.

## Quick Start

### Option 1: One-line Install (Recommended)

```bash
curl -sL https://raw.githubusercontent.com/finnoh/ti-student-agent-pack/main/install.sh | bash
```

This will:
1. Clone the repository to `student-agent-pack/` directory
2. Set up your environment
3. Prompt you to create/login OpenRouter account (`https://openrouter.ai/`) and paste your API key
4. Write `.env` defaults for OpenRouter backend (`OPENROUTER_API_KEY`, `OPENAI_BASE_URL`, default free model)
5. Optionally install OpenCode (coding agent)
6. Configure `opencode.json` with the LangChain docs MCP (`https://docs.langchain.com/mcp`)
7. Configure MCP defaults for Cursor (`.cursor/mcp.json`) and VS Code (`.vscode/mcp.json`)

**Requirements:**
- Git (for cloning)
- Python 3.10+
- uv (recommended; auto-detected by installer)

`gh` (GitHub CLI) is **not required** for Track A.

If you choose `codex` or `claude` during install, the installer also attempts a direct CLI MCP registration for that agent.

### Option 2: Manual Installation

1. Download the zip file from [GitHub releases](https://github.com/finnoh/ti-student-agent-pack/releases)
2. Extract it to a new folder
3. Run the installer:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

## What's Included

- **Exercise files (E1-E12)** - Pre-created templates for all workshop exercises
- **Submission tools** - Python scripts for submitting exercises
- **Jan coaching agent** (`AGENTS.md`) - Your AI tutor
- **Progress dashboard** - Track your exercise completion
- **Course Q&A tool** - Ask questions about course materials
- **OpenCode config** (`opencode.json`) - Jan instructions + LangChain docs MCP
- **Jan modes in OpenCode** - `teacher` (default, coach-only), `code` (selective code in `exercises/`), `supervisor` (admin recovery)
- **Cursor MCP config** (`.cursor/mcp.json`) - LangChain docs MCP
- **VS Code MCP config** (`.vscode/mcp.json`) - LangChain docs MCP
- **OpenRouter free model list** (`config/openrouter_free_models.json`) - Ranked defaults (best to worst)

## OpenRouter Defaults

- API key variable: `OPENROUTER_API_KEY` (stored in root `.env`)
- Backend URL: `https://openrouter.ai/api/v1`
- Default model ranking (best to worst):
  1. `nvidia/nemotron-3-super-120b-a12b:free`
  2. `minimax/minimax-m2.5:free`
  3. `stepfun/step-3.5-flash:free`
  4. `arcee-ai/trinity-large-preview:free`
  5. `openai/gpt-oss-120b:free`
  6. `z-ai/glm-4.5-air:free`

Students can override model settings in `.env`, but the installer sets this free-model order as default.

## Next Steps

1. Open the `student-agent-pack/` folder in your coding agent (VS Code, Cursor, OpenCode, etc.)
2. Use `teacher` mode for guidance; switch to `code` mode when you want Jan to create/edit small files in `exercises/`.
3. Ask explicitly: "Create `exercises/...` now and tell me how to open it in VS Code."
4. Run `uv sync` once to create `.venv` (if installer did not already do it)
5. Confirm `.env` contains your `OPENROUTER_API_KEY`
6. Edit `config/form_config.json` with your Google Form details
7. Complete `BOOTSTRAP.md` with your information
8. Start working on exercises in the `exercises/` directory

## Manual Backup Mode

If agent-assisted flow fails, print a fallback packet + manual submission link:

```bash
uv run python tools/print_exercise_packet.py --exercise-id E3
```

This shows the objective, deliverable target, and the Google Form URL (prefilled with `exercise_id` when field IDs are configured).

## Exercise Progress Dashboard

Track all exercises with status symbols:

```bash
uv run python tools/progress_dashboard.py
```

Legend: blank = not started, `[ ]` = started, `[X]` = submitted.

Sequential recommendation helper:

```bash
uv run python tools/recommend_next_exercise.py
```

## Startup File Hygiene

To keep shared repos clean, remove the local startup marker before push:

```bash
uv run python tools/strip_startup_complete.py
```

The installer also sets a local pre-push hook that checks this automatically.

## Exercise Script Hygiene

To reset Python scripts under `exercises/` to a minimal template before push:

```bash
uv run python tools/strip_exercise_scripts.py
```

The local pre-push hook runs this automatically and blocks push if it rewrote files.

## Full Reset (Dangerous)

Reset is allowed only in supervisor mode.

To reset `student-agent-pack/` to a fresh remote state:

```bash
uv run python tools/full_reset_student_pack.py
```

The command asks for explicit confirmation (`RESET`) before discarding local changes.
It must be run in an interactive terminal; confirmation cannot be bypassed.

## Jan - Your AI Tutor

Jan is your AI tutor for the Tinbergen Institute workshop.

## Teacher Mode (OpenCode)

OpenCode includes a `teacher` primary agent mode in `opencode.json`.

- It is coaching-only and intentionally restricted.
- It can run `bash`, `webfetch`, `task`, and `skill` tools for coaching support.
- It cannot edit files.
- It asks students to execute steps and provide evidence.
- It cannot execute the full reset flow.

For programming subtasks, Jan should suggest switching to `code` mode, apply one small patch, and then return to teacher coaching.

Default: the OpenCode `build` agent is configured to start in this teacher mode behavior.

In OpenCode, use Tab to cycle primary agents and select `teacher`.
Use Tab to switch to `code` for selective coding help.
Use `supervisor` mode only for administrative recovery actions like full reset.
When you open Jan, it guides you through exercises with concise step-by-step coaching.

## More Information

- Full documentation: See `AGENTS.md`
- Workshop materials: Visit [Tinbergen Institute Workshop Site](https://finnoh.github.io/ws_genai_eb/)
