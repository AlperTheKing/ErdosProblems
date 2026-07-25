"""H4: EXACT decision of  a(N) >= T ?   for triangle-free graphs on N vertices.

a(N) = max { bip(G) : G triangle-free on N vertices },  bip(G) = |E(G)| - maxcut(G).

MODEL.  One boolean x_uv per vertex pair.  Constraints:

  (T)  triangle-freeness:  ~x_ab v ~x_ac v ~x_bc  for every triple.
  (C)  bip >= T  <=>  EVERY bipartition leaves >= T monochromatic edges.
       With `--cuts full` ALL 2^(N-1) cut constraints are posted explicitly, so the
       model is an exact, complete, finite encoding of the decision problem --
       no counterexample-guided loop, no incompleteness risk.
       With `--cuts lazy` they are added CEGAR-style in batches.
  (M)  maximality (optional, SOUND by lemma L1 in h4_lemmas.py: bip is monotone
       under triangle-free edge addition, so a(N) is attained at a MAXIMAL
       triangle-free graph).  Every non-adjacent pair gets a common neighbour.
  (D)  degree window (optional, SOUND by lemma L2: bip(G) <= a(N-1) + floor(d(v)/2)
       for every v, hence d(v) >= 2*(T - a(N-1)) ).
  (E)  edge-count window.
  (S)  partial symmetry breaking: adjacent-transposition lexicographic row order
       (Codish-Miller-Prosser-Stuckey), encoded exactly as a linear inequality
       between the binary numbers formed by rows i and i+1 with columns i,i+1 removed.

Every SAT answer is re-verified from scratch (triangle-freeness + exhaustive 2^(N-1)
maxcut) before it is reported.  UNSAT answers under `--cuts full` are complete.

Usage:
  python h4_decide.py N T [--cuts full|lazy] [--maximal] [--mindeg D] [--maxdeg D]
                          [--minedges M] [--maxedges M] [--sym] [--workers W]
                          [--timeout SECONDS] [--log]
"""

import sys
import time
import argparse
from itertools import combinations

from ortools.sat.python import cp_model

from h4_lib import (g6_encode, maxcut_exact, num_edges, is_triangle_free,
                    is_maximal_triangle_free, is_bipartite)
from h4_sym import add_sym1, add_sym2


def build(args):
    n, T = args.n, args.t
    pairs = list(combinations(range(n), 2))
    idx = {p: i for i, p in enumerate(pairs)}
    P = len(pairs)

    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(P)]

    # (T) triangle-freeness
    ntri = 0
    for a, b, c in combinations(range(n), 3):
        model.AddBoolOr([x[idx[(a, b)]].Not(), x[idx[(a, c)]].Not(), x[idx[(b, c)]].Not()])
        ntri += 1

    # total edge count variable (used to express cuts on the short side)
    M = model.NewIntVar(0, P, "M")
    model.Add(M == sum(x))

    # (E) edge window
    lo = args.minedges if args.minedges is not None else T
    hi = args.maxedges if args.maxedges is not None else (n * n) // 4
    model.Add(M >= lo)
    model.Add(M <= hi)

    # (D) degree window
    deg = []
    for v in range(n):
        dv = model.NewIntVar(0, n - 1, f"d{v}")
        model.Add(dv == sum(x[idx[(min(v, u), max(v, u))]] for u in range(n) if u != v))
        deg.append(dv)
        if args.mindeg is not None:
            model.Add(dv >= args.mindeg)
        if args.maxdeg is not None:
            model.Add(dv <= args.maxdeg)

    # (M) maximality: every non-adjacent pair has a common neighbour
    naux = 0
    if args.maximal:
        for (u, v) in pairs:
            ys = []
            for w in range(n):
                if w == u or w == v:
                    continue
                y = model.NewBoolVar("")
                naux += 1
                a1 = x[idx[(min(u, w), max(u, w))]]
                a2 = x[idx[(min(v, w), max(v, w))]]
                model.AddImplication(y, a1)
                model.AddImplication(y, a2)
                ys.append(y)
            model.AddBoolOr([x[idx[(u, v)]]] + ys)

    # (S) symmetry breaking: row_i >=_lex row_{i+1} on columns != i,i+1
    if args.sym:
        add_sym1(model, x, idx, n)
        if args.sym2:
            add_sym2(model, x, idx, n)

    return model, x, M, deg, pairs, idx, ntri, naux


def cut_constraint_terms(n, mask, pairs, idx):
    """Return ('mono', list_of_pair_indices) or ('cut', list_of_pair_indices)
    whichever is the shorter description of the constraint
        #mono(mask) >= T   <=>   #cut(mask) <= M - T .
    """
    mono, cut = [], []
    for k, (u, v) in enumerate(pairs):
        if ((mask >> u) & 1) == ((mask >> v) & 1):
            mono.append(k)
        else:
            cut.append(k)
    if len(mono) <= len(cut) + 1:
        return "mono", mono
    return "cut", cut


def post_cut(model, x, M, T, kind, lst):
    if kind == "mono":
        model.Add(sum(x[i] for i in lst) >= T)
    else:
        model.Add(sum(x[i] for i in lst) <= M - T)


def extract(solver, x, n, pairs, idx):
    adj = [0] * n
    for (u, v) in pairs:
        if solver.Value(x[idx[(u, v)]]):
            adj[u] |= 1 << v
            adj[v] |= 1 << u
    return adj


def report_graph(n, adj, T, tag):
    m = num_edges(n, adj)
    mc, mask = maxcut_exact(n, adj)
    b = m - mc
    tf = is_triangle_free(n, adj)
    print(f"  [{tag}] |E|={m} maxcut={mc} bip={b} trianglefree={tf} "
          f"maximal={is_maximal_triangle_free(n, adj)} bipartite={is_bipartite(n, adj)}")
    print(f"  [{tag}] g6={g6_encode(n, adj)}")
    print(f"  [{tag}] 25*bip={25*b}  N^2={n*n}  "
          f"{'*** VIOLATION ***' if 25 * b > n * n else 'consistent'}")
    return b, tf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("t", type=int)
    ap.add_argument("--cuts", choices=["full", "lazy"], default="full")
    ap.add_argument("--maximal", action="store_true")
    ap.add_argument("--sym", action="store_true")
    ap.add_argument("--sym2", action="store_true")
    ap.add_argument("--mindeg", type=int, default=None)
    ap.add_argument("--maxdeg", type=int, default=None)
    ap.add_argument("--minedges", type=int, default=None)
    ap.add_argument("--maxedges", type=int, default=None)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--timeout", type=float, default=0.0)
    ap.add_argument("--batch", type=int, default=64, help="lazy mode: cuts added per round")
    ap.add_argument("--maxrounds", type=int, default=1000000)
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--enumerate", type=str, default=None,
                    help="dump EVERY solution of the full-cut model to this file")
    args = ap.parse_args()
    n, T = args.n, args.t

    t0 = time.time()
    model, x, M, deg, pairs, idx, ntri, naux = build(args)

    ncuts = 0
    if args.cuts == "full":
        nterms = 0
        for mask in range(1 << (n - 1)):
            kind, lst = cut_constraint_terms(n, mask, pairs, idx)
            post_cut(model, x, M, T, kind, lst)
            nterms += len(lst)
            ncuts += 1
        print(f"[build] n={n} T={T} vars={len(pairs)}(+{naux} aux) triangles={ntri} "
              f"cuts={ncuts} cut-terms={nterms}  {time.time()-t0:.1f}s", flush=True)
    else:
        seeded = set()
        # balanced + prefix cuts as a seed pool
        import random
        rnd = random.Random(7)
        for _ in range(4000):
            mask = 0
            while bin(mask).count("1") * 2 not in (n, n - 1, n + 1):
                mask = rnd.getrandbits(n) & ~1
            if mask in seeded:
                continue
            seeded.add(mask)
        for k in range(0, n):
            seeded.add(((1 << k) - 1) & ~1)
        for mask in seeded:
            kind, lst = cut_constraint_terms(n, mask, pairs, idx)
            post_cut(model, x, M, T, kind, lst)
        ncuts = len(seeded)
        print(f"[build] n={n} T={T} lazy, seeded {ncuts} cuts  {time.time()-t0:.1f}s", flush=True)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = args.workers
    if args.timeout > 0:
        solver.parameters.max_time_in_seconds = args.timeout
    solver.parameters.log_search_progress = args.log

    if args.cuts == "full" and args.enumerate:
        fh = open(args.enumerate, "w")
        st = {"n": 0}

        class _CB(cp_model.CpSolverSolutionCallback):
            def on_solution_callback(self):
                adj = [0] * n
                for (u, v) in pairs:
                    if self.Value(x[idx[(u, v)]]):
                        adj[u] |= 1 << v
                        adj[v] |= 1 << u
                fh.write(g6_encode(n, adj) + "\n")
                st["n"] += 1
                if st["n"] % 2000 == 0:
                    print(f"  ... {st['n']} solutions {time.time()-t0:.0f}s", flush=True)

        solver.parameters.enumerate_all_solutions = True
        solver.parameters.num_search_workers = 1   # CP-SAT: enumeration is sequential
        status = solver.Solve(model, _CB())
        fh.close()
        print(f"RESULT n={n} T={T}: ENUMERATED {st['n']} solutions "
              f"status={solver.StatusName(status)} [{time.time()-t0:.1f}s] -> {args.enumerate}")
        return 0

    if args.cuts == "full":
        status = solver.Solve(model)
        el = time.time() - t0
        if status == cp_model.INFEASIBLE:
            print(f"RESULT n={n} T={T}: UNSAT  (complete: all {ncuts} cut constraints posted)")
            print(f"       => a({n}) < {T}          [{el:.1f}s]")
            return 0
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            adj = extract(solver, x, n, pairs, idx)
            b, tf = report_graph(n, adj, T, "SAT")
            ok = tf and b >= T
            print(f"RESULT n={n} T={T}: {'SAT (re-verified)' if ok else 'SAT-BUT-FAILED-VERIFY'}"
                  f"  => a({n}) >= {b}   [{el:.1f}s]")
            return 0 if ok else 9
        print(f"RESULT n={n} T={T}: {solver.StatusName(status)}  [{el:.1f}s]")
        return 3

    # ---- lazy CEGAR ----
    seeded = set(seeded)
    rounds = 0
    best = -1
    while rounds < args.maxrounds:
        rounds += 1
        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print(f"RESULT n={n} T={T}: UNSAT after {rounds} rounds, {len(seeded)} cuts "
                  f"[{time.time()-t0:.1f}s]  => a({n}) < {T}")
            return 0
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            print(f"RESULT n={n} T={T}: {solver.StatusName(status)} after {rounds} rounds "
                  f"[{time.time()-t0:.1f}s]")
            return 3
        adj = extract(solver, x, n, pairs, idx)
        m = num_edges(n, adj)
        # collect the `batch` worst cuts of this graph
        vals = []
        deg_l = [bin(a).count("1") for a in adj]
        S, cut = 0, 0
        # simple Gray walk collecting all cuts with mono < T
        cur = 0
        cutval = 0
        worst = []
        for k in range(1, 1 << (n - 1)):
            v = (k & -k).bit_length()
            a = bin(adj[v] & cur).count("1")
            if (cur >> v) & 1:
                cutval += 2 * a - deg_l[v]
                cur &= ~(1 << v)
            else:
                cutval += deg_l[v] - 2 * a
                cur |= 1 << v
            if m - cutval < T and cur not in seeded:
                worst.append((m - cutval, cur))
        worst.sort()
        b = worst[0][0] if worst else T
        best = max(best, b)
        if not worst:
            bb, tf = report_graph(n, adj, T, "SAT")
            print(f"RESULT n={n} T={T}: SAT after {rounds} rounds  => a({n}) >= {bb}  "
                  f"[{time.time()-t0:.1f}s]")
            return 0
        added = 0
        for (_, mask) in worst:
            if added >= args.batch:
                break
            if mask in seeded:
                continue
            seeded.add(mask)
            kind, lst = cut_constraint_terms(n, mask, pairs, idx)
            post_cut(model, x, M, T, kind, lst)
            added += 1
        if rounds % 10 == 0:
            print(f"  round {rounds}: bip {b} (best {best}), cuts {len(seeded)}, "
                  f"{time.time()-t0:.1f}s", flush=True)
    print(f"RESULT n={n} T={T}: round limit")
    return 5


if __name__ == "__main__":
    sys.exit(main())
