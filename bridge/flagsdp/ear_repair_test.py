"""Find the CORRECT per-ear inequality that survives BOTH extremals.

The naive ear/vertex induction fails because:
 - odd cycle Cn: m=1, Gamma=N^2 LINEAR structure (one ear = the whole cycle minus the bad edge);
 - C5[q]: m=q^2, Gamma=N^2 QUADRATIC structure (a balanced product, invisible to ears).
A single scalar per-step budget can't fit both.

REPAIR IDEA (the genuinely-new ear argument):  Do the ear decomposition of B in the
CANONICAL way that makes the FIRST cycle B_0 an ODD-LENGTH closed walk through a bad edge
(the bad edge + a shortest B-path = an odd cycle of length ell). Then every subsequent ear
is an EVEN B-path (B is bipartite => all ears between same-color endpoints are even, between
opposite-color are odd; but B itself has NO odd cycle). Track the pair (N_t, X_t) where
   X_t := sum over bad edges supported in B_t of ell(uv)
   (the LINEAR cosystole, not quadratic).
Test the per-ear inequality for the LINEAR invariant: is X = sum ell <= N always, with
equality at C5[q] (5 ells of... no, q^2 ells of 5 => X=5q^2, N=5q, X=5q^2 > 5q for q>=2)?
NO: linear sum ell is q^2*5=5q^2 >> N=5q. So linear fails at C5[q] (X grows quadratically).

So the quadratic Gamma is genuinely needed and C5[q]'s quadratic bad-edge count is the
obstruction to ANY linear/ear bookkeeping. CONFIRM numerically + identify the only viable
shape: a Cauchy-Schwarz coupling sum ell <= sqrt(beta) * sqrt(Gamma) and Gamma<=N^2.

We test the THREE candidate global inequalities to see which extremal each is tight on:
   (A) Gamma <= N^2                  [the target; tight on BOTH]
   (B) sum ell <= N * something      [linear]
   (C) beta <= N^2/25                [implied; tight on C5[q] only]
   (D) max ell <= N                  [tight on odd cycle only]
and the KEY decoupling: Gamma <= (max ell) * (sum ell)? tight where?
"""
from collections import deque
import ear_invariant as EI

def bdist(n, adjB, src):
    d = [-1] * n; d[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        for w in adjB[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d

def stats(n, adj, side):
    adjB = [set() for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            if v > u and side[u] != side[v]:
                adjB[u].add(v); adjB[v].add(u)
    M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    ells = []
    for (u, v) in M:
        d = bdist(n, adjB, u)[v]
        ells.append(d + 1)
    return n, len(M), ells

def report(name, n, m, ells):
    G = sum(e * e for e in ells)
    S = sum(ells)
    mx = max(ells) if ells else 0
    print(f" {name:14s} N={n:3d} beta={m:3d} Gamma={G:5d} (/N^2={G/n/n:.3f}) "
          f"sum_ell={S:4d} (/N={S/n:.2f}) max_ell={mx:3d} (/N={mx/n:.2f}) "
          f"Gamma<=max_ell*sum_ell: {G}<={mx*S} {'TIGHT' if G==mx*S else ''}")

if __name__ == "__main__":
    print("Comparing candidate inequalities on the two extremal families:")
    for q in [1, 2, 3, 4]:
        n, adj, side, idx = EI.C5_blowup(q)
        report(f"C5[{q}]", *stats(n, adj, side))
    for L in [5, 7, 9, 11]:
        n, adj, side = EI.odd_cycle(L)
        report(f"C{L}", *stats(n, adj, side))
    # theta
    n, adj, side, M, idx = EI.c5_paths(4)
    report("c5_paths(4)", *stats(n, adj, side))
    print()
    print("KEY OBSERVATION: Gamma <= max_ell * sum_ell is TIGHT on odd cycles (max=sum_ell-term)")
    print("but on C5[q] max_ell=5, sum_ell=5q^2, product=25q^2=N^2=Gamma -> ALSO tight!")
    print("So Gamma = max_ell * sum_ell holds with equality on BOTH extremals when all ell equal.")
    print("This suggests the bound Gamma<=N^2 factors as: (sum ell) <= N * (N/max_ell)?? test.")
    print("DONE")
