#!/usr/bin/env python3
"""Exact image-capacity probes for Problem 424, task C51.

The distinct-input rule is enforced by retaining only factor pairs a < b.
Descending stage d means T = S_{d+1}; exactly the holes of obstruction
rank at most d are absent from T.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from array import array
from bisect import bisect_right
from collections import Counter, defaultdict


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def spf_sieve(limit: int) -> array:
    spf = array("I", range(limit + 2))
    for p in range(2, int((limit + 1) ** 0.5) + 1):
        if spf[p] != p:
            continue
        for m in range(p * p, limit + 2, p):
            if spf[m] == m:
                spf[m] = p
    return spf


def divisors(n: int, spf: array) -> list[int]:
    result = [1]
    while n > 1:
        p = spf[n]
        old = len(result)
        power = 1
        while n % p == 0:
            n //= p
            power *= p
            for i in range(old):
                result.append(result[i] * power)
    return result


def factor_pairs(n: int, spf: array) -> list[tuple[int, int]]:
    product = n + 1
    result = []
    for a in divisors(product, spf):
        if a < 2:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            result.append((a, b))
    result.sort()
    return result


def easy_seed3(n: int) -> bool:
    if n % 2 or (n + 1) % 3:
        return False
    parent = (n + 1) // 3
    return parent != 3 and allowed(parent)


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    return n % 2 == 0 and bool(pairs) and not easy_seed3(n)


def build_census(limit: int, spf: array) -> dict:
    member = bytearray(limit + 1)
    rank = array("h", [-2]) * (limit + 1)
    component = array("I", [0]) * (limit + 1)
    seed2_root = array("I", [0]) * (limit + 1)
    splitless = bytearray(limit + 1)
    hard_pairs: dict[int, list[tuple[int, int]]] = {}
    terminal_targets: list[dict] = []
    exit_ordinal: dict[int, int] = defaultdict(int)

    member[2] = member[3] = 1
    rank[2] = rank[3] = -1

    for n in range(2, limit + 1):
        if not allowed(n):
            continue
        seed2_root[n] = n if n % 2 == 0 else seed2_root[(n + 1) // 2]
        if n in (2, 3):
            continue

        pairs = factor_pairs(n, spf)
        generated = any(member[a] and member[b] for a, b in pairs)
        if generated:
            member[n] = 1
            rank[n] = -1
            if n % 2:
                parent = (n + 1) // 2
                if not member[parent]:
                    root = component[parent]
                    if root == 0:
                        raise AssertionError((n, parent, "terminal root"))
                    exit_ordinal[root] += 1
                    terminal_targets.append(
                        {
                            "child": n,
                            "parent": parent,
                            "rank": rank[parent],
                            "component": root,
                            "ordinal": exit_ordinal[root],
                        }
                    )
            continue

        if not pairs:
            rank[n] = 0
            component[n] = n
            splitless[n] = 1
        else:
            scores = []
            for a, b in pairs:
                blockers = [rank[x] for x in (a, b) if not member[x]]
                if not blockers or min(blockers) < 0:
                    raise AssertionError((n, a, b, blockers))
                scores.append(min(blockers))
            rank[n] = 1 + max(scores)

            parent = None
            if n % 2:
                parent = (n + 1) // 2
            elif easy_seed3(n):
                parent = (n + 1) // 3
            if parent is None:
                component[n] = n
            else:
                if member[parent] or component[parent] == 0:
                    raise AssertionError((n, parent, "canonical parent"))
                component[n] = component[parent]

        if hard_shape(n, pairs):
            hard_pairs[n] = pairs

    maximum_rank = max(rank)
    return {
        "member": member,
        "rank": rank,
        "component": component,
        "seed2_root": seed2_root,
        "splitless": splitless,
        "hard_pairs": hard_pairs,
        "terminal_targets": terminal_targets,
        "maximum_rank": maximum_rank,
    }


def literal_stage_check(
    literal_limit: int,
    spf: array,
    member: bytearray,
    rank: array,
) -> dict:
    values = [n for n in range(2, literal_limit + 1) if allowed(n)]
    pairs = {n: factor_pairs(n, spf) for n in values}
    current = bytearray(literal_limit + 1)
    for n in values:
        current[n] = 1

    checks = 0
    stages = []
    t = 0
    while True:
        following = bytearray(literal_limit + 1)
        following[2] = following[3] = 1
        for n in values:
            if n in (2, 3):
                continue
            following[n] = any(current[a] and current[b] for a, b in pairs[n])
        t += 1
        mismatches = []
        for n in values:
            expected = bool(member[n]) or rank[n] >= t
            checks += 1
            if bool(following[n]) != expected:
                mismatches.append(n)
                if len(mismatches) == 20:
                    break
        stages.append(
            {
                "stage": t,
                "members": sum(following),
                "mismatch_prefix": mismatches,
            }
        )
        if mismatches:
            raise AssertionError((t, mismatches))
        if following == current:
            break
        current = following
    return {
        "limit": literal_limit,
        "transitions_to_fixpoint": t,
        "membership_checks": checks,
        "stages": stages,
    }


def prefix_audit(demands: list[int], targets: list[int]) -> dict:
    targets = sorted(targets)
    q = 0
    maximum = -10**9
    maximum_event = None
    first_plus_one = None
    for h_count, h in enumerate(demands, 1):
        q = bisect_right(targets, h)
        excess = h_count - q
        if excess > maximum:
            maximum = excess
            maximum_event = {"X": h, "H": h_count, "Q": q, "excess": excess}
        if excess > 1 and first_plus_one is None:
            first_plus_one = {"X": h, "H": h_count, "Q": q, "excess": excess}
    return {
        "demands": len(demands),
        "targets": len(targets),
        "maximum_excess": maximum,
        "maximum_event": maximum_event,
        "first_plus_one_failure": first_plus_one,
    }


def stage_boundaries(limit: int, d: int, census: dict) -> list[dict]:
    member = census["member"]
    rank = census["rank"]
    component = census["component"]
    seed2_root = census["seed2_root"]
    result = []
    seen_chains = set()
    for parent in range(2, (limit + 1) // 2 + 1):
        if not allowed(parent) or member[parent] or rank[parent] > d:
            continue
        child = 2 * parent - 1
        if member[child] or rank[child] > d:
            chain = seed2_root[parent]
            if chain in seen_chains:
                raise AssertionError((d, chain, child, "two stage boundaries"))
            seen_chains.add(chain)
            result.append(
                {
                    "child": child,
                    "parent": parent,
                    "parent_rank": rank[parent],
                    "child_rank": -1 if member[child] else rank[child],
                    "component": component[parent],
                    "chain": chain,
                }
            )
    return result


def compact_set(values: list[int]) -> dict:
    raw = ",".join(map(str, values)).encode("ascii")
    return {
        "count": len(values),
        "prefix": values[:30],
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def endpoint_set(
    h: int,
    d: int,
    critical_only: bool,
    hard_pairs: dict[int, list[tuple[int, int]]],
    member: bytearray,
    rank: array,
) -> set[int]:
    result = set()
    h_rank = rank[h]
    for a, b in hard_pairs[h]:
        blockers = [x for x in (a, b) if not member[x] and rank[x] <= d]
        if not blockers:
            raise AssertionError((h, d, a, b, "no stage blocker"))
        if critical_only:
            actual_blockers = [x for x in (a, b) if not member[x]]
            score = min(rank[x] for x in actual_blockers)
            if score != h_rank - 1:
                continue
            blockers = [x for x in blockers if rank[x] == h_rank - 1]
        result.update(blockers)
    return result


def matching_failure(
    demands: list[int],
    targets: list[dict],
    candidate_builder,
) -> dict | None:
    match_right = [-1] * len(targets)
    edges: list[list[int]] = []

    for source_index, h in enumerate(demands):
        candidate_indexes = sorted(set(candidate_builder(h)))
        edges.append(candidate_indexes)
        seen_left: set[int] = set()
        seen_right: set[int] = set()

        def augment(left: int) -> bool:
            if left in seen_left:
                return False
            seen_left.add(left)
            for right in edges[left]:
                if right in seen_right:
                    continue
                seen_right.add(right)
                old = match_right[right]
                if old < 0 or augment(old):
                    match_right[right] = left
                    return True
            return False

        if not augment(source_index):
            left_values = sorted(demands[i] for i in seen_left)
            right_values = sorted(targets[i]["child"] for i in seen_right)
            if len(left_values) <= len(right_values):
                raise AssertionError((h, left_values, right_values, "bad Hall witness"))
            return {
                "X": h,
                "source_rank": None,
                "source_candidates": [targets[i]["child"] for i in candidate_indexes],
                "hall_left": compact_set(left_values),
                "hall_right": compact_set(right_values),
                "defect": len(left_values) - len(right_values),
            }
    return None


def local_rule_audit(limit: int, d: int, boundaries: list[dict], census: dict) -> dict:
    member = census["member"]
    rank = census["rank"]
    component = census["component"]
    seed2_root = census["seed2_root"]
    hard_pairs = census["hard_pairs"]
    demands = sorted(h for h in hard_pairs if rank[h] <= d)

    targets = sorted(boundaries, key=lambda row: row["child"])
    target_index = {row["child"]: i for i, row in enumerate(targets)}
    by_chain = {row["chain"]: target_index[row["child"]] for row in targets}
    by_component: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for i, row in enumerate(targets):
        by_component[row["component"]].append((row["child"], i))

    def candidates(h: int, critical_only: bool, use_component: bool) -> list[int]:
        endpoints = endpoint_set(
            h, d, critical_only, hard_pairs, member, rank
        )
        result = []
        if use_component:
            for root in {component[p] for p in endpoints}:
                rows = by_component.get(root, [])
                stop = bisect_right(rows, (h, len(targets)))
                result.extend(index for _, index in rows[:stop])
        else:
            for p in endpoints:
                index = by_chain.get(seed2_root[p])
                if index is not None and targets[index]["child"] <= h:
                    result.append(index)
        return result

    result = {}
    for critical_only, use_component, name in (
        (True, False, "critical_factor_chain"),
        (False, False, "all_factor_chains"),
        (True, True, "critical_factor_components"),
        (False, True, "all_factor_components"),
    ):
        failure = matching_failure(
            demands,
            targets,
            lambda h, c=critical_only, u=use_component: candidates(h, c, u),
        )
        if failure is not None:
            failure["source_rank"] = rank[failure["X"]]
            failure["source_pairs"] = hard_pairs[failure["X"]]
        result[name] = {
            "matched_all": failure is None,
            "first_failure": failure,
        }
    return result


def birth_rule_audit(census: dict) -> dict:
    member = census["member"]
    rank = census["rank"]
    seed2_root = census["seed2_root"]
    hard_pairs = census["hard_pairs"]
    violations = []
    checks = 0
    endpoint_multiplicity: Counter[tuple[int, int]] = Counter()
    endpoint_sources: dict[tuple[int, int], set[int]] = defaultdict(set)

    for h, pairs in sorted(hard_pairs.items()):
        r = rank[h]
        candidates = set()
        critical = []
        for a, b in pairs:
            blockers = [x for x in (a, b) if not member[x]]
            score = min(rank[x] for x in blockers)
            if score != r - 1:
                continue
            for p in blockers:
                if rank[p] != r - 1:
                    continue
                critical.append(p)
                checks += 1
                first = 2 * p - 1
                if member[first] or rank[first] > r:
                    boundary = first
                else:
                    second = 2 * first - 1
                    boundary = second if member[second] or rank[second] > r else None
                if boundary is None or boundary > h:
                    violations.append(
                        {
                            "hard": h,
                            "rank": r,
                            "critical": p,
                            "boundary": boundary,
                        }
                    )
                else:
                    candidates.add(boundary)
                    endpoint_multiplicity[(r, boundary)] += 1
                    endpoint_sources[(r, boundary)].add(h)
        if not critical or not candidates:
            violations.append(
                {"hard": h, "rank": r, "critical": critical, "candidates": sorted(candidates)}
            )
    worst = endpoint_multiplicity.most_common(10)
    worst_sources = sorted(
        endpoint_sources.items(), key=lambda item: (-len(item[1]), item[0])
    )[:10]
    return {
        "critical_endpoint_checks": checks,
        "violations": violations[:20],
        "maximum_raw_collision": 0 if not worst else worst[0][1],
        "largest_collision_keys": [
            {"rank": key[0], "boundary": key[1], "uses": count}
            for key, count in worst
        ],
        "largest_distinct_source_collisions": [
            {
                "rank": key[0],
                "boundary": key[1],
                "sources": len(sources),
                "source_prefix": sorted(sources)[:20],
                "maximum_source": max(sources),
            }
            for key, sources in worst_sources
        ],
    }


def run(limit: int, literal_limit: int) -> dict:
    spf = spf_sieve(limit + 1)
    census = build_census(limit, spf)
    member = census["member"]
    rank = census["rank"]
    component = census["component"]
    splitless = census["splitless"]
    hard_pairs = census["hard_pairs"]
    terminal_targets = census["terminal_targets"]

    literal = literal_stage_check(
        min(limit, literal_limit), spf, member, rank
    )
    stage_results = []
    first_local_failures: dict[str, dict] = {}

    for d in range(census["maximum_rank"] + 1):
        demands = sorted(h for h in hard_pairs if rank[h] <= d)
        boundaries = stage_boundaries(limit, d, census)

        by_component: dict[int, list[dict]] = defaultdict(list)
        for row in boundaries:
            by_component[row["component"]].append(row)
        cap2 = []
        splitless_only = []
        for root, rows in by_component.items():
            rows.sort(key=lambda row: row["child"])
            cap2.extend(row["child"] for row in rows[:2])
            if splitless[root]:
                splitless_only.extend(row["child"] for row in rows)

        full_prefix = prefix_audit(demands, [row["child"] for row in boundaries])
        cap2_prefix = prefix_audit(demands, cap2)
        splitless_prefix = prefix_audit(demands, splitless_only)

        terminal_cap2 = [
            row["child"]
            for row in terminal_targets
            if row["rank"] <= d and row["ordinal"] <= 2
        ]
        terminal_prefix = prefix_audit(demands, terminal_cap2)

        local = local_rule_audit(limit, d, boundaries, census)
        for name, row in local.items():
            if not row["matched_all"] and name not in first_local_failures:
                first_local_failures[name] = {"stage_rank": d, **row["first_failure"]}

        stage_results.append(
            {
                "rank": d,
                "hard": len(demands),
                "boundaries": len(boundaries),
                "components_with_boundaries": len(by_component),
                "full_image_prefix": full_prefix,
                "first_two_active_per_component": cap2_prefix,
                "splitless_component_boundaries": splitless_prefix,
                "C43_terminal_first_two": terminal_prefix,
                "local_rules": local,
            }
        )

    assertions = {
        "literal_stages_match_recursive_ranks": all(
            not row["mismatch_prefix"] for row in literal["stages"]
        ),
        "full_image_strict": all(
            row["full_image_prefix"]["maximum_excess"] <= 0
            for row in stage_results
        ),
        "first_two_active_strict": all(
            row["first_two_active_per_component"]["maximum_excess"] <= 0
            for row in stage_results
        ),
        "C43_terminal_first_two_additive_one": all(
            row["C43_terminal_first_two"]["first_plus_one_failure"] is None
            for row in stage_results
        ),
    }
    if not all(assertions.values()):
        raise AssertionError(assertions)

    return {
        "schema_version": 1,
        "limit": limit,
        "distinct_input_rule": "all witnesses satisfy 2 <= a < b and ab=n+1",
        "stage_convention": "rank d is T=S_(d+1); holes have obstruction rank <=d",
        "generated": sum(member),
        "holes": sum(1 for n in range(2, limit + 1) if allowed(n) and not member[n]),
        "hard_holes": len(hard_pairs),
        "terminal_targets": len(terminal_targets),
        "maximum_rank": census["maximum_rank"],
        "rank_histogram_hard": dict(sorted(Counter(rank[h] for h in hard_pairs).items())),
        "literal_descending_approximants": literal,
        "birth_rule": birth_rule_audit(census),
        "first_local_failures": first_local_failures,
        "stages": stage_results,
        "assertions": assertions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--literal-limit", type=int, default=20_000)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    if args.limit < 1000:
        raise ValueError("limit must be at least 1000")
    if args.literal_limit < 100:
        raise ValueError("literal-limit must be at least 100")
    result = run(args.limit, args.literal_limit)
    if args.summary:
        result = {
            "schema_version": result["schema_version"],
            "limit": result["limit"],
            "distinct_input_rule": result["distinct_input_rule"],
            "stage_convention": result["stage_convention"],
            "generated": result["generated"],
            "holes": result["holes"],
            "hard_holes": result["hard_holes"],
            "terminal_targets": result["terminal_targets"],
            "maximum_rank": result["maximum_rank"],
            "rank_histogram_hard": result["rank_histogram_hard"],
            "literal_descending_approximants": result[
                "literal_descending_approximants"
            ],
            "birth_rule": result["birth_rule"],
            "first_local_failures": result["first_local_failures"],
            "stage_summary": [
                {
                    "rank": row["rank"],
                    "hard": row["hard"],
                    "boundaries": row["boundaries"],
                    "full_max": row["full_image_prefix"]["maximum_event"],
                    "active_cap2_max": row["first_two_active_per_component"][
                        "maximum_event"
                    ],
                    "splitless_first_failure": row[
                        "splitless_component_boundaries"
                    ]["first_plus_one_failure"],
                    "C43_cap2_max": row["C43_terminal_first_two"][
                        "maximum_event"
                    ],
                }
                for row in result["stages"]
            ],
            "assertions": result["assertions"],
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
