#!/usr/bin/env python3
"""
STRATEGY F core test: RANDOM C5-coloring / random circular embedding.

Idea: map V -> Z_5 (or the circle R/5Z) by a random "phase" assignment phi.
At C5[q], the deterministic homomorphism G->C5 exists: phi(v)=part(v), and then every
bad edge (within V3~V4? no -- bad edges connect adjacent parts under the cut...).
Actually the cleaner object: a random potential f: V -> R that is 1-LIPSCHITZ on B
(|f(x)-f(y)|<=1 for B-edges). For ANY such f, CD-coarea gives
   sum_{uv in M} |f(u)-f(v)|  <=  sum_{uv in B} |f(u)-f(v)|  <=  |B|.
The single-edge stretch f_e=d_B(u_e,.) gives |f_e(u)-f_e(v)|=ell_e-1 for bad edge e (and is
1-Lip on B). The SYNC problem: combine the per-edge potentials.

RANDOM-PROJECTION version (the genuine Strategy-F content):
 Embed B isometrically-ish: assign each vertex x a vector psi(x) in R^D s.t. B-edges have
 ||psi(x)-psi(y)|| <= 1 (1-Lipschitz). Then for a RANDOM unit direction theta, f_theta(x)=<psi(x),theta>
 is 1-Lipschitz on B in expectation of squared length. We get
   E_theta[ sum_M |f_theta(u)-f_theta(v)| ]  <= E_theta[ sum_B |f_theta(u)-f_theta(v)| ].
 And  E_theta[|<psi(u)-psi(v),theta>|] = c_D * ||psi(u)-psi(v)||.  So this is just
   sum_M ||psi(u)-psi(v)|| <= sum_B ||psi(u)-psi(v)||  <= |B|  (if 1-Lip).
 To get ell_e we need ||psi(u_e)-psi(v_e)|| >= ell_e-1, i.e. psi must STRETCH every bad edge to
 its full B-distance simultaneously -- this is an isometric embedding of the B-metric, which exists
 (psi(x) = (d_B(r,x))_{r in V} / sqrt(N)... but that distorts).

KEY TEST: the embedding psi(x) = full distance vector. Then
   ||psi(u)-psi(v)||^2 = sum_r (d_B(r,u)-d_B(r,v))^2 = L2(uv)  [the quantity from v3].
 We computed L2B = N|B| at C5[q] but per B-edge L2 can be < N. The 1-LIPSCHITZ condition on B
 in this embedding is: L2(B-edge) <= ??? -- NOT bounded by 1. So we must NORMALIZE.

The HONEST diagnostic: does there exist a 1-Lipschitz-on-B embedding psi into Hilbert space with
   sum_M ||psi(u)-psi(v)||^2  >=  c * Gamma   and   sum_B ||psi(u)-psi(v)||^2 <= |B| ?
 If sum_M ||.||^2 >= Gamma and sum_B ||.||^2 <= |B|, and IF additionally we had the L2-coarea
 sum_M ||.||^2 <= sum_B ||.||^2 we'd get Gamma <= |B| -- only LINEAR, wrong (need quadratic).

So a PURE coarea/Lipschitz random projection gives at best the LINEAR bound 4m<=|B|. To get
QUADRATIC (Gamma<=N^2 ~ N*|B|/4) we need to also USE that |B|<=N^2/4 ... no.

CONCLUSION TO VERIFY NUMERICALLY: the random-projection / coarea family is intrinsically LINEAR
(gives c*m <= |B|), hence cannot reach the quadratic Gamma<=N^2 unless coupled with a SECOND
mechanism that converts the per-reference variance into the extra factor of ell. We test whether
the per-reference SECOND MOMENT sum_r (dd)^2, when WEIGHTED by 1/(local B-degree), closes the gap.
"""
from collections import deque

def adjset(N, E):
    adj = [set() for _ in range(N)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    return adj

def maxcut(N, E):
    best = -1; bs = None
    for m in range(1 << (N - 1)):
        s = [(m >> u) & 1 for u in range(N)]
        c = sum(1 for u, v in E if s[u] != s[v])
        if c > best:
            best = c; bs = s
    return best, bs

def bdist(N, Badj, src):
    d = [-1] * N; d[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        for w in Badj[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d

def build_c5q(q):
    N = 5 * q
    def vid(p, i):
        return p * q + i
    part = lambda v: v // q
    Eall = []
    for p in range(5):
        for pp in range(p + 1, 5):
            if (p - pp) % 5 in (1, 4):
                for i in range(q):
                    for j in range(q):
                        Eall.append((vid(p, i), vid(pp, j)))
    M = [(u, v) for (u, v) in Eall if {part(u), part(v)} == {3, 4}]
    Bset = [(u, v) for (u, v) in Eall if {part(u), part(v)} != {3, 4}]
    return N, M, Bset

def analyze(N, M, Bset, lab):
    Badj = adjset(N, Bset)
    Dall = [bdist(N, Badj, r) for r in range(N)]
    ell = {(u, v): Dall[u][v] + 1 for (u, v) in M}
    Gamma = sum(e * e for e in ell.values())
    # weighted second moment: for each reference r, weight 1/deg_B-ish?
    # Test the "balanced" random reference where r is weighted by 1.
    # Per-bad-edge: sum_r (dd_r)^2 vs ell_e^2 ... compare distribution.
    print(f"== {lab}: N={N} m={len(M)} |B|={len(Bset)} Gamma={Gamma} N^2={N*N}")
    # crucial per-edge check: sum_r (d_B(r,u)-d_B(r,v))^2 for a single bad edge
    for (u, v) in M[:3]:
        s = sum((Dall[r][u] - Dall[r][v]) ** 2 for r in range(N))
        s1 = sum(abs(Dall[r][u] - Dall[r][v]) for r in range(N))
        print(f"   bad edge ({u},{v}) ell={ell[(u,v)]} ell^2={ell[(u,v)]**2}  "
              f"sum_r dd^2={s}  sum_r|dd|={s1}  (ratio dd^2/ell^2={s/ell[(u,v)]**2:.2f})")

def gpt_k23():
    N = 13; E = []
    for i in (0, 1):
        for j in (2, 3, 4):
            E.append((i, j))
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt + 1; nxt += 2
        E.append((x, a)); E.append((a, b)); E.append((b, y))
    return N, E

if __name__ == "__main__":
    for q in (1, 2, 3):
        N, M, Bset = build_c5q(q)
        analyze(N, M, Bset, f"C5[{q}]")
    # K23
    N, E = gpt_k23()
    mc, side = maxcut(N, E)
    M = [(u, v) for u, v in E if side[u] == side[v]]
    Bset = [(u, v) for u, v in E if side[u] != side[v]]
    analyze(N, M, Bset, "K23-N13")
    print("DONE")
