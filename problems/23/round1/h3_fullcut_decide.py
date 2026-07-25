"""COMPLETE exact decision of "a(N) >= T?" for Erdos #23, with ALL 2^(N-1) cut constraints.

a(N) = max { bip(G) : G triangle-free on N vertices },  bip(G) = |E| - maxcut(G).

bip(G) >= T  <=>  every bipartition (A, V\\A) leaves at least T monochromatic edges.
There are exactly 2^(N-1) bipartitions up to complementation, and for N <= 18 all of them are
posted as linear constraints at once, so the model is EXACT and complete -- no lazy loop, no
counterexample-guided refinement, hence UNSAT is a full proof that a(N) < T.

Variables: x_{uv} in {0,1} for each of the C(N,2) pairs.
Constraints:
  (1) triangle-freeness: x_uv + x_uw + x_vw <= 2 for every triple;
  (2) for every mask m in [0, 2^(N-1)): sum over pairs monochromatic under m of x >= T;
  (3) symmetry breaking: deg(0) >= deg(1) >= ... >= deg(N-1)   (sound: relabel by degree).

SAT  -> explicit graph, re-verified here by exhaustive Gray-code maxcut and explicit triangle test.
UNSAT -> a(N) < T, exact.

Usage: python h3_fullcut_decide.py N T [--workers W] [--maxtime S]
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
            cut += 2 * a - deg[v]
            S &= ~(1 << v)
        else:
            cut += deg[v] - 2 * a
            S |= 1 << v
        if cut > best:
            best = cut
    return best


def g6(n, adj):
    out = chr(n + 63)
    cur = nb = 0
    for j in range(1, n):
        for i in range(j):
            cur = (cur << 1) | ((adj[i] >> j) & 1)
            nb += 1
            if nb == 6:
                out += chr(cur + 63)
                cur = nb = 0
    if nb:
        out += chr((cur << (6 - nb)) + 63)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("t", type=int)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--maxtime", type=float, default=0.0)
    ap.add_argument("--nosym", action="store_true")
    args = ap.parse_args()
    n, T = args.n, args.t
    if n > 20:
        print("refusing: 2^(n-1) constraints is too many for n > 20")
        return 2

    pairs = list(combinations(range(n), 2))
    idx = {p: i for i, p in enumerate(pairs)}
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(len(pairs))]

    for a, b, c in combinations(range(n), 3):
        model.AddBoolOr([x[idx[(a, b)]].Not(), x[idx[(a, c)]].Not(), x[idx[(b, c)]].Not()])

    # all 2^(n-1) cut constraints
    for m in range(1 << (n - 1)):
        terms = [x[idx[(u, v)]] for (u, v) in pairs if ((m >> u) & 1) == ((m >> v) & 1)]
        model.Add(sum(terms) >= T)

    if not args.nosym:
        degs = []
        for v in range(n):
            d = model.NewIntVar(0, n - 1, f"d{v}")
            model.Add(d == sum(x[idx[(min(u, v), max(u, v))]] for u in range(n) if u != v))
            degs.append(d)
        for v in range(n - 1):
            model.Add(degs[v] >= degs[v + 1])

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = args.workers
    if args.maxtime > 0:
        solver.parameters.max_time_in_seconds = args.maxtime
    solver.parameters.log_search_progress = False
    status = solver.Solve(model)

    if status == cp_model.INFEASIBLE:
        print(f"RESULT n={n} t={T}: UNSAT  => a({n}) < {T}   (complete, all {1 << (n-1)} cuts posted)")
        print(f"       wall={solver.WallTime():.1f}s")
        return 0
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        adj = [0] * n
        m = 0
        for (u, v) in pairs:
            if solver.Value(x[idx[(u, v)]]):
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                m += 1
        tf = all(not (adj[u] & adj[v]) for (u, v) in pairs if (adj[u] >> v) & 1)
        mc = maxcut_exact(n, adj)
        bip = m - mc
        print(f"RESULT n={n} t={T}: SAT")
        print(f"       |E|={m} maxcut={mc} bip={bip} trianglefree={tf}")
        print(f"       25*bip={25*bip} vs N^2={n*n} -> "
              f"{'*** VIOLATES THE CONJECTURE ***' if 25*bip > n*n else 'consistent'}")
        print(f"       g6={g6(n, adj)}")
        print(f"       wall={solver.WallTime():.1f}s")
        return 0
    print(f"RESULT n={n} t={T}: {solver.StatusName(status)} (wall={solver.WallTime():.1f}s) -- undecided")
    return 3


if __name__ == "__main__":
    sys.exit(main())
