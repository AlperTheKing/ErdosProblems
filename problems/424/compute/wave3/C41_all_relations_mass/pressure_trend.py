#!/usr/bin/env python3
"""Numerical canonical pressure trend for all-side relation cutoffs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from all_relations_mass import PatternAutomaton, canonical_pressure


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--relations", type=Path, required=True)
    parser.add_argument("--minimum-length", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.relations.read_text(encoding="ascii"))
    maximum = source["max_relation_length"]
    rows = []
    for cutoff in range(args.minimum_length, maximum + 1):
        patterns = [
            pattern
            for pattern in source["minimal_sides"]
            if len(pattern) <= cutoff
        ]
        automaton = PatternAutomaton(patterns)
        transitions, _, _ = automaton.safe_dfa()
        pressure = canonical_pressure(transitions)
        rows.append(
            {
                "cutoff": cutoff,
                "minimal_sides": len(patterns),
                "safe_states": len(transitions),
                "theta_3": pressure["theta_3"],
                "theta_5": pressure["theta_5"],
                "lambda": pressure["lambda"],
                "canonical_base_per_k": pressure["canonical_base_per_k"],
                "ratio_to_Q": pressure["ratio_to_Q"],
                "optimizer_success": pressure["success"],
            }
        )

    for earlier, later in zip(rows, rows[1:]):
        if later["ratio_to_Q"] > earlier["ratio_to_Q"] + 1e-8:
            raise AssertionError("numerical pressure trend is not monotone")
    stored = source["numeric_pressure"]["ratio_to_Q"]
    if abs(rows[-1]["ratio_to_Q"] - stored) > 1e-9:
        raise AssertionError("L=14 pressure does not replay")

    payload = {
        "schema_version": 1,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "relations_sha256": hashlib.sha256(args.relations.read_bytes()).hexdigest(),
        "status": "numerical diagnostic; no certified infinite-cutoff bound",
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.output.write_text(rendered + "\n", encoding="ascii")
    print(rendered)


if __name__ == "__main__":
    main()
