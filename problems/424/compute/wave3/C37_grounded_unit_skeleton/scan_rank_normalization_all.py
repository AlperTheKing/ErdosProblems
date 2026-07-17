#!/usr/bin/env python3
"""Run the combined local death-rank normalization at every hard cutoff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from test_rank_normalization import hard_cutoffs, test_cutoff


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = [test_cutoff(cutoff) for cutoff in hard_cutoffs(args.stop)]
    failures = [result for result in results if not result["passes"]]
    payload = {
        "schema_version": 1,
        "stop": args.stop,
        "tested": len(results),
        "failure_count": len(failures),
        "first_failure": failures[0] if failures else None,
        "failures": failures,
        "results": results,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "stop": args.stop,
                "tested": len(results),
                "failure_count": len(failures),
                "first_failure_limit": failures[0]["limit"] if failures else None,
            }
        )
    )


if __name__ == "__main__":
    main()
