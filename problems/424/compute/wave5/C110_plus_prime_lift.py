#!/usr/bin/env python3
"""Exact plus-prime lift gate for the two roots in C104's j=5 bin.

For a hard product N=h+1 with N=1 (mod 3), multiplication by a new prime
q=1 (mod 3) doubles the admissible complementary pairs.  A base pair with
two missing endpoints stays blocked in both lifts.  A base pair with exactly
one missing endpoint m stays blocked in both lifts exactly when q*m is also
missing.  This script tests that criterion and then rechecks every divisor
pair of each surviving lifted product.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


DEFAULT_BASES = (
    (7_634_275, 54),
    (2_778_055, 62),
    (1_559_219_515, 54),
    (298_274_515, 62),
    (2_796_867_115, 54),
)


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def load_exact_engine(path: Path):
    name = "C110_pinned_C109_engine"
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, ("import", path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def parse_base(text: str) -> tuple[int, int]:
    product, separator, root = text.partition(":")
    if not separator:
        raise argparse.ArgumentTypeError("base must have form PRODUCT:ROOT")
    return int(product), int(root)


def lifted_factors(
    factors: tuple[tuple[int, int], ...], q: int
) -> tuple[tuple[int, int], ...]:
    result = dict(factors)
    result[q] = result.get(q, 0) + 1
    return tuple(sorted(result.items()))


def analyze_base(engine, product: int, root: int, primes: list[int]) -> dict:
    factors = engine.factor_tuple(product)
    base = engine.classify_candidate(product, factors, root)
    require(product % 3 == 1, ("base-residue", product))
    require(base.hard and base.fixed_root_witness, ("base-validation", product, root))

    forced_blockers = []
    two_hole_pairs = []
    for left, right in base.pairs:
        holes = tuple(x for x in (left, right) if not engine.generated(x))
        require(holes, ("unblocked-base-pair", product, left, right))
        if len(holes) == 1:
            forced_blockers.append(holes[0])
        else:
            require(len(holes) == 2, ("hole-count", holes))
            two_hole_pairs.append([left, right])

    tested = 0
    best_missing_count = -1
    best_rows = []
    hits = []
    for q in primes:
        if q % 3 != 1 or product % q == 0:
            continue
        if product * q > engine.UINT64_MAX:
            continue
        tested += 1
        blocker_rows = []
        missing_count = 0
        for blocker in forced_blockers:
            value = blocker * q
            is_missing = not engine.generated(value)
            missing_count += is_missing
            blocker_rows.append(
                {"base_blocker": blocker, "lifted_value": value, "missing": is_missing}
            )
        if missing_count > best_missing_count:
            best_missing_count = missing_count
            best_rows = [{"q": q, "blockers": blocker_rows}]
        elif missing_count == best_missing_count and len(best_rows) < 8:
            best_rows.append({"q": q, "blockers": blocker_rows})
        if missing_count != len(forced_blockers):
            continue

        new_product = product * q
        candidate = engine.classify_candidate(
            new_product, lifted_factors(factors, q), root
        )
        require(len(candidate.pairs) == 2 * len(base.pairs), ("pair-doubling", q))
        require(candidate.hard, ("lift-criterion-false", product, root, q))
        require(candidate.fixed_root_witness, ("root-not-preserved", product, root, q))
        hits.append(engine.candidate_json(candidate, root))

    return {
        "product": product,
        "h": product - 1,
        "root": root,
        "factorization": [[p, exponent] for p, exponent in factors],
        "base_d": len(base.pairs),
        "forced_one_hole_blockers": forced_blockers,
        "two_hole_pairs": two_hole_pairs,
        "eligible_plus_primes_tested": tested,
        "maximum_forced_blockers_remaining_missing": best_missing_count,
        "forced_blocker_count": len(forced_blockers),
        "best_prime_rows": best_rows,
        "lift_hits": hits,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime-limit", type=int, default=100_000)
    parser.add_argument("--base", type=parse_base, action="append")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(7 <= args.prime_limit <= 10_000_000, ("prime-limit", args.prime_limit))

    engine_path = Path(__file__).with_name("C109_fixed_root_search.py")
    engine_bytes = engine_path.read_bytes()
    engine = load_exact_engine(engine_path)
    primes = engine.primes_through(args.prime_limit)
    bases = tuple(args.base) if args.base else DEFAULT_BASES
    rows = [analyze_base(engine, product, root, primes) for product, root in bases]

    root_best: dict[int, int] = {}
    for row in rows:
        for hit in row["lift_hits"]:
            root = int(row["root"])
            root_best[root] = max(root_best.get(root, 0), int(hit["d"]))
    c104_falsifier = None
    if 54 in root_best and 62 in root_best:
        d = min(root_best[54], root_best[62]) - 1
        if 2 * d > 32:
            c104_falsifier = {
                "D": d,
                "j": 5,
                "roots": [54, 62],
                "lhs": 2 * d,
                "rhs": 32,
            }

    payload = {
        "schema": "C110-plus-prime-lift-gate-v1",
        "exactness": {
            "integer_domain": "unsigned 64-bit",
            "dependency": engine_path.name,
            "dependency_sha256": hashlib.sha256(engine_bytes).hexdigest().upper(),
            "primality": "deterministic Miller-Rabin below 2^64",
            "factorization": "Pollard-Brent with factor primality and product rechecks",
            "closure": "full recursive admissible-divisor membership to seeds 2,3",
            "floating_point_acceptance": False,
        },
        "prime_limit": args.prime_limit,
        "rows": rows,
        "C104_BIN_falsifier": c104_falsifier,
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.output.write_text(encoded, encoding="ascii")
    digest = hashlib.sha256(encoded.encode("ascii")).hexdigest().upper()
    print(
        f"bases={len(rows)} hits={sum(len(row['lift_hits']) for row in rows)} "
        f"falsifier={'yes' if c104_falsifier else 'no'} sha256={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
