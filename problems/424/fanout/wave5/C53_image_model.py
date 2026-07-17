#!/usr/bin/env python3
"""Exact abstract-image SAT search for Problem 424, task C53.

The abstract universe is an ordered initial segment of a commutative partial
multiplication table.  For every distinct pair (a,b), ``product[a,b]`` is
either a later vertex representing ``ab-1`` or the common overflow symbol.
The descending sets are defined by the exact biconditional S[t+1] = F(S[t]).

The script searches increasing universe sizes for violations of the
additive-one rank-prefix inequality and its canonical cap-two strengthening.
It also replays every SAT witness without OR-Tools and checks the encoding on
literal integer prefixes of the actual Problem 424 closure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from ortools.sat.python import cp_model


SEED2 = 0
SEED3 = 1


def and_var(
    model: cp_model.CpModel,
    literals: Iterable[cp_model.Literal],
    name: str,
) -> cp_model.IntVar:
    """Return a Boolean exactly equal to the conjunction of literals."""
    items = list(literals)
    out = model.new_bool_var(name)
    for literal in items:
        model.add_implication(out, literal)
    model.add_bool_or([out] + [literal.Not() for literal in items])
    return out


def or_var(
    model: cp_model.CpModel,
    literals: Iterable[cp_model.Literal],
    name: str,
) -> cp_model.IntVar:
    """Return a Boolean exactly equal to the disjunction of literals."""
    items = list(literals)
    out = model.new_bool_var(name)
    if not items:
        model.add(out == 0)
        return out
    for literal in items:
        model.add_implication(literal, out)
    model.add_bool_or(items + [out.Not()])
    return out


@dataclass
class SatInstance:
    model: cp_model.CpModel
    size: int
    rank_cutoff: int
    mode: str
    output: dict[tuple[int, int], cp_model.IntVar]
    output_is: dict[tuple[int, int, int], cp_model.IntVar]
    even: list[cp_model.IntVar]
    residue_mod9: list[cp_model.IntVar]
    residue_zero: list[cp_model.IntVar]
    alive: list[list[cp_model.IntVar]]
    hard: list[cp_model.IntVar]
    root: dict[tuple[int, int], cp_model.IntVar]
    hard_events: list[cp_model.IntVar]
    target_events: list[cp_model.IntVar]
    cap_two_events: list[cp_model.IntVar]


def build_sat(size: int, rank_cutoff: int, mode: str) -> SatInstance:
    """Build one exact finite satisfiability instance.

    ``mode`` is ``additive_one`` or ``cap_two``.  Vertex ``size`` is the
    overflow value and is not itself in the universe.
    """
    if size < 3:
        raise ValueError("size must be at least 3")
    if not 0 <= rank_cutoff < size:
        raise ValueError("rank cutoff must lie in [0,size)")
    if mode not in {"additive_one", "cap_two"}:
        raise ValueError(mode)

    model = cp_model.CpModel()
    output: dict[tuple[int, int], cp_model.IntVar] = {}
    output_is: dict[tuple[int, int, int], cp_model.IntVar] = {}

    # Every distinct pair has one later output or overflows the prefix.
    for a in range(size):
        for b in range(a + 1, size):
            out = model.new_int_var(b + 1, size, f"out_{a}_{b}")
            output[a, b] = out
            choices = []
            for n in range(b + 1, size + 1):
                flag = model.new_bool_var(f"out_{a}_{b}_is_{n}")
                model.add(out == n).only_enforce_if(flag)
                model.add(out != n).only_enforce_if(flag.Not())
                output_is[a, b, n] = flag
                choices.append(flag)
            model.add_exactly_one(choices)

    # Strict monotonicity in either parent while the larger product remains
    # finite.  Equality at the common overflow symbol is allowed.
    for x in range(size):
        others = [y for y in range(size) if y != x]
        for y, z in zip(others, others[1:]):
            p = tuple(sorted((x, y)))
            q = tuple(sorted((x, z)))
            model.add(output[p] <= output[q])
            q_finite = output_is[q[0], q[1], size].Not()
            model.add(output[p] < output[q]).only_enforce_if(q_finite)

    even = [model.new_bool_var(f"even_{n}") for n in range(size)]
    allowed_residues = (0, 2, 3, 5, 6, 8)
    residue_mod9 = [
        model.new_int_var_from_domain(
            cp_model.Domain.from_values(allowed_residues), f"residue_mod9_{n}"
        )
        for n in range(size)
    ]
    residue_is: dict[tuple[int, int], cp_model.IntVar] = {}
    residue_zero = [
        model.new_bool_var(f"residue_zero_{n}") for n in range(size)
    ]
    model.add(even[SEED2] == 1)
    model.add(residue_mod9[SEED2] == 2)
    model.add(residue_zero[SEED2] == 0)
    model.add(even[SEED3] == 0)
    model.add(residue_mod9[SEED3] == 3)
    model.add(residue_zero[SEED3] == 1)
    for n in range(size):
        choices = []
        for residue in allowed_residues:
            flag = model.new_bool_var(f"residue_{n}_is_{residue}")
            model.add(residue_mod9[n] == residue).only_enforce_if(flag)
            model.add(residue_mod9[n] != residue).only_enforce_if(flag.Not())
            residue_is[n, residue] = flag
            choices.append(flag)
        model.add_exactly_one(choices)
        model.add(
            residue_zero[n]
            == sum(residue_is[n, residue] for residue in (0, 3, 6))
        )

    # For allowed residues 0,2 mod 3, ab-1 has residue zero exactly when
    # both inputs have residue two.  It is even exactly when both inputs are
    # odd.  These pair types are shared by every finite collision output.
    pair_even: dict[tuple[int, int], cp_model.IntVar] = {}
    residue_product_rows = [
        (ra, rb, (ra * rb - 1) % 9)
        for ra in allowed_residues
        for rb in allowed_residues
    ]
    for (a, b), _ in output.items():
        pair_even[a, b] = and_var(
            model, [even[a].Not(), even[b].Not()], f"pair_even_{a}_{b}"
        )
        for n in range(b + 1, size):
            flag = output_is[a, b, n]
            model.add(even[n] == pair_even[a, b]).only_enforce_if(flag)
            model.add_allowed_assignments(
                [residue_mod9[a], residue_mod9[b], residue_mod9[n]],
                residue_product_rows,
            ).only_enforce_if(flag)

    # Any genuine prefix containing a third allowed value contains 5=2*3-1.
    model.add(output[SEED2, SEED3] < size)

    # Every nonseed odd allowed integer has its unique distinct seed-2
    # factorization.  Pair functionality makes the predecessor unique.
    for n in range(2, size):
        incoming = [
            output_is[SEED2, q, n]
            for q in range(1, n)
            if (SEED2, q, n) in output_is
        ]
        model.add(sum(incoming) + even[n] == 1)

    incoming_pairs: list[list[tuple[int, int]]] = [[] for _ in range(size)]
    for a in range(size):
        for b in range(a + 1, size):
            for n in range(b + 1, size):
                incoming_pairs[n].append((a, b))

    has_pair: list[cp_model.IntVar] = []
    seed3_pair: list[cp_model.IntVar] = []
    hard: list[cp_model.IntVar] = []
    for n in range(size):
        pair_flags = [output_is[a, b, n] for a, b in incoming_pairs[n]]
        hp = or_var(model, pair_flags, f"has_pair_{n}")
        has_pair.append(hp)
        seed3_flags = [
            output_is[min(SEED3, q), max(SEED3, q), n]
            for q in range(n)
            if q != SEED3
            and (min(SEED3, q), max(SEED3, q), n) in output_is
        ]
        sp = or_var(model, seed3_flags, f"seed3_pair_{n}")
        seed3_pair.append(sp)
        # For an even reducible allowed integer, the seed-3 factorization is
        # available exactly in residues 5 or 8 modulo 9.  Residue 8 includes
        # n=8, but that value has no distinct factor pair, so hp excludes it.
        easy_residue = or_var(
            model,
            [residue_is[n, 5], residue_is[n, 8]],
            f"easy_residue_{n}",
        )
        seed3_complete = and_var(
            model, [even[n], hp, easy_residue], f"seed3_complete_{n}"
        )
        model.add(sp == seed3_complete).only_enforce_if(even[n])
        hard.append(
            and_var(model, [even[n], hp, sp.Not()], f"hard_{n}")
        )

    # Literal descending images.  No one-way Horn relaxation appears here:
    # every S[t+1,n] is equivalent to the OR of all supported factor pairs.
    alive = [
        [model.new_bool_var(f"alive_{t}_{n}") for n in range(size)]
        for t in range(size + 1)
    ]
    for n in range(size):
        model.add(alive[0][n] == 1)
    for t in range(size):
        model.add(alive[t + 1][SEED2] == 1)
        model.add(alive[t + 1][SEED3] == 1)
        for n in range(2, size):
            witnesses = []
            for a, b in incoming_pairs[n]:
                witnesses.append(
                    and_var(
                        model,
                        [output_is[a, b, n], alive[t][a], alive[t][b]],
                        f"wit_{t}_{a}_{b}_{n}",
                    )
                )
            supported = or_var(model, witnesses, f"supported_{t}_{n}")
            model.add(alive[t + 1][n] == supported)

    # A parent-DAG on size vertices stabilizes by this point.  Keeping the
    # equality explicit makes accidental rank truncation impossible.
    for n in range(size):
        if n < 2:
            continue
        support_final = []
        for a, b in incoming_pairs[n]:
            support_final.append(
                and_var(
                    model,
                    [output_is[a, b, n], alive[size][a], alive[size][b]],
                    f"final_wit_{a}_{b}_{n}",
                )
            )
        fixed_support = or_var(model, support_final, f"fixed_support_{n}")
        model.add(alive[size][n] == fixed_support)

    hole = [model.new_bool_var(f"hole_{n}") for n in range(size)]
    for n in range(size):
        model.add(hole[n] + alive[size][n] == 1)

    # Canonical hole parent: seed 2 for odd holes, seed 3 for reducible
    # nonhard even holes.  Splitless and hard holes are roots.
    canonical_edge: dict[tuple[int, int], cp_model.IntVar] = {}
    for q in range(size):
        for n in range(q + 1, size):
            pieces = []
            key2 = tuple(sorted((SEED2, q)))
            if q != SEED2 and (key2[0], key2[1], n) in output_is:
                pieces.append(
                    and_var(
                        model,
                        [hole[n], output_is[key2[0], key2[1], n]],
                        f"canon2_{q}_{n}",
                    )
                )
            key3 = tuple(sorted((SEED3, q)))
            if q != SEED3 and (key3[0], key3[1], n) in output_is:
                pieces.append(
                    and_var(
                        model,
                        [
                            hole[n],
                            even[n],
                            has_pair[n],
                            seed3_pair[n],
                            output_is[key3[0], key3[1], n],
                        ],
                        f"canon3_{q}_{n}",
                    )
                )
            canonical_edge[q, n] = or_var(
                model, pieces, f"canonical_edge_{q}_{n}"
            )

    root: dict[tuple[int, int], cp_model.IntVar] = {}
    for n in range(size):
        for r in range(n + 1):
            root[n, r] = model.new_bool_var(f"root_{n}_{r}")
        model.add(sum(root[n, r] for r in range(n + 1)) == hole[n])
        parent_edges = [canonical_edge[q, n] for q in range(n)]
        has_parent = or_var(model, parent_edges, f"has_canonical_parent_{n}")
        root_here = and_var(
            model, [hole[n], has_parent.Not()], f"root_here_{n}"
        )
        model.add(root[n, n] == root_here)
        for r in range(n):
            inherited = []
            for q in range(r, n):
                inherited.append(
                    and_var(
                        model,
                        [canonical_edge[q, n], root[q, r]],
                        f"inherit_{q}_{n}_{r}",
                    )
                )
            inherited_root = or_var(model, inherited, f"inherited_{n}_{r}")
            model.add(root[n, r] == inherited_root)

    # Rank-prefix hard events.
    hard_events = [
        and_var(
            model,
            [hard[n], alive[rank_cutoff + 1][n].Not()],
            f"hard_event_{n}",
        )
        for n in range(size)
    ]

    # Terminal seed-2 boundaries, indexed by their child coordinate.
    target: dict[tuple[int, int], cp_model.IntVar] = {}
    target_rank_event: dict[tuple[int, int], cp_model.IntVar] = {}
    for q in range(1, size):
        for child in range(q + 1, size):
            key = (SEED2, q, child)
            if key not in output_is:
                continue
            target[q, child] = and_var(
                model,
                [output_is[key], hole[q], alive[size][child]],
                f"target_{q}_{child}",
            )
            target_rank_event[q, child] = and_var(
                model,
                [target[q, child], alive[rank_cutoff + 1][q].Not()],
                f"target_rank_{q}_{child}",
            )
    target_events = list(target_rank_event.values())

    # Root-labelled target events and the first-two selector.  Selection is
    # by child coordinate before applying the rank cutoff, exactly as in C43.
    target_root: dict[tuple[int, int, int], cp_model.IntVar] = {}
    event_at_root: dict[tuple[int, int], cp_model.IntVar] = {}
    for r in range(size):
        for child in range(size):
            pieces = []
            for (q, c), target_flag in target.items():
                if c != child or r > q:
                    continue
                tr = and_var(
                    model,
                    [target_flag, root[q, r]],
                    f"target_root_{q}_{child}_{r}",
                )
                target_root[q, child, r] = tr
                pieces.append(tr)
            event_at_root[r, child] = or_var(
                model, pieces, f"event_at_root_{r}_{child}"
            )

    under_two: dict[tuple[int, int], cp_model.IntVar] = {}
    for r in range(size):
        for child in range(size):
            earlier = sum(event_at_root[r, c] for c in range(child))
            flag = model.new_bool_var(f"under_two_{r}_{child}")
            model.add(earlier <= 1).only_enforce_if(flag)
            model.add(earlier >= 2).only_enforce_if(flag.Not())
            under_two[r, child] = flag

    cap_two_events = []
    for (q, child, r), rooted_target in target_root.items():
        cap_two_events.append(
            and_var(
                model,
                [
                    rooted_target,
                    under_two[r, child],
                    alive[rank_cutoff + 1][q].Not(),
                ],
                f"cap_two_rank_{q}_{child}_{r}",
            )
        )

    # A violation has integral excess at least two.  Requiring two hard
    # events is redundant but improves propagation substantially.
    model.add(sum(hard_events) >= 2)
    if mode == "additive_one":
        model.add(sum(hard_events) >= sum(target_events) + 2)
    else:
        model.add(sum(hard_events) >= sum(cap_two_events) + 2)

    return SatInstance(
        model=model,
        size=size,
        rank_cutoff=rank_cutoff,
        mode=mode,
        output=output,
        output_is=output_is,
        even=even,
        residue_mod9=residue_mod9,
        residue_zero=residue_zero,
        alive=alive,
        hard=hard,
        root=root,
        hard_events=hard_events,
        target_events=target_events,
        cap_two_events=cap_two_events,
    )


def solve_sat(
    size: int,
    rank_cutoff: int,
    mode: str,
    max_time_seconds: float | None,
) -> dict:
    instance = build_sat(size, rank_cutoff, mode)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 42453
    solver.parameters.symmetry_level = 2
    solver.parameters.cp_model_presolve = True
    if max_time_seconds is not None:
        solver.parameters.max_time_in_seconds = max_time_seconds
    status = solver.solve(instance.model)
    status_name = solver.status_name(status)
    row = {
        "size": size,
        "rank_cutoff": rank_cutoff,
        "mode": mode,
        "status": status_name,
        "conflicts": solver.num_conflicts,
        "branches": solver.num_branches,
        "wall_time_seconds": solver.wall_time,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        row["model"] = {
            "size": size,
            "overflow": size,
            "even": [solver.value(x) for x in instance.even],
            "residue_mod9": [
                solver.value(x) for x in instance.residue_mod9
            ],
            "residue_zero": [
                solver.value(x) for x in instance.residue_zero
            ],
            "output": {
                f"{a},{b}": solver.value(var)
                for (a, b), var in sorted(instance.output.items())
            },
            "searched_rank_cutoff": rank_cutoff,
            "searched_mode": mode,
        }
    return row


def decode_output(model_data: dict) -> dict[tuple[int, int], int]:
    return {
        tuple(map(int, key.split(","))): value
        for key, value in model_data["output"].items()
    }


def exact_stages(
    size: int, output: dict[tuple[int, int], int]
) -> list[list[bool]]:
    incoming: list[list[tuple[int, int]]] = [[] for _ in range(size)]
    for pair, child in output.items():
        if child < size:
            incoming[child].append(pair)
    current = [True] * size
    stages = [current]
    for _ in range(size):
        following = [False] * size
        following[SEED2] = following[SEED3] = True
        for n in range(2, size):
            following[n] = any(
                current[a] and current[b] for a, b in incoming[n]
            )
        stages.append(following)
        if following == current:
            while len(stages) <= size:
                stages.append(following.copy())
            break
        current = following
    if len(stages) != size + 1:
        raise AssertionError((len(stages), size))
    return stages


def integer_embedding_audit(
    size: int,
    output: dict[tuple[int, int], int],
    even: list[bool],
    residue_mod9: list[int],
) -> dict:
    """Propagate exact equations v_c + 1 = v_a*v_b where possible.

    The SAT abstraction deliberately retains only order and congruence facts,
    so a countermodel need not embed into the positive integers.  This audit
    returns the first exact obstruction rather than blurring that distinction.
    """
    known: dict[int, tuple[Fraction, str]] = {
        SEED2: (Fraction(2), "seed v_0=2"),
        SEED3: (Fraction(3), "seed v_1=3"),
    }

    def assign(vertex: int, value: Fraction, reason: str) -> dict | None:
        if vertex in known:
            old, old_reason = known[vertex]
            if old != value:
                return {
                    "kind": "inconsistent_exact_value",
                    "vertex": vertex,
                    "first_value": str(old),
                    "second_value": str(value),
                    "first_reason": old_reason,
                    "second_reason": reason,
                }
            return None
        if value.denominator != 1:
            return {
                "kind": "nonintegral_vertex",
                "vertex": vertex,
                "value": str(value),
                "reason": reason,
            }
        integer = value.numerator
        if (integer % 2 == 0) != even[vertex]:
            return {
                "kind": "parity_mismatch",
                "vertex": vertex,
                "value": integer,
                "declared_even": even[vertex],
                "reason": reason,
            }
        if integer % 9 != residue_mod9[vertex]:
            return {
                "kind": "mod9_mismatch",
                "vertex": vertex,
                "value": integer,
                "value_mod9": integer % 9,
                "declared_mod9": residue_mod9[vertex],
                "reason": reason,
            }
        known[vertex] = (value, reason)
        return None

    finite = [
        (a, b, child)
        for (a, b), child in sorted(output.items(), key=lambda item: (item[1], item[0]))
        if child < size
    ]
    changed = True
    while changed:
        changed = False
        for a, b, child in finite:
            va = known.get(a)
            vb = known.get(b)
            vc = known.get(child)
            candidate: tuple[int, Fraction, str] | None = None
            if va is not None and vb is not None:
                candidate = (
                    child,
                    va[0] * vb[0] - 1,
                    f"v_{child}=v_{a}*v_{b}-1",
                )
            elif vc is not None and va is not None:
                candidate = (
                    b,
                    (vc[0] + 1) / va[0],
                    f"v_{b}=(v_{child}+1)/v_{a}",
                )
            elif vc is not None and vb is not None:
                candidate = (
                    a,
                    (vc[0] + 1) / vb[0],
                    f"v_{a}=(v_{child}+1)/v_{b}",
                )
            if candidate is None:
                continue
            vertex, value, reason = candidate
            was_known = vertex in known
            contradiction = assign(vertex, value, reason)
            if contradiction is not None:
                return {
                    "status": "NOT_INTEGER_EMBEDDABLE",
                    "derived_values_before_obstruction": {
                        str(n): int(value[0])
                        for n, value in sorted(known.items())
                        if value[0].denominator == 1
                    },
                    "first_obstruction": contradiction,
                }
            changed |= not was_known

    known_in_order = sorted(known)
    for left, right in zip(known_in_order, known_in_order[1:]):
        if known[left][0] >= known[right][0]:
            return {
                "status": "NOT_INTEGER_EMBEDDABLE",
                "derived_values_before_obstruction": {
                    str(n): int(value[0])
                    for n, value in sorted(known.items())
                    if value[0].denominator == 1
                },
                "first_obstruction": {
                    "kind": "strict_order_mismatch",
                    "left_vertex": left,
                    "left_value": str(known[left][0]),
                    "right_vertex": right,
                    "right_value": str(known[right][0]),
                },
            }
    return {
        "status": "PARTIAL_EXACT_EMBEDDING_CONSISTENT",
        "derived_values": {
            str(n): int(value[0])
            for n, value in sorted(known.items())
            if value[0].denominator == 1
        },
        "unresolved_vertices": [n for n in range(size) if n not in known],
    }


def replay_model(model_data: dict) -> dict:
    """Independently derive all semantic fields and assert every axiom."""
    size = model_data["size"]
    overflow = model_data["overflow"]
    if overflow != size:
        raise AssertionError("overflow must equal size")
    even = [bool(x) for x in model_data["even"]]
    residue_mod9 = model_data["residue_mod9"]
    r0 = [bool(x) for x in model_data["residue_zero"]]
    output = decode_output(model_data)
    if (
        even[:2] != [True, False]
        or residue_mod9[:2] != [2, 3]
        or r0[:2] != [False, True]
    ):
        raise AssertionError("seed types")
    if any(residue not in (0, 2, 3, 5, 6, 8) for residue in residue_mod9):
        raise AssertionError("forbidden residue")
    if any(flag != (residue % 3 == 0) for flag, residue in zip(r0, residue_mod9)):
        raise AssertionError("residue-zero projection")

    expected_pairs = {
        (a, b) for a in range(size) for b in range(a + 1, size)
    }
    if set(output) != expected_pairs:
        raise AssertionError("pair table is incomplete")
    for (a, b), child in output.items():
        if not b < child <= size:
            raise AssertionError((a, b, child))
        if child < size:
            if even[child] != ((not even[a]) and (not even[b])):
                raise AssertionError(("parity", a, b, child))
            if residue_mod9[child] != (residue_mod9[a] * residue_mod9[b] - 1) % 9:
                raise AssertionError(("mod9", a, b, child))
            if r0[child] != ((not r0[a]) and (not r0[b])):
                raise AssertionError(("residue", a, b, child))
    for x in range(size):
        others = [y for y in range(size) if y != x]
        values = [output[tuple(sorted((x, y)))] for y in others]
        for left, right in zip(values, values[1:]):
            if left > right or (right < size and left >= right):
                raise AssertionError(("monotonicity", x, values))
    if output[SEED2, SEED3] >= size:
        raise AssertionError("2,3 output overflowed")

    incoming: list[list[tuple[int, int]]] = [[] for _ in range(size)]
    for pair, child in output.items():
        if child < size:
            incoming[child].append(pair)
    seed2_parent: list[int | None] = [None] * size
    seed3_parent: list[int | None] = [None] * size
    for n in range(2, size):
        p2 = [q for q in range(1, n) if output.get((SEED2, q)) == n]
        if len(p2) != int(not even[n]):
            raise AssertionError(("seed2 predecessor", n, p2, even[n]))
        seed2_parent[n] = p2[0] if p2 else None
        p3 = [
            q
            for q in range(n)
            if q != SEED3
            and output.get(tuple(sorted((SEED3, q)))) == n
        ]
        if len(p3) > 1:
            raise AssertionError(("seed3 predecessor", n, p3))
        seed3_parent[n] = p3[0] if p3 else None

    stages = exact_stages(size, output)
    final = stages[-1]
    holes = [not x for x in final]
    rank: list[int | None] = [None] * size
    for n in range(size):
        if holes[n]:
            death = next(t for t in range(1, len(stages)) if not stages[t][n])
            rank[n] = death - 1

    hard = [
        even[n] and bool(incoming[n]) and seed3_parent[n] is None
        for n in range(size)
    ]
    for n in range(size):
        if not even[n]:
            continue
        expected_seed3 = bool(
            even[n] and incoming[n] and residue_mod9[n] in (5, 8)
        )
        if (seed3_parent[n] is not None) != expected_seed3:
            raise AssertionError(("seed3 completeness", n, seed3_parent[n]))
    canonical_parent: list[int | None] = [None] * size
    root: list[int | None] = [None] * size
    for n in range(size):
        if not holes[n]:
            continue
        if not even[n] and n >= 2:
            canonical_parent[n] = seed2_parent[n]
        elif even[n] and incoming[n] and not hard[n]:
            canonical_parent[n] = seed3_parent[n]
        parent = canonical_parent[n]
        if parent is None:
            root[n] = n
        else:
            if parent >= n or not holes[parent] or root[parent] is None:
                raise AssertionError(("canonical parent", n, parent))
            root[n] = root[parent]

    targets = []
    for q in range(1, size):
        child = output.get((SEED2, q), size)
        if child < size and holes[q] and final[child]:
            targets.append(
                {
                    "parent": q,
                    "child": child,
                    "rank": rank[q],
                    "root": root[q],
                }
            )
    targets.sort(key=lambda row: row["child"])
    seen_by_root: dict[int, int] = {}
    for row in targets:
        r = row["root"]
        seen_by_root[r] = seen_by_root.get(r, 0) + 1
        row["root_ordinal"] = seen_by_root[r]
        row["cap_two"] = row["root_ordinal"] <= 2

    profiles = []
    for d in range(size):
        hard_nodes = [
            n for n in range(size) if hard[n] and rank[n] is not None and rank[n] <= d
        ]
        target_rows = [row for row in targets if row["rank"] <= d]
        cap_rows = [row for row in target_rows if row["cap_two"]]
        profiles.append(
            {
                "d": d,
                "H": len(hard_nodes),
                "Q": len(target_rows),
                "Q2": len(cap_rows),
                "H_minus_Q": len(hard_nodes) - len(target_rows),
                "H_minus_Q2": len(hard_nodes) - len(cap_rows),
                "hard_nodes": hard_nodes,
                "target_children": [row["child"] for row in target_rows],
                "cap_two_children": [row["child"] for row in cap_rows],
            }
        )
    max_ao = max(profiles, key=lambda row: row["H_minus_Q"])
    max_cap = max(profiles, key=lambda row: row["H_minus_Q2"])

    finite_outputs = [
        {"parents": [a, b], "child": child}
        for (a, b), child in sorted(output.items(), key=lambda item: (item[1], item[0]))
        if child < size
    ]
    compact_stages = [
        [n for n, present in enumerate(stage) if present] for stage in stages
    ]
    return {
        "size": size,
        "finite_outputs": finite_outputs,
        "descending_stages": compact_stages,
        "fixed_point": [n for n, present in enumerate(final) if present],
        "holes": [n for n, missing in enumerate(holes) if missing],
        "ranks": {str(n): value for n, value in enumerate(rank) if value is not None},
        "hard_nodes": [n for n, flag in enumerate(hard) if flag and holes[n]],
        "canonical_parent": {
            str(n): parent
            for n, parent in enumerate(canonical_parent)
            if parent is not None
        },
        "roots": {str(n): value for n, value in enumerate(root) if value is not None},
        "targets": targets,
        "profiles": profiles,
        "maximum_additive_one_profile": max_ao,
        "maximum_cap_two_profile": max_cap,
        "checks": {
            "exact_support_biconditional": True,
            "fixed_point_reached": stages[-1] == stages[-2],
            "distinct_inputs_only": True,
            "strict_parent_order": True,
            "strict_product_monotonicity": True,
            "parity_and_residue_rules": True,
            "mod9_seed3_completeness": True,
            "odd_seed2_predecessors": True,
            "derived_hard_and_target_predicates": True,
        },
        "integer_embedding_audit": integer_embedding_audit(
            size, output, even, residue_mod9
        ),
    }


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def actual_prefix_model(limit: int) -> dict:
    values = [n for n in range(2, limit + 1) if allowed(n)]
    index = {value: i for i, value in enumerate(values)}
    size = len(values)
    output = {}
    for a in range(size):
        for b in range(a + 1, size):
            child_value = values[a] * values[b] - 1
            output[a, b] = index.get(child_value, size)
    return {
        "size": size,
        "overflow": size,
        "even": [int(value % 2 == 0) for value in values],
        "residue_mod9": [value % 9 for value in values],
        "residue_zero": [int(value % 3 == 0) for value in values],
        "output": {f"{a},{b}": child for (a, b), child in output.items()},
        "actual_values": values,
    }


def validate_actual_prefix(limit: int) -> dict:
    model_data = actual_prefix_model(limit)
    replay = replay_model(model_data)
    values = model_data["actual_values"]
    actual_fixed = [values[i] for i in replay["fixed_point"]]

    # Independent increasing least-closure recursion.
    member = {2, 3}
    for n in values[2:]:
        for a in range(2, math.isqrt(n + 1) + 1):
            if (n + 1) % a:
                continue
            b = (n + 1) // a
            if a < b and allowed(a) and allowed(b) and a in member and b in member:
                member.add(n)
                break
    if actual_fixed != sorted(member):
        raise AssertionError((limit, actual_fixed, sorted(member)))

    max_ao = replay["maximum_additive_one_profile"]
    max_cap = replay["maximum_cap_two_profile"]
    return {
        "integer_limit": limit,
        "abstract_vertices": len(values),
        "generated_count": len(member),
        "hole_count": len(values) - len(member),
        "maximum_H_minus_Q": max_ao["H_minus_Q"],
        "maximum_H_minus_Q_at": {
            "d": max_ao["d"],
            "hard_values": [values[i] for i in max_ao["hard_nodes"]],
            "target_child_values": [
                values[i] for i in max_ao["target_children"]
            ],
        },
        "maximum_H_minus_Q2": max_cap["H_minus_Q2"],
        "maximum_H_minus_Q2_at": {
            "d": max_cap["d"],
            "hard_values": [values[i] for i in max_cap["hard_nodes"]],
            "cap_two_child_values": [
                values[i] for i in max_cap["cap_two_children"]
            ],
        },
        "checks": {
            "all_abstract_axioms": True,
            "fixed_point_equals_increasing_closure": True,
            "distinct_input_rule": True,
        },
    }


def search_minimum(
    mode: str,
    minimum_size: int,
    maximum_size: int,
    max_time_seconds: float | None,
) -> dict:
    attempts = []
    witness = None
    for size in range(minimum_size, maximum_size + 1):
        for d in range(size):
            row = solve_sat(size, d, mode, max_time_seconds)
            attempts.append({key: value for key, value in row.items() if key != "model"})
            if row["status"] in {"FEASIBLE", "OPTIMAL"}:
                replay = replay_model(row["model"])
                metric = (
                    replay["profiles"][d]["H_minus_Q"]
                    if mode == "additive_one"
                    else replay["profiles"][d]["H_minus_Q2"]
                )
                if metric < 2:
                    raise AssertionError((mode, size, d, metric))
                witness = {
                    "sat": {key: value for key, value in row.items() if key != "model"},
                    "model": row["model"],
                    "independent_replay": replay,
                }
                return {
                    "mode": mode,
                    "minimum_size": size,
                    "minimum_rank_cutoff": d,
                    "all_smaller_attempts_infeasible": all(
                        attempt["status"] == "INFEASIBLE"
                        for attempt in attempts[:-1]
                    ),
                    "global_minimum_by_top_extension": (
                        size > minimum_size
                        and len(
                            [
                                attempt
                                for attempt in attempts
                                if attempt["size"] == size - 1
                            ]
                        )
                        == size - 1
                        and all(
                            attempt["status"] == "INFEASIBLE"
                            for attempt in attempts
                            if attempt["size"] == size - 1
                        )
                    ),
                    "attempts": attempts,
                    "witness": witness,
                }
            if row["status"] != "INFEASIBLE":
                return {
                    "mode": mode,
                    "minimum_size": None,
                    "attempts": attempts,
                    "obstruction": "search returned UNKNOWN before minimality was certified",
                }
    return {
        "mode": mode,
        "minimum_size": None,
        "attempts": attempts,
        "obstruction": f"no model through size {maximum_size}",
    }


def stable_json_sha(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-size", type=int, default=20)
    parser.add_argument("--max-size", type=int, default=21)
    parser.add_argument(
        "--max-time-per-instance",
        type=float,
        default=None,
        help="Omit for exact unbounded CP-SAT runs; UNKNOWN never counts as infeasible.",
    )
    parser.add_argument(
        "--actual-limits", type=int, nargs="+", default=[74, 186, 362, 500]
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.min_size < 3 or args.max_size < args.min_size:
        raise ValueError("invalid size range")

    searches = [
        search_minimum(
            mode,
            args.min_size,
            args.max_size,
            args.max_time_per_instance,
        )
        for mode in ("additive_one", "cap_two")
    ]
    actual = [validate_actual_prefix(limit) for limit in args.actual_limits]
    payload = {
        "schema_version": 2,
        "task": "C53 exact descending-image abstract model",
        "solver": {
            "engine": "OR-Tools CP-SAT",
            "workers": 1,
            "random_seed": 42453,
            "time_limit_per_instance": args.max_time_per_instance,
            "unknown_is_never_infeasible": True,
        },
        "axioms": [
            "ordered distinct-parent product table with one common overflow",
            "strict parent order and strict one-coordinate product monotonicity",
            "exact parity and allowed-residue product rules modulo 9",
            "seed-3 availability is exact for every reducible even output",
            "2*3-1 is finite and every nonseed odd vertex has one seed-2 predecessor",
            "S_0 is the whole universe and S_(t+1)=F(S_t) by exact AND/OR biconditionals",
            "hard, target, rank, canonical root, and first-two status are all derived",
        ],
        "top_extension_certificate": {
            "statement": (
                "Every size-n model extends to size n+1 by changing old overflow n "
                "to n+1, adding an even splitless residue-0 vertex n, and making all "
                "pairs incident to n overflow. All old stages, roots, and counts persist."
            ),
            "consequence": (
                "Infeasibility at size n for every d excludes every smaller size."
            ),
        },
        "searches": searches,
        "actual_prefix_validation": actual,
    }
    payload["content_sha256_before_self_field"] = stable_json_sha(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "searches": [
                    {
                        "mode": row["mode"],
                        "minimum_size": row["minimum_size"],
                        "minimum_rank_cutoff": row.get("minimum_rank_cutoff"),
                        "attempt_count": len(row["attempts"]),
                        "obstruction": row.get("obstruction"),
                    }
                    for row in searches
                ],
                "actual_prefix_validation": actual,
                "output": str(args.output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
