# Course Context Pack (E01-E12)

## Default stack

- Day 1 default: LangChain + OpenRouter, notebook or `.py` fallback.
- Day 2 default: VS Code + OpenCode; ChatGPT/Claude allowed where task fit is stronger.
- Root `.env` stores `OPENROUTER_API_KEY` and OpenRouter base URL.

## Standard block loop

- Produce one micro artifact.
- Make one design decision explicit.
- Record one likely failure mode.
- Show one verification method.

## Canonical evaluation dimensions

- Usefulness
- Correctness
- Reproducibility
- Risk awareness

## Submission schema

- `exercise_id`
- `student_name`
- `answer`

## Exercise map

### E01 - Setup Jan + OpenRouter + hello world
- Goal: get setup operational end-to-end.
- Deliverable: minimum setup evidence + Jan response; full run log/manual check/customization note if time permits.

### E02 - Prompt anatomy in LangChain code
- Goal: convert noisy extraction into structured output.
- Deliverable: runnable list output + short orientation note.
- Extension: optional multi-agent blackjack with explicit standard rules.

### E03 - Context pipeline with retrieval
- Goal: compare no-context vs retrieval on a fixed question.
- Deliverable: A/B note + one quoted supporting chunk + boundary disclosure.

### E04 - Tool-calling mini-agent
- Goal: integrate existing tools into a two-tool workflow with no-auth fallback.
- Deliverable: tool trace + verification check + failure-mode note + fallback plan.

### E05 - Build and connect tiny MCP tool
- Goal: build one tiny custom tool and wire it.
- Deliverable: input/output demo + sanity check + handled error path.

### E06 - Memory behavior: session + retrieval
- Goal: define memory policy and separate session vs retrieval memory.
- Deliverable: trace with remembered preference, retrieved project fact, and risk note.

### E07 - Ideation project + idea napkin
- Goal: score domains and create at least two candidate idea napkins.
- Deliverable: selected lead napkin + scorecard + IP/HARKING caution.

### E08 - AI data-collection design memo
- Goal: choose exactly one A/B/C mode and produce a validity-aware mini prototype.
- Deliverable: one-page memo + prototype artifact reference.

### E09 - Evidence paragraph + claim ledger
- Goal: create auditable claim-evidence synthesis.
- Deliverable: paragraph + claim ledger (minimum two claims) + policy note + unresolved gap.

### E10 - Reproducible analysis loop
- Goal: compare direct prompting vs test-first reproducible coding.
- Deliverable: code + checks + keep/reject decision + provenance note.

### E11 - Issue -> agent -> PR workflow drill
- Goal: practice scoped issue handoff and human review checkpoints.
- Deliverable: issue + handoff + PR record + review verdict.

### E12 - Writing + syndication sprint
- Goal: turn notes into brief and dissemination-ready outputs.
- Deliverable: brief + channel plan + disclosure (optional web-ready page).
