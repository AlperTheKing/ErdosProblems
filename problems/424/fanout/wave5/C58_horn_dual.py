#!/usr/bin/env python3
"""Exact generic-Horn and arithmetic audits for C58.

The generic model has two fixed seeds, source-free nonseeds fixed to zero,
one distinguished seed-0 unary chain, and hard outputs with no seed parent.
All arithmetic checks preserve the distinct-factor convention a < b.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


Clause = tuple[int, int, int]
Edge = tuple[int, int]


def determinant(matrix: list[list[int]]) -> int:
    """Exact Bareiss determinant."""
    a = [row[:] for row in matrix]
    n = len(a)
    if any(len(row) != n for row in a):
        raise ValueError("determinant requires a square matrix")
    if n == 0:
        return 1
    sign = 1
    previous = 1
    for k in range(n - 1):
        pivot = next((r for r in range(k, n) if a[r][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        value = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * value - a[i][k] * a[k][j]) // previous
        previous = value
        for i in range(k + 1, n):
            a[i][k] = 0
    return sign * a[n - 1][n - 1]


@dataclass(frozen=True)
class HornModel:
    n: int
    clauses: tuple[Clause, ...]
    chain: tuple[Edge, ...]
    seeds: tuple[int, int] = (0, 1)

    def validate(self) -> None:
        if self.n < 2 or self.seeds != (0, 1):
            raise ValueError("C58 models use exactly the seeds 0,1")
        clauses = set(self.clauses)
        for a, b, c in self.clauses:
            if not (0 <= a < b < c < self.n):
                raise ValueError(f"non-topological clause {(a, b, c)}")
        for parent, child in self.chain:
            if (0, parent, child) not in clauses:
                raise ValueError(f"chain edge {(parent, child)} lacks seed-0 clause")

    def incoming(self) -> dict[int, list[tuple[int, int]]]:
        out = {v: [] for v in range(self.n)}
        for a, b, c in self.clauses:
            out[c].append((a, b))
        return out

    def splitless(self) -> set[int]:
        incoming = self.incoming()
        return {v for v in range(self.n) if v not in self.seeds and not incoming[v]}

    def hard(self) -> set[int]:
        incoming = self.incoming()
        seeds = set(self.seeds)
        return {
            v
            for v in range(self.n)
            if incoming[v]
            and all(a not in seeds and b not in seeds for a, b in incoming[v])
        }

    def closed_masks(self) -> list[int]:
        self.validate()
        seeds = set(self.seeds)
        splitless = self.splitless()
        out: list[int] = []
        for mask in range(1 << self.n):
            if any(not ((mask >> v) & 1) for v in seeds):
                continue
            if any((mask >> v) & 1 for v in splitless):
                continue
            if any(
                ((mask >> a) & 1)
                and ((mask >> b) & 1)
                and not ((mask >> c) & 1)
                for a, b, c in self.clauses
            ):
                continue
            out.append(mask)
        return out

    def counts(self, mask: int) -> tuple[int, int]:
        hard_holes = sum(not ((mask >> v) & 1) for v in self.hard())
        boundary = sum(
            not ((mask >> parent) & 1) and ((mask >> child) & 1)
            for parent, child in self.chain
        )
        return hard_holes, boundary


def generic_six_node_model() -> HornModel:
    # s0,s1,r,x,y,h, with r -> x -> y the full distinguished chain.
    return HornModel(
        n=6,
        clauses=((0, 2, 3), (0, 3, 4), (3, 4, 5)),
        chain=((2, 3), (3, 4)),
    )


def raw_five_node_model() -> HornModel:
    # s0,s1,r,c,h.  The chain edge s1 -> c is forced, while r is splitless.
    return HornModel(
        n=5,
        clauses=((0, 1, 3), (2, 3, 4)),
        chain=((1, 3),),
    )


def audit_raw_generic_counterexample() -> dict:
    model = raw_five_node_model()
    mask = (1 << 0) | (1 << 1) | (1 << 3)
    if mask not in model.closed_masks():
        raise RuntimeError("raw five-node witness is not closed")
    h_count, q_count = model.counts(mask)
    if (h_count, q_count) != (1, 0):
        raise RuntimeError("raw generic counterexample did not replay")
    return {
        "node_names": ["s0", "s1", "r", "c", "h"],
        "clauses": [list(row) for row in model.clauses],
        "distinguished_chain": [list(edge) for edge in model.chain],
        "splitless": sorted(model.splitless()),
        "hard": sorted(model.hard()),
        "closed_set": [0, 1, 3],
        "H": h_count,
        "Q": q_count,
        "minimality_reason": "two seeds + splitless parent + chain child + hard output require five distinct vertices",
    }


def audit_generic_counterexample() -> dict:
    model = generic_six_node_model()
    masks = model.closed_masks()
    seed_mask = (1 << 0) | (1 << 1)
    if seed_mask not in masks:
        raise RuntimeError("seed mask is not closed")
    h_count, q_count = model.counts(seed_mask)
    if (h_count, q_count) != (1, 0):
        raise RuntimeError("generic counterexample did not replay")

    # Exact fractional vertex of the t/q relaxation:
    # t_r=0, t_x=t_y=1/2, t_h=0, q_x=1/2, q_y=0.
    t = {
        0: Fraction(1),
        1: Fraction(1),
        2: Fraction(0),
        3: Fraction(1, 2),
        4: Fraction(1, 2),
        5: Fraction(0),
    }
    q = {(2, 3): Fraction(1, 2), (3, 4): Fraction(0)}
    for a, b, c in model.clauses:
        if t[a] + t[b] - t[c] > 1:
            raise RuntimeError("fractional point violates Horn closure")
    for edge, value in q.items():
        parent, child = edge
        if not (0 <= value <= 1 - t[parent]):
            raise RuntimeError("fractional point violates q <= 1-parent")
        if value > t[child]:
            raise RuntimeError("fractional point violates q <= child")
        if value < t[child] - t[parent]:
            raise RuntimeError("fractional point violates q >= child-parent")

    # Active rows in variables (t_x,t_y,t_h,q_x,q_y).  Determinant 2 proves
    # that the displayed feasible point is a fractional vertex and the full
    # constraint matrix is not totally unimodular.
    active = [
        [1, -1, 0, 0, 0],
        [1, 1, -1, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 0, 0, -1, 0],
        [0, 0, 0, 0, 1],
    ]
    det = determinant(active)
    if abs(det) != 2:
        raise RuntimeError(f"unexpected active determinant {det}")

    return {
        "node_names": ["s0", "s1", "r", "x", "y", "h"],
        "clauses": [list(row) for row in model.clauses],
        "distinguished_chain": [list(edge) for edge in model.chain],
        "splitless": sorted(model.splitless()),
        "hard": sorted(model.hard()),
        "closed_set": [0, 1],
        "H": h_count,
        "Q": q_count,
        "fractional_membership": {str(k): str(v) for k, v in t.items()},
        "fractional_boundary": {f"{a}->{b}": str(v) for (a, b), v in q.items()},
        "active_matrix_determinant": det,
    }


def exhaustive_raw_smallest() -> dict:
    """Exhaust the raw two-seed, one-chain schema through five vertices."""
    first = None
    by_n: dict[str, dict[str, int | bool]] = {}
    for n in range(3, 6):
        models_n = 0
        sets_n = 0
        found_n = False
        chain_vertices = list(range(1, n))
        for path_size in range(2, len(chain_vertices) + 1):
            for path in itertools.combinations(chain_vertices, path_size):
                mandatory = {(0, path[i], path[i + 1]) for i in range(len(path) - 1)}
                optional = [
                    (a, b, c)
                    for c in range(2, n)
                    for a in range(1, c)
                    for b in range(a + 1, c)
                ]
                for option_mask in range(1 << len(optional)):
                    clauses = set(mandatory)
                    clauses.update(
                        optional[i]
                        for i in range(len(optional))
                        if (option_mask >> i) & 1
                    )
                    model = HornModel(
                        n=n,
                        clauses=tuple(sorted(clauses)),
                        chain=tuple(zip(path, path[1:])),
                    )
                    if not model.splitless():
                        continue
                    models_n += 1
                    closed = model.closed_masks()
                    sets_n += len(closed)
                    for mask in closed:
                        h_count, q_count = model.counts(mask)
                        if h_count > q_count:
                            found_n = True
                            if first is None:
                                first = {
                                    "n": n,
                                    "path": list(path),
                                    "clauses": [list(row) for row in model.clauses],
                                    "closed_set": [v for v in range(n) if (mask >> v) & 1],
                                    "H": h_count,
                                    "Q": q_count,
                                }
                            break
                    if found_n:
                        break
                if found_n:
                    break
            if found_n:
                break
        by_n[str(n)] = {
            "models_checked": models_n,
            "closed_sets_checked": sets_n,
            "counterexample": found_n,
        }
        if found_n:
            break
    if first is None or first["n"] != 5:
        raise RuntimeError(f"unexpected smallest raw counterexample: {first}")
    return {"by_n": by_n, "first_counterexample": first}


def exhaustive_smallest_core() -> dict:
    """Exhaust the strengthened one-chain schema through six vertices.

    All seed-0 clauses are exactly the edges of one increasing chain rooted
    at a splitless node.  Every parent of a hard clause must be a positive
    chain vertex.  Other clauses may omit seed 0.
    """
    checked_models = 0
    checked_closed_sets = 0
    first = None
    by_n: dict[str, dict[str, int | bool]] = {}

    for n in range(3, 7):
        models_n = 0
        sets_n = 0
        found_n = False
        vertices = list(range(2, n))
        for path_size in range(2, len(vertices) + 1):
            for path in itertools.combinations(vertices, path_size):
                mandatory = {(0, path[i], path[i + 1]) for i in range(len(path) - 1)}
                optional = [
                    (a, b, c)
                    for c in range(2, n)
                    for a in range(1, c)
                    for b in range(a + 1, c)
                ]
                for option_mask in range(1 << len(optional)):
                    clauses = set(mandatory)
                    clauses.update(
                        optional[i]
                        for i in range(len(optional))
                        if (option_mask >> i) & 1
                    )
                    model = HornModel(
                        n=n,
                        clauses=tuple(sorted(clauses)),
                        chain=tuple(zip(path, path[1:])),
                    )
                    if path[0] not in model.splitless():
                        continue
                    hard = model.hard()
                    targets = set(path[1:])
                    incoming = model.incoming()
                    if any(
                        a not in targets or b not in targets
                        for h in hard
                        for a, b in incoming[h]
                    ):
                        continue
                    models_n += 1
                    closed = model.closed_masks()
                    sets_n += len(closed)
                    for mask in closed:
                        h_count, q_count = model.counts(mask)
                        if h_count > q_count:
                            found_n = True
                            if first is None:
                                first = {
                                    "n": n,
                                    "path": list(path),
                                    "clauses": [list(row) for row in model.clauses],
                                    "closed_set": [v for v in range(n) if (mask >> v) & 1],
                                    "H": h_count,
                                    "Q": q_count,
                                }
                            break
                    if found_n:
                        break
                if found_n:
                    break
            if found_n:
                break
        checked_models += models_n
        checked_closed_sets += sets_n
        by_n[str(n)] = {
            "models_checked": models_n,
            "closed_sets_checked": sets_n,
            "counterexample": found_n,
        }
        if found_n:
            break

    if first is None or first["n"] != 6:
        raise RuntimeError(f"unexpected smallest generic core: {first}")
    return {
        "schema": "two seeds; splitless chain root; one full seed-0 chain; hard parents are positive chain vertices",
        "by_n": by_n,
        "total_models_checked": checked_models,
        "total_closed_sets_checked": checked_closed_sets,
        "first_counterexample": first,
    }


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def admissible_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    out: list[tuple[int, int]] = []
    a = 2
    while a * a < product:
        if product % a == 0:
            b = product // a
            if allowed(a) and allowed(b):
                out.append((a, b))
        a += 1
    return out


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    parent = (n + 1) // 3
    return not (allowed(parent) and parent != 3)


def least_closure(limit: int, pairs: dict[int, list[tuple[int, int]]]) -> bytearray:
    member = bytearray(limit + 1)
    member[2] = member[3] = 1
    for n in range(4, limit + 1):
        if allowed(n):
            member[n] = any(member[a] and member[b] for a, b in pairs[n])
    return member


def audit_arithmetic(limit: int = 10010) -> dict:
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pairs = {n: admissible_pairs(n) for n in values}
    member = least_closure(limit, pairs)

    splitless_odd = [n for n in values if n not in (2, 3) and not pairs[n] and n % 2]
    if splitless_odd:
        raise RuntimeError(f"odd splitless nonseed found: {splitless_odd[0]}")

    checked_hard_pairs = 0
    for n in values:
        if not hard_shape(n, pairs[n]):
            continue
        for a, b in pairs[n]:
            checked_hard_pairs += 1
            for u in (a, b):
                predecessor = (u + 1) // 2
                if u % 2 != 1 or u < 5:
                    raise RuntimeError(f"hard parent parity failure at {(n, a, b)}")
                if not allowed(predecessor) or not (2 < predecessor < u):
                    raise RuntimeError(f"hard parent predecessor failure at {(n, u)}")
                if (2, predecessor) not in admissible_pairs(u):
                    raise RuntimeError(f"missing seed-2 representation at {(n, u)}")
                if 4 * u - 3 > n:
                    raise RuntimeError(f"two-step bound failure at {(n, u)}")

    # Exact local-capacity falsifier for the least closure G.
    h = 74
    endpoint = 15
    chain = [endpoint, 2 * endpoint - 1, 4 * endpoint - 3]
    if pairs[h] != [(5, 15)] or not hard_shape(h, pairs[h]) or member[h]:
        raise RuntimeError("74 is not the expected hard hole")
    if any(member[n] for n in chain):
        raise RuntimeError("the 15->29->57 chain unexpectedly re-enters G")

    hard_holes = [n for n in values if n <= h and hard_shape(n, pairs[n]) and not member[n]]
    boundaries = [
        2 * m - 1
        for m in values
        if 2 * m - 1 <= h and not member[m] and member[2 * m - 1]
    ]
    if hard_holes != [54, 74] or boundaries != [41, 69]:
        raise RuntimeError((hard_holes, boundaries))

    return {
        "limit": limit,
        "odd_splitless_nonseeds": splitless_odd,
        "hard_factorizations_checked": checked_hard_pairs,
        "local_falsifier": {
            "hard_hole": h,
            "factorization": [5, 15],
            "absent_endpoint_chain": chain,
            "hard_holes_through_74": hard_holes,
            "all_seed2_boundaries_through_74": boundaries,
            "endpoint_component_boundaries_through_74": [],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = {
        "raw_generic_counterexample": audit_raw_generic_counterexample(),
        "raw_smallest_exhaustion": exhaustive_raw_smallest(),
        "strengthened_generic_counterexample": audit_generic_counterexample(),
        "strengthened_smallest_core_exhaustion": exhaustive_smallest_core(),
        "arithmetic_audit": audit_arithmetic(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
