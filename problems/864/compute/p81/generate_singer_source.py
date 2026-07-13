#!/usr/bin/env python3
"""Generate a minimal stored Singer source for the P81 cut scanner."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ALGEBRAIC_SCAN = ROOT / "problems/864/compute/p12/algebraic_scan.py"


def load_algebraic_scan():
    spec = importlib.util.spec_from_file_location("p12_algebraic_scan_p81", ALGEBRAIC_SCAN)
    if spec is None or spec.loader is None:
        raise RuntimeError(ALGEBRAIC_SCAN)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    module = load_algebraic_scan()
    modulus, residues, metadata = module.singer(args.q)
    record = {
        "family": "singer",
        "parameter": args.q,
        "modulus": modulus,
        "residue_size": len(residues),
        "residues": residues,
        "metadata": metadata,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({"q": args.q, "modulus": modulus, "size": len(residues)}))


if __name__ == "__main__":
    main()
