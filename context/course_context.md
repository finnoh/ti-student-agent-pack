# Course Context Pack (E1-E8)

## Default stack

- LangChain deep-agent is the default exercise pattern.
- OpenRouter is the default model backend.
- Root `.env` stores `OPENROUTER_API_KEY`.
- Prefer free models first; students may override.

## Standard block loop

- Observe one decision.
- Build one micro artifact.
- Fail one assumption.
- Verify one method.
- Reflect one reusable pattern.

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

### E1 - Prompt anatomy lab

- Goal: set up OpenRouter + deep-agent defaults and verify one run.
- Deliverable: setup note with model choice and successful test output.
- Failure risk: key/config mismatch in `.env`.

### E2 - Prompt rewrite challenge

- Goal: define deep-agent task prompt + tool constraints.
- Deliverable: system prompt plus one tool-routing decision table.
- Failure risk: prompt is broad and causes unstable tool use.

### E3 - IDE coding sprint

- Goal: implement one deep-agent module with LangChain docs support.
- Deliverable: patch summary and verification trace.
- Failure risk: API mismatch from skipping docs lookup.

### E4 - Draft and verify paragraph

- Goal: add structured output for one deep-agent step.
- Deliverable: schema + validated sample output.
- Failure risk: output schema too weak for verification.

### E5 - Design an agent workflow

- Goal: design reliability-aware deep-agent workflow.
- Deliverable: architecture sketch and fallback path.
- Failure risk: missing human escalation.

### E6 - Build a mini pipeline

- Goal: add memory/retrieval to deep-agent pipeline.
- Deliverable: protocol note with sample artifacts.
- Failure risk: overclaiming from retrieved snippets.

### E7 - Evaluate two outputs

- Goal: compare two free OpenRouter models on same task.
- Deliverable: scored table plus short adoption memo.
- Failure risk: uncontrolled prompt/settings across model runs.

### E8 - Resilience protocol plan

- Goal: create a deep-agent resilience protocol.
- Deliverable: one-page protocol with trigger rules.
- Failure risk: generic rules with no trigger conditions.
