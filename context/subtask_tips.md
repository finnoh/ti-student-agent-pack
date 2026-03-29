# Subtask Tip Bank (E01-E12)

Use these hints when a student is stuck. Keep hints short and actionable.

Legend:
- Terminal = shell commands
- IDE = VS Code/Cursor file edits and run buttons
- Notebook = Jupyter cell-by-cell workflow

## E01 - Setup Jan + OpenRouter + hello world

Subtask 1 - Install + startup checks
- Terminal: `uv run python tools/startup_check.py`
- Tip: If `uv` fails, use `python tools/startup_check.py`.

Subtask 2 - OpenRouter key + defaults
- IDE: open `.env` and confirm `OPENROUTER_API_KEY` and `OPENAI_BASE_URL`.
- Terminal: rerun startup check after edits.

Subtask 3 - Hello world run
- Terminal: `uv run python exercises/01/hello_world.py`
- Notebook: better if student wants to inspect rows step by step.
- Tip: minimum completion is startup check + one Jan response; hello-world run is tier-2 if setup succeeds.

## E02 - Prompt anatomy in LangChain code

Subtask 1 - First prompt run
- IDE: create `exercises/02/prompt_lab.py` or notebook cell with `ChatPromptTemplate`.
- Tip: start simple and print the model output.

Subtask 2 - Country extraction task
- IDE: use the noisy paragraph and ask for a Python list only.
- Tip: include typo-fix rule and fictional-place filter in the prompt.

Subtask 3 - Structured output
- IDE: define a simple Pydantic model with `countries: list[str]`.
- Terminal: run script and verify output parses cleanly.

Subtask 4 - Model and docs orientation
- Browser: scan https://openrouter.ai/rankings and pick one model for E02.
- Browser: read https://opencode.ai/docs/ and note 2 actionable features.
- Browser: read https://docs.langchain.com/oss/python/deepagents/harness and note 2 implementation takeaways.
- Tip: one practical takeaway is sufficient for minimum completion.

Subtask 5 - Optional blackjack multi-agent extension
- IDE: create small role prompts for `Dealer`, `Gambler`, and `Referee`.
- Tip: print the blackjack rules in plain text before simulation.
- Rule reminder: dealer hits to 17+, bust > 21, blackjack is two-card 21, equal totals push.

Jan docs-linking hints for E02
- Prompt step: include a LangChain prompt-template doc link from `docs-langchain` MCP search.
- Structured output step: include a LangChain structured-output doc link from `docs-langchain` MCP search.
- Deep-agent context step: include https://docs.langchain.com/oss/python/deepagents/harness.

## E03 - Context pipeline with retrieval

Subtask 1 - Baseline (no retrieval)
- Terminal: `uv run python exercises/03/retrieval_ab.py`
- Tip: keep question fixed for fair A/B comparison.

Subtask 2 - Retrieval pipeline
- IDE: start from `exercises/03/retrieval_ab.py` and local docs in `exercises/03/local_docs/`.
- Tip: use 4-6 short documents to make retrieval behavior visible.
- Notebook: useful for inspecting chunks and retrieved docs.

Subtask 3 - A/B comparison
- IDE: document one failure in baseline fixed by retrieval.
- IDE: include one quoted retrieved chunk that supports the improved answer.
- IDE: add one boundary disclosure (privacy/copyright) for the corpus used.
- Terminal: rerun both paths to confirm consistency.

## E04 - Tool-calling mini-agent

Subtask 1 - Define tools
- IDE: implement in `exercises/04/tool_agent.py` with clear names/docstrings.
- Tip: integrate one existing research tool (arXiv/Zotero/etc.) plus one local helper tool.
- Tip: define a local no-auth fallback route before external tool setup.
- Tip: one tool = one responsibility.

Subtask 2 - Agent wiring
- IDE: keep one test question requiring both tools.
- Terminal: `uv run python exercises/04/tool_agent.py` and log notes in `exercises/04/tool_trace_notes.md`.

Subtask 3 - Output check
- IDE: add one plausibility check (range/sign/unit check).
- IDE: add one observed failure-mode note and what caused it.
- Terminal: rerun after adding check.

## E05 - Tiny MCP tool

Subtask 1 - Build tool endpoint/function
- IDE: implement tiny tool in `exercises/05/tiny_tool.py` first.
- Tip: define input/output contract (args, units, return fields) before coding.
- Tip: validate one required argument early.

Subtask 2 - Connect to workflow
- IDE: add minimal client call and error handling.
- Terminal: `uv run python exercises/05/tiny_tool.py` for success + error path.

Subtask 3 - Sanity check
- IDE: compare tool output to hand calculation.
- Terminal: log both values side by side.

## E06 - Memory behavior

Subtask 1 - Memory policy
- IDE: write store/ignore/prune rules in `exercises/06/memory_policy.md` first.
- Tip: keep policy to 5-8 bullet points max.
- IDE: align `AGENTS.md` with when to update `MEMORY.md`.

Subtask 2 - Session memory test
- Notebook: useful for turn-by-turn behavior; `.py` fallback is `exercises/06/memory_demo.py`.
- Tip: script 3-5 turns before running.

Subtask 3 - Retrieval memory test
- IDE: add one retrievable project fact in `exercises/06/PROJECT_BACKGROUND.md` and query it later.
- Terminal: run and capture proof + risk note.

## E07 - Ideation napkin

Subtask 1 - Domain scoring
- IDE: use `exercises/07/domain_scorecard.md`.
- Tip: add short researcher context first (methods, data, constraints).
- Tip: keep weights simple and explicit.

Subtask 2 - Idea napkin draft
- IDE: fill `exercises/07/idea_napkin.md`.
- Tip: draft at least two napkins before selecting a lead idea.
- Tip: one sentence per field first.

Subtask 3 - Risk note
- IDE: add one IP/HARKING caution and mitigation.
- Terminal: optional, if using CLI notes workflow.

## E08 - Data collection memo

Subtask 1 - Choose mode A/B/C
- IDE: use `exercises/08/design_memo.md`.
- Tip: include one key validity threat.
- Tip: choose exactly one mode (A or B or C), avoid hybrids in this exercise.

Subtask 2 - Protocol sketch
- IDE: define instrument/data flow and checkpoints.
- IDE: create one tiny prototype artifact (stimulus, survey skeleton, or synthetic respondent prompt).
- Notebook: useful for pilot simulation notes.

Subtask 3 - Verification plan
- IDE: add concrete pass/fail condition.
- Tip: specify what would falsify your setup.

## E09 - Evidence + claim ledger

Subtask 1 - Evidence paragraph
- IDE: draft in `exercises/09/evidence_paragraph.md`.
- Tip: keep claims count low (2-3 strong claims).
- IDE: add one short journal-policy note on AI-assisted literature use.
- Tip: minimum target is two papers and two claims.

Subtask 2 - Claim ledger
- IDE: fill `exercises/09/claim_ledger.md`.
- Terminal: optional if parsing citations from files.

Subtask 3 - Gap disclosure
- IDE: list one unresolved gap + next query.
- Tip: do not hide missing evidence.

## E10 - Reproducible analysis loop

Subtask 1 - Prompt -> code
- IDE: start in `exercises/10/analysis.py`.
- Tip: first run a direct-prompt baseline and record it.
- Tip: commit to one testable output.

Subtask 2 - Run -> test -> fix
- Terminal: `uv run python exercises/10/analysis.py` then `uv run python -m pytest exercises/10/test_analysis.py`.
- IDE: patch smallest possible change.

Subtask 3 - Keep/reject decision
- IDE: write decision with one assumption + one limitation.
- IDE: add AI provenance note (model/date) in code comment or notes.
- Tip: explicit reject criteria improve rigor.

## E11 - Issue -> agent -> PR drill

Subtask 1 - Scoped issue
- IDE: draft in `exercises/11/issue_template.md`.
- Tip: one issue, one outcome, with explicit acceptance criteria.

Subtask 2 - Agent handoff
- IDE: write in `exercises/11/handoff_prompt.md`.
- Terminal: optional `gh issue`/`gh pr` workflow.

Subtask 3 - PR review verdict
- IDE: fill `exercises/11/pr_review_checklist.md` and decide accept/revise.
- Tip: cite one concrete diff/test signal.
- Tip: include PR link if available; otherwise include simulated PR summary.
- Tip: simulated PR record is acceptable if repo permissions block real PR.

## E12 - Writing + syndication

Subtask 1 - Brief draft
- IDE: draft in `exercises/12/brief_template.md`.
- Tip: thesis first, caveat second.

Subtask 2 - Channel adaptation
- IDE: use `exercises/12/syndication_plan.md` for the 3 channels.
- Tip: change style, not core claim.

Subtask 3 - Web-ready draft
- IDE: add one markdown landing page draft for your paper/topic.
- Tip: keep it concise with thesis, contribution, and caveat.
- Tip: this subtask is optional extension work.

Subtask 4 - Disclosure
- IDE: finalize `exercises/12/disclosure.md`.
- Tip: keep it factual and specific.
