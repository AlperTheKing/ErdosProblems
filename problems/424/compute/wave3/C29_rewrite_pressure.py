"""Finite rewrite-language upper bound for affine offset supports.

Every exact equal-count identity u=v can be oriented from the lexicographically
larger word to the smaller word.  A lexicographically minimal representative of
an affine map avoids every oriented left side.  Thus D_(a,b,c) is at most the
number of multiset words avoiding any finite collection of such left sides.

This script discovers identities through a chosen length, removes rules whose
left side already contains a shorter forbidden pattern, builds the exact
Aho--Corasick avoidance automaton, and minimizes its weighted pressure on the
ray (3,2,1).  It then constructs a rational Collatz--Wielandt certificate
A*h <= lambda*h.  The strict exact inequality

    lambda^6 < 360*y^2*z

would be an exponential falsifier for the mass gate on that ray.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import deque
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import minimize


ALPHABET = "235"
SHIFT = {"2": 0, "3": 1, "5": 3}
LETTER_INDEX = {"2": 0, "3": 1, "5": 2}


def word_offset(word: str) -> int:
    value = 0
    for letter in reversed(word):
        value = int(letter) * value + SHIFT[letter]
    return value


def word_counts(word: str) -> tuple[int, int, int]:
    return word.count("2"), word.count("3"), word.count("5")


def discover(max_rule_length: int):
    support_sizes: list[dict[tuple[int, int, int], int]] = [
        {(0, 0, 0): 1}
    ]
    candidates: list[tuple[str, str]] = []
    class_counts = []

    for length in range(1, max_rule_length + 1):
        representatives: dict[
            tuple[tuple[int, int, int], int], str
        ] = {}
        for letters in itertools.product(ALPHABET, repeat=length):
            word = "".join(letters)
            key = word_counts(word), word_offset(word)
            representative = representatives.get(key)
            if representative is None:
                representatives[key] = word
            else:
                assert representative < word
                candidates.append((word, representative))

        sizes: dict[tuple[int, int, int], int] = {}
        for counts, _ in representatives:
            sizes[counts] = sizes.get(counts, 0) + 1
        support_sizes.append(sizes)
        class_counts.append(
            {
                "length": length,
                "formal_words": 3**length,
                "affine_classes": len(representatives),
                "collisions": 3**length - len(representatives),
            }
        )

    rules: list[tuple[str, str]] = []
    forbidden: list[str] = []
    for left, right in candidates:
        if any(pattern in left for pattern in forbidden):
            continue
        assert len(left) == len(right)
        assert word_counts(left) == word_counts(right)
        assert word_offset(left) == word_offset(right)
        rules.append((left, right))
        forbidden.append(left)

    return support_sizes, class_counts, rules


def avoidance_automaton(patterns: list[str]):
    children: list[dict[str, int]] = [{}]
    failure = [0]
    terminal = [False]

    for pattern in patterns:
        state = 0
        for letter in pattern:
            next_state = children[state].get(letter)
            if next_state is None:
                next_state = len(children)
                children[state][letter] = next_state
                children.append({})
                failure.append(0)
                terminal.append(False)
            state = next_state
        terminal[state] = True

    transitions = [[0, 0, 0] for _ in children]
    queue: deque[int] = deque()
    for letter in ALPHABET:
        index = LETTER_INDEX[letter]
        child = children[0].get(letter)
        if child is None:
            transitions[0][index] = 0
        else:
            transitions[0][index] = child
            queue.append(child)

    while queue:
        state = queue.popleft()
        terminal[state] = terminal[state] or terminal[failure[state]]
        for letter in ALPHABET:
            index = LETTER_INDEX[letter]
            child = children[state].get(letter)
            if child is None:
                transitions[state][index] = transitions[failure[state]][index]
            else:
                failure[child] = transitions[failure[state]][index]
                transitions[state][index] = child
                queue.append(child)

    safe = [state for state in range(len(children)) if not terminal[state]]
    remap = {old: new for new, old in enumerate(safe)}
    safe_transitions = np.full((len(safe), 3), -1, dtype=np.int64)
    for old_state in safe:
        state = remap[old_state]
        for index in range(3):
            old_target = transitions[old_state][index]
            if not terminal[old_target]:
                safe_transitions[state, index] = remap[old_target]
    return safe_transitions


def accepted_by_counts(transitions: np.ndarray, max_length: int):
    current: dict[tuple[int, int, int, int], int] = {(0, 0, 0, 0): 1}
    layers = [{(0, 0, 0): 1}]
    for _ in range(max_length):
        following: dict[tuple[int, int, int, int], int] = {}
        for (state, a, b, c), multiplicity in current.items():
            for index in range(3):
                target = int(transitions[state, index])
                if target < 0:
                    continue
                counts = [a, b, c]
                counts[index] += 1
                key = (target, *counts)
                following[key] = following.get(key, 0) + multiplicity
        current = following
        totals: dict[tuple[int, int, int], int] = {}
        for (_, a, b, c), multiplicity in current.items():
            counts = (a, b, c)
            totals[counts] = totals.get(counts, 0) + multiplicity
        layers.append(totals)
    return layers


def apply_right(
    transitions: np.ndarray, weights: np.ndarray, vector: np.ndarray
) -> np.ndarray:
    result = np.zeros_like(vector)
    for index in range(3):
        targets = transitions[:, index]
        valid = targets >= 0
        result[valid] += weights[index] * vector[targets[valid]]
    return result


def apply_left(
    transitions: np.ndarray, weights: np.ndarray, vector: np.ndarray
) -> np.ndarray:
    result = np.zeros_like(vector)
    for index in range(3):
        targets = transitions[:, index]
        valid = targets >= 0
        np.add.at(result, targets[valid], weights[index] * vector[valid])
    return result


def perron(
    transitions: np.ndarray, theta: np.ndarray, iterations: int = 1000
):
    weights = np.array([1.0, math.exp(theta[0]), math.exp(theta[1])])
    size = len(transitions)
    right = np.ones(size)
    left = np.ones(size)

    for _ in range(iterations):
        new_right = apply_right(transitions, weights, right)
        new_right /= np.max(new_right)
        new_left = apply_left(transitions, weights, left)
        new_left /= np.max(new_left)
        error = max(
            np.max(np.abs(new_right - right)),
            np.max(np.abs(new_left - left)),
        )
        right, left = new_right, new_left
        if error < 1e-13:
            break

    image = apply_right(transitions, weights, right)
    denominator = float(np.dot(left, right))
    eigenvalue = float(np.dot(left, image) / denominator)
    return eigenvalue, right


def optimize_pressure(transitions: np.ndarray):
    cache: dict[tuple[float, float], float] = {}

    def objective(theta):
        key = (float(theta[0]), float(theta[1]))
        if key not in cache:
            eigenvalue, _ = perron(transitions, np.asarray(theta))
            cache[key] = (
                6.0 * math.log(eigenvalue) - 2.0 * theta[0] - theta[1]
            )
        return cache[key]

    initial = np.array([math.log(2.0 / 3.0), math.log(1.0 / 3.0)])
    result = minimize(
        objective,
        initial,
        method="Nelder-Mead",
        options={"maxiter": 160, "xatol": 1e-11, "fatol": 1e-12},
    )
    eigenvalue, right = perron(transitions, result.x, iterations=3000)
    return result, eigenvalue, right


def rational_certificate(
    transitions: np.ndarray, theta: np.ndarray, right: np.ndarray
):
    y = Fraction(math.exp(theta[0])).limit_denominator(1_000_000)
    z = Fraction(math.exp(theta[1])).limit_denominator(1_000_000)
    weights = (Fraction(1), y, z)

    positive = right[right > 0]
    minimum = float(np.min(positive))
    scale = 10**10
    h = [max(1, math.ceil(float(value) / minimum * scale)) for value in right]

    ratios: list[Fraction] = []
    for state in range(len(transitions)):
        image = Fraction(0)
        for index in range(3):
            target = int(transitions[state, index])
            if target >= 0:
                image += weights[index] * h[target]
        ratios.append(image / h[state])
    eigenvalue_bound = max(ratios)
    max_state = ratios.index(eigenvalue_bound)
    exact_ratio = eigenvalue_bound**6 / (Fraction(360) * y**2 * z)
    return {
        "rational_y": f"{y.numerator}/{y.denominator}",
        "rational_z": f"{z.numerator}/{z.denominator}",
        "lambda_numerator": str(eigenvalue_bound.numerator),
        "lambda_denominator": str(eigenvalue_bound.denominator),
        "max_state": max_state,
        "base_per_k_upper": float(eigenvalue_bound**6 / (y**2 * z)),
        "ratio_to_360": float(exact_ratio),
        "exact_below_360": exact_ratio < 1,
        "vector_sha256": hashlib.sha256(
            ",".join(str(value) for value in h).encode("ascii")
        ).hexdigest(),
        "vector": h if exact_ratio < 1 else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rule-length", type=int, default=12)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    support_sizes, class_counts, rules = discover(args.max_rule_length)
    transitions = avoidance_automaton([left for left, _ in rules])
    accepted = accepted_by_counts(transitions, args.max_rule_length)

    checks = []
    for length in range(args.max_rule_length + 1):
        for counts, support in support_sizes[length].items():
            normal_forms = accepted[length].get(counts, 0)
            assert normal_forms >= support
            checks.append((length, counts, support, normal_forms))

    optimization, eigenvalue, right = optimize_pressure(transitions)
    certificate = rational_certificate(
        transitions, optimization.x, right
    )

    result = {
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "max_rule_length": args.max_rule_length,
        "class_counts": class_counts,
        "candidate_rule_count": sum(item["collisions"] for item in class_counts),
        "minimal_forbidden_rule_count": len(rules),
        "automaton_safe_states": len(transitions),
        "rules": [{"left": left, "right": right} for left, right in rules],
        "support_upper_checks": len(checks),
        "largest_checked_slack": max(
            normal_forms - support
            for _, _, support, normal_forms in checks
        ),
        "optimization": {
            "success": bool(optimization.success),
            "message": str(optimization.message),
            "theta_y": float(optimization.x[0]),
            "theta_z": float(optimization.x[1]),
            "numeric_lambda": eigenvalue,
            "numeric_base_per_k": math.exp(float(optimization.fun)),
            "iterations": int(optimization.nit),
        },
        "certificate": certificate,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output is not None:
        args.output.write_text(rendered + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
