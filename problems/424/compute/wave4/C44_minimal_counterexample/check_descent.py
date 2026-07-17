#!/usr/bin/env python3
"""Exact tests for a minimal-counterexample descent for Problem 424.

The checker reconstructs the least grounded set in increasing order.  It
then audits consequences of the obstruction-rank recurrence and deliberately
strong timing claims that one might try to use at a first additive-one
violation.  Every failed claim is reported with its first exact falsifier.
"""

from __future__ import annotations

import argparse
import json
from array import array
from collections import Counter, defaultdict
from pathlib import Path


INF = 65535


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def spf_sieve(limit: int) -> array:
    spf = array("I", range(limit + 1))
    for p in range(2, int(limit**0.5) + 1):
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
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def structural_parent(n: int) -> tuple[int, str] | None:
    """Return the forced seed parent of a non-root hole."""
    if n > 3 and n % 2:
        return (n + 1) // 2, "T2"
    if n % 2 == 0 and (n + 1) % 3 == 0:
        q = (n + 1) // 3
        if allowed(q) and q != 3:
            return q, "T3"
    return None


def first_failure(current: dict | None, condition: bool, payload: dict) -> dict | None:
    if current is None and not condition:
        return payload
    return current


def audit(limit: int) -> dict:
    spf = spf_sieve(limit + 1)
    member = bytearray(limit + 1)
    rank = array("H", [INF]) * (limit + 1)
    member[2] = member[3] = 1

    hard_records: list[dict] = []
    target_records: list[dict] = []
    splitless = bytearray(limit + 1)

    recurrence_failures = {
        "finite_missing_ranks": None,
        "critical_pair_exists": None,
        "hard_rank_at_least_two": None,
    }

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs = pairs_for(n, spf)
        if any(member[a] and member[b] for a, b in pairs):
            member[n] = 1
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not member[q]:
                    target_records.append({"child": n, "parent": q, "rank": rank[q]})
            continue

        if not pairs:
            rank[n] = 0
            splitless[n] = 1
            pair_blockers: list[tuple[tuple[int, int], int]] = []
        else:
            pair_blockers = []
            for a, b in pairs:
                missing_ranks = [rank[x] for x in (a, b) if not member[x]]
                recurrence_failures["finite_missing_ranks"] = first_failure(
                    recurrence_failures["finite_missing_ranks"],
                    bool(missing_ranks) and INF not in missing_ranks,
                    {"n": n, "pair": [a, b], "missing_ranks": missing_ranks},
                )
                if not missing_ranks or INF in missing_ranks:
                    raise AssertionError((n, a, b, missing_ranks))
                pair_blockers.append(((a, b), min(missing_ranks)))
            rank[n] = 1 + max(blocker for _, blocker in pair_blockers)

        if not hard_shape(n, pairs):
            continue

        r = rank[n]
        critical_pairs = [pair for pair, blocker in pair_blockers if blocker == r - 1]
        recurrence_failures["critical_pair_exists"] = first_failure(
            recurrence_failures["critical_pair_exists"],
            bool(critical_pairs),
            {"source": n, "rank": r, "pairs": pairs},
        )
        recurrence_failures["hard_rank_at_least_two"] = first_failure(
            recurrence_failures["hard_rank_at_least_two"],
            r >= 2,
            {"source": n, "rank": r, "pairs": pairs},
        )
        critical_endpoints = sorted({
            x
            for a, b in critical_pairs
            for x in (a, b)
            if not member[x] and rank[x] == r - 1
        })
        missing_endpoints = sorted({
            x for a, b in pairs for x in (a, b) if not member[x]
        })
        hard_records.append({
            "source": n,
            "rank": r,
            "pairs": pairs,
            "critical_pairs": critical_pairs,
            "critical_endpoints": critical_endpoints,
            "missing_endpoints": missing_endpoints,
        })

    root_cache: dict[int, int] = {}

    def structural_root(n: int) -> int:
        path = []
        while n not in root_cache:
            path.append(n)
            parent = structural_parent(n)
            if parent is None:
                root_cache[n] = n
                break
            p, _ = parent
            if member[p] or rank[p] >= rank[n]:
                raise AssertionError(("bad structural edge", n, p, rank[n], rank[p]))
            n = p
        root = root_cache[n]
        for item in path:
            root_cache[item] = root
        return root

    targets_by_root: dict[int, list[dict]] = defaultdict(list)
    for target in target_records:
        target["root"] = structural_root(target["parent"])
        targets_by_root[target["root"]].append(target)

    hard_by_value = {record["source"]: record for record in hard_records}
    pullback_failure = None
    root_class_failure = None
    critical_t3_coordinate_failure = None
    critical_t3_exact_rank_failure = None
    critical_t2_or_t3_exact_rank_failure = None
    maximum_critical_child_rank_jump = None
    component_boundary_failure = None
    component_any_boundary_failure = None
    component_boundary_rank_only_failure = None
    boundary_or_hard_descent_failure = None
    adjacent_target_failure = None
    adjacent_rank_drop_failure = None
    first_critical_examples = []
    critical_root_load = Counter()

    for record in hard_records:
        source = record["source"]
        source_rank = record["rank"]
        critical_roots = set()
        pullbacks = []
        for endpoint in record["critical_endpoints"]:
            predecessor = (endpoint + 1) // 2
            root = structural_root(predecessor)
            t2_child = 2 * endpoint - 1
            t3_child = 3 * endpoint - 1
            t2_outcome = {
                "child": t2_child,
                "member": bool(member[t2_child]),
                "rank": None if member[t2_child] else rank[t2_child],
            }
            t3_outcome = {
                "child": t3_child,
                "member": bool(member[t3_child]),
                "rank": None if member[t3_child] else rank[t3_child],
            }
            critical_roots.add(root)
            pullback = {
                "endpoint": endpoint,
                "endpoint_rank": rank[endpoint],
                "predecessor": predecessor,
                "predecessor_rank": rank[predecessor],
                "root": root,
                "root_rank": rank[root],
                "root_kind": "splitless" if splitless[root] else "hard",
                "T2": t2_outcome,
                "T3": t3_outcome,
            }
            pullbacks.append(pullback)
            pullback_failure = first_failure(
                pullback_failure,
                endpoint % 2 == 1
                and allowed(predecessor)
                and not member[predecessor]
                and rank[predecessor] <= source_rank - 2,
                {"source": source, "source_rank": source_rank, **pullback},
            )
            root_class_failure = first_failure(
                root_class_failure,
                bool(splitless[root]) or root in hard_by_value,
                {"source": source, "source_rank": source_rank, **pullback},
            )
            critical_t3_coordinate_failure = first_failure(
                critical_t3_coordinate_failure,
                t3_child < source,
                {"source": source, "source_rank": source_rank, **pullback},
            )
            t3_exact = bool(member[t3_child]) or rank[t3_child] == source_rank
            t2_exact = bool(member[t2_child]) or rank[t2_child] == source_rank
            critical_t3_exact_rank_failure = first_failure(
                critical_t3_exact_rank_failure,
                t3_exact,
                {"source": source, "source_rank": source_rank, **pullback},
            )
            critical_t2_or_t3_exact_rank_failure = first_failure(
                critical_t2_or_t3_exact_rank_failure,
                t2_exact or t3_exact,
                {"source": source, "source_rank": source_rank, **pullback},
            )
            for child_kind, outcome in (("T2", t2_outcome), ("T3", t3_outcome)):
                if outcome["rank"] is None:
                    continue
                jump = outcome["rank"] - source_rank
                if (
                    maximum_critical_child_rank_jump is None
                    or jump > maximum_critical_child_rank_jump["jump"]
                ):
                    maximum_critical_child_rank_jump = {
                        "source": source,
                        "source_rank": source_rank,
                        "endpoint": endpoint,
                        "child_kind": child_kind,
                        "child": outcome["child"],
                        "child_rank": outcome["rank"],
                        "jump": jump,
                    }
            critical_root_load[root] += 1

        compatible_boundaries = sorted(
            (
                target
                for root in critical_roots
                for target in targets_by_root[root]
                if target["child"] < source and target["rank"] <= source_rank
            ),
            key=lambda target: target["child"],
        )
        arrived_boundaries = sorted(
            (
                target
                for root in critical_roots
                for target in targets_by_root[root]
                if target["child"] < source
            ),
            key=lambda target: target["child"],
        )
        lower_hard_roots = sorted(
            root for root in critical_roots
            if root in hard_by_value and rank[root] < source_rank
        )
        component_boundary_failure = first_failure(
            component_boundary_failure,
            bool(compatible_boundaries),
            {
                "source": source,
                "source_rank": source_rank,
                "critical_roots": sorted(critical_roots),
                "pullbacks": pullbacks,
            },
        )
        component_any_boundary_failure = first_failure(
            component_any_boundary_failure,
            bool(arrived_boundaries),
            {
                "source": source,
                "source_rank": source_rank,
                "critical_roots": sorted(critical_roots),
                "pullbacks": pullbacks,
            },
        )
        if arrived_boundaries and not compatible_boundaries:
            component_boundary_rank_only_failure = (
                component_boundary_rank_only_failure
                or {
                    "source": source,
                    "source_rank": source_rank,
                    "critical_roots": sorted(critical_roots),
                    "arrived_boundaries": arrived_boundaries[:20],
                    "pullbacks": pullbacks,
                }
            )
        boundary_or_hard_descent_failure = first_failure(
            boundary_or_hard_descent_failure,
            bool(compatible_boundaries or lower_hard_roots),
            {
                "source": source,
                "source_rank": source_rank,
                "critical_roots": sorted(critical_roots),
                "pullbacks": pullbacks,
            },
        )

        if len(first_critical_examples) < 20:
            first_critical_examples.append({
                "source": source,
                "source_rank": source_rank,
                "pullbacks": pullbacks,
                "arrived_component_boundaries": compatible_boundaries[:10],
                "arrived_component_boundaries_ignoring_rank": arrived_boundaries[:10],
                "lower_hard_roots": lower_hard_roots,
            })

        adjacent = source - 1 if source % 3 == 0 else source + 1
        if adjacent <= limit:
            adjacent_parent = (adjacent + 1) // 2
            is_target = bool(
                member[adjacent]
                and not member[adjacent_parent]
                and rank[adjacent_parent] <= source_rank
            )
            adjacent_target_failure = first_failure(
                adjacent_target_failure,
                is_target,
                {
                    "source": source,
                    "source_rank": source_rank,
                    "adjacent": adjacent,
                    "side": "left" if adjacent < source else "right",
                    "adjacent_member": bool(member[adjacent]),
                    "parent": adjacent_parent,
                    "parent_member": bool(member[adjacent_parent]),
                    "parent_rank": None if member[adjacent_parent] else rank[adjacent_parent],
                },
            )
            if not member[adjacent]:
                adjacent_rank_drop_failure = first_failure(
                    adjacent_rank_drop_failure,
                    rank[adjacent_parent] <= source_rank - 2,
                    {
                        "source": source,
                        "source_rank": source_rank,
                        "adjacent_hole": adjacent,
                        "adjacent_rank": rank[adjacent],
                        "parent": adjacent_parent,
                        "parent_rank": rank[adjacent_parent],
                    },
                )

    max_rank = max(
        [0]
        + [record["rank"] for record in hard_records]
        + [record["rank"] for record in target_records]
    )
    hard_counts = [0] * (max_rank + 1)
    target_counts = [0] * (max_rank + 1)
    events = [
        (record["source"], "hard", record["rank"], record)
        for record in hard_records
    ] + [
        (record["child"], "target", record["rank"], record)
        for record in target_records
    ]
    events.sort(key=lambda event: event[0])
    first_strict_violation = None
    first_additive_one_violation = None
    tight_events = []
    maximum_excess_by_rank = [-10**18] * (max_rank + 1)
    maximum_excess_event_by_rank: list[dict | None] = [None] * (max_rank + 1)
    rank_descent_failure = None
    two_rank_descent_failure = None
    event_residue_failure = None

    for coordinate, kind, event_rank, record in events:
        before = []
        hard_prefix = target_prefix = 0
        after = []
        for d in range(max_rank + 1):
            hard_prefix += hard_counts[d]
            target_prefix += target_counts[d]
            before.append(hard_prefix - target_prefix)

        if kind == "hard":
            hard_counts[event_rank] += 1
        else:
            target_counts[event_rank] += 1

        hard_prefix = target_prefix = 0
        for d in range(max_rank + 1):
            hard_prefix += hard_counts[d]
            target_prefix += target_counts[d]
            excess = hard_prefix - target_prefix
            after.append(excess)
            payload = {
                "X": coordinate,
                "d": d,
                "kind": kind,
                "event_rank": event_rank,
                "before_excess": before[d],
                "after_excess": excess,
                "H": hard_prefix,
                "Q": target_prefix,
            }
            if first_strict_violation is None and excess > 0:
                first_strict_violation = payload
            if first_additive_one_violation is None and excess > 1:
                first_additive_one_violation = payload
            if excess > maximum_excess_by_rank[d]:
                maximum_excess_by_rank[d] = excess
                maximum_excess_event_by_rank[d] = payload
            if kind == "hard" and excess == 1 and len(tight_events) < 50:
                tight_events.append(payload)
        if kind == "hard":
            event_residue_failure = first_failure(
                event_residue_failure,
                coordinate % 6 in (0, 2),
                {"X": coordinate, "kind": kind, "rank": event_rank},
            )
        else:
            event_residue_failure = first_failure(
                event_residue_failure,
                coordinate % 6 in (3, 5),
                {"X": coordinate, "kind": kind, "rank": event_rank},
            )
        for d in range(3, max_rank + 1):
            if after[d] > 0 and after[d - 1] < after[d] and rank_descent_failure is None:
                rank_descent_failure = {
                    "X": coordinate,
                    "d": d,
                    "B_d": after[d],
                    "B_d_minus_1": after[d - 1],
                    "kind": kind,
                    "event_rank": event_rank,
                }
            if after[d] > 1 and after[d - 2] <= 1 and two_rank_descent_failure is None:
                two_rank_descent_failure = {
                    "X": coordinate,
                    "d": d,
                    "B_d": after[d],
                    "B_d_minus_2": after[d - 2],
                    "kind": kind,
                    "event_rank": event_rank,
                }

    normalization = None
    if first_additive_one_violation is not None:
        row = first_additive_one_violation
        normalization = {
            "is_hard_even_event": row["kind"] == "hard" and row["X"] % 2 == 0,
            "event_rank_at_most_d": row["event_rank"] <= row["d"],
            "before_excess_is_one": row["before_excess"] == 1,
            "after_excess_is_two": row["after_excess"] == 2,
        }

    order_statistic = []
    for d in range(max_rank + 1):
        hard_coordinates = [
            record["source"] for record in hard_records if record["rank"] <= d
        ]
        target_coordinates = [
            record["child"] for record in target_records if record["rank"] <= d
        ]
        minimum_margin = None
        minimum_pair = None
        first_failure_pair = None
        for index in range(1, len(hard_coordinates)):
            if index - 1 >= len(target_coordinates):
                first_failure_pair = {
                    "hard_index": index + 1,
                    "hard": hard_coordinates[index],
                    "target_index": index,
                    "target": None,
                }
                break
            margin = hard_coordinates[index] - target_coordinates[index - 1]
            if minimum_margin is None or margin < minimum_margin:
                minimum_margin = margin
                minimum_pair = {
                    "hard_index": index + 1,
                    "hard": hard_coordinates[index],
                    "target_index": index,
                    "target": target_coordinates[index - 1],
                }
            if margin <= 0 and first_failure_pair is None:
                first_failure_pair = {
                    "hard_index": index + 1,
                    "hard": hard_coordinates[index],
                    "target_index": index,
                    "target": target_coordinates[index - 1],
                    "margin": margin,
                }
                break
        order_statistic.append({
            "d": d,
            "hard_count": len(hard_coordinates),
            "target_count": len(target_coordinates),
            "minimum_margin": minimum_margin,
            "minimum_pair": minimum_pair,
            "first_failure": first_failure_pair,
        })

    return {
        "schema_version": 1,
        "limit": limit,
        "hard_count": len(hard_records),
        "target_count": len(target_records),
        "maximum_rank": max_rank,
        "rank_histogram_hard": dict(sorted(Counter(
            record["rank"] for record in hard_records
        ).items())),
        "rank_histogram_target": dict(sorted(Counter(
            record["rank"] for record in target_records
        ).items())),
        "recurrence_failures": recurrence_failures,
        "minimal_counterexample_normalization": {
            "first_strict_violation": first_strict_violation,
            "first_additive_one_violation": first_additive_one_violation,
            "normalization_if_present": normalization,
            "tight_hard_event_prefix": tight_events,
            "event_residue_first_failure": event_residue_failure,
            "maximum_excess_by_rank": [
                {
                    "d": d,
                    "maximum_excess": maximum_excess_by_rank[d],
                    "event": maximum_excess_event_by_rank[d],
                }
                for d in range(max_rank + 1)
            ],
            "positive_excess_descends_one_rank_first_failure": rank_descent_failure,
            "additive_one_failure_descends_two_ranks_first_failure": (
                two_rank_descent_failure
            ),
        },
        "critical_pullback": {
            "claim": (
                "a critical missing endpoint q of a rank-r hard source has "
                "missing predecessor (q+1)/2 of rank at most r-2"
            ),
            "first_failure": pullback_failure,
            "root_class_first_failure": root_class_failure,
            "T3_child_below_source_first_failure": critical_t3_coordinate_failure,
            "T3_generated_or_exact_source_rank_first_failure": (
                critical_t3_exact_rank_failure
            ),
            "T2_or_T3_generated_or_exact_source_rank_first_failure": (
                critical_t2_or_t3_exact_rank_failure
            ),
            "maximum_critical_child_rank_jump": maximum_critical_child_rank_jump,
            "examples": first_critical_examples,
            "largest_root_loads": [
                {"root": root, "critical_endpoint_occurrences": count}
                for root, count in critical_root_load.most_common(20)
            ],
        },
        "candidate_descent_falsifiers": {
            "critical_component_has_arrived_boundary": component_boundary_failure,
            "critical_component_has_any_arrived_boundary": component_any_boundary_failure,
            "first_arrived_component_boundary_blocked_only_by_rank": (
                component_boundary_rank_only_failure
            ),
            "critical_component_has_arrived_boundary_or_lower_hard_root": (
                boundary_or_hard_descent_failure
            ),
            "allowed_adjacent_odd_is_compatible_target": adjacent_target_failure,
            "adjacent_hole_parent_drops_two_ranks": adjacent_rank_drop_failure,
        },
        "order_statistic_form": order_statistic,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 100:
        raise ValueError("limit must be at least 100")
    result = audit(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": result["limit"],
        "hard_count": result["hard_count"],
        "target_count": result["target_count"],
        "maximum_rank": result["maximum_rank"],
        "recurrence_failures": result["recurrence_failures"],
        "normalization": result["minimal_counterexample_normalization"],
        "pullback_failure": result["critical_pullback"]["first_failure"],
        "candidate_descent_falsifiers": result["candidate_descent_falsifiers"],
    }, indent=2))


if __name__ == "__main__":
    main()
