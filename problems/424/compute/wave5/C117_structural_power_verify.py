#!/usr/bin/env python3
"""Independent replay of C117 retained hard-source extremals."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from functools import lru_cache

import sympy


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3
NAMES = {
    OTHER: "other_hole",
    GENERATED: "generated",
    SPLITLESS: "structural_splitless",
    HARD: "hard",
}


def is_allowed(value: int) -> bool:
    return value >= 2 and value % 3 in (0, 2)


def source_shape(product: int) -> str | None:
    if product % 3 == 1:
        return "R"
    if product % 9 == 3 and (product // 3) % 3 == 1:
        return "3R"
    return None


@lru_cache(maxsize=None)
def exact_pairs(value: int) -> tuple[tuple[int, int], ...]:
    product = value + 1
    return tuple(
        (int(left), int(product // left))
        for left_value in sympy.divisors(product)
        for left in (int(left_value),)
        if 2 <= left < product // left
        and is_allowed(left)
        and is_allowed(product // left)
    )


@lru_cache(maxsize=None)
def closure_state(value: int) -> int:
    if value in (2, 3):
        return GENERATED
    if not is_allowed(value):
        return OTHER
    pairs = exact_pairs(value)
    if any(
        closure_state(left) == GENERATED and closure_state(right) == GENERATED
        for left, right in pairs
    ):
        return GENERATED
    if not pairs:
        return SPLITLESS
    if value % 2 == 0 and source_shape(value + 1) is not None:
        return HARD
    return OTHER


def iterative_seed_root(value: int) -> int:
    if value < 3 or value % 2 == 0:
        raise ValueError(("odd_endpoint_required", value))
    current = value
    while current % 2:
        current = (current + 1) // 2
    return current


def replay_record(claim: dict[str, object]) -> dict[str, object]:
    product = int(claim["N"])
    source = product - 1
    claimed_factors = {int(p): int(e) for p, e in claim["factors"].items()}  # type: ignore[union-attr]
    actual_factors = {
        int(prime): int(exponent)
        for prime, exponent in sympy.factorint(product).items()
    }
    factorization_matches = actual_factors == claimed_factors
    factor_product_matches = (
        math.prod(prime**exponent for prime, exponent in claimed_factors.items())
        == product
    )
    source_state = closure_state(source)
    pairs = exact_pairs(source)
    pair_rows = []
    structural_count = 0
    endpoint_counts: Counter[str] = Counter()
    root_counts: Counter[str] = Counter()
    pair_type_counts: Counter[str] = Counter()
    endpoints_valid = True
    for left, right in pairs:
        endpoints = []
        states = []
        structural = False
        for endpoint in (left, right):
            endpoint_state = closure_state(endpoint)
            endpoint_name = NAMES[endpoint_state]
            endpoint_counts[endpoint_name] += 1
            states.append(endpoint_name)
            if endpoint_state == GENERATED:
                root = None
                root_state = None
            else:
                root = iterative_seed_root(endpoint)
                root_code = closure_state(root)
                root_state = NAMES[root_code]
                root_counts[root_state] += 1
                structural = structural or root_code == SPLITLESS
                endpoints_valid = endpoints_valid and root_code != GENERATED
            endpoints.append({
                "value": endpoint,
                "state": endpoint_name,
                "root": root,
                "root_state": root_state,
            })
        pair_type_counts["+".join(sorted(states))] += 1
        structural_count += int(structural)
        pair_rows.append({
            "pair": [left, right],
            "endpoints": endpoints,
            "counted_in_s": structural,
        })
    d_value = len(pairs)
    s_value = structural_count
    taxonomy = {
        "endpoint_states": dict(sorted(endpoint_counts.items())),
        "missing_root_states": dict(sorted(root_counts.items())),
        "pair_types": dict(sorted(pair_type_counts.items())),
        "structural_pairs": s_value,
        "nonstructural_pairs": d_value - s_value,
    }
    target = {
        "lhs": (s_value + 8) ** 4,
        "rhs": d_value**3,
        "falsifier": (s_value + 8) ** 4 < d_value**3,
    }
    checks = {
        "factorization": factorization_matches,
        "factor_product": factor_product_matches,
        "hardness": source_state == HARD and claim["state"] == "hard",
        "shape": source_shape(product) == claim["shape"],
        "d": d_value == int(claim["d"]),
        "s": s_value == int(claim["s"]),
        "deficit": d_value - s_value == int(claim["deficit"]),
        "target_3_4": target == claim["target_3_4"],
        "endpoints_and_roots": endpoints_valid and pair_rows == claim["pairs"],
        "taxonomy": taxonomy == claim["taxonomy"],
        "all_pairs_multiply": all(left * right == product for left, right in pairs),
        "all_pairs_distinct_allowed": all(
            2 <= left < right and is_allowed(left) and is_allowed(right)
            for left, right in pairs
        ),
    }
    return {
        "h": source,
        "N": product,
        "d": d_value,
        "s": s_value,
        "shape": source_shape(product),
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


def verify(claim: dict[str, object]) -> dict[str, object]:
    records = claim["verification_records"]
    replay_rows = [replay_record(record) for record in records]  # type: ignore[arg-type]
    record_map = {int(record["N"]): record for record in records}  # type: ignore[index]
    table_checks = []
    for row in claim["extremal_by_d"]:  # type: ignore[union-attr]
        product = int(row["best_N"])
        record = record_map.get(product)
        table_checks.append({
            "d": int(row["d"]),
            "N": product,
            "record_present": record is not None,
            "record_matches": (
                record is not None
                and int(record["d"]) == int(row["d"])
                and int(record["s"]) == int(row["min_s"])
            ),
        })
    detail_digest = hashlib.sha256(
        json.dumps(records, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    digest_matches = detail_digest == claim["digests"]["verification_records_sha256"]  # type: ignore[index]
    summary_falsifiers = int(claim["summary"]["target_3_4_falsifiers"])  # type: ignore[index]
    listed_falsifiers = len(claim["falsifiers"])  # type: ignore[arg-type]
    retained_falsifiers = sum(
        int(bool(record["target_3_4"]["falsifier"])) for record in records  # type: ignore[index]
    )
    falsifier_accounting = (
        summary_falsifiers == listed_falsifiers
        and (summary_falsifiers == 0 or retained_falsifiers == summary_falsifiers)
    )
    overall = (
        all(row["status"] == "PASS" for row in replay_rows)
        and all(row["record_present"] and row["record_matches"] for row in table_checks)
        and digest_matches
        and falsifier_accounting
    )
    return {
        "schema": "C117-structural-power-verify-v1",
        "independence": {
            "imports_search_implementation": False,
            "source_factorization": "sympy.factorint",
            "source_divisors": "sympy.divisors",
            "seed_root": "iterative (p+1)/2",
            "recursive_closure": True,
        },
        "claim_schema": claim.get("schema"),
        "records_replayed": len(replay_rows),
        "record_replays": replay_rows,
        "extremal_table_checks": table_checks,
        "verification_records_digest_matches": digest_matches,
        "falsifier_accounting": falsifier_accounting,
        "cache": {
            "state_entries": closure_state.cache_info().currsize,
            "pair_entries": exact_pairs.cache_info().currsize,
        },
        "status": "PASS" if overall else "FAIL",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    with open(args.claim, "r", encoding="ascii") as handle:
        claim = json.load(handle)
    result = verify(claim)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="ascii", newline="\n") as handle:
            handle.write(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
