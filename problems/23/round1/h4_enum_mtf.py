"""H4 method 2: ENUMERATE every maximal triangle-free (MTF) graph on N vertices with
CP-SAT, then evaluate bip exactly on each.  This settles a(N) completely and
independently of the cut-constraint model of h4_decide.py.

Soundness.  bip is monotone under triangle-free edge addition (lemma L1, verified in
h4_lemmas.py), so a(N) = max { bip(G) : G MAXIMAL triangle-free on N vertices }.
MTF graphs are extremely rare: 10, 16, 31, 61, 147, 392 for N = 8..13 (verified here
against the complete geng census), so full enumeration is cheap where the census is not.

The model is: triangle-free  +  every non-adjacent pair has a common neighbour
             +  adjacent-transposition lexicographic symmetry breaking.
Symmetry breaking only removes isomorphic duplicates, so at least one representative
of every isomorphism class survives; duplicates that survive are harmless.

Output: one graph6 string per line on stdout (pipe into h4_maxtf.exe).

Usage:  python h4_enum_mtf.py N [--workers W] [--out FILE] [--mindeg D] [--minedges M]
"""

import sys
import time
import argparse
from itertools import combinations

from ortools.sat.python import cp_model

from h4_lib import g6_encode
from h4_sym import add_sym1, add_sym2


class Collector(cp_model.CpSolverSolutionCallback):
    def __init__(self, x, idx, pairs, n, fh):
        super().__init__()
        self.x, self.idx, self.pairs, self.n, self.fh = x, idx, pairs, n, fh
        self.count = 0
        self.t0 = time.time()

    def on_solution_callback(self):
        n = self.n
        adj = [0] * n
        for (u, v) in self.pairs:
            if self.Value(self.x[self.idx[(u, v)]]):
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        self.fh.write(g6_encode(n, adj) + "\n")
        self.count += 1
        if self.count % 20000 == 0:
            print(f"  ... {self.count} solutions, {time.time()-self.t0:.0f}s",
                  file=sys.stderr, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", type=str, default="-")
    ap.add_argument("--mindeg", type=int, default=None)
    ap.add_argument("--minedges", type=int, default=None)
    ap.add_argument("--nosym", action="store_true")
    ap.add_argument("--sym2", action="store_true")
    args = ap.parse_args()
    n = args.n

    pairs = list(combinations(range(n), 2))
    idx = {p: i for i, p in enumerate(pairs)}
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(len(pairs))]

    for a, b, c in combinations(range(n), 3):
        model.AddBoolOr([x[idx[(a, b)]].Not(), x[idx[(a, c)]].Not(), x[idx[(b, c)]].Not()])

    for (u, v) in pairs:
        ys = []
        for w in range(n):
            if w == u or w == v:
                continue
            a1 = x[idx[(min(u, w), max(u, w))]]
            a2 = x[idx[(min(v, w), max(v, w))]]
            y = model.NewBoolVar("")
            # full equivalence y <=> a1 AND a2, so that every auxiliary variable is
            # FUNCTIONALLY DETERMINED by the edge variables.  Without the reverse
            # implication `enumerate_all_solutions` would enumerate 2^#aux copies of
            # every graph.
            model.AddImplication(y, a1)
            model.AddImplication(y, a2)
            model.AddBoolOr([y, a1.Not(), a2.Not()])
            ys.append(y)
        model.AddBoolOr([x[idx[(u, v)]]] + ys)

    if args.minedges is not None:
        model.Add(sum(x) >= args.minedges)
    if args.mindeg is not None:
        for v in range(n):
            model.Add(sum(x[idx[(min(v, u), max(v, u))]] for u in range(n) if u != v)
                      >= args.mindeg)

    if not args.nosym:
        add_sym1(model, x, idx, n)
        if args.sym2:
            add_sym2(model, x, idx, n)

    fh = sys.stdout if args.out == "-" else open(args.out, "w")
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    solver.parameters.num_search_workers = args.workers
    cb = Collector(x, idx, pairs, n, fh)
    t0 = time.time()
    status = solver.Solve(model, cb)
    if fh is not sys.stdout:
        fh.close()
    print(f"[enum] n={n} status={solver.StatusName(status)} solutions={cb.count} "
          f"time={time.time()-t0:.1f}s", file=sys.stderr, flush=True)
    return 0 if status in (cp_model.OPTIMAL, cp_model.FEASIBLE, cp_model.INFEASIBLE) else 3


if __name__ == "__main__":
    sys.exit(main())
