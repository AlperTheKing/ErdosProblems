#!/usr/bin/env python3
"""Independent integer-only verifier for C61 witnesses and duals.

This file deliberately does not import either C61 generator.  It reconstructs
the number-theoretic model from the certificate cutoff and rejects duplicate,
invalid, wrongly signed, or nonstationary dual entries.
"""

from __future__ import annotations

import argparse
import json
import math
from array import array
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pair_iter(limit: int):
    for a in range(2, math.isqrt(limit + 1) + 1):
        if not allowed(a):
            continue
        for b in range(a + 1, (limit + 1) // a + 1):
            if allowed(b):
                yield a * b - 1, a, b


def base_data(limit: int):
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pair_count = array("I", [0]) * (limit + 1)
    total_pairs = 0
    for n, _, _ in pair_iter(limit):
        pair_count[n] += 1
        total_pairs += 1
    hard = set()
    splitless = set()
    for n in values:
        if n not in (2, 3) and pair_count[n] == 0:
            splitless.add(n)
        if n % 2 or pair_count[n] == 0:
            continue
        if (n + 1) % 3:
            hard.add(n)
        else:
            parent = (n + 1) // 3
            if not (allowed(parent) and parent != 3):
                hard.add(n)
    return values, total_pairs, hard, splitless


def verify_dual(cert: dict) -> dict:
    if cert.get("format") != "C61_SCB_REDUCED_DUAL_V1":
        raise RuntimeError("unknown certificate format")
    limit = int(cert["limit"])
    values, total_pairs, hard, splitless = base_data(limit)
    value_set = set(values)

    target = {n: int(n in hard) for n in values}
    seed2_edges = 0
    for m in values:
        child = 2 * m - 1
        if child <= limit:
            seed2_edges += 1
            target[child] += 1
            target[m] -= 1

    stationarity = {n: 0 for n in values}
    objective = 0
    seen_rows = set()
    for entry in cert["row"]:
        if len(entry) != 4:
            raise RuntimeError("malformed closure dual entry")
        n, a, b, multiplier = map(int, entry)
        key = (n, a, b)
        if key in seen_rows:
            raise RuntimeError("duplicate closure dual entry")
        seen_rows.add(key)
        if multiplier >= 0:
            raise RuntimeError("closure multiplier must be strictly negative when listed")
        if not (2 <= a < b <= limit and n == a * b - 1 <= limit):
            raise RuntimeError("invalid closure factorization")
        if not (allowed(a) and allowed(b) and allowed(n)):
            raise RuntimeError("closure factorization uses a disallowed value")
        stationarity[a] += multiplier
        stationarity[b] += multiplier
        stationarity[n] -= multiplier
        objective += multiplier

    seen_lower = set()
    for n_raw, multiplier_raw in cert["lower"]:
        n, multiplier = int(n_raw), int(multiplier_raw)
        if n in seen_lower or n not in value_set:
            raise RuntimeError("duplicate or invalid lower-bound entry")
        seen_lower.add(n)
        if multiplier <= 0:
            raise RuntimeError("listed lower-bound multiplier must be positive")
        stationarity[n] += multiplier
        lower = 1 if n in (2, 3) else 0
        objective += lower * multiplier

    seen_upper = set()
    for n_raw, multiplier_raw in cert["upper"]:
        n, multiplier = int(n_raw), int(multiplier_raw)
        if n in seen_upper or n not in value_set:
            raise RuntimeError("duplicate or invalid upper-bound entry")
        seen_upper.add(n)
        if multiplier >= 0:
            raise RuntimeError("listed upper-bound multiplier must be negative")
        stationarity[n] += multiplier
        if n in splitless:
            upper = 0
        else:
            upper = 1
        objective += upper * multiplier

    bad = [n for n in values if stationarity[n] != target[n]]
    if bad:
        n = bad[0]
        raise RuntimeError(
            f"stationarity failure at {n}: got {stationarity[n]}, expected {target[n]}"
        )
    if int(cert["hard_count"]) != len(hard):
        raise RuntimeError("hard-count metadata mismatch")
    if int(cert["splitless_count"]) != len(splitless):
        raise RuntimeError("splitless-count metadata mismatch")
    if int(cert["value_count"]) != len(values):
        raise RuntimeError("value-count metadata mismatch")
    if int(cert["pair_count"]) != total_pairs:
        raise RuntimeError("pair-count metadata mismatch")
    if int(cert["seed2_edges"]) != seed2_edges:
        raise RuntimeError("seed2-edge metadata mismatch")
    if objective < len(hard):
        raise RuntimeError("dual objective does not prove SCB")
    return {
        "limit": limit,
        "hard_count": len(hard),
        "exact_dual_objective": objective,
        "exact_margin": objective - len(hard),
        "nonzero_closure_rows": len(seen_rows),
        "nonzero_lower_bounds": len(seen_lower),
        "nonzero_upper_bounds": len(seen_upper),
        "conclusion": "NO_BOOLEAN_COUNTEREXAMPLE",
    }


def verify_witness(payload: dict) -> dict:
    limit = int(payload["limit"])
    members_list = [int(n) for n in payload["members"]]
    if len(members_list) != len(set(members_list)):
        raise RuntimeError("duplicate witness member")
    members = set(members_list)
    values, total_pairs, hard, splitless = base_data(limit)
    value_set = set(values)
    if not members <= value_set:
        raise RuntimeError("witness member outside the allowed cutoff universe")
    if not {2, 3} <= members:
        raise RuntimeError("witness omits 2 or 3")
    if members & splitless:
        raise RuntimeError("witness contains a structural splitless nonseed")
    for n, a, b in pair_iter(limit):
        if a in members and b in members and n not in members:
            raise RuntimeError(f"closure failure {a}*{b}-1={n}")
    hard_holes = sorted(hard - members)
    boundaries = []
    for m in values:
        child = 2 * m - 1
        if child <= limit and m not in members and child in members:
            boundaries.append(child)
    score = len(hard_holes) - len(boundaries)
    if score <= 0:
        raise RuntimeError("witness does not falsify SCB")
    return {
        "limit": limit,
        "pair_count": total_pairs,
        "H": len(hard_holes),
        "Q": len(boundaries),
        "H_minus_Q": score,
        "conclusion": "BOOLEAN_COUNTEREXAMPLE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--certificate", type=Path)
    group.add_argument("--witness", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    if args.certificate:
        payload = json.loads(args.certificate.read_text(encoding="utf-8"))
        certs = payload if isinstance(payload, list) else [payload]
        summary = [verify_dual(cert) for cert in certs]
    else:
        summary = [verify_witness(json.loads(args.witness.read_text(encoding="utf-8")))]
    text = json.dumps(summary, indent=2)
    print(text)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
