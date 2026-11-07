"""Unit tests for cryptographic SHA-256 data integrity and schema validation."""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import pytest

from src.data.audit import compute_sha256, load_and_validate_manifest, verify_manifest_entry
from src.data.ingestion import is_shutdown_regime, map_hour_to_shift, validate_raw_gc_sum


def test_manifest_file_exists_and_valid():
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "data" / "manifests" / "sha256_manifest.json"
    res = load_and_validate_manifest(manifest_path)
    assert res["total_entries"] >= 6


def test_verify_manifest_entry_rejects_short_hash():
    assert verify_manifest_entry({"file_name": "a.xlsx", "sha256": "abc123", "size_bytes": 10}) is False


def test_compute_sha256_empty_bytes(tmp_path: Path):
    f = tmp_path / "empty.bin"
    f.write_bytes(b"")
    assert compute_sha256(f) == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_shift_mapping_and_shutdown_guards():
    assert map_hour_to_shift(7.5) == 1
    assert map_hour_to_shift(14.0) == 2
    assert map_hour_to_shift(22.0) == 3
    assert is_shutdown_regime(45.0) is True
    assert is_shutdown_regime(520.0) is False
    assert validate_raw_gc_sum(100.1) is True
    assert validate_raw_gc_sum(80.0) is False


def test_processed_parquet_schemas_exist():
    root = Path(__file__).resolve().parents[1]
    feat_pq = root / "data" / "processed" / "features_unleakaged.parquet"
    targ_pq = root / "data" / "processed" / "target_energy.parquet"
    assert feat_pq.exists()
    assert targ_pq.exists()
    df_x = pd.read_parquet(feat_pq)
    df_y = pd.read_parquet(targ_pq)
    assert len(df_x) == len(df_y)
    assert "H4TI004B" in df_x.columns
    assert "total_shaft_power_mw" in df_y.columns

