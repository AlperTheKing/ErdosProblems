#!/usr/bin/env python3
"""Sparse exact single-source falsifier search for C108-MOVE-PACK."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import sympy


def load_classifier(path: Path):
    spec = importlib.util.spec_from_file_location("c113_c105_classifier", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_row(module, q: int) -> dict[str, object] | None:
    h = module.COEFFICIENT * q - 1
    if module.state(h) != module.HARD:
        return None
    d, structural, pairs = module.pair_audit(h)
    if d != 8:
        raise RuntimeError((q, h, d))
    roots = sorted({
        int(endpoint["root"])
        for pair in pairs
        for endpoint in pair["endpoints"]
        if endpoint["state"] != "generated"
        and endpoint["root_state"] != "structural_splitless"
    })
    bins: dict[int, list[int]] = {}
    for root in roots:
        bins.setdefault((root - 1).bit_length() - 1, []).append(root)
    minimum = None
    failure = None
    weight = 3
    for j, bin_roots in sorted(bins.items()):
        bin_roots.sort()
        for index, root in enumerate(bin_roots[1:], start=1):
            lhs = weight * index
            rhs = root - (1 << j)
            candidate = {
                "j": j,
                "root": root,
                "index": index + 1,
                "lhs": lhs,
                "rhs": rhs,
                "slack": rhs - lhs,
                "bin_source_roots": bin_roots,
            }
            if minimum is None or candidate["slack"] < minimum["slack"]:
                minimum = candidate
            if lhs > rhs and failure is None:
                failure = candidate
    return {
        "q": q,
        "h": h,
        "d": d,
        "s": structural,
        "reducible_roots": roots,
        "minimum_single_source_slack": minimum,
        "failure": failure,
    }


def run(module, prime_start: int, prime_limit: int) -> dict[str, object]:
    tested = 0
    eligible = 0
    hard_rows = []
    closest = None
    first_failure = None
    for raw_q in sympy.primerange(max(5, prime_start), prime_limit + 1):
        q = int(raw_q)
        tested += 1
        if q % 3 != 2 or module.COEFFICIENT % q == 0:
            continue
        eligible += 1
        row = source_row(module, q)
        if row is None:
            continue
        hard_rows.append(row)
        minimum = row["minimum_single_source_slack"]
        if minimum is not None and (
            closest is None or minimum["slack"] < closest["minimum_single_source_slack"]["slack"]
        ):
            closest = row
        if row["failure"] is not None:
            first_failure = row
            break
    return {
        "schema": "C113-single-source-c105-family-v1",
        "arithmetic": "exact integers only",
        "prime_start": prime_start,
        "prime_limit": prime_limit,
        "primes_tested": tested,
        "eligible_primes": eligible,
        "hard_count": len(hard_rows),
        "first_C108_MOVE_PACK_failure": first_failure,
        "closest_row": closest,
        "hard_rows": hard_rows,
        "cache": {
            "state_entries": module.state.cache_info().currsize,
            "factor_pair_entries": module.factor_pairs.cache_info().currsize,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime-start", type=int, default=5)
    parser.add_argument("--prime-limit", type=int, required=True)
    parser.add_argument("--classifier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 5 <= args.prime_start <= args.prime_limit <= 100_000_000:
        raise RuntimeError((args.prime_start, args.prime_limit))
    module = load_classifier(args.classifier)
    payload = run(module, args.prime_start, args.prime_limit)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("ascii")
    args.output.write_bytes(encoded)
    print(hashlib.sha256(encoded).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
