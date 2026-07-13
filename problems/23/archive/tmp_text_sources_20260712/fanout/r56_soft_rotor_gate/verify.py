#!/usr/bin/env python3
"""Independent deterministic replay for the R56 soft-rotor finite gate."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(32, os.cpu_count() or 1))
    parser.add_argument("--input", type=Path, default=HERE / "results.json")
    args = parser.parse_args()
    if not 1 <= args.workers <= 32:
        parser.error("workers must be in 1..32")
    input_path = args.input.resolve()
    if input_path.parent != HERE.resolve():
        parser.error("input must stay inside tmp/fanout/r56_soft_rotor_gate")
    expected = json.loads(input_path.read_text(encoding="ascii"))
    actual = gate.build_payload(args.workers)
    expected_bytes = gate.canonical_bytes(expected)
    actual_bytes = gate.canonical_bytes(actual)
    if expected_bytes != actual_bytes:
        print(json.dumps({
            "verdict": "FAIL_REPLAY_MISMATCH",
            "expectedSha256": gate.hashlib.sha256(expected_bytes).hexdigest().upper(),
            "actualSha256": gate.hashlib.sha256(actual_bytes).hexdigest().upper(),
        }, sort_keys=True, separators=(",", ":")))
        return 1
    result = {
        "schema": "R56_GLOBAL_SOFTCAP_SATURATED_ROTOR_REPLAY_V1",
        "verdict": "PASS_EXACT_REPLAY",
        "inputSha256": gate.sha256(input_path),
        "exactCounts": actual["exactCounts"],
    }
    output = HERE / "verification.json"
    output.write_bytes(gate.canonical_bytes(result))
    manifest_files = [
        "gate.py",
        "verify.py",
        input_path.name,
        "verification.json",
        "REPORT.md",
        "REPLAY.md",
    ]
    manifest = "".join(
        f"{gate.sha256(HERE / name)}  {name}\n" for name in manifest_files
    )
    (HERE / "MANIFEST.sha256").write_text(
        manifest, encoding="ascii", newline="\n"
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
