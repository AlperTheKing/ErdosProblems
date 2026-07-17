"""Correlated carry potentials for the affine offset inverse branches.

For a potential phi on residues modulo Q and nonnegative branch weights
alpha_m, every integer d with residue r has one lift t modulo 30Q.  Hence

  sum_{m | d-q_m} alpha_m phi((d-q_m)/m mod Q)

is one of only 30 correlated actions attached to r.  A positive vector with
every action <= lambda*phi(r) is therefore an exact Bellman certificate; it
keeps the parent residues correlated, unlike independent residue suprema.

The canonical letter proportions (15,10,6)/31 give equal normalized branch
weights alpha_2=alpha_3=alpha_5=30/31.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


BRANCHES = ((2, 0), (3, 1), (5, 3))
CANONICAL_ALPHA = (
    Fraction(30, 31),
    Fraction(30, 31),
    Fraction(30, 31),
)


def reachable_residues(modulus: int) -> list[int]:
    reached = {0}
    frontier = [0]
    while frontier:
        residue = frontier.pop()
        for multiplier, shift in BRANCHES:
            image = (multiplier * residue + shift) % modulus
            if image not in reached:
                reached.add(image)
                frontier.append(image)
    return sorted(reached)


def build_actions(modulus: int):
    residues = reachable_residues(modulus)
    state_of = {residue: state for state, residue in enumerate(residues)}
    actions: list[list[tuple[tuple[int, int], ...]]] = []

    for residue in residues:
        state_actions = set()
        for carry in range(30):
            lifted = residue + modulus * carry
            action = []
            for index, (multiplier, shift) in enumerate(BRANCHES):
                if (lifted - shift) % multiplier != 0:
                    continue
                parent = ((lifted - shift) // multiplier) % modulus
                parent_state = state_of.get(parent)
                if parent_state is not None:
                    action.append((index, parent_state))
            state_actions.add(tuple(action))
        actions.append(sorted(state_actions))
    return residues, actions


def exact_action_checks(
    modulus: int,
    residues: list[int],
    actions,
    limit: int,
) -> int:
    state_of = {residue: state for state, residue in enumerate(residues)}
    checks = 0
    for value in range(limit + 1):
        state = state_of.get(value % modulus)
        if state is None:
            continue
        actual = []
        for index, (multiplier, shift) in enumerate(BRANCHES):
            if (value - shift) % multiplier == 0:
                parent = ((value - shift) // multiplier) % modulus
                parent_state = state_of.get(parent)
                if parent_state is not None:
                    actual.append((index, parent_state))
        assert tuple(actual) in actions[state]
        checks += 1
    return checks


def constraint_matrix(actions, alpha, eigenvalue: float):
    rows = []
    columns = []
    data = []
    row = 0
    for state, state_actions in enumerate(actions):
        for action in state_actions:
            for branch, parent in action:
                rows.append(row)
                columns.append(parent)
                data.append(float(alpha[branch]))
            rows.append(row)
            columns.append(state)
            data.append(-eigenvalue)
            row += 1
    matrix = coo_matrix(
        (data, (rows, columns)), shape=(row, len(actions))
    ).tocsr()
    return matrix


def feasible(actions, alpha, eigenvalue: float):
    matrix = constraint_matrix(actions, alpha, eigenvalue)
    root = np.zeros((1, len(actions)))
    root[0, 0] = 1.0
    result = linprog(
        np.zeros(len(actions)),
        A_ub=matrix,
        b_ub=np.zeros(matrix.shape[0]),
        A_eq=root,
        b_eq=np.ones(1),
        bounds=(1e-9, 1e9),
        method="highs",
        options={"dual_feasibility_tolerance": 1e-9},
    )
    return result


def critical_potential(actions, alpha):
    lower = 0.0
    upper = sum(float(value) for value in alpha)
    best = None
    for _ in range(45):
        middle = (lower + upper) / 2.0
        result = feasible(actions, alpha, middle)
        if result.success:
            upper = middle
            best = result
        else:
            lower = middle
    if best is None:
        best = feasible(actions, alpha, upper)
    return lower, upper, best


def rational_certificate(actions, alpha, potential):
    positive = potential[potential > 0]
    minimum = float(np.min(positive))
    scale = 10**9
    integer_potential = [
        max(1, math.ceil(float(value) / minimum * scale))
        for value in potential
    ]

    ratios = []
    locations = []
    for state, state_actions in enumerate(actions):
        for action_index, action in enumerate(state_actions):
            image = sum(
                alpha[branch] * integer_potential[parent]
                for branch, parent in action
            )
            ratio = image / integer_potential[state]
            ratios.append(ratio)
            locations.append((state, action_index))
    bound = max(ratios)
    location = locations[ratios.index(bound)]
    return {
        "lambda_numerator": str(bound.numerator),
        "lambda_denominator": str(bound.denominator),
        "lambda_float": float(bound),
        "exact_at_most_one": bound <= 1,
        "max_state": location[0],
        "max_action": location[1],
        "potential_sha256": hashlib.sha256(
            ",".join(str(value) for value in integer_potential).encode(
                "ascii"
            )
        ).hexdigest(),
        "potential": integer_potential if bound <= 1 else None,
    }


def run_modulus(modulus: int, check_limit: int):
    residues, actions = build_actions(modulus)
    checks = exact_action_checks(
        modulus, residues, actions, check_limit
    )
    lower, upper, result = critical_potential(
        actions, CANONICAL_ALPHA
    )
    certificate = rational_certificate(
        actions, CANONICAL_ALPHA, result.x
    )
    return {
        "modulus": modulus,
        "reachable_states": len(residues),
        "distinct_actions": sum(len(item) for item in actions),
        "exact_action_checks": checks,
        "lp_lower": lower,
        "lp_upper": upper,
        "lp_status": int(result.status),
        "lp_message": result.message,
        "certificate": certificate,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moduli", default="30,150,900")
    parser.add_argument("--check-limit", type=int, default=100_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    moduli = [int(item) for item in args.moduli.split(",")]
    result = {
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "canonical_alpha": [
            f"{value.numerator}/{value.denominator}"
            for value in CANONICAL_ALPHA
        ],
        "results": [
            run_modulus(modulus, args.check_limit)
            for modulus in moduli
        ],
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output is not None:
        args.output.write_text(rendered + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
