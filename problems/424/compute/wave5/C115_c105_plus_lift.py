#!/usr/bin/env python3
"""Exact plus-prime lift test for C105 structural-pair deficit examples.

For a hard product N=h+1 and a new prime q=1 (mod 3), the admissible
factor pairs of Nq are the two lifts of every pair of N.  If a base pair
has exactly one missing endpoint m, both lifted pairs remain blocked iff
qm is missing.  Pairs with two missing endpoints need no extra condition.

The script tests that criterion, reclassifies every surviving lift using
the pinned recursive closure engine, and computes the literal C105
structural-pair statistic s.  All arithmetic is exact below 2^64.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def load_engine(path: Path):
    spec = importlib.util.spec_from_file_location("C115_pinned_engine", path)
    require(spec is not None and spec.loader is not None, ("import", path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def lifted_factors(factors: tuple[tuple[int, int], ...], q: int):
    out = dict(factors)
    out[q] = out.get(q, 0) + 1
    return tuple(sorted(out.items()))


def structural_root(engine, endpoint: int) -> bool:
    root = engine.seed_root(endpoint)
    return not engine.admissible_pairs_from_product(root + 1)


def literal_s(engine, pairs: tuple[tuple[int, int], ...]):
    rows = []
    s = 0
    for left, right in pairs:
        endpoint_rows = []
        counted = False
        for endpoint in (left, right):
            present = engine.generated(endpoint)
            root = None if present else engine.seed_root(endpoint)
            structural = False if present else structural_root(engine, endpoint)
            counted = counted or structural
            endpoint_rows.append(
                {
                    "value": endpoint,
                    "generated": present,
                    "root": root,
                    "root_structural_splitless": structural,
                }
            )
        require(any(not row["generated"] for row in endpoint_rows), ("unblocked", left, right))
        s += int(counted)
        rows.append({"a": left, "b": right, "counted_in_s": counted, "endpoints": endpoint_rows})
    return s, rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", type=int, required=True)
    parser.add_argument("--prime-limit", type=int, default=100_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    require(7 <= args.prime_limit <= 10_000_000, ("prime-limit", args.prime_limit))
    engine_path = Path(__file__).with_name("C109_fixed_root_search.py")
    engine = load_engine(engine_path)
    factors = engine.factor_tuple(args.product)
    base_pairs = engine.admissible_pairs_from_product(args.product, factors)
    base = engine.classify_candidate(args.product, factors, 2)
    require(base.hard, ("base-not-hard", args.product))
    base_s, base_rows = literal_s(engine, base_pairs)

    forced = []
    two_hole = []
    for left, right in base_pairs:
        holes = [x for x in (left, right) if not engine.generated(x)]
        require(holes, ("base-unblocked", left, right))
        if len(holes) == 1:
            forced.append(holes[0])
        else:
            require(len(holes) == 2, ("hole-count", left, right, holes))
            two_hole.append([left, right])

    hits = []
    best_missing = -1
    best_primes = []
    tested = 0
    for q in engine.primes_through(args.prime_limit):
        if q % 3 != 1 or args.product % q == 0:
            continue
        if args.product * q > engine.UINT64_MAX:
            continue
        tested += 1
        missing = sum(not engine.generated(q * m) for m in forced)
        if missing > best_missing:
            best_missing = missing
            best_primes = [q]
        elif missing == best_missing and len(best_primes) < 16:
            best_primes.append(q)
        if missing != len(forced):
            continue

        product = args.product * q
        candidate = engine.classify_candidate(product, lifted_factors(factors, q), 2)
        require(candidate.hard, ("lift-criterion", q, product))
        require(len(candidate.pairs) == 2 * len(base_pairs), ("pair-doubling", q))
        s, rows = literal_s(engine, candidate.pairs)
        hits.append(
            {
                "q": q,
                "product": product,
                "h": product - 1,
                "d": len(candidate.pairs),
                "s": s,
                "deficit": len(candidate.pairs) - s,
                "pairs": rows,
            }
        )

    payload = {
        "schema": "C115-c105-plus-lift-v1",
        "exactness": {
            "integer_domain": "unsigned 64-bit",
            "dependency": engine_path.name,
            "dependency_sha256": hashlib.sha256(engine_path.read_bytes()).hexdigest().upper(),
            "primality": "deterministic Miller-Rabin below 2^64",
            "factorization": "Pollard-Brent with exact product recheck",
            "closure": "full recursive admissible-divisor membership to seeds 2,3",
            "floating_point_acceptance": False,
        },
        "prime_limit": args.prime_limit,
        "base": {
            "product": args.product,
            "h": args.product - 1,
            "factorization": [[p, e] for p, e in factors],
            "d": len(base_pairs),
            "s": base_s,
            "pairs": base_rows,
            "forced_one_hole_blockers": forced,
            "two_hole_pairs": two_hole,
        },
        "eligible_plus_primes_tested": tested,
        "maximum_forced_blockers_remaining_missing": best_missing,
        "best_primes": best_primes,
        "hits": hits,
        "deficit_nine_falsifier": next((row for row in hits if row["deficit"] >= 9), None),
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.output.write_text(encoded, encoding="ascii")
    digest = hashlib.sha256(encoded.encode("ascii")).hexdigest().upper()
    print(
        f"base_d={len(base_pairs)} base_s={base_s} tested={tested} hits={len(hits)} "
        f"max_deficit={max((row['deficit'] for row in hits), default=-1)} sha256={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
