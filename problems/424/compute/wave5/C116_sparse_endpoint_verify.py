#!/usr/bin/env python3
"""Independent recursive replay of a sparse C116 endpoint certificate."""

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
    spec = importlib.util.spec_from_file_location("C116_recursive_engine", path)
    require(spec is not None and spec.loader is not None, ("import", path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def claim_row(path: Path, h: int) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="ascii"))
    rows = [row for row in payload["hard_rows"] if row["h"] == h]
    require(len(rows) == 1, ("claim row", h, len(rows)))
    row = rows[0]
    e0 = 0
    e1 = 0
    for pair in row["pairs"]:
        for endpoint in pair["endpoints"]:
            if endpoint["state"] == "generated":
                continue
            if endpoint["root_state"] == "structural_splitless":
                e0 += 1
            else:
                e1 += 1
    return {"d": row["d"], "s": row["s"], "E0": e0, "E1": e1}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", type=int, required=True)
    parser.add_argument("--claim", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(args.product >= 3 and args.product % 2 == 1, ("product", args.product))

    engine_path = Path(__file__).with_name("C109_fixed_root_search.py")
    engine = load_engine(engine_path)
    factors = engine.factor_tuple(args.product)
    pairs = engine.admissible_pairs_from_product(args.product, factors)
    candidate = engine.classify_candidate(args.product, factors, 2)
    require(candidate.hard, ("not hard", args.product, candidate))
    require(tuple(candidate.pairs) == tuple(pairs), "candidate pair mismatch")

    e0: set[int] = set()
    e1: set[int] = set()
    s = 0
    t = 0
    prefix_t = 0
    prefix_slacks = []
    pair_rows = []
    for index, (left, right) in enumerate(pairs, start=1):
        structural_pair = False
        endpoint_rows = []
        missing = 0
        for endpoint in (left, right):
            generated = engine.generated(endpoint)
            if generated:
                endpoint_rows.append(
                    {
                        "value": endpoint,
                        "generated": True,
                        "root": None,
                        "root_pair_count": None,
                        "root_structural_splitless": False,
                    }
                )
                continue
            missing += 1
            root = engine.seed_root(endpoint)
            root_pairs = engine.admissible_pairs_from_product(root + 1)
            structural = not root_pairs
            require(not engine.generated(root), ("generated root", endpoint, root))
            if structural:
                e0.add(endpoint)
                structural_pair = True
            else:
                e1.add(endpoint)
            endpoint_rows.append(
                {
                    "value": endpoint,
                    "generated": False,
                    "root": root,
                    "root_pair_count": len(root_pairs),
                    "root_structural_splitless": structural,
                }
            )
        require(missing >= 1, ("unblocked", left, right))
        s += int(structural_pair)
        canonical = left if not engine.generated(left) else right
        canonical_root = engine.seed_root(canonical)
        canonical_structural = not engine.admissible_pairs_from_product(canonical_root + 1)
        t += int(canonical_structural)
        prefix_t += int(canonical_structural)
        prefix_slack = 2 * prefix_t - index + 8
        prefix_slacks.append(prefix_slack)
        require(prefix_slack >= 0, ("prefix balance", index, prefix_t, pairs))
        pair_rows.append(
            {
                "prefix_index": index,
                "prefix_t": prefix_t,
                "prefix_slack": prefix_slack,
                "pair": [left, right],
                "counted_in_s": structural_pair,
                "canonical_blocker": canonical,
                "canonical_root": canonical_root,
                "counted_in_t": canonical_structural,
                "endpoints": endpoint_rows,
            }
        )

    d = len(pairs)
    replay = {"d": d, "s": s, "E0": len(e0), "E1": len(e1)}
    pinned = claim_row(args.claim, args.product - 1)
    require(replay == pinned, ("claim mismatch", replay, pinned))
    require(len(e1) > len(e0) + 8, ("not an endpoint falsifier", replay))
    require(d - s <= len(e1), "first bridge")
    require(len(e0) <= 2 * s, "second bridge")

    result = {
        "schema": "C116-sparse-endpoint-replay-v2",
        "exactness": {
            "arithmetic": "integers only",
            "closure": "recursive least-closure membership over all admissible divisors",
            "factorization": "Pollard-Brent with exact product recheck",
            "primality": "deterministic Miller-Rabin below 2^64",
            "floating_point_acceptance": False,
            "engine": engine_path.name,
            "engine_sha256": hashlib.sha256(engine_path.read_bytes()).hexdigest().upper(),
            "claim_sha256": hashlib.sha256(args.claim.read_bytes()).hexdigest().upper(),
        },
        "product": args.product,
        "h": args.product - 1,
        "factorization": [[prime, exponent] for prime, exponent in factors],
        "d": d,
        "s": s,
        "t": t,
        "E0": sorted(e0),
        "E1": sorted(e1),
        "endpoint_imbalance": {
            "lhs_E1": len(e1),
            "rhs_E0_plus_8": len(e0) + 8,
            "failure_margin": len(e1) - len(e0) - 8,
        },
        "power_bridge": {
            "lhs_3s": 3 * s,
            "rhs_d_minus_8": d - 8,
            "passes": 3 * s >= d - 8,
        },
        "canonical_power": {
            "lhs_2t": 2 * t,
            "rhs_d_minus_8": d - 8,
            "passes": 2 * t >= d - 8,
        },
        "canonical_prefix_balance": {
            "minimum_slack": min(prefix_slacks),
            "passes": min(prefix_slacks) >= 0,
        },
        "claim_replay": {"expected": pinned, "actual": replay, "status": "PASS"},
        "pairs": pair_rows,
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_bytes(encoded.encode("ascii"))
    print(hashlib.sha256(encoded.encode("ascii")).hexdigest().upper())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
