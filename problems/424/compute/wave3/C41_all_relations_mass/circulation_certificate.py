#!/usr/bin/env python3
"""Construct an exact high-entropy circulation in the C41 avoidance DFA.

The numerical Perron chain is only a search heuristic.  The output
certificate contains integer edge multiplicities and is checked using:

* exact flow balance at every state;
* exact canonical letter totals (15r,10r,6r);
* strong connectivity of the positive support; and
* the exact integer inequality

      product_v d_v**d_v
      --------------------------------  > Q**r.
      product_e n_e**n_e

By the BEST theorem and Stirling, this inequality gives exponentially more
than Q**(rm) safe cyclic words for all sufficiently large repetitions m.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import Counter, deque
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from all_relations_mass import (
    ALPHABET,
    CANONICAL,
    LETTER_INDEX,
    Q,
    PatternAutomaton,
    perron,
)


def largest_scc(transitions: np.ndarray):
    rows: list[int] = []
    columns: list[int] = []
    for state in range(len(transitions)):
        for index in range(3):
            target = int(transitions[state, index])
            if target >= 0:
                rows.append(state)
                columns.append(target)
    graph = csr_matrix(
        (np.ones(len(rows), dtype=np.int8), (rows, columns)),
        shape=(len(transitions), len(transitions)),
    )
    count, component = connected_components(
        graph, directed=True, connection="strong"
    )
    sizes = np.bincount(component)
    largest = int(np.argmax(sizes))
    members = np.flatnonzero(component == largest)
    return count, component, sizes, largest, members


def restrict_to_component(
    transitions: np.ndarray, component: np.ndarray, component_id: int
) -> np.ndarray:
    restricted = np.full_like(transitions, -1)
    for state in range(len(transitions)):
        if int(component[state]) != component_id:
            continue
        for index in range(3):
            target = int(transitions[state, index])
            if target >= 0 and int(component[target]) == component_id:
                restricted[state, index] = target
    return restricted


def shortest_trees(
    transitions: np.ndarray, members: np.ndarray, start: int
):
    member = np.zeros(len(transitions), dtype=bool)
    member[members] = True

    parent_state = np.full(len(transitions), -1, dtype=np.int32)
    parent_letter = np.full(len(transitions), -1, dtype=np.int8)
    parent_state[start] = start
    queue: deque[int] = deque([start])
    while queue:
        state = queue.popleft()
        for index in range(3):
            target = int(transitions[state, index])
            if target < 0 or not member[target] or parent_state[target] >= 0:
                continue
            parent_state[target] = state
            parent_letter[target] = index
            queue.append(target)

    reverse: list[list[tuple[int, int]]] = [
        [] for _ in range(len(transitions))
    ]
    for state in members:
        state = int(state)
        for index in range(3):
            target = int(transitions[state, index])
            if target >= 0 and member[target]:
                reverse[target].append((state, index))

    return_letter = np.full(len(transitions), -1, dtype=np.int8)
    return_target = np.full(len(transitions), -1, dtype=np.int32)
    return_target[start] = start
    queue = deque([start])
    while queue:
        target = queue.popleft()
        for predecessor, index in reverse[target]:
            if return_target[predecessor] >= 0:
                continue
            return_letter[predecessor] = index
            return_target[predecessor] = target
            queue.append(predecessor)

    if np.any(parent_state[members] < 0) or np.any(return_target[members] < 0):
        raise AssertionError("largest SCC shortest trees are incomplete")
    return parent_state, parent_letter, return_target, return_letter


def add_return_path(
    counts: Counter[int],
    transitions: np.ndarray,
    state: int,
    start: int,
    return_target: np.ndarray,
    return_letter: np.ndarray,
) -> int:
    steps = 0
    while state != start:
        index = int(return_letter[state])
        if index < 0:
            raise AssertionError("missing return edge")
        counts[3 * state + index] += 1
        state = int(return_target[state])
        steps += 1
        if steps > len(transitions):
            raise AssertionError("return tree contains a cycle")
    return steps


def edge_probabilities(
    transitions: np.ndarray, theta: np.ndarray, left: np.ndarray, right: np.ndarray
):
    weights = np.array([1.0, math.exp(theta[0]), math.exp(theta[1])])
    stationary = left * right
    start = int(np.argmax(stationary))
    probabilities: list[list[float]] = [[0.0, 0.0, 0.0] for _ in transitions]
    for state in range(len(transitions)):
        if right[state] <= 0:
            continue
        raw = []
        total = 0.0
        for index in range(3):
            target = int(transitions[state, index])
            value = 0.0 if target < 0 else weights[index] * right[target]
            raw.append(value)
            total += value
        if total > 0:
            probabilities[state] = [value / total for value in raw]
    return start, probabilities, stationary


def choose_letter(
    rng: random.Random,
    transitions: np.ndarray,
    state: int,
    probabilities: list[list[float]],
    bias: tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> int:
    weighted = [probabilities[state][i] * bias[i] for i in range(3)]
    total = sum(weighted)
    if total <= 0:
        raise AssertionError("sampled state has no recurrent outgoing edge")
    threshold = rng.random() * total
    partial = 0.0
    for index, value in enumerate(weighted):
        partial += value
        if threshold <= partial and int(transitions[state, index]) >= 0:
            return index
    for index in range(2, -1, -1):
        if int(transitions[state, index]) >= 0 and weighted[index] > 0:
            return index
    raise AssertionError("failed to sample a letter")


def sampled_cycle(
    transitions: np.ndarray,
    probabilities: list[list[float]],
    start: int,
    walk_length: int,
    rng: random.Random,
    return_target: np.ndarray,
    return_letter: np.ndarray,
    bias: tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> Counter[int]:
    counts: Counter[int] = Counter()
    state = start
    for _ in range(walk_length):
        index = choose_letter(rng, transitions, state, probabilities, bias)
        counts[3 * state + index] += 1
        state = int(transitions[state, index])
    add_return_path(
        counts,
        transitions,
        state,
        start,
        return_target,
        return_letter,
    )
    return counts


def cycle_statistics(counts: Counter[int]):
    letters = [0, 0, 0]
    for edge, multiplicity in counts.items():
        letters[edge % 3] += multiplicity
    length = sum(letters)
    deviation = (
        31 * letters[0] - CANONICAL[0] * length,
        31 * letters[1] - CANONICAL[1] * length,
    )
    return letters, length, deviation


def fundamental_cycle(
    state: int,
    index: int,
    transitions: np.ndarray,
    start: int,
    parent_state: np.ndarray,
    parent_letter: np.ndarray,
    return_target: np.ndarray,
    return_letter: np.ndarray,
) -> Counter[int]:
    reverse_edges: list[int] = []
    cursor = state
    while cursor != start:
        predecessor = int(parent_state[cursor])
        letter = int(parent_letter[cursor])
        reverse_edges.append(3 * predecessor + letter)
        cursor = predecessor
    counts: Counter[int] = Counter(reversed(reverse_edges))
    counts[3 * state + index] += 1
    target = int(transitions[state, index])
    add_return_path(
        counts,
        transitions,
        target,
        start,
        return_target,
        return_letter,
    )
    return counts


def correction_library(
    transitions: np.ndarray,
    members: np.ndarray,
    probabilities: list[list[float]],
    start: int,
    parent_state: np.ndarray,
    parent_letter: np.ndarray,
    return_target: np.ndarray,
    return_letter: np.ndarray,
    rng: random.Random,
    random_cycles: int,
):
    best: dict[tuple[int, int], tuple[int, Counter[int]]] = {}

    def retain(counts: Counter[int]) -> None:
        _, length, deviation = cycle_statistics(counts)
        if deviation == (0, 0):
            return
        old = best.get(deviation)
        if old is None or length < old[0]:
            best[deviation] = (length, counts)

    for state_raw in members:
        state = int(state_raw)
        for index in range(3):
            if int(transitions[state, index]) < 0:
                continue
            retain(
                fundamental_cycle(
                    state,
                    index,
                    transitions,
                    start,
                    parent_state,
                    parent_letter,
                    return_target,
                    return_letter,
                )
            )

    biases = [
        (1.0, 1.0, 1.0),
        (12.0, 1.0, 1.0),
        (1.0, 12.0, 1.0),
        (1.0, 1.0, 12.0),
        (6.0, 6.0, 1.0),
        (6.0, 1.0, 6.0),
        (1.0, 6.0, 6.0),
    ]
    for number in range(random_cycles):
        bias = biases[number % len(biases)]
        walk_length = rng.randint(8, 300)
        retain(
            sampled_cycle(
                transitions,
                probabilities,
                start,
                walk_length,
                rng,
                return_target,
                return_letter,
                bias,
            )
        )
    return [
        {"deviation": deviation, "length": length, "counts": counts}
        for deviation, (length, counts) in sorted(best.items())
    ]


def solve_correction(base: Counter[int], library: list[dict], time_limit: float):
    _, _, deviation = cycle_statistics(base)
    target = -deviation[0], -deviation[1]

    best_pair = None
    for first_index, first in enumerate(library):
        x1, y1 = first["deviation"]
        for second_index in range(first_index + 1, len(library)):
            second = library[second_index]
            x2, y2 = second["deviation"]
            determinant = x1 * y2 - x2 * y1
            if not determinant:
                continue
            first_numerator = target[0] * y2 - x2 * target[1]
            second_numerator = x1 * target[1] - target[0] * y1
            if first_numerator % determinant or second_numerator % determinant:
                continue
            first_scale = first_numerator // determinant
            second_scale = second_numerator // determinant
            if first_scale < 0 or second_scale < 0:
                continue
            cost = (
                first_scale * first["length"]
                + second_scale * second["length"]
            )
            candidate = (
                cost,
                first_index,
                second_index,
                first_scale,
                second_scale,
            )
            if best_pair is None or candidate < best_pair:
                best_pair = candidate

    if best_pair is not None:
        cost, first_index, second_index, first_scale, second_scale = best_pair
        multiplicities = [0] * len(library)
        multiplicities[first_index] = first_scale
        multiplicities[second_index] = second_scale
        return {
            "message": "exact two-cycle correction",
            "objective": cost,
        }, multiplicities

    matrix = np.array(
        [[item["deviation"][row] for item in library] for row in range(2)],
        dtype=float,
    )
    objective = np.array([item["length"] for item in library], dtype=float)
    constraint = LinearConstraint(
        csr_matrix(matrix),
        np.array([-deviation[0], -deviation[1]], dtype=float),
        np.array([-deviation[0], -deviation[1]], dtype=float),
    )
    result = milp(
        objective,
        integrality=np.ones(len(library), dtype=np.int8),
        bounds=Bounds(np.zeros(len(library)), np.full(len(library), np.inf)),
        constraints=constraint,
        options={"time_limit": time_limit, "mip_rel_gap": 0.0},
    )
    if not result.success or result.x is None:
        raise RuntimeError(f"integer correction failed: {result.message}")
    multiplicities = np.rint(result.x).astype(object)
    exact = [
        deviation[row]
        + sum(
            int(multiplicities[i]) * library[i]["deviation"][row]
            for i in range(len(library))
        )
        for row in range(2)
    ]
    if exact != [0, 0]:
        raise AssertionError(f"rounded MILP correction is not exact: {exact}")
    return {
        "message": str(result.message),
        "objective": float(result.fun),
    }, [int(value) for value in multiplicities]


def add_scaled(target: Counter[int], source: Counter[int], scale: int) -> None:
    if scale <= 0:
        return
    for edge, multiplicity in source.items():
        target[edge] += scale * multiplicity


def verify_circulation(counts: Counter[int], transitions: np.ndarray):
    incoming = [0] * len(transitions)
    outgoing = [0] * len(transitions)
    letters = [0, 0, 0]
    rows: list[int] = []
    columns: list[int] = []
    for edge, multiplicity in counts.items():
        if multiplicity <= 0:
            raise AssertionError("edge multiplicities must be positive")
        state, index = divmod(edge, 3)
        target = int(transitions[state, index])
        if target < 0:
            raise AssertionError("certificate uses a forbidden DFA edge")
        outgoing[state] += multiplicity
        incoming[target] += multiplicity
        letters[index] += multiplicity
        rows.append(state)
        columns.append(target)
    if incoming != outgoing:
        defects = [
            (state, outgoing[state] - incoming[state])
            for state in range(len(transitions))
            if outgoing[state] != incoming[state]
        ]
        raise AssertionError(f"flow is not balanced: {defects[:10]}")
    length = sum(letters)
    if length % 31:
        raise AssertionError("canonical circulation length is not divisible by 31")
    ray = length // 31
    if letters != [value * ray for value in CANONICAL]:
        raise AssertionError(f"noncanonical letter totals: {letters}")

    support = [state for state, degree in enumerate(outgoing) if degree]
    graph = csr_matrix(
        (np.ones(len(rows), dtype=np.int8), (rows, columns)),
        shape=(len(transitions), len(transitions)),
    )
    _, components = connected_components(
        graph, directed=True, connection="strong"
    )
    support_components = {int(components[state]) for state in support}
    if len(support_components) != 1:
        raise AssertionError(
            f"positive circulation support has {len(support_components)} SCCs"
        )
    return incoming, outgoing, letters, ray, support


def smallest_prime_factors(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    if limit >= 1:
        spf[1] = 1
    for prime in range(2, int(limit**0.5) + 1):
        if spf[prime] != prime:
            continue
        for value in range(prime * prime, limit + 1, prime):
            if spf[value] == value:
                spf[value] = prime
    return spf


def add_factorization(
    exponents: Counter[int], value: int, scale: int, spf: list[int]
) -> None:
    while value > 1:
        prime = spf[value]
        power = 0
        while value % prime == 0:
            value //= prime
            power += 1
        exponents[prime] += scale * power


def entropy_comparison(
    counts: Counter[int], outgoing: list[int], ray: int
):
    maximum = max(max(outgoing), max(counts.values()))
    spf = smallest_prime_factors(maximum)
    exponents: Counter[int] = Counter()
    for degree in outgoing:
        if degree:
            add_factorization(exponents, degree, degree, spf)
    for multiplicity in counts.values():
        add_factorization(exponents, multiplicity, -multiplicity, spf)
    exponents[2] -= CANONICAL[0] * ray
    exponents[3] -= CANONICAL[1] * ray
    exponents[5] -= CANONICAL[2] * ray
    exponents = Counter(
        {prime: exponent for prime, exponent in exponents.items() if exponent}
    )

    numerator = 1
    denominator = 1
    for prime, exponent in sorted(exponents.items()):
        if exponent > 0:
            numerator *= prime**exponent
        else:
            denominator *= prime ** (-exponent)
    log_gap = sum(exponent * math.log(prime) for prime, exponent in exponents.items())
    return {
        "exact_above_Q": numerator > denominator,
        "log_gap": log_gap,
        "log_ratio_per_k": log_gap / ray,
        "ratio_per_k": math.exp(log_gap / ray),
        "numerator_bits": numerator.bit_length(),
        "denominator_bits": denominator.bit_length(),
        "numerator_sha256": hashlib.sha256(
            numerator.to_bytes((numerator.bit_length() + 7) // 8, "big")
        ).hexdigest(),
        "denominator_sha256": hashlib.sha256(
            denominator.to_bytes((denominator.bit_length() + 7) // 8, "big")
        ).hexdigest(),
        "prime_exponents": [
            [prime, exponent] for prime, exponent in sorted(exponents.items())
        ],
    }


def edge_digest(counts: Counter[int], transitions: np.ndarray) -> str:
    digest = hashlib.sha256()
    for edge, multiplicity in sorted(counts.items()):
        state, index = divmod(edge, 3)
        target = int(transitions[state, index])
        digest.update(
            f"{state},{ALPHABET[index]},{target},{multiplicity}\n".encode("ascii")
        )
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--relations", type=Path, required=True)
    parser.add_argument("--walk-length", type=int, default=200_000)
    parser.add_argument("--random-cycles", type=int, default=700)
    parser.add_argument("--seed", type=int, default=42441)
    parser.add_argument("--milp-time-limit", type=float, default=120.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    relation_data = json.loads(args.relations.read_text(encoding="ascii"))
    automaton = PatternAutomaton(relation_data["minimal_sides"])
    transitions, labels, root = automaton.safe_dfa()
    component_count, component, sizes, component_id, members = largest_scc(
        transitions
    )
    recurrent = restrict_to_component(transitions, component, component_id)

    theta = np.array(
        [
            relation_data["numeric_pressure"]["theta_3"],
            relation_data["numeric_pressure"]["theta_5"],
        ]
    )
    eigenvalue, left, right = perron(recurrent, theta, iterations=5000)
    start, probabilities, stationary = edge_probabilities(
        recurrent, theta, left, right
    )
    if int(component[start]) != component_id:
        raise AssertionError("Perron start state is outside the recurrent core")
    parent_state, parent_letter, return_target, return_letter = shortest_trees(
        recurrent, members, start
    )

    rng = random.Random(args.seed)
    base = sampled_cycle(
        recurrent,
        probabilities,
        start,
        args.walk_length,
        rng,
        return_target,
        return_letter,
    )
    library = correction_library(
        recurrent,
        members,
        probabilities,
        start,
        parent_state,
        parent_letter,
        return_target,
        return_letter,
        rng,
        args.random_cycles,
    )
    correction, multiplicities = solve_correction(
        base, library, args.milp_time_limit
    )

    final = Counter(base)
    selected = []
    for item, multiplicity in zip(library, multiplicities):
        if not multiplicity:
            continue
        add_scaled(final, item["counts"], multiplicity)
        selected.append(
            {
                "deviation": list(item["deviation"]),
                "cycle_length": item["length"],
                "multiplicity": multiplicity,
            }
        )

    incoming, outgoing, letters, ray, support = verify_circulation(
        final, recurrent
    )
    comparison = entropy_comparison(final, outgoing, ray)
    edge_rows = []
    for edge, multiplicity in sorted(final.items()):
        state, index = divmod(edge, 3)
        edge_rows.append(
            {
                "source": state,
                "letter": ALPHABET[index],
                "target": int(recurrent[state, index]),
                "multiplicity": multiplicity,
            }
        )

    base_letters, base_length, base_deviation = cycle_statistics(base)
    payload = {
        "schema_version": 1,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "relations_path": str(args.relations),
        "relation_fibers_sha256": relation_data["relation_fibers_sha256"],
        "minimal_sides_sha256": relation_data["minimal_sides_sha256"],
        "parameters": {
            "walk_length": args.walk_length,
            "random_cycles": args.random_cycles,
            "seed": args.seed,
            "milp_time_limit": args.milp_time_limit,
        },
        "automaton": {
            "safe_states": len(transitions),
            "component_count": component_count,
            "recurrent_states": int(sizes[component_id]),
            "start_state": start,
            "start_label": labels[start],
            "numeric_lambda": eigenvalue,
            "stationary_mass_at_start": float(stationary[start] / np.sum(stationary)),
        },
        "search": {
            "base_length": base_length,
            "base_letter_counts": base_letters,
            "base_deviation": list(base_deviation),
            "base_edges": len(base),
            "correction_library": len(library),
            "correction_message": correction["message"],
            "correction_objective": correction["objective"],
            "selected_corrections": selected,
        },
        "certificate": {
            "gate_passed": comparison["exact_above_Q"],
            "total_length": sum(letters),
            "canonical_k": ray,
            "letter_counts": letters,
            "support_states": len(support),
            "support_edges": len(final),
            "balanced": incoming == outgoing,
            "strongly_connected": True,
            "edge_sha256": edge_digest(final, recurrent),
            "entropy_comparison": comparison,
            "edges": edge_rows,
        },
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.output.write_text(rendered + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "canonical_k": ray,
                "support_states": len(support),
                "support_edges": len(final),
                "log_gap": comparison["log_gap"],
                "ratio_per_k": comparison["ratio_per_k"],
                "edge_sha256": payload["certificate"]["edge_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
