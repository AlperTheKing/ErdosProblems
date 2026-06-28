"""Codex diagnostic: Capacitated Adaptive Gate Edge (CAGE) scout.

This is a floating-point feasibility scout for GPT-Pro's CAGE certificate.
It is not an acceptance checker.  Any survivor must be rationalized and
checked exactly with Fraction arithmetic.

For each bad edge f and each shortest-geodesic gap t, CAGE fixes the total
interval-pair demand routed through each actual B-edge gate at that gap.  It
then asks for shared gate ratios r_g so that the AM-GM majorant fits every
vertex budget N-S(v).

The scout alternates:
  1. fixed adaptive routing alpha -> convex optimization in log(r_g);
  2. fixed log(r_g) -> linear program in alpha and max ratio eta.
"""

from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog, minimize

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
class AlphaVar:
    pair: int
    gate: int
    left: list[tuple[int, float]]
    right: list[tuple[int, float]]
    init: float


@dataclass
class CAGEInstance:
    label: str
    n: int
    cap: np.ndarray
    gates: list[tuple[int, int, tuple[int, int]]]
    vars: list[AlphaVar]
    Aeq: np.ndarray
    beq: np.ndarray
    alpha0: np.ndarray


def build_instance(info, label: str) -> CAGEInstance | None:
    n = info["n"]
    if not info["M"]:
        return None
    S = np.zeros(n)
    gates: list[tuple[int, int, tuple[int, int]]] = []
    gate_index: dict[tuple[int, int, tuple[int, int]], int] = {}
    pair_index: dict[tuple[int, int, int], int] = {}
    pair_count = 0
    vars_: list[AlphaVar] = []
    r2_rows: dict[int, dict[int, float]] = {}
    r2_rhs: dict[int, float] = {}

    for f_idx, f in enumerate(info["M"]):
        paths = info["cyc"][f]
        nf = len(paths)
        if nf == 0:
            raise AssertionError(("no paths", label, f))
        L = info["ell"][f]
        layer_vertices: list[dict[int, float]] = [dict() for _ in range(L)]
        for P in paths:
            if len(P) != L:
                raise AssertionError((label, f, P, L))
            for i, v in enumerate(P):
                layer_vertices[i][v] = layer_vertices[i].get(v, 0.0) + 1.0 / nf
        for i in range(L):
            for v, pfv in layer_vertices[i].items():
                S[v] += pfv

        # pi[t][edge] = fraction of shortest paths using edge at gap t.
        pi: list[dict[tuple[int, int], float]] = [dict() for _ in range(L - 1)]
        for P in paths:
            for t in range(L - 1):
                e = canon_edge(P[t], P[t + 1])
                pi[t][e] = pi[t].get(e, 0.0) + 1.0 / nf

        H = []
        for t in range(L - 1):
            ht = 0.0
            for i in range(t + 1):
                for j in range(t + 1, L):
                    ht += 1.0 / (j - i)
            H.append(ht)

        for i in range(L):
            for j in range(i + 1, L):
                pair_index[(f_idx, i, j)] = pair_count
                pair_count += 1

        for t in range(L - 1):
            for e, pe in pi[t].items():
                key = (f_idx, t, e)
                g = len(gates)
                gate_index[key] = g
                gates.append(key)
                r2_rows[g] = {}
                r2_rhs[g] = H[t] * pe

        for i in range(L):
            for j in range(i + 1, L):
                pidx = pair_index[(f_idx, i, j)]
                gap = j - i
                for t in range(i, j):
                    for e, pe in pi[t].items():
                        g = gate_index[(f_idx, t, e)]
                        init = pe / gap
                        vidx = len(vars_)
                        vars_.append(
                            AlphaVar(
                                pair=pidx,
                                gate=g,
                                left=list(layer_vertices[i].items()),
                                right=list(layer_vertices[j].items()),
                                init=init,
                            )
                        )
                        r2_rows[g][vidx] = 1.0

    m = len(vars_)
    rows = []
    rhs = []
    for p in range(pair_count):
        row = np.zeros(m)
        for k, av in enumerate(vars_):
            if av.pair == p:
                row[k] = 1.0
        rows.append(row)
        rhs.append(1.0)
    for g in range(len(gates)):
        row = np.zeros(m)
        for k, coeff in r2_rows[g].items():
            row[k] = coeff
        rows.append(row)
        rhs.append(r2_rhs[g])
    Aeq = np.vstack(rows)
    beq = np.array(rhs)
    alpha0 = np.array([av.init for av in vars_])
    if np.max(np.abs(Aeq @ alpha0 - beq)) > 1e-8:
        raise AssertionError((label, "uniform alpha violates equalities", np.max(np.abs(Aeq @ alpha0 - beq))))
    cap = np.array([n - S[v] for v in range(n)])
    if np.any(cap <= 0):
        raise AssertionError((label, "nonpositive cap", cap))
    return CAGEInstance(label=label, n=n, cap=cap, gates=gates, vars=vars_, Aeq=Aeq, beq=beq, alpha0=alpha0)


def aggregate(inst: CAGEInstance, alpha: np.ndarray):
    g = len(inst.gates)
    A = np.zeros((g, inst.n))
    B = np.zeros((g, inst.n))
    for val, av in zip(alpha, inst.vars):
        if val == 0:
            continue
        for v, pfv in av.left:
            A[av.gate, v] += val * pfv
        for v, pfv in av.right:
            B[av.gate, v] += val * pfv
    return A, B


def budget(A: np.ndarray, B: np.ndarray, x: np.ndarray):
    ep = np.exp(x)
    em = np.exp(-x)
    return ep @ A + em @ B


def solve_x(inst: CAGEInstance, alpha: np.ndarray, x0=None, bound=18.0):
    A, B = aggregate(inst, alpha)
    g = len(inst.gates)
    n = inst.n
    if x0 is None:
        x0 = np.zeros(g)

    def obj(z):
        return float(z[-1])

    def jac_obj(z):
        out = np.zeros_like(z)
        out[-1] = 1.0
        return out

    def cons_fun(z):
        x = z[:-1]
        t = z[-1]
        return t - budget(A, B, x) / inst.cap

    def cons_jac(z):
        x = z[:-1]
        ep = np.exp(x)
        em = np.exp(-x)
        J = np.zeros((n, g + 1))
        J[:, :g] = (-(ep[:, None] * A) + (em[:, None] * B)).T / inst.cap[:, None]
        J[:, g] = 1.0
        return J

    ratio0 = budget(A, B, x0) / inst.cap
    z0 = np.concatenate([x0, [max(1.0, float(np.max(ratio0)))]] )
    res = minimize(
        obj,
        z0,
        jac=jac_obj,
        constraints=[{"type": "ineq", "fun": cons_fun, "jac": cons_jac}],
        bounds=[(-bound, bound)] * g + [(0.0, None)],
        method="SLSQP",
        options={"maxiter": 1500, "ftol": 1e-11, "disp": False},
    )
    x = res.x[:-1]
    ratio = budget(A, B, x) / inst.cap
    return float(np.max(ratio)), x, bool(res.success), str(res.message)


def solve_alpha(inst: CAGEInstance, x: np.ndarray):
    m = len(inst.vars)
    n = inst.n
    C = np.zeros((n, m))
    ep = np.exp(x)
    em = np.exp(-x)
    for k, av in enumerate(inst.vars):
        for v, pfv in av.left:
            C[v, k] += ep[av.gate] * pfv
        for v, pfv in av.right:
            C[v, k] += em[av.gate] * pfv
    Aub = np.zeros((n, m + 1))
    Aub[:, :m] = C
    Aub[:, m] = -inst.cap
    bub = np.zeros(n)
    Aeq = np.zeros((inst.Aeq.shape[0], m + 1))
    Aeq[:, :m] = inst.Aeq
    c = np.zeros(m + 1)
    c[m] = 1.0
    bounds = [(0.0, None)] * m + [(0.0, None)]
    res = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=inst.beq, bounds=bounds, method="highs")
    if not res.success:
        return None, float("inf"), str(res.message)
    return res.x[:m], float(res.x[m]), str(res.message)


def solve_cage_from_x(inst: CAGEInstance, x_start: np.ndarray, rounds=8):
    alpha0, _eta0, _msg0 = solve_alpha(inst, x_start)
    alpha = inst.alpha0.copy() if alpha0 is None else alpha0
    x = x_start.copy()
    best = None
    history = []
    for _ in range(rounds):
        t_x, x, ok_x, msg_x = solve_x(inst, alpha, x0=x)
        alpha2, eta, msg_a = solve_alpha(inst, x)
        if alpha2 is None:
            history.append((t_x, eta, ok_x, msg_x, msg_a))
            break
        alpha = alpha2
        t_after, x, ok_after, msg_after = solve_x(inst, alpha, x0=x)
        history.append((t_x, eta, ok_after, msg_after, msg_a))
        cur = (t_after, eta, x.copy(), alpha.copy(), history[-1])
        if best is None or max(t_after, eta) < max(best[0], best[1]):
            best = cur
        if t_after <= 1.0000005 and eta <= 1.0000005:
            break
    if best is None:
        return {"ratio": float("inf"), "eta": float("inf"), "history": history, "gap": float("inf")}
    ratio, eta, x_best, alpha_best, _last = best
    A, B = aggregate(inst, alpha_best)
    raw = budget(A, B, x_best)
    return {
        "ratio": ratio,
        "eta": eta,
        "gap": float(np.max(raw - inst.cap)),
        "maxv": int(np.argmax(raw - inst.cap)),
        "history": history,
        "vars": len(inst.vars),
        "gates": len(inst.gates),
        "eqs": int(inst.Aeq.shape[0]),
        "x": x_best,
        "alpha": alpha_best,
    }


def solve_cage(inst: CAGEInstance, rounds=8, restarts=1):
    rng = np.random.default_rng(4127)
    starts = [np.zeros(len(inst.gates))]
    scales = [0.5, 1.0, 2.0, 3.0]
    for k in range(max(0, restarts - 1)):
        starts.append(rng.normal(0.0, scales[k % len(scales)], len(inst.gates)))
    best = None
    for x0 in starts:
        row = solve_cage_from_x(inst, x0, rounds=rounds)
        row["restarts"] = len(starts)
        if best is None or row["gap"] < best["gap"]:
            best = row
        if row["gap"] <= -1e-7:
            # A negative gap is already enough for a floating scout survivor.
            break
    return best


def run_info(label: str, info, rounds: int, restarts: int):
    inst = build_instance(info, label)
    if inst is None:
        return None
    row = solve_cage(inst, rounds=rounds, restarts=restarts)
    row["label"] = label
    row["n"] = inst.n
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--restarts", type=int, default=1)
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--nmin", type=int, default=8)
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--stride", type=int, default=1)
    args = ap.parse_args()

    print("=== CAGE adaptive gate scout ===")
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
        row = run_info(f"{g6}[{blow}]", info, args.rounds, args.restarts)
        if row:
            print(
                f"{row['label']:17} N={row['n']:3d} gates={row['gates']:4d} vars={row['vars']:5d} "
                f"eqs={row['eqs']:4d} ratio={row['ratio']:.9f} eta={row['eta']:.9f} "
                f"gap={row['gap']:+.3e} maxv={row['maxv']}",
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
                row = run_info(g6, info, max(3, args.rounds // 2), args.restarts)
                if not row:
                    continue
                count += 1
                if row["gap"] > 1e-5:
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
