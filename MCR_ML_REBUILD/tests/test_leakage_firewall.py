"""Unit tests for the Target Leakage Firewall and Quarantine Governance."""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import pytest

from src.data.governance import (
    DEFAULT_QUARANTINED_TAGS,
    enforce_leakage_firewall,
    filter_quarantined_dataframe,
    is_quarantined_column,
)


def test_default_quarantined_tags_count():
    assert len(DEFAULT_QUARANTINED_TAGS) == 10
    assert "H4FI029A" in DEFAULT_QUARANTINED_TAGS
    assert "total_shaft_power_mw" in DEFAULT_QUARANTINED_TAGS


def test_case_insensitive_and_derived_variant_detection():
    assert is_quarantined_column("h4fi029a") is True
    assert is_quarantined_column("H4FI030A_norm") is True
    assert is_quarantined_column("H4FI031A_rolling6") is True
    assert is_quarantined_column("H1PIC033_norm") is False


def test_enforce_leakage_firewall_raises_on_violation():
    with pytest.raises(ValueError, match="Target leakage firewall violation"):
        enforce_leakage_firewall(["H1FI012", "H0TI001", "H5FI006A"])


def test_filter_quarantined_dataframe_strips_all_targets():
    df = pd.DataFrame({
        "H1FI012": [700.0, 710.0],
        "H4FI029A": [150.0, 155.0],
        "total_shaft_power_mw": [105.0, 106.0],
    })
    clean = filter_quarantined_dataframe(df)
    assert list(clean.columns) == ["H1FI012"]


def test_processed_features_contain_zero_quarantined_tags():
    root = Path(__file__).resolve().parents[1]
    df = pd.read_parquet(root / "data" / "processed" / "features_unleakaged.parquet")
    enforce_leakage_firewall(list(df.columns))

