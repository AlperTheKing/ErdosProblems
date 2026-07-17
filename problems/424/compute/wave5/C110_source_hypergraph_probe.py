#!/usr/bin/env python3
"""Exact small-prefix falsifier for source-to-witness-root incidence claims."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


GENERATED = 1
SPLITLESS = 2
HARD = 3


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def full_spf(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    for p in range(2, int(limit**0.5) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit + 1, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def divisors(n: int, spf: list[int]) -> list[int]:
    factors: list[tuple[int, int]] = []
    while n > 1:
        p = spf[n]
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        factors.append((p, exponent))
    result = [1]
    for p, exponent in factors:
        old = tuple(result)
        power = 1
        for _ in range(exponent):
            power *= p
            result.extend(value * power for value in old)
    return result


def admissible_pairs(n: int, spf: list[int]) -> list[tuple[int, int]]:
    product = n + 1
    pairs = []
    for left in divisors(product, spf):
        if left < 2 or left * left >= product:
            continue
        right = product // left
        if allowed(left) and allowed(right):
            pairs.append((left, right))
    return sorted(pairs)


def seed_root(endpoint: int) -> int:
    require(endpoint > 1 and endpoint % 2 == 1, ("endpoint", endpoint))
    shifted = endpoint - 1
    return 1 + shifted // (shifted & -shifted)


def certificate(
    h: int,
    pairs: list[tuple[int, int]],
    state: bytearray,
) -> dict[str, object]:
    all_roots: set[int] = set()
    reducible_roots: set[int] = set()
    endpoint_rows = []
    for left, right in pairs:
        blocked = []
        for endpoint in (left, right):
            if state[endpoint] == GENERATED:
                continue
            root = seed_root(endpoint)
            all_roots.add(root)
            if state[root] != SPLITLESS:
                reducible_roots.add(root)
            blocked.append(
                {
                    "endpoint": endpoint,
                    "root": root,
                    "root_state": int(state[root]),
                }
            )
        require(blocked, ("unblocked", h, left, right))
        endpoint_rows.append({"pair": [left, right], "missing": blocked})
    return {
        "h": h,
        "d": len(pairs),
        "all_root_count": len(all_roots),
        "reducible_root_count": len(reducible_roots),
        "all_roots": sorted(all_roots),
        "reducible_roots": sorted(reducible_roots),
        "pairs": endpoint_rows,
    }


def first_failure(
    failures: dict[str, dict[str, object] | None],
    name: str,
    condition: bool,
    row: dict[str, object],
) -> None:
    if not condition and failures[name] is None:
        failures[name] = row


def run(limit: int, reference_path: Path | None) -> dict[str, object]:
    spf = full_spf(limit + 1)
    state = bytearray(limit + 1)
    maximum_d: dict[int, int] = {}
    failures: dict[str, dict[str, object] | None] = {
        "all_roots_squared_ge_d": None,
        "nonempty_reducible_roots_squared_ge_d_minus_1": None,
        "upgrade_source_reducible_roots_squared_ge_new_q": None,
        "all_times_reducible_ge_d_minus_1": None,
    }
    totals = {
        "generated": 0,
        "structural_splitless": 0,
        "hard": 0,
        "hard_with_reducible_root": 0,
        "maximum_pair_count": 0,
    }
    source_claim_tests = 0
    upgrade_claim_tests = 0

    for n in range(2, limit + 1):
        pairs: list[tuple[int, int]] = []
        current = 0
        if n in (2, 3):
            current = GENERATED
        elif allowed(n):
            pairs = admissible_pairs(n, spf)
            if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
                current = GENERATED
            elif not pairs:
                current = SPLITLESS
            elif n % 2 == 0:
                product = n + 1
                seed_three_easy = (
                    product % 3 == 0
                    and product // 3 != 3
                    and allowed(product // 3)
                )
                if not seed_three_easy:
                    current = HARD
        state[n] = current
        if current == GENERATED:
            totals["generated"] += 1
        elif current == SPLITLESS:
            totals["structural_splitless"] += 1
        elif current == HARD:
            totals["hard"] += 1
            totals["maximum_pair_count"] = max(totals["maximum_pair_count"], len(pairs))
            row = certificate(n, pairs, state)
            a = int(row["all_root_count"])
            m = int(row["reducible_root_count"])
            d = len(pairs)
            totals["hard_with_reducible_root"] += bool(m)
            source_claim_tests += 1
            first_failure(failures, "all_roots_squared_ge_d", a * a >= d, row)
            if m:
                first_failure(
                    failures,
                    "nonempty_reducible_roots_squared_ge_d_minus_1",
                    m * m >= d - 1,
                    row,
                )
                first_failure(
                    failures,
                    "all_times_reducible_ge_d_minus_1",
                    a * m >= d - 1,
                    row,
                )
            for root in row["reducible_roots"]:
                old_d = maximum_d.get(root, 0)
                if d <= old_d:
                    continue
                upgrade_claim_tests += 1
                first_failure(
                    failures,
                    "upgrade_source_reducible_roots_squared_ge_new_q",
                    m * m >= d - 1,
                    {**row, "upgraded_root": root, "old_d": old_d},
                )
                maximum_d[root] = d

        if n % 2 and allowed(n) and current != GENERATED:
            parent = (n + 1) // 2
            require(allowed(parent) and state[parent] != GENERATED, ("parent", n, parent))

    reference = None
    if reference_path is not None:
        raw = reference_path.read_bytes()
        parsed = json.loads(raw)
        require(int(parsed["limit"]) == limit, "reference limit")
        require(parsed["totals"] == totals, ("reference totals", totals, parsed["totals"]))
        reference = {
            "path": reference_path.as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "totals_exact_match": True,
        }

    return {
        "schema": "C110-source-hypergraph-probe-v1",
        "limit": limit,
        "arithmetic": "exact integers only",
        "totals": totals,
        "source_claim_tests": source_claim_tests,
        "upgrade_claim_tests": upgrade_claim_tests,
        "first_failures": failures,
        "reference": reference,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(1_000 <= args.limit <= 1_000_000, ("limit", args.limit))
    payload = run(args.limit, args.reference)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("ascii")
    args.output.write_bytes(encoded)
    print(hashlib.sha256(encoded).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
