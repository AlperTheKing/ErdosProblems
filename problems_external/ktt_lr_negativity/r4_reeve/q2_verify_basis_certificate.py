#!/usr/bin/env python3
"""Independent exact replay of ``q2_basis_witness_certificate.json``.

Only Python's standard library is used.  In particular, this checker does not
call the generator's vertex, edge, lattice-count, rank, or interpolation code.
It reconstructs all 72 polytopes from their inequalities and checks:

* deterministic seed/ordinal provenance of every right-hand side;
* complete exact integral vertex sets and dimension three;
* exact edge-length vectors from genuine facets;
* Ehrhart counts L(0),...,L(5), hence the recorded a_1 values;
* rank(B)=27, B Lambda^T=0, and rank(Lambda)=72=99-rank(B);
* the embedded rational vector mu is componentwise nonnegative and satisfies
  Lambda*mu=a_1 on every basis witness.
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
DEFAULT_CERT = os.path.join(HERE, "q2_basis_witness_certificate.json")


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def det3(rows):
    a, b, c = rows
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def solve3(rows, rhs):
    d = det3(rows)
    if d == 0:
        return None
    cols = [[Fraction(x) for x in r] for r in rows]
    out = []
    for k in range(3):
        m = [r[:] for r in cols]
        for i in range(3):
            m[i][k] = Fraction(rhs[i])
        out.append(det3(m) / d)
    return tuple(out)


def matrix_rank(rows):
    if not rows:
        return 0
    M = [[Fraction(x) for x in row] for row in rows]
    r = 0
    for c in range(len(M[0])):
        p = next((i for i in range(r, len(M)) if M[i][c]), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        q = M[r][c]
        M[r] = [x / q for x in M[r]]
        for i in range(r + 1, len(M)):
            if M[i][c]:
                q = M[i][c]
                M[i] = [x - q * y for x, y in zip(M[i], M[r])]
        r += 1
        if r == len(M):
            break
    return r


def affine_rank(points):
    if len(points) <= 1:
        return 0
    p0 = points[0]
    return matrix_rank([[x - y for x, y in zip(p, p0)] for p in points[1:]])


def enumerate_vertices(A, b):
    found = set()
    for I in itertools.combinations(range(len(A)), 3):
        rows = [A[i] for i in I]
        v = solve3(rows, [b[i] for i in I])
        if v is not None and all(dot(row, v) <= rhs for row, rhs in zip(A, b)):
            found.add(v)
    return sorted(found)


def primitive_cross(a, b):
    u = [a[1] * b[2] - a[2] * b[1],
         a[2] * b[0] - a[0] * b[2],
         a[0] * b[1] - a[1] * b[0]]
    g = 0
    for x in u:
        g = gcd(g, abs(x))
    return None if g == 0 else [x // g for x in u]


def nonparallel_pairs(A):
    return [(i, j) for i, j in itertools.combinations(range(len(A)), 2)
            if primitive_cross(A[i], A[j]) is not None]


def edge_vector(A, b, vertices, pairs):
    """Reconstruct total lattice edge lengths, without project imports."""
    genuine = []
    for i, (row, rhs) in enumerate(zip(A, b)):
        on = [v for v in vertices if dot(row, v) == rhs]
        if affine_rank(on) == 2:
            genuine.append(i)
    pair_pos = {p: k for k, p in enumerate(pairs)}
    lengths = [0] * len(pairs)
    for i, j in itertools.combinations(genuine, 2):
        on = [v for v in vertices if dot(A[i], v) == b[i] and dot(A[j], v) == b[j]]
        if affine_rank(on) != 1:
            continue
        p, q = max(itertools.combinations(on, 2),
                   key=lambda pq: sum((x - y) ** 2 for x, y in zip(*pq)))
        delta = [int(x - y) for x, y in zip(p, q)]
        g = 0
        for x in delta:
            g = gcd(g, abs(x))
        if g == 0:
            raise AssertionError("zero-length edge")
        lengths[pair_pos[(i, j)]] += g
    return lengths


def lattice_count(A, b, vertices, n):
    if n == 0:
        return 1
    lo = [min(int(v[k]) for v in vertices) * n for k in range(3)]
    hi = [max(int(v[k]) for v in vertices) * n for k in range(3)]
    total = 0
    for x in range(lo[0], hi[0] + 1):
        for y in range(lo[1], hi[1] + 1):
            for z in range(lo[2], hi[2] + 1):
                v = (x, y, z)
                if all(dot(row, v) <= n * rhs for row, rhs in zip(A, b)):
                    total += 1
    return total


def polymul(p, q):
    out = [Fraction(0)] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            out[i + j] += x * y
    return out


def interpolate(values):
    out = [Fraction(0)] * len(values)
    for i, value in enumerate(values):
        p = [Fraction(1)]
        den = Fraction(1)
        for j in range(len(values)):
            if i == j:
                continue
            p = polymul(p, [Fraction(-j), Fraction(1)])
            den *= i - j
        for k, x in enumerate(p):
            out[k] += Fraction(value) * x / den
    return out


def polyval(coeffs, x):
    out = Fraction(0)
    for c in reversed(coeffs):
        out = out * x + c
    return out


def balance_matrix(A, pairs):
    B = [[0] * len(pairs) for _ in range(3 * len(A))]
    for c, (i, j) in enumerate(pairs):
        u = primitive_cross(A[i], A[j])
        for k in range(3):
            B[3 * i + k][c] = u[k]
            B[3 * j + k][c] = -u[k]
    return B


def parse_fraction(x):
    return Fraction(str(x))


def canonical_fraction(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def replay_b(A, seed, ordinal, slack):
    rng = random.Random(seed)
    b = None
    for _ in range(ordinal + 1):
        x0 = [rng.randint(-slack, slack) for _ in range(3)]
        b = [dot(row, x0) + rng.randint(0, slack) for row in A]
    return b


def verify(path):
    with open(path, "rb") as f:
        raw = f.read()
    cert = json.loads(raw)
    if cert.get("schema") != "r4-edge-basis-certificate-v1":
        raise AssertionError("unexpected certificate schema")
    A = [[int(x) for x in row] for row in cert["normals"]]
    if len(A) != 15 or any(len(row) != 3 for row in A):
        raise AssertionError("normal matrix is not 15x3")
    pairs = nonparallel_pairs(A)
    if [list(p) for p in pairs] != cert["nonparallel_pairs"] or len(pairs) != 99:
        raise AssertionError("nonparallel-pair coordinate list mismatch")

    all_pairs = list(itertools.combinations(range(15), 2))
    all_index = {p: i for i, p in enumerate(all_pairs)}
    if [all_index[p] for p in pairs] != cert["original_105_pair_indices"]:
        raise AssertionError("105-pair index map mismatch")

    B = balance_matrix(A, pairs)
    brank = matrix_rank(B)
    if brank != cert["balance_rank"] or brank != 27:
        raise AssertionError(f"balance rank mismatch: {brank}")
    if cert["kernel_dimension"] != 99 - brank or cert["kernel_dimension"] != 72:
        raise AssertionError("kernel dimension mismatch")

    mu = [parse_fraction(x) for x in cert["mu"]]
    if len(mu) != 99 or min(mu) < 0:
        raise AssertionError("mu is not a 99-vector in Q_{>=0}")
    slack = int(cert["generation"]["slack_bound"])
    rows = []
    for number, w in enumerate(cert["witnesses"]):
        b = [int(x) for x in w["b"]]
        if b != replay_b(A, int(w["seed"]), int(w["ordinal_within_seed"]), slack):
            raise AssertionError(f"witness {number}: deterministic b replay failed")
        vertices = enumerate_vertices(A, b)
        stored_vertices = sorted(tuple(parse_fraction(x) for x in v) for v in w["vertices"])
        if vertices != stored_vertices:
            raise AssertionError(f"witness {number}: complete vertex set mismatch")
        if affine_rank(vertices) != 3 or any(x.denominator != 1 for v in vertices for x in v):
            raise AssertionError(f"witness {number}: not an integral 3-polytope")

        row = edge_vector(A, b, vertices, pairs)
        if row != [int(x) for x in w["edge_lengths"]]:
            raise AssertionError(f"witness {number}: edge vector mismatch")
        if any(sum(x * y for x, y in zip(br, row)) for br in B):
            raise AssertionError(f"witness {number}: B*Lambda != 0")

        L = [lattice_count(A, b, vertices, n) for n in range(6)]
        if L != [int(x) for x in w["L_0_through_5"]]:
            raise AssertionError(f"witness {number}: lattice counts mismatch")
        poly = interpolate(L[:4])
        if polyval(poly, 4) != L[4] or polyval(poly, 5) != L[5]:
            raise AssertionError(f"witness {number}: degree-3 interpolation check failed")
        if [canonical_fraction(x) for x in poly] != w["ehrhart_coefficients"]:
            raise AssertionError(f"witness {number}: Ehrhart coefficients mismatch")
        if parse_fraction(w["a1"]) != poly[1]:
            raise AssertionError(f"witness {number}: a1 mismatch")
        if parse_fraction(w["normalized_volume"]) != 6 * poly[3]:
            raise AssertionError(f"witness {number}: normalized volume mismatch")
        if dot(row, mu) != poly[1]:
            raise AssertionError(f"witness {number}: Lambda*mu != a1")
        rows.append(row)

    wrank = matrix_rank(rows)
    if len(rows) != 72 or wrank != 72 or wrank != cert["witness_rank"]:
        raise AssertionError(f"witness basis rank mismatch: {len(rows)} rows, rank {wrank}")
    if wrank + brank != len(pairs):
        raise AssertionError("rowspan(Lambda) cannot equal ker(B) by dimension")
    print("PASS")
    print(f"certificate_sha256={hashlib.sha256(raw).hexdigest()}")
    print(f"witnesses={len(rows)} witness_rank={wrank} balance_rank={brank} "
          f"kernel_dimension={len(pairs)-brank} min_mu={canonical_fraction(min(mu))}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = ap.parse_args(argv)
    verify(os.path.abspath(args.certificate))
    return 0


if __name__ == "__main__":
    sys.exit(main())
