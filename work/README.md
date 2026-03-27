# Student work files

Write exercise work in markdown files in this folder.

Recommended pattern:

1. Initialize all exercise files once:

```bash
uv run python tools/init_exercises.py --student-name "Alex"
```

2. Open the relevant file (for example `E3.md`, now available for E1-E12).
3. Fill the answer sections iteratively with the tutor.
4. Submit directly from markdown:

```bash
uv run python tools/submit_exercise.py --from-markdown work/E3.md
```

Backup manual mode:

```bash
uv run python tools/print_exercise_packet.py --exercise-id E3
```

This prints the exercise packet and a Google Form link for manual submission.

Progress view:

```bash
uv run python tools/progress_dashboard.py
```
