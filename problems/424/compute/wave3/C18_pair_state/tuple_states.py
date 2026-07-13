"""Exact affine-parameter transition graph for pair and triple orbit states."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import product
from math import gcd, lcm


GENERATORS = (2, 3, 5)


@dataclass(frozen=True, order=True)
class Form:
    slope: int
    intercept: int


@dataclass(frozen=True, order=True)
class TupleState:
    forms: tuple[Form, ...]


ROOTS = {
    "P23": TupleState((Form(2, 0), Form(3, 0))),
    "P25": TupleState((Form(2, 0), Form(5, 0))),
    "P35": TupleState((Form(3, 0), Form(5, 0))),
    "P235": TupleState((Form(6, 0), Form(10, 0), Form(15, 0))),
}


def canonical(forms: tuple[Form, ...]) -> TupleState:
    """Canonicalize permutation and an integral shift of the parameter."""

    ordered = sorted(forms)
    anchor = ordered[0]
    shift = anchor.intercept // anchor.slope
    shifted = tuple(
        Form(form.slope, form.intercept - form.slope * shift) for form in ordered
    )
    return TupleState(tuple(sorted(shifted)))


def linear_congruence(form: Form, generator: int) -> tuple[int, int] | None:
    """Solve ``form(t) + 1 == 0 (mod generator)`` as ``t == r (mod m)``."""

    common = gcd(form.slope, generator)
    target = -(form.intercept + 1)
    if target % common:
        return None
    modulus = generator // common
    if modulus == 1:
        return (0, 1)
    coefficient = form.slope // common
    residue = (target // common) * pow(coefficient, -1, modulus) % modulus
    return residue, modulus


def transition(
    state: TupleState, generators: tuple[int, ...]
) -> tuple[int, int, TupleState] | None:
    """Return ``(modulus, residue, parent_state)`` for one map assignment."""

    congruences = []
    modulus = 1
    for form, generator in zip(state.forms, generators, strict=True):
        congruence = linear_congruence(form, generator)
        if congruence is None:
            return None
        congruences.append(congruence)
        modulus = lcm(modulus, congruence[1])

    residues = [
        candidate
        for candidate in range(modulus)
        if all(candidate % mod == residue for residue, mod in congruences)
    ]
    if not residues:
        return None
    if len(residues) != 1:
        raise AssertionError((state, generators, residues))
    residue = residues[0]

    parents = []
    for form, generator in zip(state.forms, generators, strict=True):
        slope = form.slope * modulus // generator
        intercept = (form.slope * residue + form.intercept + 1) // generator
        parents.append(Form(slope, intercept))
    return modulus, residue, canonical(tuple(parents))


def enumerate_states(root: TupleState, max_depth: int) -> dict[TupleState, int]:
    depth = {root: 0}
    frontier = {root}
    for level in range(max_depth):
        following = set()
        for state in frontier:
            for generators in product(GENERATORS, repeat=len(state.forms)):
                result = transition(state, generators)
                if result is None:
                    continue
                child = result[2]
                if child not in depth:
                    depth[child] = level + 1
                    following.add(child)
        frontier = following
    return depth


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", choices=ROOTS, required=True)
    parser.add_argument("--depth", type=int, required=True)
    args = parser.parse_args()

    root = ROOTS[args.root]
    depth = enumerate_states(root, args.depth)
    cumulative = 0
    print("depth\tnew\tcumulative\tmax_slope\tmax_abs_intercept")
    for level in range(args.depth + 1):
        states = [state for state, value in depth.items() if value == level]
        cumulative += len(states)
        print(
            level,
            len(states),
            cumulative,
            max((form.slope for state in states for form in state.forms), default=0),
            max(
                (abs(form.intercept) for state in states for form in state.forms),
                default=0,
            ),
            sep="\t",
        )

    print("\nroot transitions")
    for generators in product(GENERATORS, repeat=len(root.forms)):
        result = transition(root, generators)
        if result is not None:
            print(f"maps={generators}\tmod={result[0]}\tres={result[1]}\t{result[2]!r}")


if __name__ == "__main__":
    main()
