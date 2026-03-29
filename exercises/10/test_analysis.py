from pathlib import Path

from analysis import compute_mean, load_values


def test_load_values_reads_three_rows() -> None:
    data_path = Path(__file__).resolve().parent / "data" / "sample.csv"
    values = load_values(data_path)
    assert len(values) == 3


def test_compute_mean_returns_expected_value() -> None:
    result = compute_mean([10.0, 12.0, 14.0])
    assert result == 12.0
