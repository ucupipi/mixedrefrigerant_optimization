"""Unit tests for deterministic reproducibility across data generation and model training."""
from __future__ import annotations

from pathlib import Path
import numpy as np

from src.config import load_config
from src.data.ingestion import build_clean_shift_datasets
from src.features.engineering import chronological_train_test_split
from src.models.pipeline import run_training_pipeline


def test_deterministic_shift_dataset_generation():
    df1, y1 = build_clean_shift_datasets(n_shifts=60, random_state=123)
    df2, y2 = build_clean_shift_datasets(n_shifts=60, random_state=123)
    np.testing.assert_allclose(df1["H1FI012"].to_numpy(), df2["H1FI012"].to_numpy())
    np.testing.assert_allclose(y1["total_shaft_power_mw"].to_numpy(), y2["total_shaft_power_mw"].to_numpy())


def test_chronological_split_preserves_order():
    df, _ = build_clean_shift_datasets(n_shifts=100, random_state=42)
    train_df, test_df = chronological_train_test_split(df, test_ratio=0.20, purge_buffer=2, timestamp_col="shift_id")
    assert train_df["shift_id"].max() + 2 < test_df["shift_id"].min()


def test_end_to_end_pipeline_qualification():
    cfg = load_config()
    root = cfg.project_root
    report = run_training_pipeline(
        processed_dir=root / "data" / "processed",
        models_dir=root / "models",
        reports_dir=root / "reports",
        random_state=42,
    )
    assert report["qualified"] is True
    assert report["surrogate_test_metrics"]["mae_mw"] < 1.0
    assert report["surrogate_test_metrics"]["nmae_pct"] < 1.0
    assert report["surrogate_test_metrics"]["r2"] >= 0.60

