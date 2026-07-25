"""Q1_mycielski.py -- is the failure of the neighbourhood-union cut certificate a one-off
(the Grotzsch graph) or systematic?  Test the Mycielski tower and related 4-chromatic
triangle-free graphs.  Exact integers throughout.

For each graph G we compute
    bip(G)                    = min over ALL cuts of the number of monochromatic edges
    fam(G)                    = min over all cuts of the form  union_{v in I} N(v)
and compare fam(G) with n^2/25 (the certificate target).
"""
from fractions import Fraction
from itertools import combinations


def cycle(k):
    adj = [0] * k
    for i in range(k):
        j = (i + 1) % k
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    return k, adj


def mycielski(n, adj):
    """M(G): u_0..u_{n-1} copy of G, v_0..v_{n-1} shadows (v_i ~ N_G(u_i)), w ~ all v_i"""
    m = 2 * n + 1
    a = [0] * m
    for i in range(n):
        a[i] |= adj[i]                                    # u_i ~ u_j
        for j in range(n):
            if adj[i] >> j & 1:
                a[n + i] |= 1 << j                        # v_i ~ u_j
                a[j] |= 1 << (n + i)
        a[2 * n] |= 1 << (n + i)                          # w ~ v_i
        a[n + i] |= 1 << (2 * n)
    return m, a


def edge_list(n, adj):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if adj[i] >> j & 1]


def triangle_free(n, adj):
    for i, j in edge_list(n, adj):
        if adj[i] & adj[j]:
            return False
    return True


def mono(E, S):
    return sum(1 for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))


def bip(n, adj):
    E = edge_list(n, adj)
    best = len(E)
    for S in range(1 << (n - 1)):
        m = mono(E, S << 1)
        if m < best:
            best = m
    return best


def neighbourhood_union_cuts(n, adj):
    """the union-closure of {N(v)} : all sets of the form union_{v in I} N(v)"""
    seen = {0}
    frontier = [0]
    while frontier:
        nf = []
        for S in frontier:
            for v in range(n):
                T = S | adj[v]
                if T not in seen:
                    seen.add(T)
                    nf.append(T)
        frontier = nf
    return seen


def fam(n, adj):
    E = edge_list(n, adj)
    best = (len(E), None)
    for S in neighbourhood_union_cuts(n, adj):
        m = mono(E, S)
        if m < best[0]:
            best = (m, S)
    return best


def report(name, n, adj, do_bip=True):
    E = edge_list(n, adj)
    tf = triangle_free(n, adj)
    f, S = fam(n, adj)
    b = bip(n, adj) if do_bip else None
    tgt = Fraction(n * n, 25)
    fails = 25 * f > n * n
    print(f"{name:22s} n={n:3d} |E|={len(E):3d} tri-free={tf}  "
          f"bip={b if b is not None else '-':>4}  fam={f:4d}  n^2/25={str(tgt):>9} = {float(tgt):8.4f}  "
          f"family FAILS 1/25: {fails}"
          + (f"   excess = {Fraction(f, n*n) - Fraction(1,25)}" if fails else ""))
    return b, f


if __name__ == "__main__":
    print("=== Mycielski tower over odd cycles ===")
    for k in [5, 7, 9, 11, 13]:
        n0, a0 = cycle(k)
        n1, a1 = mycielski(n0, a0)
        report(f"M(C{k})", n1, a1, do_bip=(n1 <= 21))
    print()
    print("=== odd cycles themselves (calibration) ===")
    for k in [5, 7, 9, 11]:
        n0, a0 = cycle(k)
        report(f"C{k}", n0, a0)
    print()
    print("=== second Mycielskian M(M(C5)) = M(Grotzsch), 23 vertices (fam only) ===")
    n0, a0 = cycle(5)
    n1, a1 = mycielski(n0, a0)
    n2, a2 = mycielski(n1, a1)
    report("M(M(C5))", n2, a2, do_bip=False)
