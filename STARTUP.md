# Startup Checklist

Run this once at the beginning:

```bash
uv run python tools/startup_check.py
```

Note: `gh` (GitHub CLI) is optional in Track A.

If `uv` is unavailable, fallback to:

```bash
python tools/startup_check.py
```

If checks pass during your local session, you may add this header at the top of this file:

`## STARTUP COMPLETE`

The startup check now verifies:

- `OPENROUTER_API_KEY` in environment or root `.env`
- OpenCode default `build` agent is configured for teacher mode

Before committing/pushing, remove `## STARTUP COMPLETE` so the shared template stays clean.

Use:

```bash
uv run python tools/strip_startup_complete.py
```
