#!/usr/bin/env python3

# Imports
from dataclasses import dataclass


# Functions
@dataclass
class ToolOutput:
    ok: bool
    value: float | None
    message: str


def simple_npv(cash_flows: list[float], discount_rate: float) -> ToolOutput:
    if discount_rate < 0:
        return ToolOutput(ok=False, value=None, message="discount_rate must be non-negative")

    total = 0.0
    for period, flow in enumerate(cash_flows, start=1):
        total += flow / ((1 + discount_rate) ** period)
    return ToolOutput(ok=True, value=total, message="computed")


def run_demo() -> tuple[ToolOutput, ToolOutput]:
    success = simple_npv([100, 120, 140], 0.10)
    invalid = simple_npv([100, 120, 140], -0.10)
    return success, invalid


# Code
def main() -> int:
    success, invalid = run_demo()
    print(f"success_ok={success.ok} value={success.value} message={success.message}")
    print(f"invalid_ok={invalid.ok} value={invalid.value} message={invalid.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
