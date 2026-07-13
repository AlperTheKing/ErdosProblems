#!/usr/bin/env python3
"""Run the endpoint census and numerical IG2=>C20 implication gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ig2_implication_gate import audit_exhaustive, audit_implication


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exhaustive-max-n", type=int, default=20)
    parser.add_argument("--implication-max-n", type=int, default=10000)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p36/ig2_core_gate.json"),
    )
    args = parser.parse_args()
    result = {
        "arithmetic": "integer/rational",
        "exhaustive": audit_exhaustive(args.exhaustive_max_n),
        "implication_relaxation": audit_implication(args.implication_max_n),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
