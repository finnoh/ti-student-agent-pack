#!/usr/bin/env python3

# Imports
from dataclasses import dataclass


# Functions
@dataclass
class ToolResult:
    name: str
    value: str


def calc_average(values: list[float]) -> ToolResult:
    average = sum(values) / len(values)
    return ToolResult(name="calc_average", value=f"{average:.2f}")


def lookup_label(code: str) -> ToolResult:
    labels = {"A": "North region", "B": "South region", "C": "West region"}
    return ToolResult(name="lookup_label", value=labels.get(code, "Unknown region"))


def run_example_query() -> list[ToolResult]:
    first = lookup_label("C")
    second = calc_average([12.0, 15.0, 18.0])
    return [first, second]


# Code
def main() -> int:
    results = run_example_query()
    for item in results:
        print(f"tool={item.name} value={item.value}")

    print("final_note=Check whether reported average and region label are plausible.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
