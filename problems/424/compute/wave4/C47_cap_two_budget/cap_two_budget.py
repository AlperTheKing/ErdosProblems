#!/usr/bin/env python3
"""Exact audits for the unranked cap-two canonical-exit inequality.

The script reconstructs the least grounded set G by ascending divisor
recursion.  It then checks the exact forest identity and several increasingly
restrictive online matchings.  All arithmetic and comparisons are integral.
"""

from __future__ import annotations

import argparse
import bisect
import json
import math
from array import array
from collections import Counter, deque
from pathlib import Path


SPLITLESS, ODD, EASY3, HARD = range(1, 5)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def spf_sieve(limit: int) -> array:
    spf = array("I", range(limit + 1))
    for p in range(2, math.isqrt(limit) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit + 1, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def divisors(n: int, spf: array) -> list[int]:
    result = [1]
    while n > 1:
        p = spf[n]
        old_length = len(result)
        power = 1
        while n % p == 0:
            n //= p
            power *= p
            for i in range(old_length):
                result.append(result[i] * power)
    return result


def pairs_for(n: int, spf: array) -> list[tuple[int, int]]:
    result = []
    for a in divisors(n + 1, spf):
        if a < 2:
            continue
        b = (n + 1) // a
        if a < b and allowed(a) and allowed(b):
            result.append((a, b))
    return sorted(result)


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    parent = (n + 1) // 3
    return not (allowed(parent) and parent != 3)


class ExactData:
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.member = bytearray(limit + 1)
        self.kind = bytearray(limit + 1)
        self.parent = array("I", [0]) * (limit + 1)
        self.root = array("I", [0]) * (limit + 1)
        self.target_parent = array("I", [0]) * (limit + 1)
        self.pairs: dict[int, list[tuple[int, int]]] = {}
        self.missing_endpoints: dict[int, list[int]] = {}


def build_exact(limit: int) -> ExactData:
    data = ExactData(limit)
    spf = spf_sieve(limit + 1)
    data.member[2] = data.member[3] = 1

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs = pairs_for(n, spf)
        if any(data.member[a] and data.member[b] for a, b in pairs):
            data.member[n] = 1
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not data.member[q]:
                    data.target_parent[n] = q
            continue

        if not pairs:
            data.kind[n] = SPLITLESS
            data.root[n] = n
        elif n % 2:
            q = (n + 1) // 2
            assert not data.member[q]
            data.kind[n] = ODD
            data.parent[n] = q
            data.root[n] = data.root[q]
        elif hard_shape(n, pairs):
            data.kind[n] = HARD
            data.root[n] = n
            data.pairs[n] = pairs
            data.missing_endpoints[n] = sorted({
                x
                for a, b in pairs
                for x in (a, b)
                if not data.member[x]
            })
        else:
            q = (n + 1) // 3
            assert q % 2 and allowed(q) and not data.member[q]
            data.kind[n] = EASY3
            data.parent[n] = q
            data.root[n] = data.root[q]
    return data


def cap_two_events(data: ExactData) -> tuple[list[dict], list[dict], list[int]]:
    ordinals: Counter[int] = Counter()
    hard = []
    targets = []
    all_target_children = []
    for n in range(2, data.limit + 1):
        if data.kind[n] == HARD:
            endpoints = data.missing_endpoints[n]
            hard.append({
                "child": n,
                "minimum_missing_endpoint": min(endpoints),
                "maximum_missing_endpoint": max(endpoints),
                "minimum_factor": min(a for a, _ in data.pairs[n]),
                "maximum_factor": max(b for _, b in data.pairs[n]),
                "missing_roots": sorted({data.root[x] for x in endpoints}),
            })
        q = data.target_parent[n]
        if not q:
            continue
        all_target_children.append(n)
        root = data.root[q]
        ordinals[root] += 1
        if ordinals[root] <= 2:
            targets.append({
                "child": n,
                "parent": q,
                "root": root,
                "ordinal": ordinals[root],
            })
    return hard, targets, all_target_children


def prefix_audit(hard: list[dict], targets: list[dict], limit: int) -> dict:
    hi = ti = h_count = q_count = 0
    maximum = -10**9
    first_strict_failure = None
    equality_events = []
    for x in range(2, limit + 1):
        while hi < len(hard) and hard[hi]["child"] == x:
            h_count += 1
            hi += 1
        while ti < len(targets) and targets[ti]["child"] == x:
            q_count += 1
            ti += 1
        excess = h_count - q_count
        maximum = max(maximum, excess)
        if excess > 0 and first_strict_failure is None:
            first_strict_failure = {"X": x, "H": h_count, "Q2": q_count}
        if excess == 0 and hi and hard[hi - 1]["child"] == x:
            equality_events.append(x)
    return {
        "claim": "H(X) <= Q2(X)",
        "maximum_excess": maximum,
        "first_strict_failure": first_strict_failure,
        "hard_total": len(hard),
        "cap_two_target_total": len(targets),
        "hard_event_equalities": equality_events,
    }


def greedy_interval_matching(
    hard: list[dict], targets: list[dict], numerator: int, denominator: int
) -> dict:
    """Match h to arrived q with q >= ceil(numerator*(h+1)/denominator).

    Target parents arrive in increasing order because their child is 2q-1.
    The lower bounds increase with h, so discarding stale parents and taking
    the least eligible parent is the canonical greedy interval algorithm.
    """
    available: deque[dict] = deque()
    target_index = 0
    discarded = 0
    first_failure = None
    maximum_queue = 0
    first_pairs = []
    for row in hard:
        h = row["child"]
        while target_index < len(targets) and targets[target_index]["child"] < h:
            available.append(targets[target_index])
            target_index += 1
        lower = (numerator * (h + 1) + denominator - 1) // denominator
        while available and available[0]["parent"] < lower:
            available.popleft()
            discarded += 1
        if not available:
            first_failure = {
                "hard": row,
                "required_parent_at_least": lower,
                "arrived_targets": target_index,
                "discarded_targets": discarded,
            }
            break
        target = available.popleft()
        if len(first_pairs) < 30:
            first_pairs.append({"hard": h, "target": target})
        maximum_queue = max(maximum_queue, len(available))
    return {
        "threshold": f"q >= ceil({numerator}*(h+1)/{denominator})",
        "first_failure": first_failure,
        "matched": len(hard) if first_failure is None else None,
        "discarded_stale_targets": discarded,
        "maximum_queue_after_match": maximum_queue,
        "first_pairs": first_pairs,
    }


def greedy_key_matching(
    hard: list[dict], targets: list[dict], hard_key: str, target_key: str
) -> dict:
    """Deadline greedy for a lower-bound key not monotone in h."""
    available: list[tuple[int, int, dict]] = []
    target_index = 0
    first_failure = None
    for row in hard:
        h = row["child"]
        while target_index < len(targets) and targets[target_index]["child"] < h:
            target = targets[target_index]
            bisect.insort(
                available,
                (target[target_key], target["child"], target),
            )
            target_index += 1
        lower = row[hard_key]
        index = bisect.bisect_left(available, (lower, -1, {}))
        if index == len(available):
            first_failure = {
                "hard": row,
                "required_key_at_least": lower,
                "available_tail": [entry[2] for entry in available[-10:]],
            }
            break
        available.pop(index)
    return {
        "hard_key": hard_key,
        "target_key": target_key,
        "first_failure": first_failure,
    }


def local_component_matching(hard: list[dict], targets: list[dict]) -> dict:
    """Test the ancestry-local relation killed by the source 74."""
    available_by_root: dict[int, list[dict]] = {}
    target_index = 0
    first_failure = None
    for row in hard:
        h = row["child"]
        while target_index < len(targets) and targets[target_index]["child"] < h:
            target = targets[target_index]
            available_by_root.setdefault(target["root"], []).append(target)
            target_index += 1
        chosen_root = next(
            (root for root in row["missing_roots"] if available_by_root.get(root)),
            None,
        )
        if chosen_root is None:
            first_failure = {
                "hard": row,
                "available_in_missing_components": {
                    str(root): available_by_root.get(root, [])
                    for root in row["missing_roots"]
                },
            }
            break
        available_by_root[chosen_root].pop(0)
    return {
        "relation": "target root is a canonical root of a missing factor",
        "first_failure": first_failure,
    }


def frontier_identity(
    data: ExactData,
    hard: list[dict],
    targets: list[dict],
    all_target_children: list[int],
) -> dict:
    """Verify H-Q2 = A2-S-E+(Q-Q2) at every cutoff."""
    limit = data.limit
    holes = array("I", [0]) * (limit + 1)
    splitless = array("I", [0]) * (limit + 1)
    easy3 = array("I", [0]) * (limit + 1)
    hp = array("I", [0]) * (limit + 1)
    q2p = array("I", [0]) * (limit + 1)
    qallp = array("I", [0]) * (limit + 1)
    hard_set = {row["child"] for row in hard}
    q2_set = {row["child"] for row in targets}
    qall_set = set(all_target_children)
    failures = []
    maximum_rhs = -10**9
    maximum_rhs_x = 0
    for x in range(2, limit + 1):
        holes[x] = holes[x - 1] + int(allowed(x) and not data.member[x])
        splitless[x] = splitless[x - 1] + int(data.kind[x] == SPLITLESS)
        easy3[x] = easy3[x - 1] + int(data.kind[x] == EASY3)
        hp[x] = hp[x - 1] + int(x in hard_set)
        q2p[x] = q2p[x - 1] + int(x in q2_set)
        qallp[x] = qallp[x - 1] + int(x in qall_set)
        half = (x + 1) // 2
        a2 = holes[x] - holes[half]
        extra = qallp[x] - q2p[x]
        left = int(hp[x]) - int(q2p[x])
        right = int(a2) - int(easy3[x]) - int(splitless[x]) + int(extra)
        if right > maximum_rhs:
            maximum_rhs = right
            maximum_rhs_x = x
        if left != right and len(failures) < 10:
            failures.append({"X": x, "left": left, "right": right})
    return {
        "identity": "H-Q2 = (M(X)-M(floor((X+1)/2))) - S - E + (Q-Q2)",
        "failures": failures,
        "maximum_residual": maximum_rhs,
        "maximum_residual_X": maximum_rhs_x,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 100:
        raise ValueError("limit must be at least 100")

    data = build_exact(args.limit)
    hard, targets, all_target_children = cap_two_events(data)
    payload = {
        "schema_version": 1,
        "limit": args.limit,
        "prefix": prefix_audit(hard, targets, args.limit),
        "frontier_identity": frontier_identity(
            data, hard, targets, all_target_children
        ),
        "interval_matchings": [
            greedy_interval_matching(hard, targets, 1, 3),
            greedy_interval_matching(hard, targets, 3, 8),
        ],
        "factor_threshold_matchings": [
            greedy_key_matching(
                hard, targets, "maximum_missing_endpoint", "parent"
            ),
            greedy_key_matching(hard, targets, "maximum_factor", "parent"),
            greedy_key_matching(
                hard, targets, "maximum_missing_endpoint", "root"
            ),
        ],
        "local_component_matching": local_component_matching(hard, targets),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": args.limit,
        "prefix": payload["prefix"],
        "frontier_identity": payload["frontier_identity"],
        "interval_matchings": [
            {
                "threshold": row["threshold"],
                "first_failure": row["first_failure"],
            }
            for row in payload["interval_matchings"]
        ],
        "factor_threshold_matchings": payload["factor_threshold_matchings"],
        "local_component_matching": payload["local_component_matching"],
    }, indent=2))


if __name__ == "__main__":
    main()
