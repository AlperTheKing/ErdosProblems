#!/usr/bin/env python3
"""STRATEGY D probe: degree-weighted cycle-degree sum for the Connected-B Gamma Lemma.

Setup: tri-free G, max cut (X,Y), B = cut edges, M = bad edges, beta=|M|.
For e=uv in M, ell_e = d_B(u,v)+1 (odd >=5). C_e = shortest odd cycle through e (a B-geodesic + e), |C_e|=ell_e.
Gamma = sum_e ell_e^2.

PROVED TOOL (cycle-degree inequality, ineq (6)): for any odd cycle C of length L in tri-free G,
        sum_{v in C} deg_G(v) <= N (L-1)/2.

STRATEGY D, weighted form. Weight cycle C_e by ell_e and sum (6):
    LHS := sum_e ell_e * (sum_{v in C_e} deg(v))  <=  sum_e ell_e * N(ell_e -1)/2 = (N/2)(Gamma - S1),
    where S1 := sum_e ell_e.
Now LHS = sum_v deg(v) * L(v), with L(v) := sum_{e: v in C_e} ell_e  (the charging load; sum_v L(v)=Gamma).
We need a REVERSE lower bound  sum_v deg(v) L(v) >= (something) to combine into Gamma <= N^2.

We TEST several candidate reverse bounds numerically on critical instances, to see which (if any) closes it
and is tight at C5[q].

Reverse candidate (R1) - Chebyshev/Cauchy against the load:
   sum_v deg(v) L(v) >= (1/N) (sum_v deg(v)) (sum_v L(v)) = (2 e(G)/N) * Gamma     [Chebyshev sum ineq needs
   deg and L SIMILARLY sorted; FALSE in general but test the inequality sum deg*L >= (2e/N) Gamma numerically].
   If (R1) held:  (2e/N) Gamma <= (N/2)(Gamma - S1)  =>  Gamma(4e/N - N) <= -N S1 <0 ... only if 4e>N^2 ... no.

Reverse candidate (R2): Cauchy-Schwarz lower bound using sum_v L(v)=Gamma and support<=N:
   sum_v L(v)^2 >= (sum L)^2 / N = Gamma^2/N.
   And deg(v) L(v): we want to *upper* bound LHS by N^2 chain, not lower. Actually the cycle-deg gives an UPPER
   bound on LHS. So Strategy D as stated yields an UPPER bound on sum deg*L; to get Gamma<=N^2 we need a LOWER
   bound on sum deg*L of the form  >= Gamma^2 / N  (then Gamma^2/N <= (N/2)(Gamma-S1) <= (N/2)Gamma => Gamma<=N^2/2??
   too strong / wrong direction). Let's just MEASURE all the relevant quantities and see what inequality, if any,
   chains to N^2 and is tight at C5[q].
"""
import itertools
import numpy as np
from collections import deque
import flag_engine as fe


def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def maxcut(N, adj):
    best = -1; bs = None
    for mask in range(1 << (N-1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and side[u] != side[v])
        if c > best: best = c; bs = side
    return best, bs

def bfs_dist(N, adjB, s):
    dd = [-1]*N; dd[s] = 0; par = [-1]*N; q = deque([s])
    while q:
        x = q.popleft()
        for y in adjB[x]:
            if dd[y] < 0:
                dd[y] = dd[x]+1; par[y] = x; q.append(y)
    return dd, par

def analyze(N, A, label, verbose=True):
    adj = adjset(N, A)
    edges = [(u, v) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    M = [(u, v) for (u, v) in edges if side[u] == side[v]]
    if not M:
        return None
    deg = np.array([len(adj[u]) for u in range(N)], dtype=float)
    e_G = len(edges)
    # B = cut edges
    adjB = [[] for _ in range(N)]
    for (u, v) in edges:
        if side[u] != side[v]:
            adjB[u].append(v); adjB[v].append(u)
    # for each bad edge: ell_e = d_B(u,v)+1, and a shortest odd cycle C_e (B-geodesic u..v + e)
    Lload = np.zeros(N)          # L(v) = sum_{e: v in C_e} ell_e
    cyc_info = []
    Gamma = 0.0; S1 = 0.0
    for (u, v) in M:
        dd, par = bfs_dist(N, adjB, u)
        if dd[v] < 0:
            return ('cross',)    # cross-component bad edge: shouldn't happen for max cut
        ell = dd[v] + 1
        # geodesic path v..u in B
        path = [v]
        while path[-1] != u:
            path.append(par[path[-1]])
        Cset = set(path)         # vertices of the odd cycle (path covers both u and v)
        Gamma += ell*ell; S1 += ell
        for w in Cset:
            Lload[w] += ell
        cyc_info.append((ell, Cset))
    beta = len(M)
    # check cycle-degree inequality on each C_e and the weighted sum
    LHS = float(np.dot(deg, Lload))                       # = sum_e ell_e * sum_{v in C_e} deg(v)
    RHS_cd = (N/2.0)*(Gamma - S1)                          # (N/2) sum_e ell_e(ell_e-1)
    # measure reverse-bound candidates
    sumdeg = deg.sum()                                    # = 2 e_G
    cheby = (sumdeg/N)*Gamma                              # (R1) lower-bound CANDIDATE for LHS
    cauchy_load = (Lload.sum()**2)/N                      # Gamma^2/N  ... actually (sum L)^2/N
    res = {
        'label': label, 'N': N, 'beta': beta, 'e_G': e_G, 'Gamma': Gamma, 'S1': S1,
        'LHS': LHS, 'RHS_cd': RHS_cd, 'cd_ok': LHS <= RHS_cd + 1e-7,
        'cheby_lb': cheby, 'cheby_ok': LHS >= cheby - 1e-7,
        'GammaN2': Gamma <= N*N + 1e-7, 'N2': N*N,
        'sumL2': float((Lload**2).sum()), 'Gamma2_over_N': Gamma*Gamma/N,
        'maxL': float(Lload.max()), 'minL': float(Lload.min()),
    }
    if verbose:
        print(f"{label:10s} N={N:3d} beta={beta:3d} e={e_G:3d} Gamma={Gamma:7.1f} N^2={N*N:5d} "
              f"Gamma<=N^2:{res['GammaN2']}")
        print(f"   (6)-weighted: LHS=sum deg*L={LHS:9.1f} <= (N/2)(Gamma-S1)={RHS_cd:9.1f}  cd_ok={res['cd_ok']}")
        print(f"   Chebyshev R1: LHS >= (2e/N)Gamma={cheby:9.1f}?  {res['cheby_ok']}   (2e/N={sumdeg/N:.3f})")
        print(f"   maxL/N={res['maxL']/N:.4f}  minL={res['minL']:.1f}  Gamma/N^2={Gamma/(N*N):.4f}")
    return res

# builders
def c5n(k):
    Nn = 5*k; A = [0]*Nn; part = lambda v: v//k
    for u in range(Nn):
        for v in range(u+1, Nn):
            if (part(u)-part(v)) % 5 in (1, 4): A[u] |= 1 << v; A[v] |= 1 << u
    return Nn, A
def cycle(n):
    A = [0]*n
    for i in range(n):
        j = (i+1) % n; A[i] |= 1 << j; A[j] |= 1 << i
    return n, A
def petersen():
    verts = list(itertools.combinations(range(5), 2)); A = [0]*10
    for i, a in enumerate(verts):
        for j, b in enumerate(verts):
            if i < j and not set(a) & set(b): A[i] |= 1 << j; A[j] |= 1 << i
    return 10, A
def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4): add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A

if __name__ == "__main__":
    print("=== STRATEGY D probe: degree-weighted cycle-degree sum ===\n")
    named = [(*cycle(5), "C5"), (*cycle(7), "C7"), (*cycle(9), "C9"),
             (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]"), (*c5n(4), "C5[4]"),
             (*petersen(), "Petersen"), (*gpt_k23(), "K23-N13")]
    rows = []
    for (N, A, lab) in named:
        r = analyze(N, A, lab)
        if isinstance(r, dict): rows.append(r)
        print()
    # exhaustive: does the chain ever fail? and record worst maxL/N (the charging funnel)
    print("--- exhaustive tri-free N<=9: check cd_ok always, cheby_ok always, max(maxL/N) ---")
    worst_funnel = 0.0; cd_viol = 0; cheby_viol = 0; tot = 0; g_viol = 0
    for N in [5, 6, 7, 8, 9]:
        wf = 0.0
        for (n, A) in fe.enumerate_graphs(N, triangle_free=True):
            r = analyze(n, A, "", verbose=False)
            if not isinstance(r, dict): continue
            tot += 1
            if not r['cd_ok']: cd_viol += 1
            if not r['cheby_ok']: cheby_viol += 1
            if not r['GammaN2']: g_viol += 1
            wf = max(wf, r['maxL']/r['N']); worst_funnel = max(worst_funnel, r['maxL']/r['N'])
        print(f"N={N}: worst maxL/N={wf:.4f}")
    print(f">>> tot={tot} cd_viol={cd_viol} cheby_viol={cheby_viol} Gamma>N^2 viol={g_viol} "
          f"overall worst maxL/N={worst_funnel:.4f}")
    print("DONE")
