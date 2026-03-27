# Subtask Tip Bank (E1-E12)

Use these hints when a student is stuck. Keep hints short and actionable.

Legend:
- Terminal = shell commands
- IDE = VS Code/Cursor file edits and run buttons
- Notebook = Jupyter cell-by-cell workflow

## E1 - Setup Jan + OpenRouter + hello world

Subtask 1 - Install + startup checks
- Terminal: `uv run python tools/startup_check.py`
- Tip: If `uv` fails, use `python tools/startup_check.py`.

Subtask 2 - OpenRouter key + defaults
- IDE: open `.env` and confirm `OPENROUTER_API_KEY` and `OPENAI_BASE_URL`.
- Terminal: rerun startup check after edits.

Subtask 3 - Hello world run
- Terminal: `uv run python exercises/e1/hello_world.py`
- Notebook: better if student wants to inspect rows step by step.

## E2 - Prompt anatomy in LangChain code

Subtask 1 - First prompt run
- IDE: create `exercises/e2/prompt_lab.py` or notebook cell with `ChatPromptTemplate`.
- Tip: start simple and print the model output.

Subtask 2 - Country extraction task
- IDE: use the noisy paragraph and ask for a Python list only.
- Tip: include typo-fix rule and fictional-place filter in the prompt.

Subtask 3 - Structured output
- IDE: define a simple Pydantic model with `countries: list[str]`.
- Terminal: run script and verify output parses cleanly.

Subtask 4 - Model and docs orientation
- Browser: scan https://openrouter.ai/rankings and pick one model for E2.
- Browser: read https://opencode.ai/docs/ and note 2 actionable features.
- Browser: read https://docs.langchain.com/oss/python/deepagents/harness and note 2 implementation takeaways.

Jan docs-linking hints for E2
- Prompt step: include a LangChain prompt-template doc link from `docs-langchain` MCP search.
- Structured output step: include a LangChain structured-output doc link from `docs-langchain` MCP search.
- Deep-agent context step: include https://docs.langchain.com/oss/python/deepagents/harness.

## E3 - Context pipeline with retrieval

Subtask 1 - Baseline (no retrieval)
- Terminal: run baseline prompt once and save output in notes.
- Tip: keep question fixed for fair A/B comparison.

Subtask 2 - Retrieval pipeline
- IDE: wire loader -> splitter -> retriever chain.
- Notebook: useful for inspecting chunks and retrieved docs.

Subtask 3 - A/B comparison
- IDE: document one failure in baseline fixed by retrieval.
- Terminal: rerun both paths to confirm consistency.

## E4 - Tool-calling mini-agent

Subtask 1 - Define tools
- IDE: implement two small tool functions with clear docstrings.
- Tip: one tool = one responsibility.

Subtask 2 - Agent wiring
- IDE: bind tools to model; keep one test question requiring both tools.
- Terminal: run once and capture tool trace/log.

Subtask 3 - Output check
- IDE: add one plausibility check (range/sign/unit check).
- Terminal: rerun after adding check.

## E5 - Tiny MCP tool

Subtask 1 - Build tool endpoint/function
- IDE: implement tiny tool in one file first.
- Tip: validate one required argument early.

Subtask 2 - Connect to workflow
- IDE: add minimal client call and error handling.
- Terminal: run one success path + one error path.

Subtask 3 - Sanity check
- IDE: compare tool output to hand calculation.
- Terminal: log both values side by side.

## E6 - Memory behavior

Subtask 1 - Memory policy
- IDE: write store/ignore/prune rules in markdown first.
- Tip: keep policy to 5-8 bullet points max.

Subtask 2 - Session memory test
- Notebook: useful for showing turn-by-turn behavior.
- Tip: script 3-5 turns before running.

Subtask 3 - Retrieval memory test
- IDE: add one retrievable fact and query it later.
- Terminal: run and capture proof + risk note.

## E7 - Ideation napkin

Subtask 1 - Domain scoring
- IDE: make a small score table with 3-5 criteria.
- Tip: keep weights simple and explicit.

Subtask 2 - Idea napkin draft
- IDE: fill problem, mechanism, data, identification, risk.
- Tip: one sentence per field first.

Subtask 3 - Risk note
- IDE: add one IP/HARKING caution and mitigation.
- Terminal: optional, if using CLI notes workflow.

## E8 - Data collection memo

Subtask 1 - Choose mode A/B/C
- IDE: write one paragraph: why this mode, why not others.
- Tip: include one key validity threat.

Subtask 2 - Protocol sketch
- IDE: define instrument/data flow and checkpoints.
- Notebook: useful for pilot simulation notes.

Subtask 3 - Verification plan
- IDE: add concrete pass/fail condition.
- Tip: specify what would falsify your setup.

## E9 - Evidence + claim ledger

Subtask 1 - Evidence paragraph
- IDE: draft paragraph with explicit claim markers.
- Tip: keep claims count low (2-3 strong claims).

Subtask 2 - Claim ledger
- IDE: add table columns claim/source/snippet/confidence/gap.
- Terminal: optional if parsing citations from files.

Subtask 3 - Gap disclosure
- IDE: list one unresolved gap + next query.
- Tip: do not hide missing evidence.

## E10 - Reproducible analysis loop

Subtask 1 - Prompt -> code
- IDE: write small function first, not full pipeline.
- Tip: commit to one testable output.

Subtask 2 - Run -> test -> fix
- Terminal: run script/tests; capture failing then passing state.
- IDE: patch smallest possible change.

Subtask 3 - Keep/reject decision
- IDE: write decision with one assumption + one limitation.
- Tip: explicit reject criteria improve rigor.

## E11 - Issue -> agent -> PR drill

Subtask 1 - Scoped issue
- IDE: draft issue with scope, acceptance criteria, out-of-scope.
- Tip: one issue, one outcome.

Subtask 2 - Agent handoff
- IDE: write handoff prompt with constraints and verification steps.
- Terminal: optional `gh issue`/`gh pr` workflow.

Subtask 3 - PR review verdict
- IDE: fill checklist and accept/revise decision.
- Tip: cite one concrete diff/test signal.

## E12 - Writing + syndication

Subtask 1 - Brief draft
- IDE: convert rough notes into 300-500 words.
- Tip: thesis first, caveat second.

Subtask 2 - Channel adaptation
- IDE: create 3 channel variants (web/slides/post).
- Tip: change style, not core claim.

Subtask 3 - Disclosure
- IDE: add AI-assistance disclosure sentence.
- Tip: keep it factual and specific.
