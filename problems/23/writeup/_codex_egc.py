"""Codex diagnostic: B-edge-gated corridor (EGC) feasibility.

GPT-Pro proposed a restricted corridor certificate for CORR.

For each bad edge f, layer pair i<j is routed through the actual B-edges
between consecutive shortest-geodesic layers. The weight on a B-edge e is

    alpha_{f,i,j}(e) = (1/(j-i)) * sum_{t=i}^{j-1} pi_{f,t}(e),

where pi_{f,t}(e) is the fraction of shortest f-geodesics using e between
layers t and t+1. Thus sum_e alpha_{f,i,j}(e)=1.

Define A_e(v) from left layer masses and B_e(v) from right layer masses:

    A_e(v)=sum_{f,i<j, v in I_i(f)} alpha_{f,i,j}(e) p_f(v)
    B_e(v)=sum_{f,i<j, v in I_j(f)} alpha_{f,i,j}(e) p_f(v)

The EGC-dual certificate asks for r_e>0 such that for all vertices v,

    sum_e ( r_e A_e(v) + r_e^{-1} B_e(v) ) <= N - S(v).

This implies CORR by sqrt(L_e R_e) <= (r_e L_e + r_e^{-1} R_e)/2.

This script is a floating-point scout. Any survivor must be rationalized and
checked with Fraction arithmetic before use.
"""

from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from _h import GENG, dec, loads


def canon_edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def blowup_edges(g6: str, t: int):
    n, edges = dec(g6)
    out = []
    for a, b in edges:
        for i in range(t):
            for j in range(t):
                out.append((a * t + i, b * t + j))
    return n * t, out


@dataclass
class EGCInstance:
    label: str
    n: int
    b_edges: list[tuple[int, int]]
    S: np.ndarray
    A: np.ndarray  # shape (m_edges, n)
    C: np.ndarray  # right-side coefficient, shape (m_edges, n)


def build_instance(info, label: str) -> EGCInstance | None:
    n = info["n"]
    b_edges = sorted(canon_edge(a, b) for a, b in info["Bset"])
    if not b_edges or not info["M"]:
        return None
    eidx = {e: k for k, e in enumerate(b_edges)}
    m = len(b_edges)
    S = np.zeros(n)
    A = np.zeros((m, n))
    C = np.zeros((m, n))

    for f in info["M"]:
        paths = info["cyc"][f]
        nf = len(paths)
        if nf == 0:
            raise AssertionError(("no paths", f))
        L = info["ell"][f]

        # Layer counts and p_f(v), using the orientation of paths in info['cyc'].
        layer_vertices: list[dict[int, float]] = [dict() for _ in range(L)]
        for P in paths:
            if len(P) != L:
                raise AssertionError((f, P, L))
            for i, v in enumerate(P):
                layer_vertices[i][v] = layer_vertices[i].get(v, 0.0) + 1.0 / nf

        for i in range(L):
            for v, pfv in layer_vertices[i].items():
                S[v] += pfv

        # pi[t][edge_index] = fraction of paths using this B-edge between t,t+1.
        pi = [dict() for _ in range(L - 1)]
        for P in paths:
            for t in range(L - 1):
                e = canon_edge(P[t], P[t + 1])
                k = eidx[e]
                pi[t][k] = pi[t].get(k, 0.0) + 1.0 / nf

        # Route every layer pair uniformly through the intervening gaps.
        for i in range(L):
            for j in range(i + 1, L):
                gap = j - i
                alpha = {}
                for t in range(i, j):
                    for k, val in pi[t].items():
                        alpha[k] = alpha.get(k, 0.0) + val / gap
                # Numerical sanity: alpha should be a probability over B-edges.
                s_alpha = sum(alpha.values())
                if abs(s_alpha - 1.0) > 1e-8:
                    raise AssertionError((label, f, i, j, s_alpha))
                for k, av in alpha.items():
                    for v, pfv in layer_vertices[i].items():
                        A[k, v] += av * pfv
                    for v, pfv in layer_vertices[j].items():
                        C[k, v] += av * pfv

    return EGCInstance(label=label, n=n, b_edges=b_edges, S=S, A=A, C=C)


def egc_budget(inst: EGCInstance, x: np.ndarray) -> np.ndarray:
    ep = np.exp(x)
    em = np.exp(-x)
    return ep @ inst.A + em @ inst.C


def solve_egc(inst: EGCInstance, restarts: int = 4, bound: float = 18.0):
    m = len(inst.b_edges)
    n = inst.n
    cap = inst.n - inst.S
    rng = np.random.default_rng(29)

    def obj(z):
        return float(z[-1])

    def jac_obj(z):
        g = np.zeros_like(z)
        g[-1] = 1.0
        return g

    def cons_fun(z):
        x = z[:-1]
        t = z[-1]
        # t >= normalized load budget/cap; cap should be positive.
        return t - egc_budget(inst, x) / cap

    def cons_jac(z):
        x = z[:-1]
        ep = np.exp(x)
        em = np.exp(-x)
        J = np.zeros((n, m + 1))
        # d(t - budget_v/cap_v)/dx_e
        J[:, :m] = (-(ep[:, None] * inst.A) + (em[:, None] * inst.C)).T / cap[:, None]
        J[:, m] = 1.0
        return J

    starts = [np.zeros(m)]
    for scale in [0.25, 0.8, 1.6]:
        for _ in range(max(1, restarts // 3)):
            starts.append(rng.normal(0.0, scale, size=m))

    best = None
    for x0 in starts:
        ratio0 = egc_budget(inst, x0) / cap
        z0 = np.concatenate([x0, [max(1.0, float(np.max(ratio0)))]])
        res = minimize(
            obj,
            z0,
            jac=jac_obj,
            constraints=[{"type": "ineq", "fun": cons_fun, "jac": cons_jac}],
            bounds=[(-bound, bound)] * m + [(0.0, None)],
            method="SLSQP",
            options={"maxiter": 1200, "ftol": 1e-10, "disp": False},
        )
        x = res.x[:-1]
        ratio = egc_budget(inst, x) / cap
        t = float(np.max(ratio))
        if best is None or t < best[0]:
            best = (t, x, res.success, str(res.message), int(np.argmax(ratio)))
    return best


def run_info(label: str, info, restarts: int):
    inst = build_instance(info, label)
    if inst is None:
        return None
    t, x, ok, msg, maxv = solve_egc(inst, restarts=restarts)
    raw = egc_budget(inst, x)
    gap = float(np.max(raw - (inst.n - inst.S)))
    return {
        "label": label,
        "n": inst.n,
        "bedges": len(inst.b_edges),
        "t": t,
        "gap": gap,
        "ok": ok,
        "msg": msg,
        "maxv": maxv,
        "cap": float(inst.n - inst.S[maxv]),
        "budget": float(raw[maxv]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restarts", type=int, default=5)
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--nmin", type=int, default=8)
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--stride", type=int, default=1)
    args = ap.parse_args()

    print("=== B-edge-gated corridor scout ===")
    tests = [
        ("FCp`_", 1),
        ("H?bB@_W", 1),
        ("I?BD@g]Qo", 1),
        ("I?ABCc]}?", 1),
        ("J?AEB?oE?W?", 1),
        ("J???E?pNu\\?", 2),
    ]
    for g6, blow in tests:
        if blow == 1:
            n, edges = dec(g6)
        else:
            n, edges = blowup_edges(g6, blow)
        info = loads(n, edges)
        if info is None:
            continue
        row = run_info(f"{g6}[{blow}]", info, args.restarts)
        if row:
            print(
                f"{row['label']:17} N={row['n']:3d} B={row['bedges']:3d} "
                f"ratio={row['t']:.9f} gap={row['gap']:+.3e} ok={row['ok']} "
                f"maxv={row['maxv']} budget/cap={row['budget']:.6f}/{row['cap']:.6f}",
                flush=True,
            )

    if args.census:
        for nn in range(args.nmin, args.nmax + 1):
            out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout.split()
            count = 0
            bad = 0
            worst = None
            for g6 in out[:: args.stride]:
                info = loads(*dec(g6))
                if info is None:
                    continue
                row = run_info(g6, info, max(2, args.restarts // 2))
                if not row:
                    continue
                count += 1
                if row["gap"] > 1e-6:
                    bad += 1
                if worst is None or row["gap"] > worst["gap"]:
                    worst = row
            print(
                f"census N={nn}: count={count} bad={bad} "
                f"worst_gap={None if worst is None else worst['gap']:+.3e} "
                f"@{None if worst is None else worst['label']}",
                flush=True,
            )


if __name__ == "__main__":
    main()
