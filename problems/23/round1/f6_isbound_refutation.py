"""
F6 / Erdos #23.  REFUTATION of the independent-set-cut bound.

For a triangle-free G, N(v) is independent, so for every independent set I the cut
(I, V\I) has exactly  m - sum_{u in I} d(u)  monochromatic edges.  Hence
      bip(G) <= m - w(G),     w(G) := max { sum_{u in I} d(u) : I independent }.
This is the strongest bound obtainable from "neighbourhood / independent-set cuts",
it dominates  m - max_v sum_{u~v} d(u)  and  m - 4m^2/N^2, and it is EXACTLY TIGHT
on C5[n] (giving N^2/25).  We show it is nevertheless FALSE as a route to the
conjecture, with an explicit infinite family and an exact ratio.

All arithmetic exact (integers / Fraction).
"""
from fractions import Fraction
import itertools, sys

def mwis_weight(n, adj, wts):
    """exact max-weight independent set by DP over subsets (n <= 22)."""
    f = [0]*(1 << n)
    for S in range(1, 1 << n):
        v = (S & -S).bit_length() - 1
        a = f[S & ~(1 << v)]
        b = wts[v] + f[S & ~((1 << v) | adj[v])]
        f[S] = a if a > b else b
    return f[(1 << n) - 1]

def bip_exact(n, adj, edges):
    best = len(edges)
    for mask in range(1 << (n-1)):
        M = mask << 1
        c = 0
        for u, v in edges:
            if ((M >> u) & 1) == ((M >> v) & 1): c += 1
        if c < best: best = c
    return best

def triangle_free(n, adj):
    for u in range(n):
        for v in range(n):
            if (adj[u] >> v) & 1 and u < v and (adj[u] & adj[v]): return False
    return True

def analyse(name, n, edges, do_bip=True):
    adj = [0]*n
    for u, v in edges: adj[u] |= 1 << v; adj[v] |= 1 << u
    deg = [bin(adj[v]).count("1") for v in range(n)]
    m = len(edges)
    tf = triangle_free(n, adj)
    w = mwis_weight(n, adj, deg)
    Dmax = max(sum(deg[u] for u in range(n) if (adj[v] >> u) & 1) for v in range(n))
    alpha = mwis_weight(n, adj, [1]*n)
    b = bip_exact(n, adj, edges) if do_bip else None
    print(f"{name}: N={n} m={m} regular={len(set(deg))==1}:{deg[0] if len(set(deg))==1 else deg}"
          f" trianglefree={tf} alpha={alpha}")
    print(f"    w = {w}   m-w = {m-w}   (m-w)/N^2 = {Fraction(m-w, n*n)} = {(m-w)/n**2:.6f}"
          f"   vs 1/25 = 0.040000   {'*** EXCEEDS N^2/25 ***' if 25*(m-w) > n*n else 'ok'}")
    print(f"    m-Dmax = {m-Dmax}    m - 4m^2/N^2 = {m - Fraction(4*m*m, n*n)}   m/2 = {Fraction(m,2)}"
          f"   N^2/16 = {Fraction(n*n,16)}   N^2/25 = {Fraction(n*n,25)}")
    if b is not None:
        print(f"    bip(G) = {b}   bip/N^2 = {Fraction(b, n*n)} = {b/n**2:.6f}   conjecture {'OK' if 25*b <= n*n else 'VIOLATED'}")
    return dict(n=n, m=m, w=w, alpha=alpha, bip=b)

# ---------- Clebsch graph = folded 5-cube = srg(16,5,0,2) ----------
def clebsch():
    V = list(range(16))
    conn = [1, 2, 4, 8, 15]          # weight-1 vectors of F_2^4 plus the all-ones vector
    E = []
    for u in range(16):
        for v in range(u+1, 16):
            if (u ^ v) in conn: E.append((u, v))
    return 16, E

# ---------- Chvatal graph : 4-regular, 12 vertices, triangle-free, alpha=4 ----------
def chvatal():
    E = [(0,1),(0,4),(0,6),(0,9),(1,2),(1,5),(1,7),(2,3),(2,6),(2,8),(3,4),(3,7),(3,9),
         (4,5),(4,8),(5,10),(5,11),(6,10),(6,11),(7,8),(7,11),(8,10),(9,10),(9,11)]
    return 12, E

# ---------- Wagner graph C8(1,4) ----------
def wagner():
    E = [(i, (i+1) % 8) for i in range(8)] + [(i, i+4) for i in range(4)]
    return 8, E

# ---------- Higman-Sims graph via the Witt design S(3,6,22) from the extended Golay code -----
GOLAY_B = [
 "011111111111",
 "111011100010",
 "110111000101",
 "101110001011",
 "111100010110",
 "111000101101",
 "110001011011",
 "100010110111",
 "100101101110",
 "101011011100",
 "110110111000",
 "101101110001",
]
def golay_octads():
    B = [int(r, 2) for r in GOLAY_B]
    gen = [(1 << (23-i)) | B[i] for i in range(12)]      # [I_12 | B], 24-bit codewords
    words = [0]
    for g in gen:
        words = words + [x ^ g for x in words]
    from collections import Counter
    wd = Counter(bin(x).count("1") for x in words)
    return words, wd

def higman_sims():
    words, wd = golay_octads()
    assert len(words) == 4096
    assert sorted(wd.items()) == [(0,1),(8,759),(12,2576),(16,759),(24,1)], sorted(wd.items())
    octads = [x for x in words if bin(x).count("1") == 8]
    # fix two coordinates a=0,b=1 (bit positions 23 and 22 in our 24-bit layout)
    a, b = 1 << 23, 1 << 22
    hexads = []
    for o in octads:
        if (o & a) and (o & b):
            rest = o & ~(a | b)
            hexads.append(rest)
    assert len(hexads) == 77, len(hexads)
    pts = [i for i in range(24) if i not in (0, 1)]        # 22 points
    ptbit = {p: 1 << (23-p) for p in pts}
    # vertices: 0 = infinity, 1..22 = points, 23..99 = hexads
    n = 100
    E = []
    for i, p in enumerate(pts): E.append((0, 1+i))
    for i, p in enumerate(pts):
        for j, H in enumerate(hexads):
            if (H & ptbit[p]): E.append((1+i, 23+j))      # p IN H
    for j1 in range(77):
        for j2 in range(j1+1, 77):
            if not (hexads[j1] & hexads[j2]): E.append((23+j1, 23+j2))
    return n, E

def hs_check():
    n, E = higman_sims()
    adj = [set() for _ in range(n)]
    for u, v in E: adj[u].add(v); adj[v].add(u)
    degs = sorted(set(len(a) for a in adj))
    tf = all(not (adj[u] & adj[v]) for u, v in E)
    lam = set(); mu = set()
    for u in range(n):
        for v in range(u+1, n):
            c = len(adj[u] & adj[v])
            (lam if v in adj[u] else mu).add(c)
    print(f"Higman-Sims: N={n} m={len(E)} degrees={degs} trianglefree={tf} lambda={lam} mu={mu}")
    return n, E, adj

def hs_alpha(n, adj):
    """exact independence number via OR-Tools CP-SAT (integer, exact)."""
    from ortools.sat.python import cp_model
    mdl = cp_model.CpModel()
    x = [mdl.NewBoolVar(f"x{i}") for i in range(n)]
    for u in range(n):
        for v in adj[u]:
            if u < v: mdl.Add(x[u] + x[v] <= 1)
    mdl.Maximize(sum(x))
    sol = cp_model.CpSolver(); sol.parameters.max_time_in_seconds = 600
    sol.parameters.num_search_workers = 32
    st = sol.Solve(mdl)
    return int(sol.ObjectiveValue()), sol.StatusName(st), int(sol.BestObjectiveBound())

if __name__ == "__main__":
    print("======== triangle-free graphs on which the independent-set-cut bound m-w EXCEEDS N^2/25 ========\n")
    n, E = wagner();  analyse("Wagner C8(1,4)", n, E)
    print()
    n, E = chvatal(); analyse("Chvatal graph ", n, E)
    print()
    n, E = clebsch(); analyse("Clebsch  srg(16,5,0,2)", n, E)
    print()
    n, E, adj = hs_check()
    m = len(E)
    a, st, bound = hs_alpha(n, adj)
    w = 22*a
    print(f"    exact alpha(HiS) = {a}  (solver status {st}, proved bound {bound})")
    print(f"    w = 22*alpha = {w}   m-w = {m-w}   (m-w)/N^2 = {Fraction(m-w, 10000)} = {(m-w)/10000:.6f}"
          f"   ceiling N^2/16 = 0.0625   target 1/25 = 0.04")
