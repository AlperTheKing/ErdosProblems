"""EXACT decision of "a(N) >= T ?" with the COMPLETE cut system loaded up front.

For N <= 18 the number of bipartitions is 2^(N-1) <= 131072, so every constraint
    for each cut (A,B):  sum_{uv inside A} x_uv + sum_{uv inside B} x_uv >= T
can be posted directly, with no counterexample-guided loop. That makes the answer a single
CP-SAT call whose UNSAT verdict is a complete infeasibility proof over ALL triangle-free graphs
on N vertices -- i.e. an exact determination of whether a(N) >= T.

Symmetry breaking used (sound: every graph has a labelling satisfying it):
  * degree of vertex 0 is maximum,
  * the adjacency rows are lexicographically non-increasing is NOT imposed (it is not sound
    together with the above in general); instead we impose only the degree ordering
    deg(1) >= deg(2) >= ... >= deg(N-1), which any graph can be relabelled to satisfy while
    keeping vertex 0 of maximum degree.

Usage: python claude_decide_full.py N T [--workers W] [--maxedges M]
"""

import sys
import argparse
from itertools import combinations
from ortools.sat.python import cp_model


def maxcut_exact(n, adj):
    deg = [bin(a).count("1") for a in adj]
    S, cut = 1, deg[0]
    best = cut
    for k in range(1, 1 << (n - 1)):
        v = (k & -k).bit_length()
        a = bin(adj[v] & S).count("1")
        if S >> v & 1:
            cut += 2 * a - deg[v]; S &= ~(1 << v)
        else:
            cut += deg[v] - 2 * a; S |= 1 << v
        if cut > best:
            best = cut
    return best


def encode_g6(n, adj):
    out = chr(n + 63)
    cur = nb = 0
    for j in range(1, n):
        for i in range(j):
            cur = (cur << 1) | ((adj[i] >> j) & 1)
            nb += 1
            if nb == 6:
                out += chr(cur + 63); cur = nb = 0
    if nb:
        out += chr((cur << (6 - nb)) + 63)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("t", type=int)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--maxtime", type=float, default=0.0)
    args = ap.parse_args()
    n, T = args.n, args.t
    if n > 20:
        print("refusing: 2^(n-1) constraints would be excessive for n > 20")
        return 2

    pairs = list(combinations(range(n), 2))
    idx = {p: i for i, p in enumerate(pairs)}
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(len(pairs))]

    for a, b, c in combinations(range(n), 3):
        model.AddBoolOr([x[idx[(a, b)]].Not(), x[idx[(a, c)]].Not(), x[idx[(b, c)]].Not()])

    # degrees, for symmetry breaking
    degv = []
    for v in range(n):
        terms = [x[idx[(min(v, u), max(v, u))]] for u in range(n) if u != v]
        d = model.NewIntVar(0, n - 1, f"d{v}")
        model.Add(d == sum(terms))
        degv.append(d)
    for v in range(1, n):
        model.Add(degv[0] >= degv[v])          # vertex 0 has maximum degree
    for v in range(1, n - 1):
        model.Add(degv[v] >= degv[v + 1])      # remaining degrees non-increasing

    # ALL cut constraints: vertex 0 fixed on one side
    ncuts = 1 << (n - 1)
    for k in range(ncuts):
        mask = (k << 1) | 1
        terms = [x[idx[(u, v)]] for (u, v) in pairs
                 if ((mask >> u) & 1) == ((mask >> v) & 1)]
        model.Add(sum(terms) >= T)

    print(f"model: {len(pairs)} edge vars, {ncuts} cut constraints, "
          f"{len(list(combinations(range(n), 3)))} triangle clauses", flush=True)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = args.workers
    if args.maxtime > 0:
        solver.parameters.max_time_in_seconds = args.maxtime
    status = solver.Solve(model)

    if status == cp_model.INFEASIBLE:
        print(f"RESULT n={n} t={T}: UNSAT  =>  a({n}) < {T}   [complete, exact]")
        print(f"       wall {solver.WallTime():.1f}s")
        return 0
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        adj = [0] * n
        m = 0
        for (u, v) in pairs:
            if solver.Value(x[idx[(u, v)]]):
                adj[u] |= 1 << v; adj[v] |= 1 << u; m += 1
        mc = maxcut_exact(n, adj)
        bip = m - mc
        ok = bip >= T
        print(f"RESULT n={n} t={T}: SAT  =>  a({n}) >= {T}   [verified: |E|={m}, maxcut={mc}, bip={bip}]")
        print(f"       independent check passes: {ok}")
        print(f"       25*bip={25*bip} vs N^2={n*n}  -> "
              f"{'*** VIOLATES THE CONJECTURE ***' if 25*bip > n*n else 'consistent'}")
        print(f"       g6={encode_g6(n, adj)}")
        print(f"       wall {solver.WallTime():.1f}s")
        return 0
    print(f"RESULT n={n} t={T}: {solver.StatusName(status)} after {solver.WallTime():.1f}s")
    return 3


if __name__ == "__main__":
    sys.exit(main())
