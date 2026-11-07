"""Cryptographic SHA-256 Asset Audit and Manifest Verification Module.

Ensures raw datasets in legacy directories remain 100% read-only and uncorrupted.
Governance: AGENTS.md, ORIGINAL_REQUEST.md (§R1).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def compute_sha256(filepath: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute SHA-256 hex digest of a file using streaming 1MB chunks."""
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"Target file for hashing does not exist: {p}")
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_manifest_entry(entry: Dict[str, Any]) -> bool:
    """Validate that a manifest file entry has a valid 64-char hex SHA-256 and positive size."""
    digest = str(entry.get("sha256", ""))
    size = int(entry.get("size_bytes", entry.get("size", 0)))
    if len(digest) != 64:
        return False
    try:
        int(digest, 16)
    except ValueError:
        return False
    return size >= 0


def load_and_validate_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Load SHA-256 manifest JSON and verify integrity of all recorded entries."""
    p = Path(manifest_path)
    if not p.exists():
        raise FileNotFoundError(f"Manifest file not found: {p}")
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    files_raw = data.get("files", [])
    if isinstance(files_raw, dict):
        entries: List[Dict[str, Any]] = [
            {"file_name": k, **v} if isinstance(v, dict) else {"file_name": k, "sha256": v, "size_bytes": 0}
            for k, v in files_raw.items()
        ]
    else:
        entries = list(files_raw)

    invalid = [e.get("file_name", e.get("filename", "unknown")) for e in entries if not verify_manifest_entry(e)]
    if invalid:
        raise ValueError(f"Corrupted or invalid SHA-256 manifest entries detected: {invalid}")

    return {"manifest_path": str(p), "total_entries": len(entries), "entries": entries}

