"""P2 / round 6 - the SMALLEST criterion falsifiers, exact verification + graph identification.

Takes the integer weightings found by P2_exhaust.exe, re-verifies them in exact rational arithmetic
with BOTH independent implementations, brute-forces ARCBOUND and psi, and identifies the graph.

Run:  python P2_small.py
"""
from fractions import Fraction as F
from itertools import combinations
import P2_verify as V1
import P2_verify2 as V2

TARGET = F(1, 25)


def from_weights(m, w, name=""):
    pos = [F(i, m) for i in range(m) if w[i]]
    wt = [w[i] for i in range(m) if w[i]]
    return V1.Config(pos, wt, name or f"Gamma_{m} w={tuple(w)}")


def graph_id(cfg):
    n = cfg.n
    E = [(u, v) for u, v in combinations(range(n), 2) if cfg.adj[u][v]]
    deg = [sum(1 for v in range(n) if cfg.adj[u][v]) for u in range(n)]
    # bipartite?
    col = [None] * n
    bip = True
    for s in range(n):
        if col[s] is not None:
            continue
        col[s], stack = 0, [s]
        while stack:
            u = stack.pop()
            for v in range(n):
                if cfg.adj[u][v]:
                    if col[v] is None:
                        col[v] = 1 - col[u]
                        stack.append(v)
                    elif col[v] == col[u]:
                        bip = False
    # shortest odd cycle
    girth_odd = None
    for L in range(3, n + 1, 2):
        found = False
        for start in range(n):
            # BFS-free: brute force simple cycles of length L through start (small n only)
            def walk(path):
                if len(path) == L:
                    return cfg.adj[path[-1]][path[0]]
                for v in range(path[0], n):
                    if v not in path and cfg.adj[path[-1]][v]:
                        if walk(path + [v]):
                            return True
                return False
            if walk([start]):
                found = True
                break
        if found:
            girth_odd = L
            break
    return E, deg, bip, girth_odd


def full(m, w, K=12):
    c1 = from_weights(m, w)
    q = sum(w)
    P = [i for i in range(m) if w[i]]
    c2 = V2.IConfig(m, P, [w[i] for i in P], c1.name)
    W, A = c1.W(), c1.A()
    g, ms = c1.g(), c1.m()
    bs = [c1.bound(k) for k in range(K + 1)]
    crit = min([A] + bs)
    ab, arc = c1.arcbound()
    ps, side = c1.psi()
    b2, g2, m2 = c2.bounds(K)
    same = (c1.W() == c2.W() and c1.A() == c2.A() and bs == b2 and ms == m2
            and ab == c2.arcbound()[0] and ps == c2.psi()[0])
    E, deg, bip, oddg = graph_id(c1)
    print(f"--- Gamma_{m}, weights {tuple(w)}, q={q}, N={c1.n} vertices, |E|={len(E)}")
    print(f"    support     = {[i for i in range(m) if w[i]]}")
    print(f"    degrees     = {deg}   bipartite={bip}   shortest odd cycle={oddg}")
    print(f"    W = {W} = {float(W):.6f}   T/W = {c1.T()/W} = {float(c1.T()/W):.6f}   "
          f"Var(g) = {c1.var_g()}")
    print(f"    A        = {A} = {float(A):.7f}   {'>' if A > TARGET else '<='} 1/25")
    print(f"    bound_k  = {bs[0]} (k=0) ... " + ", ".join(f"{float(b):.6f}" for b in bs[:6]))
    print(f"    min_b m(b)= {min(ms)} = {float(min(ms)):.7f}   {'>' if min(ms) > TARGET else '<='} 1/25")
    print(f"    CRIT     = {crit} = {float(crit):.7f}   ratio {float(crit)*25:.5f}   "
          f"{'*** FALSIFIER ***' if crit > TARGET else 'closed'}")
    print(f"    ARCBOUND = {ab} = {float(ab):.7f}  (truth, arc {arc})    psi = {ps} = {float(ps):.7f}")
    print(f"    both implementations agree exactly: {same}")
    assert same
    return crit


if __name__ == '__main__':
    print("=" * 100)
    print("A. the smallest falsifiers found by the exhaustive sweep: Gamma_14, q = 8, UNIFORM weights")
    print("=" * 100)
    for w in ([1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1],
              [1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0],
              [1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1]):
        full(14, w)
        print()

    print("=" * 100)
    print("B. the best integer weighting found on Gamma_14 with q = 12")
    print("=" * 100)
    full(14, [2, 0, 0, 1, 1, 2, 0, 0, 1, 2, 2, 0, 0, 1])
    print()

    print("=" * 100)
    print("C. six-atom falsifier from the 3-cluster construction (2 atoms per cluster)")
    print("=" * 100)
    for den, sh in ((40, 1), (60, 1), (100, 1), (200, 1)):
        c = V2.three_cluster_robust_int(2, den, sh)
        bs, gs, ms = c.bounds(12)
        crit = min([c.A()] + bs)
        E = [(u, v) for u, v in combinations(range(c.n), 2) if c.adj[u][v]]
        print(f"    eps=1/{den}: N={c.n} |E|={len(E)} W={c.W()} A={c.A()}={float(c.A()):.6f} "
              f"bound_0={bs[0]} bound_12={float(bs[12]):.6f} min_m={min(ms)} "
              f"CRIT={crit}={float(crit):.7f} {'FALSIFIER' if crit > TARGET else 'closed'} "
              f"ARCBOUND={c.arcbound()[0]} psi={c.psi()[0]}")
    print()

    print("=" * 100)
    print("D. MANDATORY REGRESSION - the nine round5 witnesses through the same code path")
    print("=" * 100)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "wreg", r"E:\Projects\ErdosProblems\problems\23\round5\claude_witness_regression.py")
    wreg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wreg)
    for wname, m, w, why in wreg.WITNESSES:
        cfg = from_weights(m, w, wname)
        A, bs = cfg.A(), [cfg.bound(k) for k in range(9)]
        crit = min([A] + bs)
        ab = cfg.arcbound()[0]
        # cross-check ARCBOUND against the round5 implementation
        adj = wreg.gamma(m)
        q = sum(w)
        x = [F(wi, q) for wi in w]
        ab5 = wreg.arcbound(m, adj, x)
        print(f"  {wname:26s} A={float(A):.6f} b0={float(bs[0]):.6f} CRIT={float(crit):.6f} "
              f"{'FALSIFIER' if crit > TARGET else 'closed  '} ARCBOUND={ab} (round5 says {ab5}) "
              f"{'MATCH' if ab == ab5 else '*** MISMATCH ***'}")
        assert ab == ab5, "my ARCBOUND disagrees with the round5 regression module"
    print("\n  [regression: my code reproduces the round5 ARCBOUND on all nine witnesses]")
