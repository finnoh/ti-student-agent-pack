# TI Student Agent Pack (v1)

Portable, self-contained workspace for course exercises.

## What students do

1. Unzip this folder.
2. Open this folder in their coding agent.
3. Use the built-in coach in `AGENTS.md` while working on exercises.
4. Write each exercise in markdown files under `exercises/`.
5. Submit with `python tools/submit_exercise.py --from-markdown exercises/<FILE>.md`.

The coach is configured as a personalized tutor: it presents each exercise,
asks one concrete question at a time, and updates the markdown submission file
iteratively before asking for final submit confirmation.

It also shows an ASCII progress dashboard and maintains `INSIGHTS.md` with what
the student has learned so far.

On first use, the tutor checks `BOOTSTRAP.md`. If it is empty, it asks a short
3-question onboarding and saves the answers for personalized coaching.

After onboarding, the tutor should run the exercise initializer so all E1-E8
markdown files are pre-created and prefilled.

Submission identity uses `student_name` (from `BOOTSTRAP.md` by default).

## What instructors do

1. Copy `config/form_config.example.json` to `config/form_config.json`.
2. Fill in the Google Form URL and field IDs.
3. Zip and share this folder.

Fast path using workshop bootstrap output:

```bash
./scripts/google/bootstrap_workshop.sh --write-env-file website/.env.local
python scripts/course_pack/sync_student_pack_form_config.py --env-file website/.env.local
```

Field IDs are the numeric values used in prefill params like
`entry.1234567890=value`.

## Activation and removal

- Activate: open this folder as the project/workspace in the coding agent.
- Remove: close workspace and delete this folder.
- No global settings are required.

## Submission model

The submit helper validates required fields locally, writes a local record in
`submissions/`, and defaults to a prefilled Google Form browser submission.

Primary flow is now prefilled URL + student confirmation.

If Google Forms rejects direct HTTP submission, the helper automatically tries a
code fallback to Google Sheets append when `google_sheet_id` is configured and
`gws` is available.

It includes retry logic and writes a detailed receipt to
`submissions/receipts/` for every run.

If submission fails after retries, it prints a copy-paste fallback payload and
the manual prefilled link (Cmd + left click opens the link).

## Question mode (course Q&A)

You can build a lightweight local index of course material and ask questions.
By default, indexing is website-first and pulls from the published companion
site, so content stays up to date.

Default indexed sources (website mode):

- `https://finnoh.github.io/ws_genai_eb/docs/...` pages discovered from sitemap

Optional local fallback sources (local/hybrid mode):

- `student-agent-pack/context/course_context.md`
- `exercises/drafts.md`
- `exercises/rubrics.md`
- `slides/day1_foundations.qmd`
- `slides/day2_advanced.qmd`

Index data is local-only in `student-agent-pack/.index/` and is not meant to be
committed.

## Commands

```bash
python tools/submit_exercise.py
```

```bash
python tools/submit_exercise.py --from-markdown exercises/E3.md
```

```bash
python tools/submit_exercise.py --from-markdown exercises/E3.md --student-name "Alex"
```

```bash
python tools/submit_exercise.py --from-markdown exercises/E3.md --no-submit
```

```bash
python tools/submit_exercise.py --from-markdown exercises/E3.md --retry-count 3 --retry-backoff 2
```

```bash
python tools/submit_exercise.py --from-markdown exercises/E3.md --submit-mode code
```

```bash
python tools/submit_exercise.py --help
```

```bash
python tools/progress_dashboard.py
```

```bash
python tools/startup_check.py
```

```bash
python tools/init_exercises.py --student-name "Alex"
```

```bash
python tools/index_course_materials.py
```

```bash
python tools/index_course_materials.py --source-mode hybrid
```

```bash
python tools/ask_course.py --q "What is the E5 deliverable?"
```

```bash
python tools/ask_course.py --q "How do we evaluate outputs in this workshop?" --show-snippets
```

## Minimal config to start quickly

For code-based submission, configure:

- `google_form_url`
- `google_sheet_id` (recommended for robust code fallback)
- Field IDs for all required fields:
  - `exercise_id`
  - `student_name`
  - `answer`

If any required field ID is missing, the helper stops and reports which IDs are
missing.

If `google_form_url` is empty and the command runs in an interactive terminal,
the submit helper now prompts for the URL and can save it automatically.

## Notes

- If a field ID is missing in `config/form_config.json`, that field is not
  prefilled and the student can fill it manually in the form.
- The script supports `GOOGLE_FORM_URL` and field ID env vars as overrides.
- Markdown front matter keys supported by `--from-markdown`:
  - `exercise_id`, `student_name`
  - The markdown body is used as `answer`.

## Startup state

- Use `STARTUP.md` to track environment readiness.
- Once startup checks pass, add `## STARTUP COMPLETE` to `STARTUP.md`.
- The tutor will skip startup checks after that marker is present.

## Environment setup

- Default: no virtual environment needed (stdlib-only scripts).
- Optional with `uv`:

```bash
uv run python tools/submit_exercise.py --from-markdown exercises/E3.md
```
