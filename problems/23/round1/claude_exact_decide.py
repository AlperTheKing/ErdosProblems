"""EXACT decision of a(N) = max bip over triangle-free graphs on N vertices, by CP-SAT + CEGAR.

Model: binary x_uv for every pair (the edge set), triangle-freeness as 3-clause constraints.
bip(G) >= t means EVERY bipartition leaves at least t monochromatic edges, i.e.

    for every cut (A,B):   sum_{uv inside A} x_uv + sum_{uv inside B} x_uv  >=  t.

There are 2^(N-1) such constraints; we add them LAZILY (counterexample-guided): solve with the
current pool, take the returned graph, compute its exact maximum cut by full enumeration, and if
that cut leaves fewer than t monochromatic edges, add exactly that cut as a new constraint and
re-solve.  The loop terminates with either
    SAT  -> an explicit triangle-free graph with bip >= t (verified exactly), or
    UNSAT -> a proof that a(N) < t,
both exact: no floating point anywhere on the acceptance path.

Usage:  python claude_exact_decide.py N T [--workers W] [--maxrounds R]
"""

import sys
import argparse
from itertools import combinations

from ortools.sat.python import cp_model


def maxcut_exact(n, adj):
    """Exhaustive maximum cut; returns (value, best_cut_mask). Vertex 0 fixed in S."""
    deg = [bin(a).count("1") for a in adj]
    S, cut = 1, deg[0]
    best, best_S = cut, S
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
            best, best_S = cut, S
    return best, best_S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("t", type=int)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--maxrounds", type=int, default=100000)
    ap.add_argument("--seedcuts", type=int, default=400)
    args = ap.parse_args()
    n, T = args.n, args.t

    pairs = list(combinations(range(n), 2))
    idx = {p: i for i, p in enumerate(pairs)}

    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(len(pairs))]

    # triangle-freeness
    for a, b, c in combinations(range(n), 3):
        model.AddBoolOr([x[idx[(a, b)]].Not(), x[idx[(a, c)]].Not(), x[idx[(b, c)]].Not()])

    def cut_terms(mask):
        """indices of pairs monochromatic under the cut given by bitmask `mask`"""
        return [idx[(u, v)] for (u, v) in pairs
                if ((mask >> u) & 1) == ((mask >> v) & 1)]

    # seed with a spread of random-ish cuts so the first solve is not trivial
    import random
    rnd = random.Random(12345)
    seeded = set()
    for _ in range(args.seedcuts):
        m = rnd.getrandbits(n) | 1
        if m in seeded:
            continue
        seeded.add(m)
        model.Add(sum(x[i] for i in cut_terms(m)) >= T)
    # balanced cuts matter most; add all "first k vertices" style cuts too
    for k in range(1, n):
        m = (1 << k) - 1
        if m not in seeded:
            seeded.add(m)
            model.Add(sum(x[i] for i in cut_terms(m)) >= T)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = args.workers
    solver.parameters.log_search_progress = False

    rounds = 0
    while rounds < args.maxrounds:
        rounds += 1
        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print(f"RESULT n={n} t={T}: UNSAT after {rounds} rounds, {len(seeded)} cut constraints")
            print(f"       => a({n}) < {T}   (exact, complete infeasibility proof)")
            return 0
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            print(f"RESULT n={n} t={T}: solver status {solver.StatusName(status)} after {rounds} rounds")
            return 3

        adj = [0] * n
        m = 0
        for (u, v) in pairs:
            if solver.Value(x[idx[(u, v)]]):
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                m += 1
        mc, cutmask = maxcut_exact(n, adj)
        bip = m - mc
        if bip >= T:
            # verified exactly
            g6 = encode_g6(n, adj)
            print(f"RESULT n={n} t={T}: SAT after {rounds} rounds")
            print(f"       graph with |E|={m} maxcut={mc} bip={bip} >= {T}")
            print(f"       25*bip={25*bip} vs N^2={n*n}  -> "
                  f"{'*** VIOLATES THE CONJECTURE ***' if 25*bip > n*n else 'consistent'}")
            print(f"       g6={g6}")
            return 0
        # add the violated cut
        if cutmask in seeded:
            # numerically impossible, but guard against loops
            print("ERROR: repeated cut; aborting")
            return 4
        seeded.add(cutmask)
        model.Add(sum(x[i] for i in cut_terms(cutmask)) >= T)
        if rounds % 25 == 0:
            print(f"  round {rounds}: best bip so far {bip}, cuts {len(seeded)}", flush=True)

    print(f"RESULT n={n} t={T}: round limit reached ({rounds})")
    return 5


def encode_g6(n, adj):
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


if __name__ == "__main__":
    sys.exit(main())
