#!/usr/bin/env python3
"""Exact finite gates for factor-local hard-to-splitless maps.

This is intentionally independent of C67/C71.  It reconstructs the least
closure in increasing order, verifies the structural splitless and hard-shape
characterizations, computes the all-lower obstruction shadows from C38, and
tests several explicit bipartite relations by exact Hopcroft-Karp matching.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
from array import array
from collections import deque
from pathlib import Path
from typing import Callable


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def smallest_prime_factors(limit: int) -> array:
    spf = array("I", range(limit + 1))
    if limit >= 1:
        spf[1] = 1
    for p in range(2, math.isqrt(limit) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit + 1, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def factorization(n: int, spf: array) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    while n > 1:
        p = int(spf[n])
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        out.append((p, exponent))
    return out


def divisors(factors: list[tuple[int, int]]) -> list[int]:
    out = [1]
    for p, exponent in factors:
        old = out
        out = []
        power = 1
        for _ in range(exponent + 1):
            out.extend(d * power for d in old)
            power *= p
    return out


def admissible_pairs(n: int, factors: list[tuple[int, int]]) -> list[tuple[int, int]]:
    product = n + 1
    out = []
    for left in divisors(factors):
        if left < 2 or left * left >= product:
            continue
        right = product // left
        if allowed(left) and allowed(right):
            out.append((left, right))
    return sorted(out)


def predicted_splitless(n: int, factors: list[tuple[int, int]]) -> bool:
    """Exact prime-factor characterization of no admissible distinct pair."""
    product = n + 1
    if product % 3 == 1:
        bad = [(p, exponent) for p, exponent in factors if p % 3 == 2]
        if not bad:
            return True
        return len(factors) == 1 and bad == [(bad[0][0], 2)]

    exponent_three = next((e for p, e in factors if p == 3), 0)
    if exponent_three >= 2:
        return product == 9
    return not any(p % 3 == 2 for p, _ in factors)


def predicted_hard_shape(n: int, has_pair: bool) -> bool:
    return n % 2 == 0 and has_pair and n % 9 in {0, 2, 3, 6}


def build_census(limit: int, shadow_limit: int) -> dict:
    spf = smallest_prime_factors(limit + 1)
    state = bytearray(limit + 1)
    pair_map: dict[int, list[tuple[int, int]]] = {}
    factor_map: dict[int, list[tuple[int, int]]] = {}
    splitless: list[int] = []
    hard: list[int] = []
    splitless_characterization_failures = []
    hard_characterization_failures = []

    for n in range(2, limit + 1):
        if not allowed(n):
            continue
        factors = factorization(n + 1, spf)
        pairs = admissible_pairs(n, factors)
        if (not pairs) != predicted_splitless(n, factors):
            splitless_characterization_failures.append(n)
        shape = predicted_hard_shape(n, bool(pairs))
        direct_shape = False
        if n % 2 == 0 and pairs:
            if (n + 1) % 3:
                direct_shape = True
            else:
                parent = (n + 1) // 3
                direct_shape = not (allowed(parent) and parent != 3)
        if shape != direct_shape:
            hard_characterization_failures.append(n)

        generated = n in (2, 3) or any(
            state[left] == GENERATED and state[right] == GENERATED
            for left, right in pairs
        )
        if generated:
            state[n] = GENERATED
        elif not pairs:
            state[n] = SPLITLESS
            splitless.append(n)
        elif shape:
            state[n] = HARD
            hard.append(n)
        else:
            state[n] = OTHER

        if n <= shadow_limit:
            pair_map[n] = pairs
            factor_map[n] = factors

    return {
        "spf": spf,
        "state": state,
        "pairs": pair_map,
        "factors": factor_map,
        "splitless": splitless,
        "hard": hard,
        "splitless_characterization_failures": splitless_characterization_failures,
        "hard_characterization_failures": hard_characterization_failures,
    }


def build_shadows(data: dict, limit: int) -> tuple[dict[int, int], dict[int, frozenset[int]]]:
    state: bytearray = data["state"]
    pair_map: dict[int, list[tuple[int, int]]] = data["pairs"]
    rank: dict[int, int] = {}
    shadow: dict[int, frozenset[int]] = {}
    for n in range(2, limit + 1):
        if not allowed(n) or state[n] == GENERATED:
            continue
        pairs = pair_map[n]
        if not pairs:
            rank[n] = 0
            shadow[n] = frozenset({n})
            continue
        blockers_by_pair: list[list[int]] = []
        for left, right in pairs:
            blockers = [x for x in (left, right) if state[x] != GENERATED]
            if not blockers:
                raise AssertionError(("hole has generated pair", n, left, right))
            blockers_by_pair.append(blockers)
        rank_n = 1 + max(min(rank[x] for x in blockers) for blockers in blockers_by_pair)
        lower = {
            x
            for blockers in blockers_by_pair
            for x in blockers
            if rank[x] < rank_n
        }
        if not lower:
            raise AssertionError(("empty lower shadow", n, rank_n))
        rank[n] = rank_n
        shadow[n] = frozenset(e for x in lower for e in shadow[x])
        if not shadow[n] or any(state[e] != SPLITLESS for e in shadow[n]):
            raise AssertionError(("invalid splitless shadow", n, sorted(shadow[n])))
    return rank, shadow


def hopcroft_karp(
    sources: list[int],
    targets: list[int],
    neighbors: Callable[[int], list[int]],
) -> tuple[dict[int, int], dict[int, int], dict[str, list[int]] | None]:
    target_set = set(targets)
    adjacency = {u: [v for v in neighbors(u) if v in target_set] for u in sources}
    pair_u: dict[int, int] = {}
    pair_v: dict[int, int] = {}
    distance: dict[int, int] = {}
    infinity = len(sources) + 1

    while True:
        queue: deque[int] = deque()
        for u in sources:
            if u not in pair_u:
                distance[u] = 0
                queue.append(u)
            else:
                distance[u] = infinity
        found = False
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                mate = pair_v.get(v)
                if mate is None:
                    found = True
                elif distance[mate] == infinity:
                    distance[mate] = distance[u] + 1
                    queue.append(mate)
        if not found:
            break

        def augment(u: int) -> bool:
            for v in adjacency[u]:
                mate = pair_v.get(v)
                if mate is None or (
                    distance[mate] == distance[u] + 1 and augment(mate)
                ):
                    pair_u[u] = v
                    pair_v[v] = u
                    return True
            distance[u] = infinity
            return False

        for u in sources:
            if u not in pair_u:
                augment(u)

    if len(pair_u) == len(sources):
        return pair_u, pair_v, None

    reachable_u = {u for u in sources if u not in pair_u}
    reachable_v: set[int] = set()
    queue = deque(reachable_u)
    while queue:
        u = queue.popleft()
        for v in adjacency[u]:
            if pair_u.get(u) == v or v in reachable_v:
                continue
            reachable_v.add(v)
            mate = pair_v.get(v)
            if mate is not None and mate not in reachable_u:
                reachable_u.add(mate)
                queue.append(mate)
    hall = {
        "sources": sorted(reachable_u),
        "neighbors": sorted(reachable_v),
    }
    if len(hall["sources"]) <= len(hall["neighbors"]):
        raise AssertionError(("invalid Hall witness", hall))
    return pair_u, pair_v, hall


def p2_primes(factors: list[tuple[int, int]]) -> list[int]:
    return [p for p, _ in factors if p % 3 == 2]


def prime_free_kernel(factors: list[tuple[int, int]]) -> int:
    out = 1
    for p, exponent in factors:
        if p % 3 != 2:
            out *= p**exponent
    return out


def source_record(h: int, data: dict, rank: dict[int, int], shadow: dict[int, frozenset[int]]) -> dict:
    return {
        "h": h,
        "successor": h + 1,
        "factorization": data["factors"][h],
        "pairs": data["pairs"][h],
        "rank": rank[h],
        "shadow": sorted(shadow[h]),
        "p2_primes": p2_primes(data["factors"][h]),
        "prime_free_kernel": prime_free_kernel(data["factors"][h]),
    }


def target_record(e: int, data: dict) -> dict:
    return {
        "e": e,
        "successor": e + 1,
        "factorization": data["factors"][e],
    }


def first_hall_failure(
    name: str,
    data: dict,
    rank: dict[int, int],
    shadow: dict[int, frozenset[int]],
    limit: int,
    relation: Callable[[int, int], bool],
) -> dict | None:
    hard = [h for h in data["hard"] if h <= limit]
    splitless = [e for e in data["splitless"] if e <= limit]
    hard_prefix: list[int] = []
    hard_index = 0
    for x in range(2, limit + 1):
        while hard_index < len(hard) and hard[hard_index] <= x:
            hard_prefix.append(hard[hard_index])
            hard_index += 1
        if not hard_prefix:
            continue
        targets = [e for e in splitless if x // 2 < e <= x]
        matching, _, hall = hopcroft_karp(
            hard_prefix,
            targets,
            lambda h: [e for e in targets if relation(h, e)],
        )
        if hall is None:
            continue
        hall_sources = hall["sources"]
        hall_targets = hall["neighbors"]
        return {
            "relation": name,
            "X": x,
            "hard_count": len(hard_prefix),
            "upper_splitless_count": len(targets),
            "matching_size": len(matching),
            "hall_source_count": len(hall_sources),
            "hall_neighbor_count": len(hall_targets),
            "hall_sources": [source_record(h, data, rank, shadow) for h in hall_sources],
            "hall_neighbors": [target_record(e, data) for e in hall_targets],
            "upper_splitless": [target_record(e, data) for e in targets],
            "hall_adjacency": {
                str(h): [e for e in targets if relation(h, e)] for h in hall_sources
            },
        }
    return None


def scalar_audit(data: dict, limit: int) -> dict:
    state: bytearray = data["state"]
    hard_count = 0
    splitless_count = 0
    splitless_half = 0
    first_failure = None
    maximum_ratio = {"K": 0, "e_plus": 1, "X": 2}
    minimum_slack = None
    minimum_slack_x = 2
    for x in range(2, limit + 1):
        if state[x] == HARD:
            hard_count += 1
        if state[x] == SPLITLESS:
            splitless_count += 1
        if x % 2 == 0 and state[x // 2] == SPLITLESS:
            splitless_half += 1
        e_plus = splitless_count - splitless_half
        if hard_count > e_plus and first_failure is None:
            first_failure = {"X": x, "K": hard_count, "e_plus": e_plus}
        old = maximum_ratio
        if e_plus and hard_count * old["e_plus"] > old["K"] * e_plus:
            maximum_ratio = {"K": hard_count, "e_plus": e_plus, "X": x}
        slack = e_plus - hard_count
        if minimum_slack is None or slack < minimum_slack:
            minimum_slack = slack
            minimum_slack_x = x
    return {
        "checked_cutoffs": limit - 1,
        "first_failure": first_failure,
        "maximum_ratio": maximum_ratio,
        "minimum_slack": {"value": minimum_slack, "X": minimum_slack_x},
        "endpoint": {"X": limit, "K": hard_count, "e_plus": e_plus},
    }


def expanded_p2_part(factors: list[tuple[int, int]]) -> list[int]:
    return sorted(
        p for p, exponent in factors if p % 3 == 2 for _ in range(exponent)
    )


def map_audit(
    name: str,
    data: dict,
    rank: dict[int, int],
    shadow: dict[int, frozenset[int]],
    limit: int,
    mapping: Callable[[int], int],
) -> dict:
    seen: dict[int, int] = {}
    first_invalid = None
    first_outside_source_shell = None
    first_collision = None
    first_global_expiry = None
    mapped = 0
    for h in (x for x in data["hard"] if x <= limit):
        e = mapping(h)
        mapped += 1
        if not (2 <= e <= limit) or data["state"][e] != SPLITLESS:
            if first_invalid is None:
                first_invalid = {
                    "source": source_record(h, data, rank, shadow),
                    "target": e,
                }
            continue
        if not (h // 2 < e <= h) and first_outside_source_shell is None:
            first_outside_source_shell = {
                "X": h,
                "source": source_record(h, data, rank, shadow),
                "target": target_record(e, data),
            }
        if e in seen and first_collision is None:
            first_collision = {
                "X": h,
                "sources": [
                    source_record(seen[e], data, rank, shadow),
                    source_record(h, data, rank, shadow),
                ],
                "target": target_record(e, data),
            }
        else:
            seen[e] = h
        expiry_x = 2 * e
        if expiry_x >= h and (first_global_expiry is None or expiry_x < first_global_expiry[0]):
            first_global_expiry = (expiry_x, h, e)
    expiry_record = None
    if first_global_expiry is not None:
        x, h, e = first_global_expiry
        expiry_record = {
            "X": x,
            "source": source_record(h, data, rank, shadow),
            "expired_target": target_record(e, data),
            "check": f"{e} <= floor({x}/2)",
        }
    return {
        "map": name,
        "mapped_hard_holes": mapped,
        "distinct_targets": len(seen),
        "first_invalid_target": first_invalid,
        "first_outside_source_upper_half": first_outside_source_shell,
        "first_collision": first_collision,
        "first_fixed_map_expiry": expiry_record,
    }


class Dinic:
    def __init__(self, size: int) -> None:
        self.graph: list[list[list[int]]] = [[] for _ in range(size)]

    def add_edge(self, source: int, target: int, capacity: int) -> None:
        forward = [target, capacity, len(self.graph[target])]
        reverse = [source, 0, len(self.graph[source])]
        self.graph[source].append(forward)
        self.graph[target].append(reverse)

    def max_flow(self, source: int, sink: int) -> int:
        total = 0
        size = len(self.graph)
        while True:
            level = [-1] * size
            level[source] = 0
            queue = deque([source])
            while queue:
                u = queue.popleft()
                for v, capacity, _ in self.graph[u]:
                    if capacity and level[v] < 0:
                        level[v] = level[u] + 1
                        queue.append(v)
            if level[sink] < 0:
                return total
            cursor = [0] * size

            def send(u: int, available: int) -> int:
                if u == sink:
                    return available
                while cursor[u] < len(self.graph[u]):
                    edge = self.graph[u][cursor[u]]
                    v, capacity, reverse_index = edge
                    if capacity and level[v] == level[u] + 1:
                        pushed = send(v, min(available, capacity))
                        if pushed:
                            edge[1] -= pushed
                            self.graph[v][reverse_index][1] += pushed
                            return pushed
                    cursor[u] += 1
                return 0

            while True:
                pushed = send(source, 1 << 60)
                if not pushed:
                    break
                total += pushed

    def reachable(self, source: int) -> set[int]:
        seen = {source}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v, capacity, _ in self.graph[u]:
                if capacity and v not in seen:
                    seen.add(v)
                    queue.append(v)
        return seen


def grouped_kernel_probe(data: dict, x: int) -> dict:
    hard = [h for h in data["hard"] if h <= x]
    targets = [e for e in data["splitless"] if x // 2 < e <= x]
    core_demand: dict[int, int] = {}
    for h in hard:
        core = prime_free_kernel(factorization(h + 1, data["spf"]))
        core_demand[core] = core_demand.get(core, 0) + 1
    free_demand = core_demand.pop(1, 0)
    cores = sorted(core_demand)
    source = 0
    core_start = 1
    target_start = core_start + len(cores)
    sink = target_start + len(targets)
    flow = Dinic(sink + 1)
    for index, core in enumerate(cores):
        flow.add_edge(source, core_start + index, core_demand[core])
    edge_count = 0
    for target_index, e in enumerate(targets):
        node = target_start + target_index
        successor = e + 1
        for core_index, core in enumerate(cores):
            if successor % core == 0:
                flow.add_edge(core_start + core_index, node, 1)
                edge_count += 1
        flow.add_edge(node, sink, 1)
    value = flow.max_flow(source, sink)
    nontrivial_demand = sum(core_demand.values())
    total_feasible = len(hard) <= len(targets)
    feasible = total_feasible and value == nontrivial_demand
    result = {
        "X": x,
        "hard_count": len(hard),
        "upper_splitless_count": len(targets),
        "core_one_demand": free_demand,
        "nontrivial_core_count": len(cores),
        "nontrivial_core_demand": nontrivial_demand,
        "divisibility_edges": edge_count,
        "nontrivial_core_flow": value,
        "feasible": feasible,
    }
    if not feasible and total_feasible:
        reachable = flow.reachable(source)
        witness_cores = [
            core
            for index, core in enumerate(cores)
            if core_start + index in reachable
        ]
        witness_targets = [
            e
            for index, e in enumerate(targets)
            if target_start + index in reachable
        ]
        result["hall_witness"] = {
            "cores": [
                {"core": core, "demand": core_demand[core]}
                for core in witness_cores
            ],
            "demand": sum(core_demand[core] for core in witness_cores),
            "targets": witness_targets,
            "target_count": len(witness_targets),
        }
    return result


def semigroup_count_audit(spf: array, limit: int) -> dict:
    pure_one_prefix = [0] * (limit + 1)
    pure_two_even_prefix = [0] * (limit + 1)
    first_failure = None
    maximum_excess = {"value": -(1 << 60), "Y": 1, "left": 0, "right": 0}
    for value in range(1, limit + 1):
        factors = factorization(value, spf)
        pure_one = value > 1 and all(p % 3 == 1 for p, _ in factors)
        pure_two_even = (
            value > 1
            and all(p >= 5 and p % 3 == 2 for p, _ in factors)
            and sum(exponent for _, exponent in factors) % 2 == 0
        )
        pure_one_prefix[value] = pure_one_prefix[value - 1] + int(pure_one)
        pure_two_even_prefix[value] = (
            pure_two_even_prefix[value - 1] + int(pure_two_even)
        )
        left = pure_two_even_prefix[value]
        right = pure_one_prefix[value] - pure_one_prefix[value // 2]
        excess = left - right
        if excess > 0 and first_failure is None:
            first_failure = {
                "Y": value,
                "pure_2mod3_even_omega_through_Y": left,
                "pure_1mod3_in_upper_half": right,
                "excess": excess,
            }
        if excess > maximum_excess["value"]:
            maximum_excess = {
                "value": excess,
                "Y": value,
                "left": left,
                "right": right,
            }
    return {
        "checked_Y": limit,
        "first_failure": first_failure,
        "maximum_excess": maximum_excess,
        "endpoint": {
            "Y": limit,
            "pure_2mod3_even_omega_through_Y": pure_two_even_prefix[limit],
            "pure_1mod3_in_upper_half": (
                pure_one_prefix[limit] - pure_one_prefix[limit // 2]
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=200_000)
    parser.add_argument("--hall-limit", type=int, default=500)
    parser.add_argument("--kernel-probes", type=int, nargs="*", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 2 or not 2 <= args.hall_limit <= args.limit:
        raise SystemExit("require 2 <= hall-limit <= limit")
    if any(x < 2 or x > args.limit for x in args.kernel_probes):
        raise SystemExit("kernel probes must lie in [2, limit]")

    data = build_census(args.limit, args.hall_limit)
    rank, shadow = build_shadows(data, args.hall_limit)
    target_set = set(e for e in data["splitless"] if e <= args.hall_limit)

    def prime_square(h: int, e: int) -> bool:
        return any(e == p * p - 1 for p in p2_primes(data["factors"][h]))

    def kernel_multiple(h: int, e: int) -> bool:
        kernel = prime_free_kernel(data["factors"][h])
        return kernel > 1 and (e + 1) % kernel == 0

    def full_kernel_multiple(h: int, e: int) -> bool:
        kernel = prime_free_kernel(data["factors"][h])
        return (e + 1) % kernel == 0

    def leaf_multiple(h: int, e: int) -> bool:
        return any((e + 1) % (leaf + 1) == 0 for leaf in shadow[h])

    relations = {
        "prime_square": prime_square,
        "prime_free_kernel_multiple": kernel_multiple,
        "full_prime_free_kernel_replacement": full_kernel_multiple,
        "obstruction_leaf_multiple": leaf_multiple,
        "factor_local_union": lambda h, e: (
            prime_square(h, e) or kernel_multiple(h, e) or leaf_multiple(h, e)
        ),
    }
    hall_failures = {
        name: first_hall_failure(
            name, data, rank, shadow, args.hall_limit, relation
        )
        for name, relation in relations.items()
    }


    prime_one = [
        p
        for p in range(2, args.hall_limit + 2)
        if data["spf"][p] == p and p % 3 == 1
    ]
    pure_one = []
    for value in range(1, args.hall_limit + 2):
        factors = factorization(value, data["spf"])
        if all(p % 3 == 1 for p, _ in factors):
            pure_one.append(value)

    def predecessor(values: list[int], bound: int) -> int:
        index = bisect.bisect_right(values, bound)
        if index == 0:
            raise AssertionError(("no predecessor", bound))
        return values[index - 1]

    def least_square_map(h: int) -> int:
        p = min(p2_primes(data["factors"][h]))
        return p * p - 1

    def paired_substitution(h: int, replacements: list[int]) -> int:
        factors = data["factors"][h]
        occurrences = expanded_p2_part(factors)
        if len(occurrences) < 2 or len(occurrences) % 2:
            raise AssertionError(("bad p2 parity", h, occurrences))
        product = prime_free_kernel(factors)
        for index in range(0, len(occurrences), 2):
            product *= predecessor(
                replacements, occurrences[index] * occurrences[index + 1]
            )
        return product - 1

    def whole_part_substitution(h: int) -> int:
        factors = data["factors"][h]
        p2_part = math.prod(p**exponent for p, exponent in factors if p % 3 == 2)
        return prime_free_kernel(factors) * predecessor(pure_one, p2_part) - 1

    map_audits = {
        "least_p2_prime_square": map_audit(
            "least_p2_prime_square",
            data,
            rank,
            shadow,
            args.hall_limit,
            least_square_map,
        ),
        "paired_lower_prime_1mod3": map_audit(
            "paired_lower_prime_1mod3",
            data,
            rank,
            shadow,
            args.hall_limit,
            lambda h: paired_substitution(h, prime_one),
        ),
        "paired_lower_p2_free": map_audit(
            "paired_lower_p2_free",
            data,
            rank,
            shadow,
            args.hall_limit,
            lambda h: paired_substitution(h, pure_one),
        ),
        "whole_p2_part_lower_p2_free": map_audit(
            "whole_p2_part_lower_p2_free",
            data,
            rank,
            shadow,
            args.hall_limit,
            whole_part_substitution,
        ),
    }

    square_lemma_failures = []
    for h in (x for x in data["hard"] if x <= args.hall_limit):
        primes = p2_primes(data["factors"][h])
        candidates = [p * p - 1 for p in primes if p * p - 1 <= h]
        if not candidates or any(data["state"][e] != SPLITLESS for e in candidates):
            square_lemma_failures.append(source_record(h, data, rank, shadow))

    payload = {
        "parameters": {"limit": args.limit, "hall_limit": args.hall_limit},
        "counts": {
            "generated": sum(value == GENERATED for value in data["state"]),
            "splitless": len(data["splitless"]),
            "hard": len(data["hard"]),
        },
        "predicate_audits": {
            "splitless_characterization_failures": data[
                "splitless_characterization_failures"
            ],
            "hard_characterization_failures": data[
                "hard_characterization_failures"
            ],
            "square_target_lemma_failures": square_lemma_failures,
        },
        "scalar_inequality": scalar_audit(data, args.limit),
        "hall_failures": hall_failures,
        "map_audits": map_audits,
        "grouped_kernel_probes": [
            grouped_kernel_probe(data, x) for x in sorted(set(args.kernel_probes))
        ],
        "semigroup_count_audit": semigroup_count_audit(data["spf"], args.limit),
        "hall_target_count": len(target_set),
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True).encode("ascii") + b"\n"
    payload["payload_sha256_before_hash_field"] = hashlib.sha256(encoded).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
