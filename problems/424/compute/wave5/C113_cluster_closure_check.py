#!/usr/bin/env python3
"""Recursive closure check for C113 two-root multiplier candidates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path


ROOTS = (262_172, 262_176)
PRIOR_ROOT = 262_158
PRIOR_PRODUCT = 1_921_614_475


def load_engine(path: Path):
    spec = importlib.util.spec_from_file_location("c113_fixed_root_engine", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run(engine, candidates: dict[str, object], maximum_rows: int) -> dict[str, object]:
    prior_factors = engine.factor_tuple(PRIOR_PRODUCT)
    prior = engine.classify_candidate(PRIOR_PRODUCT, prior_factors, PRIOR_ROOT)
    if not prior.hard or not prior.fixed_root_witness or len(prior.pairs) != 6:
        raise RuntimeError(("prior-root-certificate", prior))
    candidate_key = "threshold_candidates" if "threshold_candidates" in candidates else "top"
    rows = candidates[candidate_key][:maximum_rows]
    checked_count = 0
    sampled_rows = []
    hard_rows = []
    first_failure = None
    scenarios = candidates.get("scenarios")
    for row in rows:
        product = int(row["product"])
        if scenarios is None:
            fixed_values = (524_343, 524_351)
        else:
            fixed_values = tuple(
                int(value) for value in scenarios[int(row["scenario"])]["endpoints"]
            )
        merged: dict[int, int] = {}
        for fixed_value in fixed_values:
            for prime, exponent in engine.factor_tuple(fixed_value):
                merged[prime] = merged.get(prime, 0) + exponent
        for prime, exponent in engine.factor_tuple(int(row["multiplier"])):
            merged[prime] = merged.get(prime, 0) + exponent
        factors = tuple(sorted(merged.items()))
        if product != math.prod(prime**exponent for prime, exponent in factors):
            raise RuntimeError(("factor-product", product, factors))
        candidate = engine.classify_candidate(product, factors, ROOTS[0])
        if len(candidate.pairs) != int(row["d"]):
            raise RuntimeError(("pair-count", product, len(candidate.pairs), row["d"]))
        witnesses = []
        if candidate.hard:
            for root in ROOTS:
                witnesses.append(any(
                    not engine.generated(endpoint) and engine.seed_root(endpoint) == root
                    for pair in candidate.pairs
                    for endpoint in pair
                ))
        result = {
            "product": product,
            "h": product - 1,
            "d": len(candidate.pairs),
            "factorization": [[p, exponent] for p, exponent in factors],
            "hard": candidate.hard,
            "root_witnesses": witnesses,
        }
        checked_count += 1
        if len(sampled_rows) < 256:
            sampled_rows.append(result)
        if candidate.hard:
            hard_rows.append(result)
        if candidate.hard and all(witnesses):
            q = len(candidate.pairs) - 1
            weight = min(math.isqrt(q) + (math.isqrt(q) ** 2 < q), 18)
            first_failure = {
                **result,
                "j": 18,
                "roots": [PRIOR_ROOT, *ROOTS],
                "weights_after_exemption": [weight, weight],
                "least_root_exempt": PRIOR_ROOT,
                "tested_root": ROOTS[1],
                "lhs": 2 * weight,
                "rhs": ROOTS[1] - (1 << 18),
            }
            if first_failure["lhs"] <= first_failure["rhs"]:
                raise RuntimeError(first_failure)
            break
    return {
        "schema": "C113-cluster-recursive-closure-check-v1",
        "arithmetic": "exact integers only",
        "candidate_schema": candidates["schema"],
        "candidate_key": candidate_key,
        "requested_rows": maximum_rows,
        "checked_rows": checked_count,
        "prior_root_certificate": {
            "root": PRIOR_ROOT,
            "product": PRIOR_PRODUCT,
            "h": PRIOR_PRODUCT - 1,
            "d": len(prior.pairs),
            "hard": prior.hard,
            "fixed_root_witness": prior.fixed_root_witness,
        },
        "first_C108_MOVE_PACK_failure": first_failure,
        "sampled_rows": sampled_rows,
        "hard_rows": hard_rows,
        "cache": {
            "generated": engine.generated.cache_info()._asdict(),
            "factorizations": engine.factor_tuple.cache_info()._asdict(),
            "primality": engine.is_prime.cache_info()._asdict(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--maximum-rows", type=int, default=256)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.maximum_rows <= 2_000_000:
        raise RuntimeError(args.maximum_rows)
    engine = load_engine(args.engine)
    candidates = json.loads(args.candidates.read_text(encoding="ascii"))
    payload = run(engine, candidates, args.maximum_rows)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("ascii")
    args.output.write_bytes(encoded)
    print(hashlib.sha256(encoded).hexdigest())
    return 0


if __name__ == "__main__":
    sys.setrecursionlimit(100_000)
    raise SystemExit(main())
