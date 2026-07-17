#!/usr/bin/env python3
"""Exact diagnostics for the C49 direct hard-hole sieve lane.

The program reconstructs the least grounded set G, obstruction ranks, hard
holes, and healed seed-2 targets.  It then measures critical-blocker fibers
and the residual after sieving hard successors by generated odd divisors.
All arithmetic is integral; no numerical optimization is used.
"""

from __future__ import annotations

import argparse
import json
from array import array
from collections import Counter
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
    out = [1]
    while n > 1:
        p = spf[n]
        old = len(out)
        power = 1
        while n % p == 0:
            n //= p
            power *= p
            for i in range(old):
                out.append(out[i] * power)
    return out


def factor_signature(n: int, spf: array) -> tuple[int, int]:
    omega = 0
    big_omega = 0
    while n > 1:
        p = spf[n]
        omega += 1
        while n % p == 0:
            n //= p
            big_omega += 1
    return omega, big_omega


def residue_factor_signature(n: int, spf: array) -> tuple[int, int, int]:
    """Return v_3 and the distinct/total counts of prime factors 2 mod 3."""
    v3 = omega2 = big_omega2 = 0
    while n > 1:
        p = spf[n]
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        if p == 3:
            v3 = exponent
        elif p % 3 == 2:
            omega2 += 1
            big_omega2 += exponent
    return v3, omega2, big_omega2


def hard_shape(n: int, has_pairs: bool) -> bool:
    if n % 2 or not has_pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def audit(limit: int, thresholds: list[int]) -> dict:
    spf = spf_sieve(limit + 1)
    member = bytearray(limit + 1)
    rank = array("H", [INF]) * (limit + 1)
    member[2] = member[3] = 1

    holes_prefix = array("I", [0]) * (limit + 1)
    splitless_prefix = array("I", [0]) * (limit + 1)
    seed3_prefix = array("I", [0]) * (limit + 1)
    hard_records: list[dict] = []
    targets: list[dict] = []
    dsu = array("I", range(limit + 1))
    graph_edges = 0
    component_cycles = array("I", [0]) * (limit + 1)
    first_component_collision = None

    def find(x: int) -> int:
        root = x
        while dsu[root] != root:
            root = dsu[root]
        while dsu[x] != x:
            parent = dsu[x]
            dsu[x] = root
            x = parent
        return root

    def unite(x: int, y: int) -> bool:
        nonlocal graph_edges
        rx, ry = find(x), find(y)
        graph_edges += 1
        if rx == ry:
            component_cycles[rx] += 1
            return False
        dsu[ry] = rx
        component_cycles[rx] += component_cycles[ry]
        return True


    for n in range(4, limit + 1):
        holes_prefix[n] = holes_prefix[n - 1]
        splitless_prefix[n] = splitless_prefix[n - 1]
        seed3_prefix[n] = seed3_prefix[n - 1]
        if not allowed(n):
            continue

        pairs: list[tuple[int, int]] = []
        blockers: list[tuple[int, int, int]] = []
        generated = False
        product = n + 1
        for a in divisors(product, spf):
            if a < 2:
                continue
            b = product // a
            if a >= b or not allowed(a) or not allowed(b):
                continue
            pairs.append((a, b))
            if member[a] and member[b]:
                generated = True
            else:
                missing = [rank[x] for x in (a, b) if not member[x]]
                if not missing or INF in missing:
                    raise AssertionError((n, a, b, missing))
                blockers.append((a, b, min(missing)))

        if generated:
            member[n] = 1
            if n % 2:
                parent = (n + 1) // 2
                if allowed(parent) and not member[parent]:
                    targets.append({"child": n, "parent": parent, "rank": rank[parent]})
            continue

        holes_prefix[n] += 1
        if not pairs:
            rank[n] = 0
            splitless_prefix[n] += 1
        else:
            rank[n] = 1 + max(row[2] for row in blockers)

        if n % 2 == 0 and (n + 1) % 3 == 0:
            q3 = (n + 1) // 3
            if allowed(q3) and q3 != 3:
                seed3_prefix[n] += 1

        is_hard = hard_shape(n, bool(pairs))
        all_factors_holes = bool(pairs) and all(
            not member[a] and not member[b] for a, b in pairs
        )
        if not pairs:
            pass
        elif n % 2:
            parent = (n + 1) // 2
            if member[parent] or not unite(n, parent):
                raise AssertionError(("odd forest edge", n, parent))
        elif not is_hard:
            parent = (n + 1) // 3
            if member[parent] or not unite(n, parent):
                raise AssertionError(("seed3 forest edge", n, parent))
        elif all_factors_holes:
            # Adding n--a and n--b creates one cycle exactly when a and b
            # already lie in the same component. Pick the pair with the
            # least resulting cyclomatic count.
            def pair_cycle_score(pair: tuple[int, int]) -> int:
                a, b = pair
                ra, rb = find(a), find(b)
                if ra == rb:
                    return component_cycles[ra] + 1
                return component_cycles[ra] + component_cycles[rb]

            a, b = min(pairs, key=lambda pair: (pair_cycle_score(pair), pair))
            score = pair_cycle_score((a, b))
            if score > 0 and first_component_collision is None:
                first_component_collision = {
                    "source": n,
                    "rank": rank[n],
                    "chosen_pair": [a, b],
                    "resulting_cycle_count": score,
                    "pairs": pairs,
                    "pair_cycle_scores": [
                        [x, y, pair_cycle_score((x, y))] for x, y in pairs
                    ],
                }
            unite(n, a)
            unite(n, b)
        else:
            mixed_pair = next(
                (pair for pair in pairs
                 if member[pair[0]] != member[pair[1]]),
                None,
            )
            if mixed_pair is None:
                raise AssertionError(("missing mixed pair", n, pairs))
            a, b = mixed_pair
            blocker = b if member[a] else a
            if not unite(n, blocker):
                raise AssertionError(("mixed forest edge", n, blocker))

        if not is_hard:
            continue

        r = rank[n]
        critical_pairs = [(a, b) for a, b, score in blockers if score == r - 1]
        endpoint_rows = []
        for a, b in critical_pairs:
            for q, other in ((a, b), (b, a)):
                if not member[q] and rank[q] == r - 1:
                    endpoint_rows.append((q, other))
        if not endpoint_rows:
            raise AssertionError(("no critical blocker", n, r, blockers))

        q, cofactor = min(endpoint_rows)
        predecessor = (q + 1) // 2
        if q % 2 != 1 or q * cofactor != product or cofactor < 5:
            raise AssertionError(("scale gate", n, q, cofactor))
        if predecessor >= q or member[predecessor] or rank[predecessor] > r - 2:
            raise AssertionError(("pullback gate", n, r, q, predecessor))

        omega, big_omega = factor_signature(cofactor, spf)
        v3, omega2, big_omega2 = residue_factor_signature(product, spf)
        hard_records.append({
            "source": n,
            "rank": r,
            "blocker": q,
            "blocker_rank": rank[q],
            "predecessor": predecessor,
            "predecessor_rank": rank[predecessor],
            "cofactor": cofactor,
            "cofactor_member": bool(member[cofactor]),
            "cofactor_prime": spf[cofactor] == cofactor,
            "cofactor_omega": omega,
            "cofactor_big_omega": big_omega,
            "pair_count": len(pairs),
            "all_admissible_factors_holes": all_factors_holes,
            "product_v3": v3,
            "product_omega2": omega2,
            "product_big_omega2": big_omega2,
        })

    # Prefix arrays skipped n=2,3; restore their constant hole-free values.
    for n in range(1, min(limit, 3) + 1):
        holes_prefix[n] = 0
        splitless_prefix[n] = 0
        seed3_prefix[n] = 0

    fiber = Counter(row["blocker"] for row in hard_records)
    predecessor_fiber = Counter(row["predecessor"] for row in hard_records)
    rank_fiber = Counter(row["blocker_rank"] for row in hard_records)

    generated_divisors = {
        t: [d for d in range(5, min(t, limit + 1), 2)
            if member[d] and (d % 3 == 2 or d % 9 == 6)]
        for t in thresholds
    }
    residual_rows = []
    for t in thresholds:
        ds = generated_divisors[t]
        residual = 0
        residual_by_blocker = Counter()
        for row in hard_records:
            product = row["source"] + 1
            if not any(
                product % d == 0
                and product // d >= 2
                and product // d != d
                and allowed(product // d)
                for d in ds
            ):
                residual += 1
                residual_by_blocker[row["blocker"]] += 1
        residual_rows.append({
            "threshold": t,
            "generated_divisor_count": len(ds),
            "residual": residual,
            "residual_fraction": [residual, len(hard_records)],
            "largest_residual_fibers": residual_by_blocker.most_common(10),
        })

    # Checkpoint summaries are recomputed from event lists to preserve exact timing.
    checkpoints = []
    checkpoint_values = []
    power = 100
    while power < limit:
        checkpoint_values.append(power)
        power *= 10
    checkpoint_values.append(limit)
    hard_sources = [row["source"] for row in hard_records]
    residual_sources = [
        row["source"] for row in hard_records
        if row["all_admissible_factors_holes"]
    ]
    target_children = [row["child"] for row in targets]
    hi = ji = qi = 0
    for x in checkpoint_values:
        while hi < len(hard_sources) and hard_sources[hi] <= x:
            hi += 1
        while ji < len(residual_sources) and residual_sources[ji] <= x:
            ji += 1
        while qi < len(target_children) and target_children[qi] <= x:
            qi += 1
        y = (x + 1) // 2
        z = (x + 1) // 3
        checkpoints.append({
            "X": x,
            "H": hi,
            "J_all_hole": ji,
            "K_mixed": hi - ji,
            "Q": qi,
            "H_minus_Q": hi - qi,
            "K_minus_Q": hi - ji - qi,
            "M_half": holes_prefix[y],
            "M_third": holes_prefix[z],
            "splitless": splitless_prefix[x],
            "seed3": seed3_prefix[x],
            "spare_third": holes_prefix[z] - seed3_prefix[x],
        })

    category = Counter()
    product_residue_signature = Counter()
    product_residue_signature_by_rank = Counter()
    for row in hard_records:
        if row["cofactor_prime"]:
            key = "prime"
        elif row["cofactor_big_omega"] == 2:
            key = "semiprime"
        else:
            key = "omega_ge_3"
        key += "_G" if row["cofactor_member"] else "_hole"
        category[key] += 1
        signature = (row["product_v3"], row["product_big_omega2"])
        product_residue_signature[signature] += 1
        product_residue_signature_by_rank[(row["rank"], *signature)] += 1

    top_fibers = []
    by_blocker: dict[int, list[dict]] = {}
    for row in hard_records:
        by_blocker.setdefault(row["blocker"], []).append(row)
    for q, count in fiber.most_common(25):
        rows = by_blocker[q]
        top_fibers.append({
            "blocker": q,
            "blocker_rank": rank[q],
            "predecessor": (q + 1) // 2,
            "count": count,
            "prime_cofactor": sum(row["cofactor_prime"] for row in rows),
            "generated_cofactor": sum(row["cofactor_member"] for row in rows),
            "unique_split": sum(row["pair_count"] == 1 for row in rows),
            "max_source": max(row["source"] for row in rows),
        })

    max_j_minus_e = 0
    max_j_minus_e_event = None
    max_j_minus_spare = 0
    max_j_minus_spare_event = None
    for index, source in enumerate(residual_sources, start=1):
        e_excess = index - splitless_prefix[source]
        z = (source + 1) // 3
        spare = holes_prefix[z] - seed3_prefix[source]
        spare_excess = index - spare
        if e_excess > max_j_minus_e:
            max_j_minus_e = e_excess
            max_j_minus_e_event = {"X": source, "J_minus_E": e_excess}
        if spare_excess > max_j_minus_spare:
            max_j_minus_spare = spare_excess
            max_j_minus_spare_event = {
                "X": source,
                "J_minus_spare": spare_excess,
            }

    mixed_events = [
        (row["source"], 1) for row in hard_records
        if not row["all_admissible_factors_holes"]
    ] + [(row["child"], -1) for row in targets]
    mixed_events.sort()
    mixed_excess = 0
    max_mixed_excess = 0
    first_mixed_failure = None
    for coordinate, delta in mixed_events:
        mixed_excess += delta
        if mixed_excess > max_mixed_excess:
            max_mixed_excess = mixed_excess
            first_mixed_failure = {
                "X": coordinate,
                "K_minus_Q": mixed_excess,
            }

    pair_bound_slacks = [
        4 * row["pair_count"] + 2 - row["product_big_omega2"]
        for row in hard_records
    ]
    if pair_bound_slacks and min(pair_bound_slacks) < 0:
        raise AssertionError(("pair-count sieve bound", min(pair_bound_slacks)))
    bounded_pair_counts = {
        str(bound): {
            "all": sum(row["pair_count"] <= bound for row in hard_records),
            "mixed": sum(
                row["pair_count"] <= bound
                and not row["all_admissible_factors_holes"]
                for row in hard_records
            ),
            "all_hole": sum(
                row["pair_count"] <= bound
                and row["all_admissible_factors_holes"]
                for row in hard_records
            ),
        }
        for bound in (1, 2, 4, 8, 16)
    }

    active_roots = {
        find(n) for n in range(2, limit + 1)
        if allowed(n) and not member[n]
    }
    cycle_profile = Counter(component_cycles[root] for root in active_roots)
    max_component_cycles = max(
        [0] + [component_cycles[root] for root in active_roots]
    )

    return {
        "schema_version": 1,
        "limit": limit,
        "hard_count": len(hard_records),
        "target_count": len(targets),
        "all_hole_factor_count": len(residual_sources),
        "mixed_factor_count": len(hard_records) - len(residual_sources),
        "unique_split_count": sum(row["pair_count"] == 1 for row in hard_records),
        "pair_count_sieve_minimum_slack": min([0] + pair_bound_slacks),
        "bounded_pair_counts": bounded_pair_counts,
        "mixed_minus_target_maximum": max_mixed_excess,
        "mixed_minus_target_first_maximum": first_mixed_failure,
        "all_hole_minus_splitless_maximum": max_j_minus_e,
        "all_hole_minus_splitless_first_maximum": max_j_minus_e_event,
        "all_hole_minus_spare_maximum": max_j_minus_spare,
        "all_hole_minus_spare_first_maximum": max_j_minus_spare_event,
        "maximum_rank": max([0] + [rank[n] for n in range(2, limit + 1)
                                   if allowed(n) and not member[n]]),
        "critical_scale_failures": 0,
        "component_graph_edges": graph_edges,
        "component_collision": first_component_collision,
        "component_cycle_profile": dict(sorted(cycle_profile.items())),
        "component_maximum_cycle_count": max_component_cycles,
        "component_pseudoforest_certifies_J_le_E": max_component_cycles <= 1,
        "cofactor_categories": dict(sorted(category.items())),
        "product_residue_signature": {
            f"v3={v3},Omega2={omega2}": count
            for (v3, omega2), count in sorted(product_residue_signature.items())
        },
        "product_residue_signature_by_rank": {
            f"rank={rank_value},v3={v3},Omega2={omega2}": count
            for (rank_value, v3, omega2), count
            in sorted(product_residue_signature_by_rank.items())
        },
        "blocker_rank_load": dict(sorted(rank_fiber.items())),
        "largest_blocker_fibers": top_fibers,
        "largest_predecessor_fibers": predecessor_fiber.most_common(25),
        "dynamic_generated_divisor_sieve": residual_rows,
        "checkpoints": checkpoints,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--thresholds", default="100,1000,10000,100000")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    thresholds = sorted({int(x) for x in args.thresholds.split(",") if x})
    result = audit(args.limit, thresholds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "limit": result["limit"],
        "hard": result["hard_count"],
        "targets": result["target_count"],
        "top_fiber": result["largest_blocker_fibers"][0],
        "categories": result["cofactor_categories"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()


