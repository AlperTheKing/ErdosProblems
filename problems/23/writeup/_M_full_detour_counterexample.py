"""Counterexample to the bare lemma (M).

Lemma (M), as stated without a minimality/reducedness hypothesis, says a
global maximum connected-B cut cannot have P-contained bad chords with
interior-overlapping intervals.  This synthetic graph shows that is false.

It starts from the N=26 nested path/detour layout and adds one extra long
all-cut detour between the endpoints of f=(0,12).  The parity cut is a global
maximum cut, B is connected, f has a unique shortest B-geodesic P=[0..12], and
the P-contained bad chords (0,8) and (2,6) interior-overlap on P.

Enumerating all optimal cuts with x_0 fixed finds 801 cuts.  The parity cut is
the unique minimum-Gamma optimal cut in that enumeration.
"""

from ortools.sat.python import cp_model

from _M_tailswitch_gate import build_pd, cutsize, tri_free
from _overlap_switch_probe import contained_intervals, interior_pair
from _satzmu_conn import struct_for_side
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _h import Bconn


def make_graph():
    n, edges = build_pd(12, [(0, 8), (2, 6)])
    side = [v % 2 for v in range(n)]
    n, edges, side = add_cut_path(n, list(edges), side, 0, 12, 14)
    return n, sorted(set(edges)), side


def maxcut(n, edges):
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(n)]
    terms = []
    for a, b in edges:
        z = model.NewBoolVar(f"e{a}_{b}")
        model.AddBoolXOr([x[a], x[b], z.Not()])
        terms.append(z)
    model.Maximize(sum(terms))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 8
    solver.parameters.max_time_in_seconds = 30
    status = solver.Solve(model)
    return status, int(solver.ObjectiveValue()), solver.BestObjectiveBound()


def structure_record(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, _T, _mu, cyc = st
    gamma = sum(ell[f] * ell[f] for f in M)
    overlap = None
    for f in M:
        if len(cyc[f]) != 1:
            continue
        path = cyc[f][0]
        pair = interior_pair(contained_intervals(M, cyc, f, path))
        if pair is not None:
            overlap = (f, path, pair)
            break
    return M, ell, gamma, overlap


def enumerate_optimal(n, edges, base_side, optimum, adj):
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(n)]
    terms = []
    for a, b in edges:
        z = model.NewBoolVar(f"e{a}_{b}")
        model.AddBoolXOr([x[a], x[b], z.Not()])
        terms.append(z)
    model.Add(sum(terms) == optimum)
    model.Add(x[0] == base_side[0])

    class Callback(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            super().__init__()
            self.count = 0
            self.gamma_hist = {}
            self.best = None
            self.best_overlap = None

        def OnSolutionCallback(self):
            side = [self.Value(v) for v in x]
            self.count += 1
            rec = structure_record(n, adj, side)
            if rec is None:
                return
            M, ell, gamma, overlap = rec
            self.gamma_hist[gamma] = self.gamma_hist.get(gamma, 0) + 1
            payload = (gamma, M, ell, overlap, "".join(map(str, side[:13])))
            if self.best is None or gamma < self.best[0]:
                self.best = payload
            if overlap is not None and (
                self.best_overlap is None or gamma < self.best_overlap[0]
            ):
                self.best_overlap = payload

    cb = Callback()
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = 60
    solver.SearchForAllSolutions(model, cb)
    return cb


def main():
    n, edges, side = make_graph()
    adj = adj_from_edges(n, edges)
    status, optimum, bound = maxcut(n, edges)
    base_cut = cutsize(n, adj, side)
    base_record = structure_record(n, adj, side)
    cb = enumerate_optimal(n, edges, side, optimum, adj)

    print(f"n={n} edges={len(edges)} triangle_free={tri_free(n, adj)}")
    print(f"base_cut={base_cut} maxcut={optimum} status={status} bound={bound}")
    print(f"base_Bconn={Bconn(n, adj, side)}")
    print(f"base_record={base_record}")
    print(f"optimal_cuts_x0_fixed={cb.count}")
    print(f"gamma_hist={sorted(cb.gamma_hist.items())}")
    print(f"best_gamma={cb.best}")
    print(f"best_overlap_gamma={cb.best_overlap}")


if __name__ == "__main__":
    main()
