#!/usr/bin/env python3
"""Exact unranked cap-two transport checker for Erdos Problem 424.

The scan reconstructs the least grounded set in increasing order.  It keeps
only factor pairs 2 <= a < b, so the distinct-input rule is enforced at the
point where membership is decided.  Hole components use the canonical C39
parent: T2 for odd holes and T3 for seed-3-easy even holes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from array import array
from dataclasses import dataclass


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def spf_sieve(bound: int) -> array:
    spf = array("I", range(bound + 1))
    for p in range(2, int(bound**0.5) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, bound + 1, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def divisors(n: int, spf: array) -> list[int]:
    result = [1]
    while n > 1:
        p = spf[n]
        old_size = len(result)
        power = 1
        while n > 1 and spf[n] == p:
            n //= p
            power *= p
            for i in range(old_size):
                result.append(result[i] * power)
    return result


def admissible_pairs(n: int, spf: array) -> list[tuple[int, int]]:
    product = n + 1
    pairs = []
    for a in divisors(product, spf):
        if a < 2:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            pairs.append((a, b))
    pairs.sort()
    return pairs


def seed_three_easy(n: int) -> bool:
    if n % 2 or (n + 1) % 3:
        return False
    parent = (n + 1) // 3
    return parent != 3 and allowed(parent)


@dataclass
class PrefixAudit:
    maximum_excess: int = 0
    maximum_x: int = 0
    first_plus_one_failure: dict | None = None

    def observe(self, x: int, hard: int, exits: int) -> None:
        excess = hard - exits
        if excess > self.maximum_excess:
            self.maximum_excess = excess
            self.maximum_x = x
        if excess > 1 and self.first_plus_one_failure is None:
            self.first_plus_one_failure = {
                "X": x,
                "H": hard,
                "Q": exits,
                "excess": excess,
            }


def literal_grounded_set(limit: int, spf: array) -> bytearray:
    """Independent literal fixed-point iteration for a small-prefix audit."""
    current = bytearray(limit + 1)
    current[2] = current[3] = 1
    while True:
        nxt = current[:]
        for n in range(4, limit + 1):
            if not allowed(n) or current[n]:
                continue
            if any(current[a] and current[b]
                   for a, b in admissible_pairs(n, spf)):
                nxt[n] = 1
        if nxt == current:
            return current
        current = nxt


def scan(limit: int, verify_limit: int) -> dict:
    spf = spf_sieve(limit + 1)
    member = bytearray(limit + 1)
    component_root = array("I", [0]) * (limit + 1)
    # Values are saturated at two because later exits are deliberately ignored.
    selected_in_component = bytearray(limit + 1)
    member[2] = member[3] = 1

    hard_events: list[int] = []
    cap_one_events: list[int] = []
    cap_two_events: list[int] = []
    hard_witnesses: list[dict] = []
    exit_witnesses: list[dict] = []
    decomposition_failures: list[dict] = []
    cap_one_audit = PrefixAudit()
    cap_two_audit = PrefixAudit()
    all_exit_count = 0
    splitless_roots = 0
    hard_roots = 0

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs = admissible_pairs(n, spf)
        generated_pair = next(
            ((a, b) for a, b in pairs if member[a] and member[b]), None
        )
        if generated_pair is not None:
            member[n] = 1
            if n % 2:
                parent = (n + 1) // 2
                if allowed(parent) and not member[parent]:
                    root = component_root[parent]
                    if root == 0:
                        decomposition_failures.append({
                            "n": n,
                            "reason": "exit parent has no canonical root",
                            "parent": parent,
                        })
                    else:
                        all_exit_count += 1
                        old_ordinal = selected_in_component[root]
                        if old_ordinal < 2:
                            selected_in_component[root] = old_ordinal + 1
                            cap_two_events.append(n)
                            if old_ordinal == 0:
                                cap_one_events.append(n)
                            if len(exit_witnesses) < 40:
                                exit_witnesses.append({
                                    "child": n,
                                    "parent": parent,
                                    "root": root,
                                    "ordinal": old_ordinal + 1,
                                    "generation_pair": list(generated_pair),
                                })
            continue

        parent = None
        parent_kind = None
        if n % 2:
            parent = (n + 1) // 2
            parent_kind = "T2"
        elif seed_three_easy(n):
            parent = (n + 1) // 3
            parent_kind = "T3"

        if parent is None:
            component_root[n] = n
        elif member[parent] or component_root[parent] == 0:
            decomposition_failures.append({
                "n": n,
                "reason": "canonical parent is not an earlier rooted hole",
                "parent": parent,
                "kind": parent_kind,
                "parent_member": bool(member[parent]),
            })
            component_root[n] = n
        else:
            component_root[n] = component_root[parent]

        hard = n % 2 == 0 and bool(pairs) and not seed_three_easy(n)
        if parent is None:
            if hard:
                hard_roots += 1
            elif not pairs:
                splitless_roots += 1
            else:
                decomposition_failures.append({
                    "n": n,
                    "reason": "noncanonical hole root is neither hard nor splitless",
                })

        if not hard:
            continue
        hard_events.append(n)
        if len(hard_witnesses) < 40:
            hard_witnesses.append({
                "source": n,
                "pairs": [list(pair) for pair in pairs],
                "blocker_roots": sorted({
                    component_root[x]
                    for pair in pairs
                    for x in pair
                    if not member[x]
                }),
            })
        cap_one_audit.observe(n, len(hard_events), len(cap_one_events))
        cap_two_audit.observe(n, len(hard_events), len(cap_two_events))

    order_failure = None
    for j in range(2, len(hard_events) + 1):
        exit_index = j - 2
        if exit_index >= len(cap_two_events) or cap_two_events[exit_index] >= hard_events[j - 1]:
            order_failure = {
                "j": j,
                "hard": hard_events[j - 1],
                "required_exit_index": j - 1,
                "exit": (
                    cap_two_events[exit_index]
                    if exit_index < len(cap_two_events) else None
                ),
            }
            break

    verify_limit = min(verify_limit, limit)
    if verify_limit >= 3:
        literal = literal_grounded_set(verify_limit, spf)
        membership_mismatches = [
            n for n in range(2, verify_limit + 1) if literal[n] != member[n]
        ]
    else:
        membership_mismatches = []

    digest = hashlib.sha256(member).hexdigest()
    return {
        "schema_version": 1,
        "limit": limit,
        "distinct_input_rule": "every tested pair satisfies 2 <= a < b",
        "member_count": sum(member),
        "member_bitmap_sha256": digest,
        "hard_count": len(hard_events),
        "hard_roots": hard_roots,
        "splitless_roots": splitless_roots,
        "all_healed_seed2_exits": all_exit_count,
        "cap_one_selected_exits": len(cap_one_events),
        "cap_two_selected_exits": len(cap_two_events),
        "cap_one_prefix": {
            "maximum_excess": cap_one_audit.maximum_excess,
            "maximum_X": cap_one_audit.maximum_x,
            "first_plus_one_failure": cap_one_audit.first_plus_one_failure,
        },
        "cap_two_prefix": {
            "maximum_excess": cap_two_audit.maximum_excess,
            "maximum_X": cap_two_audit.maximum_x,
            "first_plus_one_failure": cap_two_audit.first_plus_one_failure,
        },
        "cap_two_order_statistic_failure": order_failure,
        "cap_one_event_prefix": cap_one_events[:200],
        "cap_two_event_prefix": cap_two_events[:200],
        "decomposition_failure_count": len(decomposition_failures),
        "decomposition_failures": decomposition_failures[:20],
        "literal_fixed_point_verify_limit": verify_limit,
        "literal_fixed_point_membership_mismatches": membership_mismatches[:20],
        "first_hard_witnesses": hard_witnesses,
        "first_selected_exit_witnesses": exit_witnesses,
        "last_counts": {
            "H_minus_Q1": len(hard_events) - len(cap_one_events),
            "H_minus_Q2": len(hard_events) - len(cap_two_events),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100_000)
    parser.add_argument("--verify-limit", type=int, default=2_000)
    args = parser.parse_args()
    if args.limit < 10:
        parser.error("--limit must be at least 10")
    if args.verify_limit < 0:
        parser.error("--verify-limit must be nonnegative")
    print(json.dumps(scan(args.limit, args.verify_limit), indent=2))


if __name__ == "__main__":
    main()
