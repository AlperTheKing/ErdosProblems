#!/usr/bin/env python3
"""Verify every replay input/output and report hash recorded in manifest.json."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest().upper()


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["audit_status"] == "PASS"
    assert manifest["unexpected_exit_ids"] == []
    assert len(manifest["runs"]) == 9
    for run in manifest["runs"]:
        assert run["expected_exit"]
        assert run["exit_code"] in run["expected_exit_codes"]
        assert sha(ROOT / run["script"]) == run["script_sha256"]
        assert sha(HERE / run["stdout"]) == run["stdout_sha256"]
        assert sha(HERE / run["stderr"]) == run["stderr_sha256"]
    for relative, expected in manifest["audit_artifacts"].items():
        assert sha(HERE / relative) == expected, relative
    print("PASS_MANIFEST_HASH_AND_STATUS_AUDIT runs=9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
