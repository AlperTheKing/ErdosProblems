#!/usr/bin/env python3
"""Root-labelled C98 audit of the lower quarter inequality.

The program reconstructs the least generated closure for Problem 424 and
studies

    2 D(4Y) >= 7 A_H(Y).

It records a capacitated Hall witness at a tight finite cutoff, together
with exact counterexamples to downward-only and prime-support-local charging.
All acceptance decisions use integer arithmetic.
"""

from __future__ import annotations

import argparse
import bisect
import json
import math
from array import array
from pathlib import Path


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def smallest_prime_factors(limit: int) -> array:
    spf = array("I", range(limit + 1))
    if limit >= 1:
        spf[1] = 1
    p = 2
    while p * p <= limit:
        if spf[p] == p:
            for multiple in range(p * p, limit + 1, p):
                if spf[multiple] == multiple:
                    spf[multiple] = p
        p += 1
    return spf


def factorization(value: int, spf: array) -> list[tuple[int, int]]:
    factors: list[tuple[int, int]] = []
    while value > 1:
        p = int(spf[value])
        exponent = 0
        while value % p == 0:
            value //= p
            exponent += 1
        factors.append((p, exponent))
    return factors


def divisors(value: int, spf: array) -> list[int]:
    result = [1]
    for p, exponent in factorization(value, spf):
        old = list(result)
        power = 1
        for _ in range(exponent):
            power *= p
            result.extend(d * power for d in old)
    return result


def admissible_pairs(n: int, spf: array) -> list[tuple[int, int]]:
    product = n + 1
    result: list[tuple[int, int]] = []
    for left in divisors(product, spf):
        if left < 2:
            continue
        right = product // left
        if left >= right:
            continue
        if allowed(left) and allowed(right):
            result.append((left, right))
    result.sort()
    return result


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    product = n + 1
    if product % 3:
        return True
    parent = product // 3
    return not allowed(parent) or parent == 3


def root_of_odd(value: int) -> int:
    odd_part = value - 1
    while odd_part % 2 == 0:
        odd_part //= 2
    return odd_part + 1


def visible_chain(root: int, limit: int) -> list[int]:
    result = []
    value = root
    while value <= limit:
        result.append(value)
        value = 2 * value - 1
    return result


def build_closure(limit: int) -> dict:
    spf = smallest_prime_factors(limit + 1)
    state = bytearray(limit + 1)
    hard_roots: list[int] = []
    splitless_roots: list[int] = []
    hard_death: dict[int, int] = {}
    splitless_death: dict[int, int] = {}
    death_certificate: dict[int, tuple[int, int]] = {}

    for n in range(2, limit + 1):
        pairs: list[tuple[int, int]] = []
        if n in (2, 3):
            current = GENERATED
        elif not allowed(n):
            current = OTHER
        else:
            pairs = admissible_pairs(n, spf)
            generating = [
                (a, b) for a, b in pairs
                if state[a] == GENERATED and state[b] == GENERATED
            ]
            if generating:
                current = GENERATED
            elif not pairs:
                current = SPLITLESS
            elif hard_shape(n, pairs):
                current = HARD
            else:
                current = OTHER
        state[n] = current

        if current == HARD:
            require(n % 2 == 0, ("odd-hard", n))
            hard_roots.append(n)
        elif current == SPLITLESS:
            require(n % 2 == 0, ("odd-splitless", n))
            splitless_roots.append(n)

        if n > 3 and n % 2 == 1 and current == GENERATED:
            parent = (n + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                root = root_of_odd(n)
                require(root % 2 == 0, ("odd-root", n, root))
                certs = [
                    (a, b) for a, b in pairs
                    if state[a] == GENERATED and state[b] == GENERATED
                ]
                require(certs and certs[0][0] >= 3, ("death-cert", n, certs))
                if state[root] == HARD:
                    require(root not in hard_death, ("duplicate-hard-death", root))
                    hard_death[root] = n
                elif state[root] == SPLITLESS:
                    require(root not in splitless_death,
                            ("duplicate-splitless-death", root))
                    splitless_death[root] = n
                    death_certificate[root] = certs[0]

    return {
        "spf": spf,
        "state": state,
        "hard_roots": hard_roots,
        "splitless_roots": splitless_roots,
        "hard_death": hard_death,
        "splitless_death": splitless_death,
        "death_certificate": death_certificate,
    }


def active_hard(data: dict, cutoff: int) -> list[int]:
    death = data["hard_death"]
    return [
        root for root in data["hard_roots"]
        if root <= cutoff and death.get(root, 10**30) > cutoff
    ]


def healed_splitless(data: dict, cutoff: int) -> list[int]:
    death = data["splitless_death"]
    return sorted(root for root, time in death.items() if time <= cutoff)


def hard_detail(data: dict, root: int, cutoff: int) -> dict:
    pairs = admissible_pairs(root, data["spf"])
    return {
        "root": root,
        "pairs": [list(pair) for pair in pairs],
        "visible_chain": visible_chain(root, cutoff),
        "first_generated": data["hard_death"].get(root),
    }


def supply_detail(data: dict, root: int) -> dict:
    death = data["splitless_death"][root]
    depth = 0
    shifted = death - 1
    while shifted % 2 == 0:
        shifted //= 2
        depth += 1
    require(shifted + 1 == root, ("root-depth", root, death, depth))
    return {
        "root": root,
        "successor_factorization": [
            [p, exponent] for p, exponent in factorization(root + 1, data["spf"])
        ],
        "first_generated": death,
        "depth": depth,
        "generating_pair": list(data["death_certificate"][root]),
    }


class Fenwick:
    def __init__(self, size: int) -> None:
        self.values = [0] * (size + 1)

    def add(self, index: int) -> None:
        while index < len(self.values):
            self.values[index] += 1
            index += index & -index

    def prefix(self, index: int) -> int:
        total = 0
        while index:
            total += self.values[index]
            index -= index & -index
        return total


def scan_quarter_trajectory(data: dict, limit: int) -> dict:
    maximum_y = limit // 4
    births = [0] * (maximum_y + 1)
    hard_deaths = [0] * (maximum_y + 1)
    for root in data["hard_roots"]:
        if root <= maximum_y:
            births[root] += 1
    for time in data["hard_death"].values():
        if time <= maximum_y:
            hard_deaths[time] += 1

    supply_events = sorted(
        (time, root) for root, time in data["splitless_death"].items()
    )
    fenwick = Fenwick(maximum_y + 1)
    active = 0
    total_supply = 0
    event_index = 0
    checked = 0
    failures = 0
    first_failure = None
    first_downward_failure = None
    minimum_margin = None
    minimum_margin_row = None
    minimum_ratio = None
    largest_downward_deficit = None
    largest_downward_row = None

    for y in range(1, maximum_y + 1):
        active += births[y] - hard_deaths[y]
        while (event_index < len(supply_events)
               and supply_events[event_index][0] <= 4 * y):
            _, root = supply_events[event_index]
            total_supply += 1
            if root <= maximum_y:
                fenwick.add(root)
            event_index += 1
        if active == 0:
            continue

        checked += 1
        downward = fenwick.prefix(y)
        fresh_upper = total_supply - downward
        margin = 2 * total_supply - 7 * active
        downward_margin = 2 * downward - 7 * active
        row = {
            "Y": y,
            "A_H_Y": active,
            "D_4Y": total_supply,
            "downward_supply": downward,
            "fresh_upper_supply": fresh_upper,
            "margin_2D_minus_7A": margin,
            "downward_margin": downward_margin,
        }
        if margin < 0:
            failures += 1
            if first_failure is None:
                first_failure = row
        if minimum_margin is None or margin < minimum_margin:
            minimum_margin = margin
            minimum_margin_row = row
        if (minimum_ratio is None
                or total_supply * minimum_ratio[1] < minimum_ratio[0] * active):
            minimum_ratio = (total_supply, active, y)
        if downward_margin < 0 and first_downward_failure is None:
            first_downward_failure = row
        deficit = -downward_margin
        if largest_downward_deficit is None or deficit > largest_downward_deficit:
            largest_downward_deficit = deficit
            largest_downward_row = row

    require(minimum_ratio is not None, "no positive-demand cutoff")
    divisor = math.gcd(minimum_ratio[0], minimum_ratio[1])
    return {
        "maximum_Y": maximum_y,
        "checked_positive_demand_cutoffs": checked,
        "lower_quarter_failure_count": failures,
        "first_lower_quarter_failure": first_failure,
        "minimum_margin": minimum_margin_row,
        "minimum_ratio_D_4Y_over_A_H_Y": {
            "D_4Y": minimum_ratio[0],
            "A_H_Y": minimum_ratio[1],
            "Y": minimum_ratio[2],
            "reduced_numerator": minimum_ratio[0] // divisor,
            "reduced_denominator": minimum_ratio[1] // divisor,
        },
        "first_downward_capacity_failure": first_downward_failure,
        "largest_downward_capacity_deficit": largest_downward_row,
    }


def hall_instance(data: dict, y: int) -> dict:
    sources = active_hard(data, y)
    supplies = healed_splitless(data, 4 * y)
    prefix_rows = []
    minimum_prefix = None
    for index, root in enumerate(sources, 1):
        available = bisect.bisect_right(supplies, 2 * root)
        margin = 2 * available - 7 * index
        row = {
            "source_prefix_size": index,
            "last_source": root,
            "available_supply_roots": available,
            "margin": margin,
        }
        prefix_rows.append(row)
        if minimum_prefix is None or margin < minimum_prefix["margin"]:
            minimum_prefix = row
    require(minimum_prefix is not None and minimum_prefix["margin"] >= 0,
            ("hall-prefix-failure", y, minimum_prefix))

    slots = [(root, copy) for root in supplies for copy in (0, 1)]
    assignments = []
    cursor = 0
    for source in sources:
        chosen = slots[cursor:cursor + 7]
        require(len(chosen) == 7 and chosen[-1][0] <= 2 * source,
                ("greedy-hall-failure", source, chosen))
        assignments.append({
            "hard_root": source,
            "slots": [[root, copy] for root, copy in chosen],
        })
        cursor += 7

    return {
        "Y": y,
        "X": 4 * y,
        "active_hard_roots": sources,
        "healed_splitless_roots": supplies,
        "downward_supply_roots": [root for root in supplies if root <= y],
        "fresh_upper_supply_roots": [root for root in supplies if root > y],
        "counts": {
            "A_H_Y": len(sources),
            "D_4Y": len(supplies),
            "downward_supply": bisect.bisect_right(supplies, y),
            "fresh_upper_supply": len(supplies) - bisect.bisect_right(supplies, y),
            "total_slot_margin": 2 * len(supplies) - 7 * len(sources),
        },
        "minimum_prefix_margin": minimum_prefix,
        "prefix_rows": prefix_rows,
        "greedy_assignment": assignments,
        "unused_slots": [[root, copy] for root, copy in slots[cursor:]],
    }


def local_support_counterexample(data: dict) -> dict:
    y = 54
    supplies = healed_splitless(data, 4 * y)
    prime_support = [2, 3, 5, 7, 11]
    support_radical = math.prod(prime_support)
    neighbors = [root for root in supplies if math.gcd(root + 1, support_radical) > 1]
    square_shadows = [5 * 5 - 1, 11 * 11 - 1]
    square_in_bank = [root for root in square_shadows if root in supplies]
    leaf_lifts = [root for root in supplies if (root + 1) % 7 == 0]
    result = {
        "Y": y,
        "X": 4 * y,
        "hard_root": 54,
        "factor_descent": [
            {"hole": 54, "successor": 55, "pair": [5, 11], "missing": 11},
            {"hole": 11, "successor": 12, "pair": [2, 6], "missing": 6},
            {"splitless_leaf": 6, "successor": 7},
        ],
        "prime_support": prime_support,
        "support_radical": support_radical,
        "D_216": [supply_detail(data, root) for root in supplies],
        "support_local_neighbors": neighbors,
        "support_local_capacity": 2 * len(neighbors),
        "hard_demand": 7,
        "capacity_deficit": 7 - 2 * len(neighbors),
        "unrelated_supply_roots": [root for root in supplies if root not in neighbors],
        "prime_square_shadows": square_shadows,
        "prime_square_shadows_in_D_216": square_in_bank,
        "obstruction_leaf_lifts_in_D_216": leaf_lifts,
    }
    require(supplies == [6, 18, 20, 38, 66], supplies)
    require(neighbors == [6, 20, 38], neighbors)
    require(result["capacity_deficit"] == 1, result)
    require(square_in_bank == [] and leaf_lifts == [6, 20], result)
    return result


def exact_witness(data: dict, y: int) -> dict:
    sources = active_hard(data, y)
    supplies = healed_splitless(data, 4 * y)
    return {
        "Y": y,
        "X": 4 * y,
        "hard_roots": [hard_detail(data, root, y) for root in sources],
        "downward_supply": [
            supply_detail(data, root) for root in supplies if root <= y
        ],
        "fresh_upper_supply": [
            supply_detail(data, root) for root in supplies if root > y
        ],
        "counts": {
            "A_H_Y": len(sources),
            "D_4Y": len(supplies),
            "downward_supply": bisect.bisect_right(supplies, y),
            "fresh_upper_supply": len(supplies) - bisect.bisect_right(supplies, y),
            "total_margin": 2 * len(supplies) - 7 * len(sources),
            "downward_margin": (
                2 * bisect.bisect_right(supplies, y) - 7 * len(sources)
            ),
        },
    }


def analyze(limit: int, hall_cutoff: int) -> dict:
    require(limit >= 4 * hall_cutoff, ("limit-too-small", limit, hall_cutoff))
    require(hall_cutoff == 2064, "the checked C98 Hall cutoff is 2064")
    data = build_closure(limit)
    trajectory = scan_quarter_trajectory(data, limit)
    downward = exact_witness(data, 174)
    hall = hall_instance(data, hall_cutoff)
    local = local_support_counterexample(data)

    require(downward["counts"] == {
        "A_H_Y": 5,
        "D_4Y": 25,
        "downward_supply": 17,
        "fresh_upper_supply": 8,
        "total_margin": 15,
        "downward_margin": -1,
    }, downward["counts"])
    require(hall["counts"] == {
        "A_H_Y": 87,
        "D_4Y": 309,
        "downward_supply": 209,
        "fresh_upper_supply": 100,
        "total_slot_margin": 9,
    }, hall["counts"])
    require(hall["minimum_prefix_margin"]["margin"] == 9,
            hall["minimum_prefix_margin"])
    require(trajectory["first_downward_capacity_failure"]["Y"] == 174,
            trajectory["first_downward_capacity_failure"])
    require(trajectory["minimum_ratio_D_4Y_over_A_H_Y"]["Y"] == 2064,
            trajectory["minimum_ratio_D_4Y_over_A_H_Y"])

    return {
        "schema": "C98-lower-quarter-hall-v1",
        "limit": limit,
        "exact_integer_acceptance": True,
        "definitions": {
            "A_H_Y": "hard roots whose visible seed-2 chain is all holes at Y",
            "D_4Y": "splitless roots whose seed-2 chain first reaches G by 4Y",
            "downward_supply": "members of D(4Y) with root e<=Y",
            "fresh_upper_supply": "members of D(4Y) with Y<e<=2Y",
            "Hall_edge": "a hard root h may use either labelled copy of e when e<=2h",
        },
        "coefficient_provenance": {
            "upper_gate": "A_H(X)<=D(X)+A_H(floor(X/4))+1",
            "general_lower_rate": "D(X)>=c*A_H(floor(X/4))",
            "composed_ratio": "D(X)/A_H(X)>=c/(c+1), up to the additive constant",
            "contraction_threshold": "c/(c+1)>3/4 iff c>3",
            "smallest_half_integer_above_threshold": "7/2",
            "integer_specialization": "2D(X)>=7A_H(floor(X/4)) implies 9D(X)+7>=7A_H(X)",
        },
        "uniform_lemma_checked_contract": {
            "name": "quarter-shell Hall equivalence",
            "statement": (
                "If 2D(4z)>=7A_H(z) for every z<=Y, the graph on H_Y and "
                "two copies of D(4Y), with e adjacent to h iff e<=2h, has "
                "an integral matching giving seven slots to every h; any such "
                "matching implies 2D(4Y)>=7A_H(Y)."
            ),
            "fresh_shell_identity": (
                "D(4Y)=D_{e<=Y}(4Y)+#{Y<e<=2Y: e splitless and 2e-1 in G}."
            ),
        },
        "trajectory_audit": trajectory,
        "prime_support_local_counterexample": local,
        "first_downward_only_counterexample": downward,
        "tight_root_labelled_Hall_instance": hall,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--hall-cutoff", type=int, default=2064)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.limit, args.hall_cutoff)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps({
        "limit": result["limit"],
        "lower_failures": result["trajectory_audit"]["lower_quarter_failure_count"],
        "first_downward_failure": result["trajectory_audit"]["first_downward_capacity_failure"],
        "minimum_ratio": result["trajectory_audit"]["minimum_ratio_D_4Y_over_A_H_Y"],
        "hall_counts": result["tight_root_labelled_Hall_instance"]["counts"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
