"""Pipeline normalization tests adapted to current ETL rules."""

import pandas as pd

from app.ml.pipeline import normalize_columns


def test_normalize_columns_renames_num_to_target():
    """normalize_columns renames num -> target and removes old name."""
    df = pd.DataFrame({"num": [0, 1], "age": [25, 36]})
    result = normalize_columns(df)
    assert "target" in result.columns
    assert "num" not in result.columns


def test_normalize_columns_drops_metadata_and_binarizes_target():
    """normalize_columns drops id/dataset and converts multiclass target to binary."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "dataset": ["lol", "lol", "lol"],
            "target": [0, 2, 4],
            "kills": [1, 5, 3],
        }
    )
    result = normalize_columns(df)
    assert "id" not in result.columns
    assert "dataset" not in result.columns
    assert sorted(result["target"].unique().tolist()) == [0, 1]
