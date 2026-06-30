"""Audit GPT-Pro's two-lane counterexample to the no-bracket P198 route.

The graph has path vertices x_0..x_8 and two off-path lanes a_i,b_i.
The displayed parity cut is triangle-free, B-connected, and CP-SAT verifies
it is a global maximum cut.  For f=(x_0,x_8), the P-contained position-flow
has demand 19 and one component of capacity 18, with no bracket hub.

This script also computes exact ROWSUM rows for the displayed cut and tries to
enumerate optimal cuts to see whether the displayed cut is Gamma-minimal.
"""

from __future__ import annotations

import argparse
from fractions import Fraction as F

import numpy as np
from ortools.sat.python import cp_model

from _codex_net_globalmax_probe import contained_flow_failures
from _codex_pcontained_deficit_tail_gate import best_atom_tail, has_bracket
from _h import Bconn, bdist_restr
from _gram_spectral import build_O
from _M_full_detour_counterexample import maxcut
from _M_tailswitch_gate import boundary_gain, cutsize, tri_free
from _rowsum_verify import exact_O_rowsums
from _satzmu_conn import struct_for_side
from _tail_positive_extra_counterexample import adj_from_edges


def make_graph(length: int = 8):
    if length < 8:
        raise ValueError("length must be at least 8 for the triangle-free two-lane witness")
    L = length
    edges = []
    # path x_i = i
    for i in range(L):
        edges.append((i, i + 1))

    # a_i = (L+1)+i, b_i = 2(L+1)+i
    a0 = L + 1
    b0 = 2 * (L + 1)
    for i in range(L + 1):
        ai = a0 + i
        bi = b0 + i
        edges.append((i, ai))
        edges.append((i, bi))

    # K_{2,2} lane slabs between consecutive layers.
    for i in range(L):
        left = [a0 + i, b0 + i]
        right = [a0 + i + 1, b0 + i + 1]
        for u in left:
            for v in right:
                edges.append((u, v))

    # bad edges in the displayed parity cut
    edges.extend([(0, L), (0, L - 2), (2, L - 2), (2, L)])

    n = 3 * (L + 1)
    edges = sorted({(min(a, b), max(a, b)) for a, b in edges})
    side = [0] * n
    for i in range(L + 1):
        side[i] = i % 2
        side[a0 + i] = 1 - side[i]
        side[b0 + i] = 1 - side[i]
    return n, edges, side


def gamma_and_info(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    gamma = sum(ell[f] * ell[f] for f in M)
    return M, ell, T, mu, cyc, gamma


def rowsums_for_side(n, adj, side):
    rec = gamma_and_info(n, adj, side)
    if rec is None:
        return []
    M, ell, _T, _mu, cyc, gamma = rec
    info = {"n": n, "M": M, "cyc": cyc, "G": gamma}
    rows, _G, _N = exact_O_rowsums(info)
    return list(zip(M, rows))


def cp_enumerate_optimal(n, edges, base_side, optimum, max_seconds):
    adj = adj_from_edges(n, edges)
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(n)]
    cut_terms = []
    for a, b in edges:
        z = model.NewBoolVar(f"e{a}_{b}")
        model.AddBoolXOr([x[a], x[b], z.Not()])
        cut_terms.append(z)
    model.Add(sum(cut_terms) == optimum)
    model.Add(x[0] == base_side[0])

    class Callback(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            super().__init__()
            self.count = 0
            self.bconn = 0
            self.gamma_hist = {}
            self.best = None
            self.best_rowsum = None

        def OnSolutionCallback(self):
            side = [self.Value(v) for v in x]
            self.count += 1
            if not Bconn(n, adj, side):
                return
            rec = gamma_and_info(n, adj, side)
            if rec is None:
                return
            M, ell, _T, _mu, cyc, gamma = rec
            self.bconn += 1
            self.gamma_hist[gamma] = self.gamma_hist.get(gamma, 0) + 1
            mx = max((r for _f, r in rowsums_for_side(n, adj, side)), default=F(0))
            payload = (gamma, mx, M, "".join(map(str, side)))
            if self.best is None or gamma < self.best[0]:
                self.best = payload
            if self.best_rowsum is None or mx > self.best_rowsum[0]:
                self.best_rowsum = (mx, gamma, M, "".join(map(str, side)))

    cb = Callback()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_seconds
    solver.parameters.num_search_workers = 1  # required for solution enumeration
    status = solver.SearchForAllSolutions(model, cb)
    return status, cb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--length", type=int, default=8)
    ap.add_argument("--enum-seconds", type=float, default=180.0)
    args = ap.parse_args()

    n, edges, side = make_graph(args.length)
    adj = adj_from_edges(n, edges)
    status, optimum, bound = maxcut(n, edges)
    base_cut = cutsize(n, adj, side)
    rec = gamma_and_info(n, adj, side)

    print(f"n={n} edges={len(edges)} triangle_free={tri_free(n, adj)}")
    print(f"base_cut={base_cut} maxcut={optimum} bound={bound} status={status}")
    print(f"base_Bconn={Bconn(n, adj, side)}")
    if rec is not None:
        M, ell, _T, _mu, cyc, gamma = rec
        print(f"base_bad_edges={M}")
        print(f"base_lengths={ell}")
        print(f"base_Gamma={gamma}")
        rows = rowsums_for_side(n, adj, side)
        print(f"base_rowsums={[(f, str(r), float(r)) for f, r in rows]}")
        print(f"base_max_rowsum={max(r for _f, r in rows)} N={n}")
        info = {"n": n, "M": M, "cyc": cyc, "ell": ell}
        O, lvec, _P = build_O(info)
        rho = float(np.linalg.eigvalsh(O)[-1])
        ray = float((lvec @ (O @ lvec)) / (lvec @ lvec))
        print(f"base_rho={rho:.12g} rho_over_N={rho/n:.12g}")
        print(f"base_ell_rayleigh={ray:.12g} rayleigh_over_N={ray/n:.12g}")
        print(f"base_Oell={list(O @ lvec)}")
        print(f"base_Nell={list(n * lvec)}")

        failures = contained_flow_failures(n, adj, side)
        print(f"flow_failures={len(failures)}")
        for fail in failures:
            f, path, chords, spans, total, flow = fail
            intervals = []
            for lo, hi, g in chords:
                intervals.append((lo, hi, g))
            best, arg = best_atom_tail(n, adj, side, path, intervals)
            print(f"  f={f} path={path}")
            print(f"  chords={chords}")
            print(f"  spans={spans} demand={total} flow={flow}")
            print(f"  bracket={has_bracket(intervals)} best_tail_gain={best} arg={arg}")

    enum_status, cb = cp_enumerate_optimal(n, edges, side, optimum, args.enum_seconds)
    print(f"enum_status={enum_status} enum_total={cb.count} enum_Bconn={cb.bconn}")
    print(f"enum_gamma_hist={sorted(cb.gamma_hist.items())[:20]}")
    print(f"enum_best_gamma={cb.best}")
    print(f"enum_best_rowsum={cb.best_rowsum}")


if __name__ == "__main__":
    main()
