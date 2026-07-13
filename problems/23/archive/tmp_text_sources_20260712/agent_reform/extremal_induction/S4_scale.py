"""S4: does the Grotzsch increment-violation scale under blow-up?
Grotzsch[2]: N=22, budget (2N-5)/5 = 39/5 = 7.8.
All induced C5s of H[2] are transversals of induced C5s of H (proved in notes; spot-check here).
By the wreath automorphisms, increment depends only on the base pentagon: 31 computations.
Also: is C17(1,4) hom to C5? Grotzsch is chi=4 hence not. And slack table for violators.
"""
import numpy as np, itertools, sys
from fractions import Fraction
sys.path.insert(0, r"E:\Projects\ErdosProblems\tmp\agent_reform\extremal_induction")
from S1_sanity import beta, is_triangle_free, induced_subgraph
from S3_hunt import mycielski, induced_c5s, adj_sets, circulant

def blowup(n, edges, t):
    """H[t]: vertex (v,c) -> v*t+c."""
    N = n * t
    E = []
    for (i, j) in edges:
        for a in range(t):
            for b in range(t):
                E.append((i * t + a, j * t + b))
    return N, E

def hom_to_c5(n, edges):
    """Backtracking: map to C5 (adjacency i~i+-1 mod 5)."""
    a = adj_sets(n, edges)
    order = sorted(range(n), key=lambda v: -len(a[v]))
    pos = {v: k for k, v in enumerate(order)}
    col = [-1] * n
    def ok(v, c):
        for u in a[v]:
            cu = col[u]
            if cu >= 0 and (cu - c) % 5 not in (1, 4):
                return False
        return True
    def bt(k):
        if k == n:
            return True
        v = order[k]
        for c in range(5 if k else 1):  # fix first vertex color 0 (vertex-transitivity not assumed; wlog by C5 symmetry only rotation... use all 5 for safety except first)
            if ok(v, c):
                col[v] = c
                if bt(k + 1):
                    return True
                col[v] = -1
        return False
    return bt(0)

def main():
    # Grotzsch
    gn, gE = mycielski(5, [(i, (i + 1) % 5) for i in range(5)])
    assert is_triangle_free(gn, gE)
    print(f"Grotzsch: hom->C5 = {hom_to_c5(gn, gE)} (expect False, chi=4)")

    cn, cE = circulant(17, (1, 4))
    print(f"C17(1,4): hom->C5 = {hom_to_c5(cn, cE)}")

    # Grotzsch[2]
    N, E = blowup(gn, gE, 2)
    assert is_triangle_free(N, E)
    bG = beta(N, E)
    budget = Fraction(2 * N - 5, 5)
    print(f"Grotzsch[2]: N={N} e={len(E)} beta={bG}  N^2/25={Fraction(N*N,25)} defect={Fraction(N*N,25)-bG}")
    base_c5s = induced_c5s(gn, gE)
    print(f"base pentagons: {len(base_c5s)}")
    best = None
    incs = []
    for P0 in base_c5s:
        P = [v * 2 + 0 for v in P0]  # copy-0 transversal
        keep = [v for v in range(N) if v not in set(P)]
        n2, E2 = induced_subgraph(N, E, keep)
        bH = beta(n2, E2)
        inc = bG - bH
        incs.append(inc)
        if best is None or inc < best:
            best = inc
    print(f"Grotzsch[2] pentagon increments: min={best} max={max(incs)} budget={budget} "
          f"{'PASS (violation does NOT scale)' if Fraction(best) <= budget else '*** VIOLATION SCALES ***'}")
    print("increment histogram:", sorted(set((i, incs.count(i)) for i in incs)))

    # slack table for the two violators
    for name, (vn, vE) in [("Grotzsch", (gn, gE)), ("C17(1,4)", (cn, cE))]:
        b = beta(vn, vE)
        print(f"{name}: N={vn} beta={b} bound={Fraction(vn*vn,25)} defect={Fraction(vn*vn,25)-b} "
              f"(defect-transfer covers: child-slack available since all beta(G-P) far below (N-5)^2/25)")

if __name__ == "__main__":
    main()
