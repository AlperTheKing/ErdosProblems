#!/usr/bin/env python3
"""
exp8_v2_run.py — Pre-registered hypercube Leg-4 M_L kink test (three-null version).

Preregistration: TRACK_A_PREREGISTRATION.json (FROZEN 2026-04-19).
Hypothesis: Delta(eps)/sqrt(n) on the signed hypercube (Huang sign pattern)
            exhibits a kink at eps = M_L that is absent on three geometry-killed nulls:
            ER_Gnp, sign_randomized_cube, degree_shuffle.

Observable (as specified in task prompt):
    A(eps) = A + eps * B,  with B a fixed random symmetric +/-1 matrix
             sharing the sparsity pattern of A (seeded per realization).
    Delta(eps) = | lambda_max(A(eps)) - lambda_max(A(0)) |
    Normalize by sqrt(n).

Kink detection:
    M0: single-slope linear regression y = a + b*eps
    M1: two-slope piecewise linear with knot FIXED at eps = M_L, continuity enforced
    Delta_BIC = BIC(M0) - BIC(M1), BIC = k*ln(N) - 2*ln(L); Gaussian L reduces to
                -(N/2)*ln(RSS/N) (up to additive constants — absorbed into BIC delta).
    slope_change = |b2 - b1|

Criteria (all required for LEG4_PASS):
    C1: slope_change(cube) / slope_change(null) >= 3.0 at n >= 11, for EACH of 3 nulls.
    C2: cube slope_change strictly monotonically increasing in n = 10,11,12,13,
        AND Spearman |rho(slope_change, n)| <= 0.3 on each null.
    C3: Delta_BIC(cube) >= 10 AND at least one null has Delta_BIC <= 2.

No post-hoc tuning. If a criterion fails -> report FAIL.
"""
from __future__ import annotations

import json
import os
import sys
import time
import math
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh, ArpackNoConvergence
from scipy.stats import spearmanr

# -------- FROZEN PARAMETERS (from preregistration) --------
M_L = 0.4804530139182014
N_VALUES = [10, 11, 12, 13]
N_REALIZATIONS_PER_N = 20
EPS_MIN = 0.1
EPS_MAX = 1.0
EPS_STEP = 0.005
RANDOM_SEED_BASE = 20260419

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_JSON = os.path.join(OUT_DIR, "exp8_v2_results.json")
REPORT_MD = os.path.join(OUT_DIR, "EXP8_V2_REPORT.md")
STATUS_MD = os.path.join(OUT_DIR, "STATUS.md")

# Wall-time budget for automatic degradation per task prompt
WALL_TIME_BUDGET_SEC = 45 * 60


# -------------------- Graph constructors --------------------

def hypercube_edges(n: int) -> np.ndarray:
    """Return array of (u, v) edges for Q_n with u < v. 2^n vertices, n*2^(n-1) edges."""
    N = 1 << n
    # For each vertex v and each bit i, edge (v, v xor (1<<i)) with v < v xor (1<<i)
    us = []
    vs = []
    for i in range(n):
        mask = 1 << i
        # vertices whose bit i is 0 -> flipping produces larger neighbor (since we go 0->1)
        arr = np.arange(N, dtype=np.int64)
        lo = arr[(arr & mask) == 0]
        hi = lo | mask
        us.append(lo)
        vs.append(hi)
    u = np.concatenate(us)
    v = np.concatenate(vs)
    return u, v


def huang_signs(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Huang sign convention: edge (v, v + e_i) gets sign (-1)^{v_i}.
    Here we pick the lower endpoint u (u < v, v = u | mask, bit i was 0 in u),
    so v_i in Huang's convention = bit_i of the lower vertex u, which is 0 for all these.
    That would trivially give +1 for every edge.

    Standard Huang (2019) construction is recursive: A_1 = [[0,1],[1,0]],
      A_{n+1} = [[A_n, I], [I, -A_n]].
    Equivalent closed form (one of many): for edge flipping bit i in vertex v (where v has
    bit i = 0), sign = (-1)^{popcount(v & ((1<<i) - 1))} * s(i), or equivalently the sign
    equals (-1)^{(number of 1-bits in v strictly below bit i)}.
    We use the closed form: sign(u, u | (1<<i)) = (-1)^{popcount(u & ((1<<i) - 1))}.
    """
    # Determine bit index i for each edge: i = log2(v XOR u)
    diff = v ^ u
    # bit index
    i = np.floor(np.log2(diff.astype(np.float64))).astype(np.int64)
    # mask of bits below i
    low_mask = (np.int64(1) << i) - 1
    # number of 1-bits in u below bit i
    low_bits = u & low_mask
    # popcount
    pc = np.zeros_like(u)
    x = low_bits.copy()
    while np.any(x > 0):
        pc += (x & 1).astype(pc.dtype)
        x >>= 1
    sign = np.where((pc & 1) == 0, 1, -1).astype(np.int8)
    return sign


def build_signed_hypercube(n: int) -> Tuple[sparse.csr_matrix, np.ndarray, np.ndarray]:
    """Return (A, u, v) for the Huang-signed hypercube adjacency."""
    N = 1 << n
    u, v = hypercube_edges(n)
    s = huang_signs(u, v).astype(np.float64)
    row = np.concatenate([u, v])
    col = np.concatenate([v, u])
    data = np.concatenate([s, s])
    A = sparse.csr_matrix((data, (row, col)), shape=(N, N))
    return A, u, v


def build_cube_unsigned(n: int) -> Tuple[sparse.csr_matrix, np.ndarray, np.ndarray]:
    N = 1 << n
    u, v = hypercube_edges(n)
    row = np.concatenate([u, v])
    col = np.concatenate([v, u])
    data = np.ones(row.shape[0], dtype=np.float64)
    A = sparse.csr_matrix((data, (row, col)), shape=(N, N))
    return A, u, v


def build_sign_randomized_cube(n: int, rng: np.random.Generator) -> Tuple[sparse.csr_matrix, np.ndarray, np.ndarray]:
    N = 1 << n
    u, v = hypercube_edges(n)
    s = rng.choice(np.array([-1.0, 1.0]), size=u.shape[0])
    row = np.concatenate([u, v])
    col = np.concatenate([v, u])
    data = np.concatenate([s, s])
    A = sparse.csr_matrix((data, (row, col)), shape=(N, N))
    return A, u, v


def build_er_gnp(n: int, rng: np.random.Generator) -> Tuple[sparse.csr_matrix, np.ndarray, np.ndarray]:
    """Erdős-Rényi G(2^n, p) with p = n / 2^n. Unsigned +1 adjacency."""
    N = 1 << n
    p = n / N
    # Sample upper-triangle edges via bernoulli; use efficient sampling for small p.
    # Expected number of edges E[|E|] = C(N,2) * p = (N-1)/2 * n ≈ n*N/2.
    # Use geometric skipping for efficiency.
    edges_u = []
    edges_v = []
    # Iterate over potential edges linearly in geometric gaps
    # index space: pairs (i,j) with i<j, indexed lexicographically
    total_pairs = N * (N - 1) // 2
    if total_pairs == 0:
        raise ValueError("No pairs")
    # Geometric sampling
    idx = -1
    # Using log(1-U)/log(1-p) formula for next skip
    log_one_minus_p = math.log1p(-p)
    while True:
        gap = int(math.floor(math.log1p(-rng.random()) / log_one_minus_p))
        idx += 1 + gap
        if idx >= total_pairs:
            break
        # Convert linear idx to (i,j) with i<j. Triangular index.
        # i is the largest integer with i*(2N - i - 1)/2 <= idx. Solve approx.
        # Use float approximation then correct.
        # idx = i*(N-1) - i*(i-1)/2 + (j - i - 1), i<j<N
        # Solve for i: i*(2N-1-i)/2 <= idx
        # Use binary search for correctness
        lo, hi = 0, N - 2
        while lo < hi:
            mid = (lo + hi + 1) // 2
            # cumulative count of pairs with first index < mid:
            # sum_{k=0}^{mid-1} (N - 1 - k) = mid*(N-1) - mid*(mid-1)/2
            count = mid * (N - 1) - mid * (mid - 1) // 2
            if count <= idx:
                lo = mid
            else:
                hi = mid - 1
        i = lo
        count_i = i * (N - 1) - i * (i - 1) // 2
        j = i + 1 + (idx - count_i)
        edges_u.append(i)
        edges_v.append(j)

    if len(edges_u) == 0:
        # Handle empty graph
        A = sparse.csr_matrix((N, N), dtype=np.float64)
        return A, np.array([], dtype=np.int64), np.array([], dtype=np.int64)

    u = np.array(edges_u, dtype=np.int64)
    v = np.array(edges_v, dtype=np.int64)
    row = np.concatenate([u, v])
    col = np.concatenate([v, u])
    data = np.ones(row.shape[0], dtype=np.float64)
    A = sparse.csr_matrix((data, (row, col)), shape=(N, N))
    return A, u, v


def build_degree_shuffle(n: int, rng: np.random.Generator) -> Tuple[sparse.csr_matrix, np.ndarray, np.ndarray]:
    """Configuration-model random graph with every vertex degree = n.
    Simple double-edge swap starting from the hypercube to preserve degree sequence
    and avoid self-loops / multi-edges. More robust than raw config model for regular graphs.
    """
    N = 1 << n
    # Start from the hypercube's edge list
    u_hc, v_hc = hypercube_edges(n)
    edges = list(zip(u_hc.tolist(), v_hc.tolist()))
    E = len(edges)
    # Edge set for O(1) membership checks
    edge_set = set()
    for a, b in edges:
        if a > b:
            a, b = b, a
        edge_set.add((a, b))

    # Number of swap attempts: typical rule is ~10 * E for good mixing
    n_swaps = 10 * E
    attempts = 0
    successes = 0
    max_attempts = n_swaps * 4  # safety cap
    while successes < n_swaps and attempts < max_attempts:
        attempts += 1
        i1 = rng.integers(0, E)
        i2 = rng.integers(0, E)
        if i1 == i2:
            continue
        a, b = edges[i1]
        c, d = edges[i2]
        # Optionally flip one edge's orientation
        if rng.random() < 0.5:
            c, d = d, c
        # Proposed new edges: (a, c) and (b, d)
        if len({a, b, c, d}) < 4:
            continue
        e1 = (a, c) if a < c else (c, a)
        e2 = (b, d) if b < d else (d, b)
        if e1 in edge_set or e2 in edge_set:
            continue
        # Remove old, add new
        old1 = (a, b) if a < b else (b, a)
        old2 = (c, d) if c < d else (d, c)
        edge_set.remove(old1)
        edge_set.remove(old2)
        edge_set.add(e1)
        edge_set.add(e2)
        edges[i1] = (a, c)
        edges[i2] = (b, d)
        successes += 1

    u_arr = np.array([e[0] for e in edges], dtype=np.int64)
    v_arr = np.array([e[1] for e in edges], dtype=np.int64)
    row = np.concatenate([u_arr, v_arr])
    col = np.concatenate([v_arr, u_arr])
    data = np.ones(row.shape[0], dtype=np.float64)
    A = sparse.csr_matrix((data, (row, col)), shape=(N, N))
    return A, u_arr, v_arr


# -------------------- Perturbation and eigenvalue --------------------

def build_perturbation_B(u: np.ndarray, v: np.ndarray, N: int, rng: np.random.Generator) -> sparse.csr_matrix:
    """Symmetric +/-1 matrix with same sparsity pattern as the edge set (u,v)."""
    if u.shape[0] == 0:
        return sparse.csr_matrix((N, N), dtype=np.float64)
    s = rng.choice(np.array([-1.0, 1.0]), size=u.shape[0])
    row = np.concatenate([u, v])
    col = np.concatenate([v, u])
    data = np.concatenate([s, s])
    B = sparse.csr_matrix((data, (row, col)), shape=(N, N))
    return B


def lambda_max(A: sparse.csr_matrix) -> float:
    """Largest algebraic eigenvalue via sparse Lanczos."""
    N = A.shape[0]
    if N <= 2:
        # fall back to dense for tiny
        vals = np.linalg.eigvalsh(A.toarray())
        return float(vals.max())
    # Deterministic starting vector for reproducibility
    v0 = np.ones(N) / math.sqrt(N)
    try:
        vals = eigsh(A, k=1, which='LA', v0=v0, tol=1e-8, maxiter=2000, return_eigenvectors=False)
        return float(vals[0])
    except ArpackNoConvergence as e:
        # Retry with looser tolerance
        try:
            vals = eigsh(A, k=1, which='LA', v0=v0, tol=1e-6, maxiter=5000, return_eigenvectors=False)
            return float(vals[0])
        except Exception:
            # Final fallback: shift-and-invert via LM mode on A + cI
            # Use power iteration on A - c I with large c to dominate
            c = 2 * n_of(A)
            vals = eigsh(A + c * sparse.eye(N), k=1, which='LM', v0=v0, tol=1e-6, maxiter=5000, return_eigenvectors=False)
            return float(vals[0] - c)


def n_of(A: sparse.csr_matrix) -> float:
    return float(abs(A).sum(axis=1).max())


# -------------------- Piecewise-linear kink analysis --------------------

def fit_m0(eps: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
    """Single slope y = a + b*eps. Return (a, b, rss)."""
    X = np.column_stack([np.ones_like(eps), eps])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    a, b = coef[0], coef[1]
    resid = y - (a + b * eps)
    rss = float(np.sum(resid ** 2))
    return float(a), float(b), rss


def fit_m1_continuous_knot(eps: np.ndarray, y: np.ndarray, knot: float) -> Tuple[float, float, float, float]:
    """
    Continuous piecewise-linear at fixed knot t=knot:
      y = a + b1 * eps                        for eps < knot
      y = a + b1 * knot + b2 * (eps - knot)   for eps >= knot
    (continuity at eps=knot enforced automatically by construction).
    Equivalently, y = a + b1 * eps + (b2 - b1) * max(eps - knot, 0).

    Return (a, b1, b2, rss).
    """
    hinge = np.maximum(eps - knot, 0.0)
    # Parameters: a, b1, c where c = b2 - b1 and then b2 = b1 + c
    X = np.column_stack([np.ones_like(eps), eps, hinge])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    a, b1, c = coef[0], coef[1], coef[2]
    b2 = b1 + c
    resid = y - (a + b1 * eps + c * hinge)
    rss = float(np.sum(resid ** 2))
    return float(a), float(b1), float(b2), rss


def bic(rss: float, n_points: int, k_params: int) -> float:
    """Gaussian-residuals BIC up to an additive constant that cancels in deltas.
    BIC = k*ln(N) - 2*ln(L)
    With Gaussian likelihood and MLE sigma^2 = RSS/N:
      -2*ln(L) = N*ln(2*pi) + N*ln(RSS/N) + N   (additive consts)
    We keep only the RSS-dependent term + k*ln(N), which is standard for BIC deltas.
    """
    if rss <= 0:
        # Pathological; return a large negative value to flag
        return float('-inf')
    return k_params * math.log(n_points) + n_points * math.log(rss / n_points)


def analyze_curve(eps_grid: np.ndarray, y: np.ndarray, knot: float) -> Dict:
    a0, b0, rss0 = fit_m0(eps_grid, y)
    a1, b1l, b1r, rss1 = fit_m1_continuous_knot(eps_grid, y, knot)
    N = eps_grid.shape[0]
    bic_m0 = bic(rss0, N, k_params=2)     # a, b
    bic_m1 = bic(rss1, N, k_params=3)     # a, b1, c
    delta_bic = bic_m0 - bic_m1
    slope_change = abs(b1r - b1l)
    return {
        "M0": {"a": a0, "b": b0, "rss": rss0, "bic": bic_m0},
        "M1": {"a": a1, "b_left": b1l, "b_right": b1r, "rss": rss1, "bic": bic_m1, "knot": knot},
        "delta_bic": float(delta_bic),
        "slope_change": float(slope_change),
    }


# -------------------- Per-realization work unit --------------------

def run_one_realization(graph_type: str, n: int, realization_idx: int, eps_grid: np.ndarray) -> np.ndarray:
    """Return Delta(eps)/sqrt(n) for the 181-point eps_grid, single realization."""
    seed = RANDOM_SEED_BASE + n * 1000 + realization_idx
    rng = np.random.default_rng(seed)
    N_nodes = 1 << n

    # Build base graph A
    if graph_type == "cube":
        A, u, v = build_signed_hypercube(n)
    elif graph_type == "sign_randomized_cube":
        A, u, v = build_sign_randomized_cube(n, rng)
    elif graph_type == "ER_Gnp":
        A, u, v = build_er_gnp(n, rng)
    elif graph_type == "degree_shuffle":
        A, u, v = build_degree_shuffle(n, rng)
    else:
        raise ValueError(f"Unknown graph_type: {graph_type}")

    # Perturbation matrix B (same sparsity as A)
    B = build_perturbation_B(u, v, N_nodes, rng)

    # lambda_max at eps = 0
    lam0 = lambda_max(A)

    # Sweep eps grid
    sqrt_n = math.sqrt(n)
    # Precompute: for each eps, A + eps*B. We can't avoid recomputation of eigensolve,
    # but we can reuse the starting vector.
    out = np.empty_like(eps_grid)
    for i, eps in enumerate(eps_grid):
        A_eps = A + eps * B
        lam = lambda_max(A_eps)
        out[i] = abs(lam - lam0) / sqrt_n
    return out


# -------------------- Driver --------------------

def main():
    t_start = time.time()

    # Build eps_grid from FROZEN step spec
    # Use np.arange with careful endpoint handling
    num_points = int(round((EPS_MAX - EPS_MIN) / EPS_STEP)) + 1
    eps_grid = np.linspace(EPS_MIN, EPS_MAX, num_points)
    assert eps_grid.shape[0] == 181, f"eps_grid length = {eps_grid.shape[0]}, expected 181"
    assert abs(eps_grid[0] - EPS_MIN) < 1e-12 and abs(eps_grid[-1] - EPS_MAX) < 1e-12

    graph_types = ["cube", "ER_Gnp", "sign_randomized_cube", "degree_shuffle"]
    results_by_graph_n: Dict[str, Dict[int, Dict]] = {g: {} for g in graph_types}

    deviations: List[str] = []

    # Decide realization counts — start with 20 for all n, monitor wall time
    realizations_spec = {n: N_REALIZATIONS_PER_N for n in N_VALUES}

    print(f"[{time.strftime('%H:%M:%S')}] exp8_v2 starting. N_VALUES={N_VALUES}, grid={num_points} points", flush=True)

    for n in N_VALUES:
        # Early wall-time check: if we've burned > 70% of budget and still have n=13 to do,
        # degrade n=13 realizations to 10 (document deviation).
        if n == 13:
            elapsed = time.time() - t_start
            if elapsed > 0.6 * WALL_TIME_BUDGET_SEC:
                if realizations_spec[13] > 10:
                    realizations_spec[13] = 10
                    deviations.append(
                        f"Reduced n=13 realizations from 20 to 10 due to elapsed={elapsed:.0f}s "
                        f"(> 60% of {WALL_TIME_BUDGET_SEC}s budget at start of n=13). "
                        "Floor of 10 respected per preregistration deviation rule."
                    )
                    print(f"[DEVIATION] {deviations[-1]}", flush=True)

        for g in graph_types:
            n_real = realizations_spec[n]
            print(f"[{time.strftime('%H:%M:%S')}] n={n} graph={g} realizations={n_real}", flush=True)
            curves = np.empty((n_real, eps_grid.shape[0]), dtype=np.float64)
            t_gn = time.time()
            for r in range(n_real):
                curves[r] = run_one_realization(g, n, r, eps_grid)
                if (r + 1) % 5 == 0 or r == n_real - 1:
                    dt = time.time() - t_gn
                    print(f"    [{time.strftime('%H:%M:%S')}] {g} n={n} real {r+1}/{n_real} ({dt:.1f}s)", flush=True)
            mean_curve = curves.mean(axis=0)
            analysis = analyze_curve(eps_grid, mean_curve, knot=M_L)
            results_by_graph_n[g][n] = {
                "n_realizations": n_real,
                "mean_curve": mean_curve.tolist(),
                "analysis": analysis,
            }

            # Mid-run wall-time guard for n=13 only
            if n == 13:
                elapsed = time.time() - t_start
                if elapsed > WALL_TIME_BUDGET_SEC and g != graph_types[-1]:
                    print(f"[WARN] wall time {elapsed:.0f}s exceeds budget; continuing to completion.", flush=True)

    # Checkpoint raw curves to pickle so any downstream serialization bug doesn't
    # cost us the compute.
    import pickle
    ckpt_path = os.path.join(OUT_DIR, "exp8_v2_raw_curves.pkl")
    try:
        with open(ckpt_path, "wb") as f:
            pickle.dump({"results_by_graph_n": results_by_graph_n, "eps_grid": eps_grid, "deviations": deviations}, f)
        print(f"[{time.strftime('%H:%M:%S')}] Checkpointed raw curves to {ckpt_path}", flush=True)
    except Exception as e:
        print(f"[WARN] checkpoint failed: {e}", flush=True)

    # Assemble criterion evaluation
    cube = results_by_graph_n["cube"]
    nulls = {k: results_by_graph_n[k] for k in ["ER_Gnp", "sign_randomized_cube", "degree_shuffle"]}

    # C1: slope_change(cube) / slope_change(null) >= 3 at each n >= 11 for each null
    c1_details = {}
    c1_pass_per_null = {}
    for null_id, null_data in nulls.items():
        per_n = {}
        null_pass = True
        for n in [nn for nn in N_VALUES if nn >= 11]:
            cube_sc = cube[n]["analysis"]["slope_change"]
            null_sc = null_data[n]["analysis"]["slope_change"]
            if null_sc == 0:
                ratio = float('inf') if cube_sc > 0 else float('nan')
            else:
                ratio = cube_sc / null_sc
            ok = (ratio >= 3.0) and math.isfinite(ratio)
            per_n[n] = {"cube_slope_change": cube_sc, "null_slope_change": null_sc, "ratio": ratio, "passes_3x": ok}
            if not ok:
                null_pass = False
        c1_details[null_id] = per_n
        c1_pass_per_null[null_id] = null_pass
    c1_pass = all(c1_pass_per_null.values())

    # C2: cube strictly monotonically increasing in n; each null Spearman |rho| <= 0.3
    cube_slopes = [cube[n]["analysis"]["slope_change"] for n in N_VALUES]
    strictly_increasing = all(cube_slopes[i] < cube_slopes[i + 1] for i in range(len(cube_slopes) - 1))
    c2_null_details = {}
    c2_nulls_ok = True
    for null_id, null_data in nulls.items():
        slopes = [null_data[n]["analysis"]["slope_change"] for n in N_VALUES]
        rho, pval = spearmanr(N_VALUES, slopes)
        if not np.isfinite(rho):
            rho = 0.0
        ok = abs(rho) <= 0.3
        c2_null_details[null_id] = {"slopes": slopes, "spearman_rho": float(rho), "p_value": float(pval), "abs_rho_leq_0.3": ok}
        if not ok:
            c2_nulls_ok = False
    c2_pass = strictly_increasing and c2_nulls_ok

    # C3: cube DeltaBIC >= 10 AND at least one null DeltaBIC <= 2. Use max-n per preregistration
    # (preregistration doesn't fix which n for C3; we report all n and pass at any n where
    # cube >= 10 and at least one null <= 2. To avoid cherry-picking, we also report the
    # strict reading at the largest n.)
    # Strict version: at n = max(N_VALUES), cube DeltaBIC >= 10 AND some null DeltaBIC <= 2.
    n_max = max(N_VALUES)
    cube_dbic_nmax = cube[n_max]["analysis"]["delta_bic"]
    null_dbic_nmax = {null_id: nulls[null_id][n_max]["analysis"]["delta_bic"] for null_id in nulls}
    cube_ok = cube_dbic_nmax >= 10.0
    any_null_ok = any(v <= 2.0 for v in null_dbic_nmax.values())
    c3_pass = cube_ok and any_null_ok

    # Also report cube & nulls delta_bic across all n for transparency
    c3_by_n = {}
    for n in N_VALUES:
        c3_by_n[n] = {
            "cube_delta_bic": cube[n]["analysis"]["delta_bic"],
            "null_delta_bic": {null_id: nulls[null_id][n]["analysis"]["delta_bic"] for null_id in nulls},
        }

    verdict = "LEG4_PASS" if (c1_pass and c2_pass and c3_pass) else "LEG4_FAIL"

    wall_time_sec = time.time() - t_start

    # Assemble output JSON per preregistered schema
    def pack_by_n(d: Dict[int, Dict]) -> Dict:
        out = {}
        for n, v in d.items():
            out[str(n)] = {
                "n_realizations": v["n_realizations"],
                "mean_curve": v["mean_curve"],
                "analysis": v["analysis"],
            }
        return out

    output = {
        "experiment": "exp8_v2",
        "date": "2026-04-19",
        "preregistration_ref": "TRACK_A_PREREGISTRATION.json",
        "hypothesis": "Delta(eps)/sqrt(n) on a signed hypercube has a kink at eps = M_L that is absent on all three geometry-killed nulls.",
        "M_L": M_L,
        "eps_grid": eps_grid.tolist(),
        "by_n_cube": pack_by_n(cube),
        "by_n_ER_Gnp": pack_by_n(nulls["ER_Gnp"]),
        "by_n_sign_randomized_cube": pack_by_n(nulls["sign_randomized_cube"]),
        "by_n_degree_shuffle": pack_by_n(nulls["degree_shuffle"]),
        "model_selection": {
            "method": "piecewise_linear_continuous_knot_fixed_at_M_L",
            "M0_params": 2,
            "M1_params": 3,
            "BIC_definition": "k*ln(N) + N*ln(RSS/N) (Gaussian, additive constants dropped)",
            "delta_bic_sign_convention": "delta_bic = BIC(M0) - BIC(M1); positive => M1 preferred"
        },
        "criteria_results": {
            "C1_strength_ratio": {
                "threshold": 3.0,
                "n_min": 11,
                "per_null": c1_details,
                "per_null_pass": c1_pass_per_null,
                "overall_pass": c1_pass,
            },
            "C2_scaling_monotonic": {
                "cube_slopes_by_n": dict(zip([str(n) for n in N_VALUES], cube_slopes)),
                "cube_strictly_increasing": strictly_increasing,
                "nulls": c2_null_details,
                "overall_pass": c2_pass,
            },
            "C3_model_selection": {
                "cube_threshold": 10.0,
                "null_threshold": 2.0,
                "evaluated_at_n": n_max,
                "cube_delta_bic_at_nmax": cube_dbic_nmax,
                "null_delta_bic_at_nmax": null_dbic_nmax,
                "cube_meets_threshold": cube_ok,
                "at_least_one_null_meets_threshold": any_null_ok,
                "delta_bic_by_n": c3_by_n,
                "overall_pass": c3_pass,
            },
        },
        "verdict": verdict,
        "wall_time_sec": wall_time_sec,
        "implementation_notes": {
            "observable": "Delta(eps) = |lambda_max(A + eps*B) - lambda_max(A)|; normalize by sqrt(n).",
            "B_construction": "Symmetric +/-1 matrix with same sparsity pattern as A, entries drawn i.i.d. uniform {-1,+1}. Seeded per realization.",
            "huang_signs": "Closed-form: for edge (u, u|2^i) with u_i=0, sign = (-1)^{popcount(u & (2^i - 1))}.",
            "eigensolver": "scipy.sparse.linalg.eigsh(k=1, which='LA', v0=ones/sqrt(N), tol=1e-8).",
            "ER_sampling": "Geometric-skip sampling with linear-to-triangular index decoding.",
            "degree_shuffle": "Start from hypercube edges, perform ~10*|E| double-edge swaps preserving degree sequence with no self-loops / multi-edges.",
            "seeding": "seed = RANDOM_SEED_BASE + n*1000 + realization_idx; shared rng across graph build and B construction within a realization.",
            "deviations": deviations,
        },
    }

    def _json_default(o):
        # numpy scalar coercion
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

    with open(RESULTS_JSON, "w") as f:
        json.dump(output, f, indent=2, default=_json_default)
    print(f"[{time.strftime('%H:%M:%S')}] Wrote {RESULTS_JSON} ({os.path.getsize(RESULTS_JSON)} bytes)", flush=True)

    # --- Write report ---
    def fmt(x):
        if isinstance(x, float):
            if math.isnan(x):
                return "NaN"
            if math.isinf(x):
                return "inf"
            return f"{x:.4g}"
        return str(x)

    lines = []
    lines.append(f"# EXP8_v2 — Hypercube Leg-4 M_L Kink Test (three-null)")
    lines.append("")
    lines.append(f"**Date:** 2026-04-19  ")
    lines.append(f"**Preregistration:** `TRACK_A_PREREGISTRATION.json` (FROZEN)  ")
    lines.append(f"**Wall time:** {wall_time_sec:.1f} s  ")
    lines.append(f"**Verdict:** **{verdict}**")
    lines.append("")
    lines.append("## Hypothesis")
    lines.append("")
    lines.append("Delta(eps)/sqrt(n) on the Huang-signed hypercube exhibits a kink at eps = M_L = " + f"{M_L:.7f}" + " that is absent on three geometry-killed nulls (ER_Gnp, sign_randomized_cube, degree_shuffle).")
    lines.append("")
    lines.append("## C1 — Strength ratio (cube / null) ≥ 3 at n ≥ 11")
    lines.append("")
    lines.append("| null | n | cube Δslope | null Δslope | ratio | passes 3× |")
    lines.append("|---|---|---|---|---|---|")
    for null_id in ["ER_Gnp", "sign_randomized_cube", "degree_shuffle"]:
        for n in [11, 12, 13]:
            d = c1_details[null_id][n]
            lines.append(f"| {null_id} | {n} | {fmt(d['cube_slope_change'])} | {fmt(d['null_slope_change'])} | {fmt(d['ratio'])} | {'yes' if d['passes_3x'] else 'NO'} |")
    lines.append("")
    lines.append(f"**C1 overall:** {'PASS' if c1_pass else 'FAIL'}")
    lines.append("")
    lines.append("## C2 — Scaling")
    lines.append("")
    lines.append(f"Cube Δslope by n: " + ", ".join([f"n={n}:{fmt(s)}" for n, s in zip(N_VALUES, cube_slopes)]))
    lines.append(f"Cube strictly increasing: **{strictly_increasing}**")
    lines.append("")
    lines.append("| null | slopes n=10..13 | Spearman ρ | |ρ| ≤ 0.3 |")
    lines.append("|---|---|---|---|")
    for null_id, d in c2_null_details.items():
        lines.append(f"| {null_id} | {', '.join(fmt(s) for s in d['slopes'])} | {fmt(d['spearman_rho'])} | {'yes' if d['abs_rho_leq_0.3'] else 'NO'} |")
    lines.append("")
    lines.append(f"**C2 overall:** {'PASS' if c2_pass else 'FAIL'}")
    lines.append("")
    lines.append(f"## C3 — Model selection (evaluated at n = {n_max})")
    lines.append("")
    lines.append(f"Cube ΔBIC = {fmt(cube_dbic_nmax)} (threshold ≥ 10): **{'PASS' if cube_ok else 'FAIL'}**")
    lines.append("")
    lines.append("| null | ΔBIC at n=13 | ≤ 2 |")
    lines.append("|---|---|---|")
    for null_id, v in null_dbic_nmax.items():
        lines.append(f"| {null_id} | {fmt(v)} | {'yes' if v <= 2.0 else 'NO'} |")
    lines.append("")
    lines.append(f"At least one null ≤ 2: **{'yes' if any_null_ok else 'NO'}**")
    lines.append("")
    lines.append(f"**C3 overall:** {'PASS' if c3_pass else 'FAIL'}")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"- C1: {'PASS' if c1_pass else 'FAIL'}")
    lines.append(f"- C2: {'PASS' if c2_pass else 'FAIL'}")
    lines.append(f"- C3: {'PASS' if c3_pass else 'FAIL'}")
    lines.append("")
    lines.append(f"**LEG 4 VERDICT: {verdict}**")
    if deviations:
        lines.append("")
        lines.append("## Deviations from preregistration")
        for d in deviations:
            lines.append(f"- {d}")

    with open(REPORT_MD, "w") as f:
        f.write("\n".join(lines))
    print(f"[{time.strftime('%H:%M:%S')}] Wrote {REPORT_MD}", flush=True)

    print("")
    print(f"==== FINAL VERDICT: {verdict} ====")
    print(f"Wall time: {wall_time_sec:.1f}s")
    if deviations:
        print("Deviations:")
        for d in deviations:
            print(f"  - {d}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Document any blocker in STATUS.md per task prompt rules
        import traceback
        tb = traceback.format_exc()
        with open(STATUS_MD, "w") as f:
            f.write(f"# exp8_v2 STATUS\n\nDate: 2026-04-19\n\n**BLOCKED**\n\n")
            f.write(f"Exception: `{e.__class__.__name__}: {e}`\n\n")
            f.write(f"```\n{tb}\n```\n")
        print(f"[FATAL] {e}", file=sys.stderr)
        print(tb, file=sys.stderr)
        sys.exit(1)
