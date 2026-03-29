# Student exercise files

Write exercise drafts in markdown files in this folder.

Recommended pattern:

1. Initialize all exercise files once:

```bash
uv run python tools/init_exercises.py --student-name "Alex"
```

2. Open the relevant file (for example `E03.md`, now available for E01-E12).
   - Optional scaffold folders: `exercises/01/` and `exercises/02/`.
3. Fill the answer sections iteratively with the tutor.
4. Submit directly from markdown:

```bash
uv run python tools/submit_exercise.py --from-markdown exercises/03/E03.md
```

Backup manual mode:

```bash
uv run python tools/print_exercise_packet.py --exercise-id E03
```

This prints the exercise packet and a Google Form link for manual submission.

Progress view:

```bash
uv run python tools/progress_dashboard.py
```
