"""Class-symmetric quotient scout for y-dependent CAGE on nonuniform C5 blowups.

This avoids expanding all shortest geodesics.  It tests the family

    C5[k+1,k,k+1,k,k+1]

with the gamma-min cut leaving the edge class A0-A1 bad.  For one bad edge
f=(a0,a1), the shortest blue rows have layer order

    A0, A4, A3, A2, A1.

For class-symmetric y, the per-f CAGE problem quotients to variables
beta_{i,j,t}, where i<=t<j.  Pair marginals are sum_t beta=1 and total gate
gap marginals are sum_{i<=t<j} beta=H_t.  If actual gates of a gap type are
used symmetrically, their multiplicity cancels from
sum_g 2 sqrt(A_g^y B_g^y), leaving one conic term per gap t.

This is a scale diagnostic, not a proof and not an all-y checker.
"""

from __future__ import annotations

import argparse

import numpy as np
from scipy.optimize import linprog, minimize


PAIRS = [(i, j) for i in range(5) for j in range(i + 1, 5)]
VARS = [(i, j, t) for i, j in PAIRS for t in range(i, j)]
H = np.array([25.0 / 12.0, 35.0 / 12.0, 35.0 / 12.0, 25.0 / 12.0])


def constraints():
    rows = []
    rhs = []
    for i, j in PAIRS:
        rows.append([1.0 if (a, b) == (i, j) else 0.0 for a, b, _t in VARS])
        rhs.append(1.0)
    for t in range(4):
        rows.append([1.0 if tt == t else 0.0 for _i, _j, tt in VARS])
        rhs.append(H[t])
    return np.array(rows), np.array(rhs)


AEQ, BEQ = constraints()
BOUNDS = [(0.0, None)] * len(VARS)


def layer_weights_from_classes(y_class):
    # layer order for a bad edge in A0-A1: A0,A4,A3,A2,A1
    return np.array([y_class[0], y_class[4], y_class[3], y_class[2], y_class[1]], dtype=float)


def phi(beta, w):
    out = 0.0
    for t in range(4):
        A = 0.0
        B = 0.0
        for val, (i, j, tt) in zip(beta, VARS):
            if tt != t or val <= 0.0:
                continue
            A += val * w[i]
            B += val * w[j]
        out += 2.0 * np.sqrt(max(A, 0.0) * max(B, 0.0))
    return float(out)


def solve_phi(w, samples, seed):
    rng = np.random.default_rng(seed)
    starts = []
    # A deterministic feasible point from a zero objective LP.
    res0 = linprog(np.zeros(len(VARS)), A_eq=AEQ, b_eq=BEQ, bounds=BOUNDS, method="highs")
    if not res0.success:
        raise RuntimeError(res0.message)
    starts.append(res0.x)

    best = (phi(res0.x, w), "feasible", res0.x)
    for s in range(samples):
        c = rng.normal(size=len(VARS))
        res = linprog(c, A_eq=AEQ, b_eq=BEQ, bounds=BOUNDS, method="highs")
        if not res.success:
            continue
        val = phi(res.x, w)
        if val < best[0]:
            best = (val, f"lp{s}", res.x)
        starts.append(res.x)

    def obj(x):
        return phi(x, w)

    cons = [{"type": "eq", "fun": lambda x, row=row, rhs=rhs: float(row @ x - rhs)} for row, rhs in zip(AEQ, BEQ)]
    for si, st in enumerate(starts[: min(len(starts), 12)]):
        res = minimize(
            obj,
            st,
            method="SLSQP",
            bounds=BOUNDS,
            constraints=cons,
            options={"maxiter": 1000, "ftol": 1e-12, "disp": False},
        )
        if res.success:
            val = phi(res.x, w)
            if val < best[0]:
                best = (val, f"slsqp{si}", res.x)
    return best


def c5_data(k):
    sizes = np.array([k + 1, k, k + 1, k, k + 1], dtype=float)
    n = float(np.sum(sizes))
    m = sizes[0] * sizes[1]
    S = np.array(
        [
            sizes[1],
            sizes[0],
            m / sizes[2],
            m / sizes[3],
            m / sizes[4],
        ],
        dtype=float,
    )
    cap = n - S
    return sizes, n, m, S, cap


def normalize_y(y, sizes, cap):
    y = np.maximum(np.array(y, dtype=float), 0.0)
    den = float(np.sum(sizes * cap * y))
    if den <= 0:
        y = np.ones(5)
        den = float(np.sum(sizes * cap * y))
    return y / den


def gap_for_y(k, y, samples, seed):
    sizes, _n, m, _S, cap = c5_data(k)
    y = normalize_y(y, sizes, cap)
    w = layer_weights_from_classes(y)
    val, src, beta = solve_phi(w, samples=samples, seed=seed)
    gap = m * val - 1.0
    return gap, val, src, y, beta


def maximize_gap(k, samples, y_samples, seed):
    rng = np.random.default_rng(seed)
    candidates = [np.ones(5)]
    candidates.extend(np.eye(5))
    candidates.extend(rng.random(5) ** 2 for _ in range(y_samples))
    best = None
    for idx, y0 in enumerate(candidates):
        gap, val, src, y, beta = gap_for_y(k, y0, samples=samples, seed=seed + 17 * idx)
        if best is None or gap > best[0]:
            best = (gap, val, src, y, beta, idx)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--kmax", type=int, default=0)
    ap.add_argument("--samples", type=int, default=80)
    ap.add_argument("--y-samples", type=int, default=40)
    ap.add_argument("--seed", type=int, default=20260701)
    args = ap.parse_args()

    ks = range(args.k, args.kmax + 1) if args.kmax else [args.k]
    for k in ks:
        sizes, n, m, S, cap = c5_data(k)
        best = maximize_gap(k, samples=args.samples, y_samples=args.y_samples, seed=args.seed + k)
        gap, val, src, y, beta, idx = best
        nnz = int(np.sum(beta > 1e-9))
        print(
            f"k={k} N={int(n)} m={int(m)} gap={gap:+.12g} phi={val:.12g} "
            f"src={src} yidx={idx} beta_nnz={nnz}",
            flush=True,
        )
        print(
            "  sizes={} S={} cap={} y={}".format(
                [int(x) for x in sizes],
                [float(f"{x:.6g}") for x in S],
                [float(f"{x:.6g}") for x in cap],
                [float(f"{x:.6g}") for x in y],
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
