# E1 Hello-World Scaffold

Use this folder for Exercise E1.

## Goal

Run one tiny LangChain deep-agent style task:

- Read `data/tiny.csv`
- Compute one summary statistic (`mean_income`)
- Print result clearly

## Suggested run

```bash
uv run python exercises/e1/hello_world.py
```

## Verification idea

Cross-check the printed mean with a manual calculation from the CSV values.

## Backup mode

If submission flow is blocked:

```bash
uv run python tools/print_exercise_packet.py --exercise-id E1
```
