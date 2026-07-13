#!/usr/bin/env python3
"""Independent replay of every retained P118 affine-insertion row."""

from __future__ import annotations

import argparse
import importlib.util
from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_INPUT = ROOT / "problems/864/compute/p118/affine_insertion_search.json"
DEFAULT_OUTPUT = ROOT / "problems/864/compute/p118/affine_insertion_verification.json"


def load_verifier():
    path = ROOT / "problems/864/compute/p118/verify_p113_falsifier.py"
    spec = importlib.util.spec_from_file_location("p118_independent_verifier", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.input = args.input.resolve()
    args.output = args.output.resolve()
    payload = json.loads(args.input.read_text(encoding="ascii"))
    verifier = load_verifier()
    unique = {}
    for row in payload["best"]:
        unique[str(row["sha256"])] = row
    for task in payload["tasks"]:
        for row in task["best"]:
            unique[str(row["sha256"])] = row
    for row in unique.values():
        verifier.verify_row(row)
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "matching_algorithm": "independent Dinic max flow",
        "input": str(args.input.relative_to(ROOT)),
        "input_sha256": sha256(args.input.read_bytes()).hexdigest(),
        "retained_rows_checked": len(unique),
        "falsifiers_checked": sum(int(row["hall_deficiency"] > 0) for row in unique.values()),
        "status": "PASS",
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
