#!/usr/bin/env python3
"""STRATEGY E -- the C5 VECTOR-EMBEDDING double count (genuine hom-density form).

A single scalar potential caps at the linear bound (confirmed). C5's extremal
power is its 2-DIMENSIONAL eigenspace (the regular pentagon), so the right
object is a VECTOR embedding x: V -> R^2 (or the complex circle), giving the
hom-density / Lovasz-theta flavour.

THE C5 STRUCTURE THEOREM we exploit.  C5 = Cayley graph of Z/5 with connection
set {+-1}? No: C5's vertices in cyclic order 0..4, edges i~i+1; but as a circulant
its adjacency eigenvalues are 2cos(2pi k/5). The eigenvalue mu = 2cos(2pi/5) =
(sqrt5-1)/2 has eigenvectors  e_k = (cos(2pi k j/5), sin(2pi k j/5)).

C5-blowup test.  For G with a hom phi:V->C5 (e.g. C5[q]), set
   x_v = ( cos(2pi phi(v)/5), sin(2pi phi(v)/5) ) in R^2.
Then for ANY edge uv of G, phi(u)~phi(v) in C5 so |phi(u)-phi(v)|=1 mod 5, hence
   <x_u, x_v> = cos(2pi/5) = mu/2  for EVERY edge.
This is the key rigidity: in a C5-blowup, EVERY edge has the SAME inner product
mu/2 ~ 0.309. A bad edge and a B-edge are indistinguishable to this embedding!

So the embedding alone can't separate M from B; we need to combine it with the
B-DISTANCE.  The candidate double count:

  Build the embedding from the SHORTEST-PATH STRUCTURE of B, not from a given hom.
  For a connected bipartite B with a max cut, the natural circular coordinate is
  the FIEDLER-like winding. We test whether
       sum_{uv in M} ell(uv)^2  =  Gamma
  is captured by the QUADRATIC FORM  x^T (something) x  maximised by the pentagon.

TWO concrete computations:
  (A) The "C5 Gram/theta" upper bound:  max over unit vectors x_v in R^d, d free,
      of  sum_{uv in M} <x_u,x_v>^{-?} ...  -- instead we use the SHARP known one:
      the fractional-chromatic / vector-chromatic SDP of the ODD-CYCLE structure.
  (B) The DIRECT winding identity: for each bad edge, its shortest odd cycle C_e
      (length ell) is a closed walk; embed it on the circle as a regular ell-gon;
      its "enclosed area" = ell * (1/2) sin(2pi/ell) ... and SUM of areas vs N^2.

We test (B): AREA(G) := sum_{uv in M} ell^2 / (2 tan(pi/ell))  ... and simpler,
just verify the geometric identity that on C5[q] the bad-edge pentagons TILE a
region of total area proportional to N^2.
"""
import math
import numpy as np
from collections import deque
from strat_e_probe import adjset, maxcut, petersen, c5n, gpt_k23, theta46
import flag_engine as fe


def cut_structure(N, adj):
    mc, side = maxcut(N, adj)
    adjB=[set() for _ in range(N)]; M=[]
    for u in range(N):
        for v in adj[u]:
            if v>u:
                if side[u]!=side[v]: adjB[u].add(v); adjB[v].add(u)
                else: M.append((u,v))
    return side, adjB, M


def bfs_dist(N, adjB, src):
    d=[-1]*N; d[src]=0; dq=deque([src])
    while dq:
        x=dq.popleft()
        for w in adjB[x]:
            if d[w]<0: d[w]=d[x]+1; dq.append(w)
    return d


def gamma_struct(N, adj):
    side, adjB, M = cut_structure(N, adj)
    ells=[]
    for (u,v) in M:
        d=bfs_dist(N,adjB,u); ells.append(d[v]+1)
    return sum(l*l for l in ells), M, ells, adjB, side


# ---------------------------------------------------------------------------
# THE CYCLE-DEGREE / CAUCHY IDENTITY, rewritten as a hom-style double count.
# The proved bound nu* <= N^2/25 comes from:  for an odd cycle C of length L,
#   sum_{v in C} d(v) <= N(L-1)/2     (cycle-degree ineq (6))
# Summing the *shortest-cycle-per-bad-edge* family with weights gives the link.
# We make the DUAL (upper-bound-on-Gamma) version explicit and test tightness.
# ---------------------------------------------------------------------------

def cycle_degree_check(N, adj):
    """Verify cycle-degree ineq (6) on the shortest odd cycle of each bad edge,
    and accumulate the Cauchy bound that yields Gamma <= N^2 IF the cycles were
    edge-disjoint. Returns the deficit = N^2 - (Cauchy estimate)."""
    G, M, ells, adjB, side = gamma_struct(N, adj)
    deg=[len(adj[v]) for v in range(N)]
    # For each bad edge, reconstruct a shortest odd cycle and check sum deg <= N(L-1)/2
    viol=0
    rows=[]
    for (u,v) in M:
        d=bfs_dist(N,adjB,u)
        L=d[v]+1
        # reconstruct one shortest B-path u..v
        # rebuild path via repeated BFS parent
        prev={u:None}; dq=deque([u])
        while dq:
            x=dq.popleft()
            if x==v: break
            for w in adjB[x]:
                if w not in prev:
                    prev[w]=x; dq.append(w)
        path=[]; cur=v
        while cur is not None: path.append(cur); cur=prev[cur]
        sd=sum(deg[w] for w in path)
        bound=N*(L-1)//2 if (N*(L-1))%2==0 else N*(L-1)/2
        if sd>bound+1e-9: viol+=1
        rows.append((L, sd, bound))
    return rows, viol


def run():
    def cycle(L):
        A=[0]*L
        for i in range(L):
            A[i]|=1<<((i+1)%L); A[(i+1)%L]|=1<<i
        return L,A
    named=[(*c5n(1),"C5[1]"),(*c5n(2),"C5[2]"),(*c5n(3),"C5[3]"),
           (*petersen(),"Petersen"),(*gpt_k23(),"K23-N13"),(*theta46(),"theta46"),
           (*cycle(7),"C7"),(*cycle(9),"C9")]
    print("=== Strategy E: cycle-degree (6) on shortest odd cycle per bad edge ===", flush=True)
    for (N,A,label) in named:
        adj=adjset(N,A)
        rows, viol = cycle_degree_check(N,adj)
        tight = sum(1 for (L,sd,b) in rows if abs(sd-b)<1e-9)
        print(f"  {label:10s} N={N:2d} #bad={len(rows):2d} (6)-violations={viol} "
              f"#tight={tight}  rows(L,sumdeg,bound)={rows[:4]}", flush=True)


if __name__ == "__main__":
    run()
