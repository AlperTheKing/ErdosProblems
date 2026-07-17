#!/usr/bin/env python3
"""Exact small-limit adversarial gates for the C104-BIN inequality.

This implementation reconstructs the closure from the defining factor rule.
For each non-splitless witness root r it records

    q_X(r) = max_h (d(h) - 1),

where h ranges over hard sources through X witnessed by r.  The layer-cake
identity turns sum(q_X(r)) into the total number of threshold tokens carried
by the root.  The script also tests two nested-neighborhood token injections.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


GENERATED = 1
SPLITLESS = 2
HARD = 3


@dataclass(frozen=True)
class Certificate:
    q: int
    source: int
    endpoint: int


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
            result.extend(d * power for d in old)
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
    return pairs


def seed_root(endpoint: int) -> int:
    shifted = endpoint - 1
    return 1 + shifted // (shifted & -shifted)


def first_failure(
    old: dict | None,
    *,
    x: int,
    j: int,
    lhs: int,
    rhs: int,
    root: int,
) -> dict | None:
    if old is not None or lhs <= rhs:
        return old
    return {"X": x, "j": j, "lhs": lhs, "rhs": rhs, "root": root}


def ordered_gate_failures(
    by_bin: dict[int, dict[int, Certificate]], x: int
) -> tuple[dict | None, dict | None]:
    lower_deadline = None
    upper_release = None
    for j, roots in by_bin.items():
        lower = 1 << j
        upper = 1 << (j + 1)
        ordered = sorted((root - 1, root, cert.q) for root, cert in roots.items())

        prefix = 0
        for denominator, root, q in ordered:
            prefix += q
            lower_deadline = first_failure(
                lower_deadline,
                x=x,
                j=j,
                lhs=prefix,
                rhs=denominator - lower + 1,
                root=root,
            )

        suffix = 0
        for denominator, root, q in reversed(ordered):
            suffix += q
            upper_release = first_failure(
                upper_release,
                x=x,
                j=j,
                lhs=suffix,
                rhs=upper - denominator,
                root=root,
            )
    return lower_deadline, upper_release


def analyze(limit: int) -> dict:
    spf = full_spf(limit + 1)
    state = bytearray(limit + 1)
    certificates: dict[int, Certificate] = {}
    by_bin: dict[int, dict[int, Certificate]] = {}
    first_bin_failure = None
    first_weighted_failure = None
    first_lower_deadline_failure = None
    first_upper_release_failure = None
    hard_sources = 0
    root_upgrade_events = 0

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

        if current != HARD:
            continue
        hard_sources += 1
        d = len(pairs)
        witnessed: dict[int, int] = {}
        for left, right in pairs:
            blocked = False
            for endpoint in (left, right):
                if state[endpoint] == GENERATED:
                    continue
                blocked = True
                root = seed_root(endpoint)
                if state[root] == GENERATED:
                    raise AssertionError(("generated witness root", n, endpoint, root))
                if state[root] != SPLITLESS:
                    witnessed.setdefault(root, endpoint)
            if not blocked:
                raise AssertionError(("unblocked hard pair", n, left, right))

        touched = False
        for root, endpoint in witnessed.items():
            q = d - 1
            old = certificates.get(root)
            if old is not None and old.q >= q:
                continue
            cert = Certificate(q=q, source=n, endpoint=endpoint)
            certificates[root] = cert
            denominator = root - 1
            j = denominator.bit_length() - 1
            by_bin.setdefault(j, {})[root] = cert
            root_upgrade_events += 1
            touched = True

        if not touched:
            continue

        for j, roots in by_bin.items():
            capacity = 1 << j
            weights = [cert.q for cert in roots.values()]
            weighted = sum(weights)
            first_weighted_failure = first_failure(
                first_weighted_failure,
                x=n,
                j=j,
                lhs=weighted,
                rhs=capacity,
                root=max(roots),
            )
            for threshold in range(1, max(weights, default=0) + 1):
                count = sum(q >= threshold for q in weights)
                first_bin_failure = first_failure(
                    first_bin_failure,
                    x=n,
                    j=j,
                    lhs=threshold * count,
                    rhs=capacity,
                    root=max(roots),
                )

        lower_failure, upper_failure = ordered_gate_failures(by_bin, n)
        if first_lower_deadline_failure is None:
            first_lower_deadline_failure = lower_failure
        if first_upper_release_failure is None:
            first_upper_release_failure = upper_failure

    bins = []
    for j, roots in sorted(by_bin.items()):
        ordered = sorted(roots.items())
        weighted = sum(cert.q for _, cert in ordered)
        bins.append(
            {
                "j": j,
                "capacity": 1 << j,
                "root_count": len(ordered),
                "threshold_token_sum": weighted,
                "maximum_q": max(cert.q for _, cert in ordered),
                "roots": [
                    {
                        "root": root,
                        "q": cert.q,
                        "source": cert.source,
                        "endpoint": cert.endpoint,
                    }
                    for root, cert in ordered
                ],
            }
        )

    return {
        "schema": "C108-c104-bin-token-gate-v1",
        "limit": limit,
        "arithmetic": "exact integers only",
        "hard_sources": hard_sources,
        "distinct_reducible_witness_roots": len(certificates),
        "root_upgrade_events": root_upgrade_events,
        "first_C104_BIN_failure": first_bin_failure,
        "first_weighted_token_budget_failure": first_weighted_failure,
        "first_lower_deadline_injection_failure": first_lower_deadline_failure,
        "first_upper_release_injection_failure": first_upper_release_failure,
        "bins": bins,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 2:
        raise ValueError("limit must be at least 2")
    result = analyze(args.limit)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_bytes(payload.encode("ascii"))
    print(hashlib.sha256(payload.encode("ascii")).hexdigest().upper())


if __name__ == "__main__":
    main()
