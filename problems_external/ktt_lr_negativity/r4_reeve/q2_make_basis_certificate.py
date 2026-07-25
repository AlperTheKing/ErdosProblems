#!/usr/bin/env python3
"""Build a reproducible witness basis for the r=4 edge-local proof.

The old ``q2_fitdata.json`` records a 72-dimensional edge-length basis but not
the polytopes that produced its rows.  This generator fixes that provenance
gap.  It deterministically searches small *lattice* polytopes

    P(b) = {x in R^3 : n_i . x <= b_i, i=0,...,14}

with the fixed r=4 normal set, greedily keeps 72 independent edge-length
vectors, and stores enough exact data to reconstruct every row.  The output is
new and is never overwritten by this program.

This is certificate generation, not a proof checker.  Use
``q2_verify_basis_certificate.py`` for an independent exact replay.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import random
import sys
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import hive4  # noqa: E402
from q2_farkas import phase1  # noqa: E402
from q2_localfit2 import rand_relaxed  # noqa: E402
from q2_localformula import edge_data  # noqa: E402
from q2_relaxed_simplex import NORMALS  # noqa: E402


ALL_PAIRS = list(itertools.combinations(range(len(NORMALS)), 2))
ALL_PAIR_INDEX = {p: k for k, p in enumerate(ALL_PAIRS)}


def primitive_cross(a, b):
    u = [a[1] * b[2] - a[2] * b[1],
         a[2] * b[0] - a[0] * b[2],
         a[0] * b[1] - a[1] * b[0]]
    g = 0
    for x in u:
        g = gcd(g, abs(x))
    if g == 0:
        return None
    return [x // g for x in u]


NONPARALLEL_PAIRS = [p for p in ALL_PAIRS
                     if primitive_cross(NORMALS[p[0]], NORMALS[p[1]]) is not None]
USED_PAIR_INDICES = [ALL_PAIR_INDEX[p] for p in NONPARALLEL_PAIRS]


def balance_matrix():
    """Facet-boundary closure map B: Q^99 -> Q^(15*3)."""
    B = [[0] * len(NONPARALLEL_PAIRS) for _ in range(3 * len(NORMALS))]
    for c, (i, j) in enumerate(NONPARALLEL_PAIRS):
        u = primitive_cross(NORMALS[i], NORMALS[j])
        for k in range(3):
            B[3 * i + k][c] = u[k]
            B[3 * j + k][c] = -u[k]
    return B


class ExactBasis:
    """Incremental RREF over Q, used only to choose independent witnesses."""

    def __init__(self, ncols):
        self.ncols = ncols
        self.rows = {}

    @property
    def rank(self):
        return len(self.rows)

    def add(self, values):
        v = [Fraction(x) for x in values]
        for p in sorted(self.rows):
            if v[p]:
                f = v[p]
                v = [x - f * y for x, y in zip(v, self.rows[p])]
        try:
            p = next(i for i, x in enumerate(v) if x)
        except StopIteration:
            return False
        f = v[p]
        v = [x / f for x in v]
        for q in list(self.rows):
            if self.rows[q][p]:
                f = self.rows[q][p]
                self.rows[q] = [x - f * y for x, y in zip(self.rows[q], v)]
        self.rows[p] = v
        return True


def matrix_rank(rows):
    if not rows:
        return 0
    basis = ExactBasis(len(rows[0]))
    for row in rows:
        basis.add(row)
    return basis.rank


def dense_edge_vector(lam):
    return [int(lam.get(ALL_PAIR_INDEX[p], 0)) for p in NONPARALLEL_PAIRS]


def closure_zero(B, row):
    return all(sum(a * x for a, x in zip(br, row)) == 0 for br in B)


def frac_text(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def load_nonnegative_mu():
    fit_path = os.path.join(HERE, "q2_fitdata.json")
    mu_path = os.path.join(HERE, "q2_farkas.json")
    with open(fit_path, encoding="utf-8") as f:
        fit = json.load(f)
    if fit["used"] != USED_PAIR_INDICES:
        raise RuntimeError("q2_fitdata coordinate order differs from nonparallel-pair order")
    with open(mu_path, "rb") as f:
        raw = f.read()
    data = json.loads(raw)
    if not data.get("feasible"):
        raise RuntimeError("q2_farkas.json has no feasible nonnegative certificate")
    mu = [Fraction(x) for x in data["mu"]]
    if len(mu) != len(NONPARALLEL_PAIRS) or min(mu) < 0:
        raise RuntimeError("invalid mu vector in q2_farkas.json")
    return mu, hashlib.sha256(raw).hexdigest()


def witness_from_candidate(seed, ordinal, b, verts, row, mu):
    box = hive4.bounding_box(verts)
    L = [1] + [hive4.lattice_count(NORMALS, b, n, box) for n in range(1, 6)]
    poly = hive4.interpolate(L[:4])
    if hive4.polyval(poly, 4) != L[4] or hive4.polyval(poly, 5) != L[5]:
        raise RuntimeError("Ehrhart interpolation failed at n=4 or n=5")
    a1 = poly[1]
    if sum(x * y for x, y in zip(row, mu)) != a1:
        raise RuntimeError("stored nonnegative mu fails on a new actual witness")
    volume = hive4.normalized_volume(NORMALS, b, verts)
    if 6 * poly[3] != volume:
        raise RuntimeError("volume / Ehrhart leading-coefficient mismatch")
    return {
        "seed": seed,
        "ordinal_within_seed": ordinal,
        "b": list(map(int, b)),
        "vertices": [[frac_text(x) for x in v] for v in sorted(map(tuple, verts))],
        "L_0_through_5": list(map(int, L)),
        "ehrhart_coefficients": [frac_text(x) for x in poly],
        "a1": frac_text(a1),
        "normalized_volume": frac_text(volume),
        "edge_lengths": list(map(int, row)),
    }


def generate(output, seed0, seeds, candidates_per_seed, slack):
    if os.path.exists(output):
        raise FileExistsError(f"refusing to overwrite existing output: {output}")

    mu, mu_sha256 = load_nonnegative_mu()
    B = balance_matrix()
    brank = matrix_rank(B)
    if len(NONPARALLEL_PAIRS) != 99 or brank != 27:
        raise RuntimeError(f"unexpected balance dimensions/rank: 99,27 expected; got "
                           f"{len(NONPARALLEL_PAIRS)},{brank}")

    basis = ExactBasis(len(NONPARALLEL_PAIRS))
    witnesses = []
    tested = usable = 0
    for seed in range(seed0, seed0 + seeds):
        rng = random.Random(seed)
        for ordinal in range(candidates_per_seed):
            tested += 1
            A, b = rand_relaxed(rng, slack)
            verts = hive4.vertices(A, b)
            if not verts or hive4._affine_rank(verts) != 3:
                continue
            if max(hive4.denominators(verts)) != 1:
                continue
            lam = edge_data(A, b, verts)
            if lam is None:
                continue
            row = dense_edge_vector(lam)
            if not closure_zero(B, row):
                raise RuntimeError("facet-boundary closure failed on a candidate")
            usable += 1
            if not basis.add(row):
                continue
            witnesses.append(witness_from_candidate(seed, ordinal, b, verts, row, mu))
            print(f"rank {basis.rank:2d}/72 at seed={seed} ordinal={ordinal} "
                  f"(tested={tested}, usable={usable})", flush=True)
            if basis.rank == 72:
                break
        if basis.rank == 72:
            break

    if basis.rank != 72:
        raise RuntimeError(f"rank stopped at {basis.rank}; increase --seeds or --per-seed")

    cert = {
        "schema": "r4-edge-basis-certificate-v1",
        "description": "72 actual integral lattice polytopes spanning ker(B)",
        "generation": {
            "seed0": seed0,
            "seeds_allowed": seeds,
            "candidates_per_seed": candidates_per_seed,
            "slack_bound": slack,
            "candidates_tested": tested,
            "usable_integral_dim3_candidates": usable,
        },
        "normals": NORMALS,
        "nonparallel_pairs": [list(p) for p in NONPARALLEL_PAIRS],
        "original_105_pair_indices": USED_PAIR_INDICES,
        "balance_rank": brank,
        "kernel_dimension": len(NONPARALLEL_PAIRS) - brank,
        "witness_rank": basis.rank,
        "mu": [frac_text(x) for x in mu],
        "mu_source_sha256": mu_sha256,
        "witnesses": witnesses,
    }
    with open(output, "x", encoding="utf-8", newline="\n") as f:
        json.dump(cert, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"WROTE {output}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=os.path.join(HERE, "q2_basis_witness_certificate.json"))
    ap.add_argument("--seed0", type=int, default=31337)
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--per-seed", type=int, default=1000)
    ap.add_argument("--slack", type=int, default=4)
    args = ap.parse_args(argv)
    generate(os.path.abspath(args.output), args.seed0, args.seeds, args.per_seed, args.slack)
    return 0


if __name__ == "__main__":
    sys.exit(main())
