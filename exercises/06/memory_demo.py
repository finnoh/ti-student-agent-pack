#!/usr/bin/env python3

# Imports


# Functions
def scripted_dialogue() -> list[str]:
    return [
        "User: My preferred chart style is line charts.",
        "Agent: Noted. I will default to line charts.",
        "User: Please remind me what style I prefer.",
        "Agent: You prefer line charts.",
    ]


def retrieval_fact_demo() -> tuple[str, str]:
    stored_note = "Project deadline is 2026-05-15."
    retrieved = "Retrieved fact: Project deadline is 2026-05-15."
    return stored_note, retrieved


# Code
def main() -> int:
    print("session_trace=")
    for line in scripted_dialogue():
        print(line)

    stored, retrieved = retrieval_fact_demo()
    print("\nstored_note=")
    print(stored)
    print("retrieval_output=")
    print(retrieved)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
