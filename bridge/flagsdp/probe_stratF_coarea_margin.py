#!/usr/bin/env python3
"""
STRATEGY F: the CLEANEST honest formulation and its tightness audit.

THE coarea identity (provable, exact): CD <=> for all f:V->R,
    sum_{uv in M} |f(u)-f(v)|  <=  sum_{uv in B} |f(u)-f(v)|.     (COAREA-CD)

Single-block proof uses ONE f=min(d_B(A,.),4) stretching all bad edges by 4 -> gives 4m<=|B| LINEAR.
To reach QUADRATIC Gamma=sum ell^2<=N^2, Strategy F integrates over a FAMILY of potentials.

THE RANDOM-THRESHOLD / RANDOM-LEVEL formulation (genuinely new, fractional):
 Pick a random reference r ~ Unif(V) AND a random threshold t ~ Unif. Consider the cut
   S_{r,t} = { x : d_B(r,x) <= t }.  This is a sublevel cut of the 1-Lipschitz potential d_B(r,.).
 CD gives |delta_M(S_{r,t})| <= |delta_B(S_{r,t})| for EVERY (r,t).  Integrate:
   sum_{uv in M} (# thresholds t separating u,v from r) = sum_{uv in M} |d_B(r,u)-d_B(r,v)|.
 A bad edge uv with d_B(u,v)=ell-1: how many (r,t) separate it?  EXACTLY the L1 quantity.

 So  E_r[ sum_M |dd_r| ]  is the natural fractional 'stretch'. AT C5[q], per bad edge the average
 stretch  (sum_r |dd_r|)/N  -> ?  We measured sum_r|dd| per edge = 12(q=1),20(q=2),28(q=3)
 i.e. 4q+8, so /N=(4q+8)/(5q) -> 4/5.  So average stretch -> 4/5 NOT 4.  The random reference
 DILUTES the stretch by factor ~1/5 (only refs in the 'right' parts see the full spread).

 => E_r[sum_M|dd_r|] ~ (4/5) m  while E_r[sum_B|dd_r|] = |B|*(avg B-stretch). This gives a LINEAR
 relation again, weaker than 4m<=|B|.  The random reference is WORSE than the single best potential.

CONCLUSION: uniform random reference is the WRONG measure (it dilutes). The right Strategy-F object
must be a NON-UNIFORM / IMPORTANCE-WEIGHTED random potential concentrating on references that see
each bad edge's full spread -- but that importance weight is exactly the per-edge source choice,
which re-introduces the SYNC problem (one f per edge). So entropy-over-uniform fails; entropy-over-
optimal-weights = the Sync gap = the self-tight wall.

This script DOCUMENTS that dilution exactly, to make the verdict rigorous.
"""
from collections import deque
from fractions import Fraction

def adjset(N, E):
    adj = [set() for _ in range(N)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    return adj

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
    vid = lambda p, i: p * q + i
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

print("C5[q]: uniform-random-reference DILUTION of bad-edge stretch")
print(f"{'q':>2} {'N':>3} {'avg_stretch_M':>14} {'(ell-1)=4':>10} {'dilution':>10}  "
      f"{'sumM|dd|':>9} {'sumB|dd|':>9} {'4m vs |B|':>12}")
for q in range(1, 7):
    N, M, Bset = build_c5q(q)
    Badj = adjset(N, Bset)
    Dall = [bdist(N, Badj, r) for r in range(N)]
    sumMdd = sum(abs(Dall[r][u] - Dall[r][v]) for r in range(N) for (u, v) in M)
    sumBdd = sum(abs(Dall[r][u] - Dall[r][v]) for r in range(N) for (u, v) in Bset)
    avg_stretch = Fraction(sumMdd, N * len(M))
    print(f"{q:>2} {N:>3} {str(avg_stretch):>14} {'4':>10} "
          f"{float(avg_stretch)/4:>10.3f}  {sumMdd:>9} {sumBdd:>9} "
          f"{str(4*len(M))+' vs '+str(len(Bset)):>12}")
print()
print("avg_stretch -> 4/5 (NOT 4): uniform reference dilutes by ~1/5. Confirms verdict.")
print("DONE")
