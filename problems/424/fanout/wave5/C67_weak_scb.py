#!/usr/bin/env python3
"""Exact max-closure probes for weak C60 cut inequalities.

The feasible source-side sets contain every structural splitless root and are
closed under both C60 unary descents and reverse seed-2 edges.  The latter is
the extra condition satisfied by Boolean forward-closed sets: membership on
each missing seed-2 chain is an initial segment.

All optimization is an integral s-t min cut.  Floating point is not used for
acceptance.
"""

from __future__ import annotations

import argparse
import json
from array import array
from collections import deque
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def smallest_prime_factors(limit: int) -> array:
    spf = array("I", range(limit + 1))
    if limit >= 1:
        spf[1] = 1
    p = 2
    while p * p <= limit:
        if spf[p] == p:
            start = p * p
            for n in range(start, limit + 1, p):
                if spf[n] == n:
                    spf[n] = p
        p += 1
    return spf


def divisors_from_spf(n: int, spf: array) -> list[int]:
    factors: list[tuple[int, int]] = []
    while n > 1:
        p = int(spf[n])
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        factors.append((p, exponent))
    divisors = [1]
    for p, exponent in factors:
        old = divisors
        divisors = []
        power = 1
        for _ in range(exponent + 1):
            divisors.extend(d * power for d in old)
            power *= p
    return divisors


def admissible_pairs(n: int, spf: array) -> list[tuple[int, int]]:
    total = n + 1
    out: list[tuple[int, int]] = []
    for a in divisors_from_spf(total, spf):
        if a < 2 or a * a >= total or total % a:
            continue
        b = total // a
        if allowed(a) and allowed(b):
            out.append((a, b))
    out.sort()
    return out


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    parent = (n + 1) // 3
    return not (allowed(parent) and parent != 3)


def build_arithmetic(limit: int) -> dict:
    spf = smallest_prime_factors(limit + 1)
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pair_map = {n: admissible_pairs(n, spf) for n in values}
    generated: set[int] = set()
    for n in values:
        if n in (2, 3) or any(a in generated and b in generated for a, b in pair_map[n]):
            generated.add(n)
    holes = set(values) - generated
    splitless = {n for n in holes if not pair_map[n]}
    hard = {n for n in holes if hard_shape(n, pair_map[n])}

    root_of: dict[int, int] = {}
    terminal_of_root: dict[int, int] = {}
    for n in sorted(holes):
        if n % 2 == 0:
            root_of[n] = n
        else:
            parent = (n + 1) // 2
            if parent not in holes:
                raise AssertionError(("odd hole has nonhole parent", n, parent))
            root_of[n] = root_of[parent]
        terminal_of_root[root_of[n]] = n

    roots = set(terminal_of_root)
    top_of_root: dict[int, int] = {}
    for root in roots:
        top = root
        while 2 * top - 1 <= limit:
            top = 2 * top - 1
        top_of_root[root] = top
    if hard - roots or splitless - roots:
        raise AssertionError("hard and splitless holes must be even chain roots")
    seed3_roots = roots - hard - splitless
    return {
        "values": values,
        "pairs": pair_map,
        "generated": generated,
        "holes": holes,
        "hard": hard,
        "splitless": splitless,
        "seed3_roots": seed3_roots,
        "root_of": root_of,
        "terminal_of_root": terminal_of_root,
        "top_of_root": top_of_root,
    }


def max_closure(
    limit: int,
    data: dict,
    positive: dict[int, int] | set[int],
    negative: dict[int, int] | set[int],
) -> tuple[int, set[int]]:
    """Maximize the supplied positive minus negative vertex weights."""
    if isinstance(positive, set):
        positive = {v: 1 for v in positive}
    if isinstance(negative, set):
        negative = {v: 1 for v in negative}
    holes: set[int] = data["holes"]
    generated: set[int] = data["generated"]
    splitless: set[int] = data["splitless"]
    pair_map: dict[int, list[tuple[int, int]]] = data["pairs"]
    source, sink = limit + 1, limit + 2
    finite = sum(positive.values()) + sum(negative.values())
    infinity = finite + 1
    caps: dict[tuple[int, int], int] = {}

    def add(u: int, v: int, cap: int) -> None:
        caps[u, v] = caps.get((u, v), 0) + cap

    for v, weight in positive.items():
        add(source, v, weight)
    for v, weight in negative.items():
        add(v, sink, weight)
    for root in splitless:
        add(source, root, infinity)

    # C60 unary closure: n in S forces each hole cofactor of a generated factor.
    for n in holes:
        for a, b in pair_map[n]:
            if (a in generated) != (b in generated):
                add(n, b if a in generated else a, infinity)

    # Boolean forward closure makes a hole-chain source side a prefix:
    # child in S forces parent in S.
    for parent in holes:
        child = 2 * parent - 1
        if child <= limit and child in holes:
            add(child, parent, infinity)

    rows = np.fromiter((u for u, _ in caps), dtype=np.int64)
    cols = np.fromiter((v for _, v in caps), dtype=np.int64)
    vals = np.fromiter(caps.values(), dtype=np.int64)
    matrix = coo_matrix(
        (vals, (rows, cols)), shape=(limit + 3, limit + 3), dtype=np.int64
    ).tocsr()
    result = maximum_flow(matrix, source, sink)
    flow = result.flow.tocsr()

    residual: list[list[int]] = [[] for _ in range(limit + 3)]
    for (u, v), cap in caps.items():
        sent = int(flow[u, v])
        if cap - sent > 0:
            residual[u].append(v)
        if sent > 0:
            residual[v].append(u)
    reachable = {source}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in residual[u]:
            if v not in reachable:
                reachable.add(v)
                queue.append(v)
    source_side = holes & reachable
    value = sum(w for v, w in positive.items() if v in source_side) - sum(
        w for v, w in negative.items() if v in source_side
    )
    expected = sum(positive.values()) - int(result.flow_value)
    if value != expected:
        raise AssertionError(("max closure replay", value, expected))
    return value, source_side


def direct_statistics(limit: int, data: dict, source_side: set[int]) -> dict:
    hard: set[int] = data["hard"]
    splitless: set[int] = data["splitless"]
    seed3: set[int] = data["seed3_roots"]
    top: dict[int, int] = data["top_of_root"]
    roots = set(top)
    included_roots = roots & source_side
    unhealed = {r for r in included_roots if top[r] in source_side}
    healed = included_roots - unhealed
    boundaries = {
        r
        for r in included_roots
        if any(
            parent in source_side and 2 * parent - 1 <= limit
            and 2 * parent - 1 not in source_side
            for parent in _chain_nodes(r, limit, data["holes"])
        )
    }
    if boundaries != healed:
        raise AssertionError(("prefix boundary replay", healed ^ boundaries))
    return {
        "hard_in_S": len(hard & source_side),
        "seed_boundaries": len(boundaries),
        "unhealed_hard": len(unhealed & hard),
        "unhealed_splitless": len(unhealed & splitless),
        "unhealed_seed3": len(unhealed & seed3),
        "healed_hard": len(healed & hard),
        "healed_splitless": len(healed & splitless),
        "healed_seed3": len(healed & seed3),
    }


def _chain_nodes(root: int, limit: int, holes: set[int]):
    n = root
    while n <= limit and n in holes:
        yield n
        n = 2 * n - 1


def probe(limit: int) -> dict:
    data = build_arithmetic(limit)
    top: dict[int, int] = data["top_of_root"]
    # A root can be unhealed only when its literal top iterate is still a hole.
    hard_terminals = {top[r] for r in data["hard"] if top[r] in data["holes"]}
    splitless_terminals = {
        top[r] for r in data["splitless"] if top[r] in data["holes"]
    }
    nonhard_terminals = {
        top[r]
        for r in data["splitless"] | data["seed3_roots"]
        if top[r] in data["holes"]
    }

    hs_value, hs_side = max_closure(
        limit, data, hard_terminals, splitless_terminals
    )
    hn_value, hn_side = max_closure(limit, data, hard_terminals, nonhard_terminals)
    weighted_value, weighted_side = max_closure(
        limit,
        data,
        {v: 11 for v in hard_terminals},
        {v: 5 for v in splitless_terminals},
    )
    double_value, double_side = max_closure(
        limit,
        data,
        {v: 2 for v in hard_terminals},
        splitless_terminals,
    )
    hs_stats = direct_statistics(limit, data, hs_side)
    hn_stats = direct_statistics(limit, data, hn_side)
    actual_unhealed_hard = sum(
        top[r] in data["holes"] for r in data["hard"]
    )
    actual_unhealed_splitless = sum(
        top[r] in data["holes"] for r in data["splitless"]
    )
    missing_upper_shell = sum(n > limit // 2 for n in data["holes"])
    splitless_upper_shell = sum(n > limit // 2 for n in data["splitless"])
    return {
        "limit": limit,
        "holes": len(data["holes"]),
        "hard_roots": len(data["hard"]),
        "splitless_roots": len(data["splitless"]),
        "seed3_roots": len(data["seed3_roots"]),
        "max_unhealed_hard_minus_splitless": hs_value,
        "max_unhealed_hard_minus_nonhard": hn_value,
        "max_11_unhealed_hard_minus_5_splitless": weighted_value,
        "max_2_unhealed_hard_minus_splitless": double_value,
        "actual_unhealed_hard": actual_unhealed_hard,
        "actual_unhealed_splitless": actual_unhealed_splitless,
        "missing_upper_shell": missing_upper_shell,
        "splitless_upper_shell": splitless_upper_shell,
        "actual_unhealed_hard_over_missing_upper_shell": {
            "numerator": actual_unhealed_hard,
            "denominator": missing_upper_shell,
        },
        "hard_vs_splitless_witness": hs_stats,
        "hard_vs_nonhard_witness": hn_stats,
        "weighted_11_to_5_witness": direct_statistics(limit, data, weighted_side),
        "weighted_2_to_1_witness": direct_statistics(limit, data, double_side),
        "hard_vs_splitless_source_side_sample": sorted(hs_side)[:80],
        "weighted_11_to_5_source_side_if_positive": (
            sorted(weighted_side) if weighted_value > 0 and limit <= 2000 else []
        ),
        "weighted_2_to_1_source_side_if_positive": (
            sorted(double_side) if double_value > 0 and limit <= 2000 else []
        ),
    }


def weighted_excess(limit: int, hard_weight: int, splitless_weight: int) -> int:
    data = build_arithmetic(limit)
    top: dict[int, int] = data["top_of_root"]
    hard_terminals = {top[r] for r in data["hard"] if top[r] in data["holes"]}
    splitless_terminals = {
        top[r] for r in data["splitless"] if top[r] in data["holes"]
    }
    value, _ = max_closure(
        limit,
        data,
        {v: hard_weight for v in hard_terminals},
        {v: splitless_weight for v in splitless_terminals},
    )
    return value


def first_positive(max_limit: int, hard_weight: int, splitless_weight: int) -> dict:
    for limit in range(2, max_limit + 1):
        value = weighted_excess(limit, hard_weight, splitless_weight)
        if value > 0:
            return {"limit": limit, "excess": value}
    return {"limit": None, "excess": None, "searched_through": max_limit}


def scalar_terminal_scan(max_limit: int) -> dict:
    """Scan two cut-independent sufficient bounds at every cutoff."""
    data = build_arithmetic(max_limit)
    holes: set[int] = data["holes"]
    generated: set[int] = data["generated"]
    hard: set[int] = data["hard"]
    splitless: set[int] = data["splitless"]
    delta = [0] * (max_limit + 2)
    for root in hard:
        delta[root] += 1
        child = 2 * root - 1
        while child <= max_limit and child in holes:
            child = 2 * child - 1
        if child <= max_limit:
            if child not in generated:
                raise AssertionError(("chain exits neither holes nor generated", root, child))
            delta[child] -= 1

    e_prefix = [0] * (max_limit + 1)
    h_prefix = [0] * (max_limit + 1)
    active_hard = 0
    first_terminal_failure = None
    first_all_hard_failure = None
    max_terminal_ratio = (0, 1, 0)
    max_all_hard_ratio = (0, 1, 0)
    for limit in range(2, max_limit + 1):
        active_hard += delta[limit]
        e_prefix[limit] = e_prefix[limit - 1] + int(limit in splitless)
        h_prefix[limit] = h_prefix[limit - 1] + int(limit in hard)
        e_shell = e_prefix[limit] - e_prefix[limit // 2]
        if active_hard > e_shell and first_terminal_failure is None:
            first_terminal_failure = {
                "limit": limit,
                "unhealed_hard_roots": active_hard,
                "upper_shell_splitless": e_shell,
            }
        if h_prefix[limit] > e_shell and first_all_hard_failure is None:
            first_all_hard_failure = {
                "limit": limit,
                "hard_roots": h_prefix[limit],
                "upper_shell_splitless": e_shell,
            }
        if e_shell:
            if active_hard * max_terminal_ratio[1] > max_terminal_ratio[0] * e_shell:
                max_terminal_ratio = (active_hard, e_shell, limit)
            if h_prefix[limit] * max_all_hard_ratio[1] > max_all_hard_ratio[0] * e_shell:
                max_all_hard_ratio = (h_prefix[limit], e_shell, limit)
    return {
        "searched_through": max_limit,
        "first_unhealed_hard_gt_upper_shell_splitless": first_terminal_failure,
        "first_all_hard_gt_upper_shell_splitless": first_all_hard_failure,
        "max_unhealed_hard_ratio": {
            "numerator": max_terminal_ratio[0],
            "denominator": max_terminal_ratio[1],
            "limit": max_terminal_ratio[2],
        },
        "max_all_hard_ratio": {
            "numerator": max_all_hard_ratio[0],
            "denominator": max_all_hard_ratio[1],
            "limit": max_all_hard_ratio[2],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, required=True)
    parser.add_argument("--scan-max", type=int, default=0)
    parser.add_argument("--scalar-scan-max", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for limit in args.limits:
        row = probe(limit)
        rows.append(row)
        print(
            json.dumps(
                {
                    "limit": limit,
                    "UH_minus_UE": row["max_unhealed_hard_minus_splitless"],
                    "11UH_minus_5UE": row[
                        "max_11_unhealed_hard_minus_5_splitless"
                    ],
                    "2UH_minus_UE": row[
                        "max_2_unhealed_hard_minus_splitless"
                    ],
                },
                sort_keys=True,
            )
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = {"probes": rows}
    if args.scan_max:
        result["first_failures"] = {
            "11UH_gt_5UE": first_positive(args.scan_max, 11, 5),
            "2UH_gt_UE": first_positive(args.scan_max, 2, 1),
            "UH_gt_UE": first_positive(args.scan_max, 1, 1),
        }
    if args.scalar_scan_max:
        result["scalar_terminal_scan"] = scalar_terminal_scan(args.scalar_scan_max)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
