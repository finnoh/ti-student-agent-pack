# Student work files

Write exercise work in markdown files in this folder.

Recommended pattern:

1. Initialize all exercise files once:

```bash
python tools/init_exercises.py --student-name "Alex"
```

2. Open the relevant file (for example `E3.md`).
3. Fill the answer sections iteratively with the tutor.
4. Submit directly from markdown:

```bash
python tools/submit_exercise.py --from-markdown work/E3.md
```
