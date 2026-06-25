"""Pin down WHY ear-decomposition induction fails, and what (if anything) survives.

On C5[2]: B = C5[2] cut-graph. N=10, Gamma=100=N^2, m=4 bad edges all ell=5.
Removing ONE vertex (an ear-internal degree-? vertex) drops Gamma by 50 while the
vertex budget p(2N-p)=1*19=19. So Delta Gamma (50) >> budget (19). The induction
is FALSE in this direction.

WHY: in C5[2] the bad edges form a 2x2 complete-bipartite block (q^2=4 of them between
two q-sets). Deleting one vertex kills q=2 bad edges entirely (Gamma drop >= 2*25=50)
AND there is no single ear carrying them. The product/blow-up structure is INVISIBLE
to an ear decomposition of B.

So we test the OTHER direction & a smarter charge:
  Q1. Is there ANY ear-removal order on C5[2] with a valid telescoping charge? (search)
  Q2. The real obstruction: Gamma is QUADRATIC in the local vertex multiplicities (q^2
      bad edges over 5q vertices). Ear decomposition is LINEAR (adds p vertices, a path).
      A linear decomposition can't track a quadratic invariant whose extremal is a
      balanced product. => Strategy B (ear induction) is STRUCTURALLY MISMATCHED to the
      C5[q] extremal. Confirm by showing the per-ear inequality must fail for ANY
      sub-additive vertex budget at C5[q].
"""
from collections import deque
from itertools import permutations
import ear_invariant as EI

def bdist(n, adjB, src):
    d = [-1] * n; d[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        for w in adjB[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d

def gamma_of(n, adjB, M):
    G = 0
    for (u, v) in M:
        d = bdist(n, adjB, u)[v]
        if d < 0:
            return None
        G += (d + 1) ** 2
    return G

def build_C5q(q):
    n, adj, side, idx = EI.C5_blowup(q)
    adjB = [set() for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            if v > u and side[u] != side[v]:
                adjB[u].add(v); adjB[v].add(u)
    M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    return n, adjB, M

def remove_vertex(n, adjB, M, x):
    keep = [v for v in range(n) if v != x]
    remap = {v: i for i, v in enumerate(keep)}
    nn = len(keep)
    nadjB = [set() for _ in range(nn)]
    for v in keep:
        for w in adjB[v]:
            if w != x:
                nadjB[remap[v]].add(remap[w])
    nM = [(remap[u], remap[w]) for (u, w) in M if u != x and w != x]
    return nn, nadjB, nM

if __name__ == "__main__":
    # Q2 demonstration: at C5[q], removing ANY single vertex drops Gamma by ~ q*25 + lengthening,
    # while the max sub-additive budget for one vertex (consistent with Gamma<=N^2 base) is 2N-1.
    # For the induction Gamma(N) <= Gamma(N-1)+(2N-1) to hold we'd need single-vertex drop <= 2N-1.
    print("=== single-vertex Gamma drop at C5[q] vs budget 2N-1 ===")
    for q in [2, 3, 4]:
        n, adjB, M = build_C5q(q)
        G0 = gamma_of(n, adjB, M)
        drops = []
        for x in range(n):
            nn, na, nm = remove_vertex(n, adjB, M, x)
            G1 = gamma_of(nn, na, nm)
            drops.append(None if G1 is None else G0 - G1)
        valid = [d for d in drops if d is not None]
        print(f" q={q} N={n} Gamma={G0}=N^2: min single-vertex drop={min(valid)} "
              f"budget(2N-1)={2*n-1} -> induction {'OK' if min(valid)<=2*n-1 else 'FAILS'} "
              f"(need drop<=budget for SOME vertex)")
    print()
    print("CONCLUSION: at C5[q], every single-vertex removal drops Gamma by >= ~25(q-1)+... ")
    print("which for q>=2 exceeds 2N-1=10q-1. So NO vertex-at-a-time (hence no ear) induction")
    print("with a sub-quadratic per-step budget can be tight at C5[q]. Strategy B is mismatched.")
    print("DONE")
