#!/usr/bin/env python3
"""Exact event diagnostics for the C95 quarter-scale amortization.

This is a discovery/falsification tool, not a proof.  It reconstructs the
least generated set for Problem 424, records hard-root births/deaths and
structural-splitless chain healings, and studies the exact signed event
process

    F(X) = D(X) + A_H(floor(X/4)) - A_H(X).

All acceptance arithmetic is integral.  The output retains root-labelled
events at every new minimum of F, together with greedy prefix pairings, so a
candidate structural injection can be audited rather than inferred from a
count alone.
"""

from __future__ import annotations

import argparse
import json
from array import array
from collections import Counter, deque
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def smallest_prime_factors(limit: int) -> array:
    spf = array("I", range(limit + 1))
    if limit >= 1:
        spf[1] = 1
    p = 2
    while p * p <= limit:
        if spf[p] == p:
            for n in range(p * p, limit + 1, p):
                if spf[n] == n:
                    spf[n] = p
        p += 1
    return spf


def divisors(n: int, spf: array) -> list[int]:
    factors: list[tuple[int, int]] = []
    while n > 1:
        p = int(spf[n])
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        factors.append((p, exponent))
    out = [1]
    for p, exponent in factors:
        old = out
        out = []
        power = 1
        for _ in range(exponent + 1):
            out.extend(d * power for d in old)
            power *= p
    return out


def admissible_pairs(n: int, spf: array) -> list[tuple[int, int]]:
    product = n + 1
    out = []
    for a in divisors(product, spf):
        if a < 2 or a * a >= product:
            continue
        b = product // a
        if allowed(a) and allowed(b):
            out.append((a, b))
    return sorted(out)


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n & 1 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    parent = (n + 1) // 3
    return not (allowed(parent) and parent != 3)


def root_of_chain_value(value: int) -> int:
    if value & 1 == 0:
        return value
    shifted = value - 1
    return (shifted >> ((shifted & -shifted).bit_length() - 1)) + 1


def build(limit: int) -> dict:
    spf = smallest_prime_factors(limit + 1)
    generated = bytearray(limit + 1)
    splitless = bytearray(limit + 1)
    hard = bytearray(limit + 1)
    pairs_by_value: dict[int, list[tuple[int, int]]] = {}

    hard_birth_at: dict[int, list[int]] = {}
    hard_death_at: dict[int, list[int]] = {}
    splitless_heal_at: dict[int, list[int]] = {}

    for n in range(2, limit + 1):
        if not allowed(n):
            continue
        pairs = admissible_pairs(n, spf)
        pairs_by_value[n] = pairs
        if n in (2, 3) or any(generated[a] and generated[b] for a, b in pairs):
            generated[n] = 1
        elif not pairs:
            splitless[n] = 1
        elif hard_shape(n, pairs):
            hard[n] = 1
            hard_birth_at.setdefault(n, []).append(n)

        if n > 3 and n & 1 and generated[n]:
            parent = (n + 1) // 2
            if allowed(parent) and not generated[parent]:
                root = root_of_chain_value(n)
                if hard[root]:
                    hard_death_at.setdefault(n, []).append(root)
                elif splitless[root]:
                    splitless_heal_at.setdefault(n, []).append(root)

    return {
        "generated": generated,
        "splitless": splitless,
        "hard": hard,
        "pairs": pairs_by_value,
        "hard_birth_at": hard_birth_at,
        "hard_death_at": hard_death_at,
        "splitless_heal_at": splitless_heal_at,
    }


def analyze(limit: int) -> dict:
    data = build(limit)
    births = data["hard_birth_at"]
    deaths = data["hard_death_at"]
    heals = data["splitless_heal_at"]

    active_history = array("I", [0]) * (limit + 1)
    active = 0
    healed = 0
    minimum_f = 10**18
    minimum_rows = []
    maximum_g = -(10**18)
    maximum_g_rows = []
    signed_events = []

    # Positive event tokens are consumed FIFO by negative events.  A deficit
    # token is recorded explicitly; this pairing has no theorem status.
    positive_tokens: deque[dict] = deque()
    unmatched_negative = []
    pair_samples = []

    for x in range(2, limit + 1):
        local = []
        for root in births.get(x, ()):
            active += 1
            local.append({"sign": -1, "kind": "hard_birth", "root": root, "time": x})
        for root in deaths.get(x, ()):
            active -= 1
            local.append({"sign": 1, "kind": "hard_death", "root": root, "time": x})
        for root in heals.get(x, ()):
            healed += 1
            local.append({"sign": 1, "kind": "splitless_heal", "root": root, "time": x})

        active_history[x] = active

        if x % 4 == 0:
            t = x // 4
            for root in births.get(t, ()):
                local.append({"sign": 1, "kind": "scaled_hard_birth", "root": root, "time": x})
            for root in deaths.get(t, ()):
                local.append({"sign": -1, "kind": "scaled_hard_death", "root": root, "time": x})

        for event in local:
            if event["sign"] > 0:
                positive_tokens.append(event)
            elif positive_tokens:
                source = positive_tokens.popleft()
                if len(pair_samples) < 200:
                    pair_samples.append({"negative": event, "positive": source})
            else:
                unmatched_negative.append(event)

        if local:
            signed_events.append({"X": x, "events": local})

        quarter = int(active_history[x // 4])
        f = healed + quarter - active
        g = 7 * quarter - 2 * healed
        row = {
            "X": x,
            "A_H": active,
            "D": healed,
            "A_H_floor_X_over_4": quarter,
            "F": f,
            "G": g,
            "local_events": local,
        }
        if f < minimum_f:
            minimum_f = f
            minimum_rows = [row]
        elif f == minimum_f and len(minimum_rows) < 20:
            minimum_rows.append(row)
        if g > maximum_g:
            maximum_g = g
            maximum_g_rows = [row]
        elif g == maximum_g and len(maximum_g_rows) < 20:
            maximum_g_rows.append(row)

    final_active = int(active_history[limit])
    final_healed = sum(len(v) for v in heals.values())
    if final_active != sum(len(v) for v in births.values()) - sum(len(v) for v in deaths.values()):
        raise RuntimeError("hard event accounting failed")
    if healed != final_healed:
        raise RuntimeError("splitless event accounting failed")

    # Retain only event neighborhoods around new minima for manageable output.
    critical_times = {row["X"] for row in minimum_rows + maximum_g_rows}
    critical_events = [
        row for row in signed_events
        if any(abs(row["X"] - t) <= 8 for t in critical_times)
    ]

    return {
        "limit": limit,
        "definitions": {
            "F": "D(X)+A_H(floor(X/4))-A_H(X)",
            "G": "7*A_H(floor(X/4))-2*D(X)",
        },
        "endpoint": {
            "A_H": final_active,
            "D": final_healed,
            "A_H_floor_X_over_4": int(active_history[limit // 4]),
        },
        "minimum_F": minimum_f,
        "minimum_F_rows": minimum_rows,
        "maximum_G": maximum_g,
        "maximum_G_rows": maximum_g_rows,
        "greedy_event_pairing": {
            "unmatched_negative_count": len(unmatched_negative),
            "unmatched_negative_first": unmatched_negative[:100],
            "remaining_positive_count": len(positive_tokens),
            "pair_samples": pair_samples,
        },
        "critical_event_neighborhoods": critical_events,
        "event_counts": {
            "hard_birth": sum(len(v) for v in births.values()),
            "hard_death": sum(len(v) for v in deaths.values()),
            "splitless_heal": final_healed,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 2:
        raise ValueError("limit must be at least 2")
    result = analyze(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
