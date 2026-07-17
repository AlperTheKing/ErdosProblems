#!/usr/bin/env python3
"""Exact recursive test of the C116 odd powers of 11 construction."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


MAX_U64 = (1 << 64) - 1


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def load_engine(path: Path):
    spec = importlib.util.spec_from_file_location("C116_odd_power_engine", path)
    require(spec is not None and spec.loader is not None, ("import", path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    engine_path = Path(__file__).with_name("C109_fixed_root_search.py")
    engine = load_engine(engine_path)
    odd_power_rows = []
    first_failure = None

    exponent = 1
    while 11**exponent <= MAX_U64:
        p = 11**exponent
        root = engine.seed_root(p)
        require(root == (p + 1) // 2, ("unexpected 2-adic root", exponent, p, root))
        root_product = root + 1
        root_factors = engine.factor_tuple(root_product)
        root_pairs = engine.admissible_pairs_from_product(root_product, root_factors)
        is_generated = engine.generated(p)
        expected_structural = exponent == 1
        structural = not root_pairs
        passes = not is_generated and structural == expected_structural
        row = {
            "exponent": exponent,
            "p": p,
            "generated": is_generated,
            "root": root,
            "root_product": root_product,
            "root_product_factorization": [list(item) for item in root_factors],
            "root_pairs": [list(pair) for pair in root_pairs],
            "root_structural_splitless": structural,
            "passes_claim_IV": passes,
        }
        odd_power_rows.append(row)
        if not passes and first_failure is None:
            first_failure = row
        exponent += 2

    source_rows = []
    m = 2
    while 11 ** (2 * m) <= MAX_U64:
        product = 11 ** (2 * m)
        factors = ((11, 2 * m),)
        candidate = engine.classify_candidate(product, factors, 6)
        expected_pairs = tuple(
            (11**i, 11 ** (2 * m - i)) for i in range(1, m, 2)
        )
        require(candidate.pairs == expected_pairs, ("source pairs", m, candidate.pairs))
        pair_rows = []
        s = 0
        for left, right in candidate.pairs:
            endpoint_rows = []
            structural_pair = False
            for endpoint in (left, right):
                generated = engine.generated(endpoint)
                root = None if generated else engine.seed_root(endpoint)
                root_pairs = (
                    ()
                    if generated
                    else engine.admissible_pairs_from_product(root + 1)
                )
                structural = not generated and not root_pairs
                structural_pair = structural_pair or structural
                endpoint_rows.append(
                    {
                        "value": endpoint,
                        "generated": generated,
                        "root": root,
                        "root_pair_count": None if generated else len(root_pairs),
                        "root_structural_splitless": structural,
                    }
                )
            blocked = any(not row["generated"] for row in endpoint_rows)
            s += int(structural_pair)
            pair_rows.append(
                {
                    "pair": [left, right],
                    "blocked": blocked,
                    "structural": structural_pair,
                    "endpoints": endpoint_rows,
                }
            )
        d = len(candidate.pairs)
        expected_d = m // 2
        passes = candidate.hard and d == expected_d and s == 1
        source_row = {
            "m": m,
            "h": candidate.h,
            "product": product,
            "factorization": [[11, 2 * m]],
            "hard": candidate.hard,
            "d": d,
            "expected_d": expected_d,
            "s": s,
            "passes_counterfamily_prefix": passes,
            "pairs": pair_rows,
        }
        source_rows.append(source_row)
        if not passes and first_failure is None:
            first_failure = source_row
        m += 1

    result = {
        "schema": "C116-odd-power-search-v1",
        "exactness": {
            "arithmetic": "integers only",
            "maximum": "2^64-1",
            "closure": "recursive least closure over every admissible factor pair",
            "factorization": "Pollard-Brent with exact product recheck",
            "primality": "deterministic Miller-Rabin below 2^64",
            "floating_point_acceptance": False,
            "engine": engine_path.name,
            "engine_sha256": hashlib.sha256(engine_path.read_bytes()).hexdigest().upper(),
        },
        "odd_power_rows": odd_power_rows,
        "source_rows": source_rows,
        "first_failure": first_failure,
        "status": "PASS" if first_failure is None else "FAIL",
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_bytes(encoded.encode("ascii"))
    print(hashlib.sha256(encoded.encode("ascii")).hexdigest().upper())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
