#!/usr/bin/env python3
"""STRATEGY E -- the WINDING / circular-embedding double count.

The genuine "homomorphism to C5" content for the Gamma lemma is NOT the integer
count hom(G,C5) (constant =10 on all C5[q]); it is the CONTINUOUS hom-density:
embed V(G) on the unit CIRCLE so that the bad edges are forced to "wind" while
B-edges only make small steps.  C5[q] is the unique maximiser, where Gamma=N^2.

Concrete construction tested here
---------------------------------
Pick a vertex potential theta: V -> R/(2*pi Z) (an angle).  Define the
WIND ENERGY of an edge set F by
        W(F; theta) = sum_{uv in F} (1 - cos(theta_u - theta_v)).
For the max cut we want B-edges to have SMALL wind and M-edges LARGE wind.
C5's winding angle is 2*pi/5 between consecutive vertices: a B-step is one
C5-step (angle 2pi/5), and a bad edge spans the SAME 2pi/5 (it closes the odd
cycle) -- all edges of C5[q] sit at angular separation 2pi/5.

Two double counts we test as the "C5 identity":

(I) DISTANCE-COSINE.  Along a shortest B-path of length ell-1 from u to v, the
    angle change is at most (ell-1)*max-step.  We measure
       LHS = sum_{uv in M} (ell-1)^2     (the Gamma surrogate, = sum (ell-1)^2)
    vs an embedding upper bound.  Calibrates the COAREA cap (linear).

(II) C5 QUADRATIC FORM.  Put x_v = e^{i theta_v} on the circle; the relevant
    operator is L_wind = (2 cos(2pi/5)) D - A  restricted to ... -- test the
    Rayleigh quotient against Gamma.

The OUTPUT we want: a SCALAR functional Phi(G) with
        25 * beta  <=  Gamma  <=  Phi(G)  <=  N^2,
all tight at C5[q] and at C_{2k+1}, where the middle <= is the NEW C5 double
count (not a self-tight certificate: Phi is built from the embedding, not from
an optimisation whose optimum equals Gamma).
"""
import math
import numpy as np
from collections import deque
from strat_e_probe import adjset, maxcut, petersen, c5n, gpt_k23, theta46
import flag_engine as fe


def cut_structure(N, adj):
    mc, side = maxcut(N, adj)
    adjB = [set() for _ in range(N)]
    M = []
    for u in range(N):
        for v in adj[u]:
            if v > u:
                if side[u] != side[v]:
                    adjB[u].add(v); adjB[v].add(u)
                else:
                    M.append((u, v))
    return side, adjB, M


def bfs_dist(N, adjB, src):
    d = [-1]*N; d[src]=0; dq=deque([src])
    while dq:
        x=dq.popleft()
        for w in adjB[x]:
            if d[w]<0:
                d[w]=d[x]+1; dq.append(w)
    return d


def gamma_and_struct(N, adj):
    side, adjB, M = cut_structure(N, adj)
    ells=[]
    for (u,v) in M:
        d=bfs_dist(N,adjB,u)
        ells.append(d[v]+1)
    G=sum(l*l for l in ells)
    return G, M, ells, adjB, side


# ---------------------------------------------------------------------------
# The "winding" identity test.
# The shortest odd cycle through bad edge uv has length ell. On C5[q] every
# such cycle is a 5-cycle and the WHOLE graph is a single 5-winding. The
# quantity we want to lower bound by Gamma and upper bound by N^2 is the
# "total squared winding" of the bad-edge family in the B-metric.
# ---------------------------------------------------------------------------

def coarea_linear_bound(N, adj):
    """Single-potential coarea: pick phi=BFS layer index from one root in B.
    sum over bad edges of |phi_u-phi_v| relates to sum (ell-1) -- LINEAR, the
    known cap. Returns (sum ell, sum (ell-1), eB) to show 4 beta <= eB style."""
    side, adjB, M = cut_structure(N, adj)
    eB = sum(len(s) for s in adjB)//2
    s_ellm1 = 0
    for (u,v) in M:
        d=bfs_dist(N,adjB,u)
        s_ellm1 += d[v]  # ell-1
    return sum_ell(N,adj), s_ellm1, eB


def sum_ell(N, adj):
    G,M,ells,_,_ = gamma_and_struct(N,adj)
    return sum(ells)


def c5_spectral_embed_bound(N, adj):
    """The C5 second-eigenvalue embedding. C5's adjacency has eigenvalue
    mu = 2 cos(2pi/5) = (sqrt5 - 1)/2 ~ 0.618 with a 2-dim eigenspace
    (cos, sin of 2pi k /5). The C5-blowup G=C5[q] inherits this: the operator
    (A - mu D) has the winding pair in its kernel direction... we compute the
    Rayleigh comparison
        R = max over x perp 1 of  x^T A x / x^T D x
    and relate (1 - R) to Gamma / (something). Diagnostic only."""
    A=np.zeros((N,N)); deg=np.zeros(N)
    for u in range(N):
        for v in adj[u]:
            A[u][v]=1.0
        deg[u]=len(adj[u])
    if deg.min()<=0:
        return None
    Dm12=np.diag(1.0/np.sqrt(deg))
    Anorm=Dm12@A@Dm12
    w=np.linalg.eigvalsh(Anorm)
    return float(w[-1]), float(w[-2]), float(w[0])  # lam1(=1), lam2, lam_min


def run():
    def cycle(L):
        A=[0]*L
        for i in range(L):
            A[i]|=1<<((i+1)%L); A[(i+1)%L]|=1<<i
        return L,A
    named=[(*c5n(1),"C5[1]"),(*c5n(2),"C5[2]"),(*c5n(3),"C5[3]"),(*c5n(4),"C5[4]"),
           (*petersen(),"Petersen"),(*gpt_k23(),"K23-N13"),(*theta46(),"theta46"),
           (*cycle(5),"C5"),(*cycle(7),"C7"),(*cycle(9),"C9"),(*cycle(11),"C11")]
    print("=== Strategy E winding: coarea (linear) vs Gamma (quadratic) calibration ===", flush=True)
    print(f"{'name':10s} {'N':>3s} {'beta':>4s} {'Gamma':>6s} {'4beta':>5s} {'sum(l-1)':>8s} {'eB':>4s} "
          f"{'lam2norm':>8s}", flush=True)
    for (N,A,label) in named:
        adj=adjset(N,A)
        G,M,ells,adjB,side=gamma_and_struct(N,adj)
        beta=len(M)
        sl,s_ellm1,eB=coarea_linear_bound(N,adj)
        sp=c5_spectral_embed_bound(N,adj)
        lam2=sp[1] if sp else float('nan')
        print(f"{label:10s} {N:>3d} {beta:>4d} {G:>6d} {4*beta:>5d} {s_ellm1:>8d} {eB:>4d} "
              f"{lam2:>8.4f}", flush=True)
    # The point: Gamma is QUADRATIC in ell, coarea only controls sum(ell-1) (linear).
    # C5 supplies the quadratic via a 5-fold winding. Print the key ratio.
    print("\nNote: on C5[q], lam2norm should approach 2cos(2pi/5)/2 = cos(2pi/5) = %.4f"
          % math.cos(2*math.pi/5), flush=True)


if __name__ == "__main__":
    run()
