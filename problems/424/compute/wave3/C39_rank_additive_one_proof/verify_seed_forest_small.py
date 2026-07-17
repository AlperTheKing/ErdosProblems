#!/usr/bin/env python3
"""Independent trial-divisor and literal-stage replay for C39."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pairs_for(n: int) -> list[tuple[int, int]]:
    result = []
    a = 2
    while a * a < n + 1:
        if (n + 1) % a == 0:
            b = (n + 1) // a
            if allowed(a) and allowed(b):
                result.append((a, b))
        a += 1
    return result


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def structural_parent(n: int) -> int | None:
    if n > 3 and n % 2:
        return (n + 1) // 2
    if n % 2 == 0 and (n + 1) % 3 == 0:
        q = (n + 1) // 3
        if allowed(q) and q != 3:
            return q
    return None


def structural_root(n: int) -> int:
    while (parent := structural_parent(n)) is not None:
        n = parent
    return n


def greedy(hard: list[tuple[int, int]], targets: list[tuple[int, int]],
           selected: set[int]) -> list[tuple[int, int]]:
    available = [[] for _ in range(64)]
    target_pos = 0
    unmatched = []
    for source, source_rank in hard:
        while target_pos < len(targets) and targets[target_pos][0] <= source:
            child, target_rank = targets[target_pos]
            if child in selected:
                available[target_rank].append(child)
            target_pos += 1
        for target_rank in range(source_rank, -1, -1):
            if available[target_rank]:
                available[target_rank].pop()
                break
        else:
            unmatched.append((source, source_rank))
    return unmatched


def audit(limit: int) -> dict:
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pairs = {n: pairs_for(n) for n in values}
    member = {2, 3}
    rank: dict[int, int] = {}
    hard = []
    targets_with_root = []
    forest_failures = []

    for n in values:
        if n in (2, 3):
            continue
        if any(a in member and b in member for a, b in pairs[n]):
            member.add(n)
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and q not in member:
                    targets_with_root.append((n, q, rank[q], structural_root(q)))
            continue
        if not pairs[n]:
            rank[n] = 0
        else:
            rank[n] = 1 + max(
                min(rank[x] for x in (a, b) if x not in member)
                for a, b in pairs[n]
            )
        parent = structural_parent(n)
        if parent is None:
            if not (not pairs[n] or hard_shape(n, pairs[n])):
                forest_failures.append((n, "root classification"))
        elif parent in member or rank[parent] >= rank[n]:
            forest_failures.append((n, parent, rank.get(parent), rank[n]))
        if hard_shape(n, pairs[n]):
            hard.append((n, rank[n]))

    stage = set(values)
    first_absent = {}
    stage_index = 0
    while True:
        following = {2, 3}
        for n in values:
            if n in (2, 3):
                continue
            if any(a in stage and b in stage for a, b in pairs[n]):
                following.add(n)
        for n in stage - following:
            first_absent[n] = stage_index + 1
        stage_index += 1
        if following == stage:
            break
        stage = following
    stage_mismatches = [
        {"n": n, "member": n in member, "stage_member": n in stage,
         "rank": rank.get(n), "first_absent": first_absent.get(n)}
        for n in values
        if (n in member) != (n in stage)
        or (n not in member and first_absent[n] != rank[n] + 1)
    ]

    ordinal = defaultdict(int)
    first_k = {1: set(), 2: set()}
    all_targets = set()
    target_rows = []
    component_targets = defaultdict(list)
    for child, parent, target_rank, root in targets_with_root:
        ordinal[root] += 1
        all_targets.add(child)
        for cap in first_k:
            if ordinal[root] <= cap:
                first_k[cap].add(child)
        target_rows.append((child, target_rank))
        component_targets[root].append({
            "child": child, "parent": parent, "rank": target_rank,
            "ordinal": ordinal[root],
        })

    full_unmatched = greedy(hard, target_rows, all_targets)
    one_unmatched = greedy(hard, target_rows, first_k[1])
    two_unmatched = greedy(hard, target_rows, first_k[2])
    global_74 = [
        {"child": child, "parent": parent, "rank": target_rank, "root": root}
        for child, parent, target_rank, root in targets_with_root
        if child <= 74 and target_rank <= 2
    ]
    component_8 = component_targets[8]
    hard_lookup = {n: r for n, r in hard}
    target_lookup = {child: target_rank for child, target_rank in target_rows}
    max_rank = max(rank.values(), default=0)
    potential_mismatches = []
    for d in range(max_rank + 1):
        m_prefix = [0] * (limit + 1)
        odd_m_prefix = [0] * (limit + 1)
        e_prefix = [0] * (limit + 1)
        h_prefix = [0] * (limit + 1)
        q_prefix = [0] * (limit + 1)
        a2_prefix = [0] * (limit + 1)
        a3_prefix = [0] * (limit + 1)
        r3_prefix = [0] * (limit + 1)
        for n in values:
            if n not in member and rank[n] <= d:
                m_prefix[n] += 1
                if n % 2:
                    odd_m_prefix[n] += 1
            if n not in member and not pairs[n]:
                e_prefix[n] += 1
            if n in hard_lookup and hard_lookup[n] <= d:
                h_prefix[n] += 1
            if n in target_lookup and target_lookup[n] <= d:
                q_prefix[n] += 1
        for parent in values:
            if parent in member or rank[parent] > d:
                continue
            for multiplier, transient_prefix, terminal_prefix in (
                (2, a2_prefix, None), (3, a3_prefix, r3_prefix)
            ):
                if multiplier == 3 and parent % 2 == 0:
                    continue
                child = multiplier * parent - 1
                if child > limit:
                    continue
                if child in member:
                    if terminal_prefix is not None:
                        terminal_prefix[child] += 1
                elif rank[child] > d:
                    transient_prefix[child] += 1
        arrays = (m_prefix, odd_m_prefix, e_prefix, h_prefix, q_prefix,
                  a2_prefix, a3_prefix, r3_prefix)
        for x in range(1, limit + 1):
            for row in arrays:
                row[x] += row[x - 1]
            y = (x + 1) // 2
            z = (x + 1) // 3
            left = h_prefix[x] - q_prefix[x]
            right = (
                m_prefix[x] - e_prefix[x] - m_prefix[y] - odd_m_prefix[z]
                + a2_prefix[x] + a3_prefix[x] + r3_prefix[x]
            )
            if left != right:
                potential_mismatches.append({
                    "X": x, "d": d, "left": left, "right": right,
                })
                break
        if potential_mismatches:
            break
    assertions = {
        "forest_decomposition": not forest_failures,
        "literal_stages_match": not stage_mismatches,
        "full_unmatched_is_362": full_unmatched == [(362, 2)],
        "two_boundary_unmatched_is_362": two_unmatched == [(362, 2)],
        "source_74_has_no_local_arrived_credit": not [
            row for row in component_8 if row["child"] <= 74 and row["rank"] <= 2
        ],
        "source_74_global_credits_are_41_69": [
            row["child"] for row in global_74
        ] == [41, 69],
        "rank_filtered_potential_identity": not potential_mismatches,
    }
    if not all(assertions.values()):
        raise AssertionError((assertions, potential_mismatches[:1]))

    return {
        "schema_version": 1,
        "limit": limit,
        "algorithm": "trial divisors plus literal descending stages",
        "generated": len(member),
        "hard": len(hard),
        "targets": len(target_rows),
        "stages_to_fixpoint": stage_index,
        "rank_histogram_hard": dict(sorted(Counter(r for _, r in hard).items())),
        "rank_histogram_target": dict(sorted(Counter(r for _, r in target_rows).items())),
        "forest_failures": forest_failures,
        "stage_mismatches": stage_mismatches,
        "potential_identity_mismatches": potential_mismatches,
        "full_unmatched": full_unmatched,
        "one_boundary_unmatched_prefix": one_unmatched[:30],
        "one_boundary_unmatched_count": len(one_unmatched),
        "two_boundary_unmatched": two_unmatched,
        "component_8_target_prefix": component_8[:5],
        "global_credits_at_74_rank_le_2": global_74,
        "assertions": assertions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = audit(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": payload["limit"],
        "hard": payload["hard"],
        "targets": payload["targets"],
        "stages": payload["stages_to_fixpoint"],
        "one_boundary_unmatched": payload["one_boundary_unmatched_count"],
        "two_boundary_unmatched": payload["two_boundary_unmatched"],
        "assertions": payload["assertions"],
    }, indent=2))


if __name__ == "__main__":
    main()
