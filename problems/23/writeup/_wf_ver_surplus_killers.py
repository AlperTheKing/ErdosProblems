"""Report exact central-inequality margins on the named killer configs."""
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def margin_of(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    if not M:
        return None
    N = F(n); beta = len(M); Gamma = sum(F(ell[f])**2 for f in M)
    V2 = sum((t - N)**2 for t in T)
    TVcut = F(0); TVbad = F(0)
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            d = abs(T[u] - T[v])
            if side[u] != side[v]:
                TVcut += d
            else:
                TVbad += d
    rhs = Gamma * (F(n*n, 25) - beta)
    lhs = V2 + N*(Gamma - N*N) + F(n, 5)*(TVcut - TVbad)
    return dict(n=n, beta=beta, Gamma=Gamma, V2=V2, TVcut=TVcut, TVbad=TVbad,
                margin=rhs - lhs, rhs=rhs, lhs=lhs)

def adj_of(n, E):
    a = [set() for _ in range(n)]
    for x, y in E:
        a[x].add(y); a[y].add(x)
    return a

def bridge(b1, b2, u, v):
    nn, E = union_disjoint(b1, b2); n1 = b1[0]
    return nn, E + [(u, n1 + v)]

grot = mycielski(5, Cn(5)); mycg = mycielski(grot[0], grot[1])
named = [
    ("Myc(Grotzsch)N23", mycg),
    ("bridge(C7,Grotzsch)", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
    ("bridge(C9,C9)", bridge((9, Cn(9)), (9, Cn(9)), 0, 0)),
    ("M(C7)", mycielski(7, Cn(7))),
    ("M(C9)", mycielski(9, Cn(9))),
]
for nm, (nn, E) in named:
    adj, cuts = gmins(nn, E)
    best = None
    for s in cuts:
        r = margin_of(nn, adj, s)
        if r is None:
            continue
        if best is None or r['margin'] < best['margin']:
            best = r
    if best:
        print("%-22s N=%d beta=%d Gamma=%s V2=%s TVcut=%s TVbad=%s  margin=%s (>=0: %s)" % (
            nm, best['n'], best['beta'], best['Gamma'], best['V2'], best['TVcut'], best['TVbad'],
            best['margin'], best['margin'] >= 0))
    else:
        print("%-22s : no valid B-connected gamma-min cut with bad edge" % nm)

# k-lane breakers
for (Ll, k, gap) in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
    bad = greedy_chords(Ll, k, gap)
    n, E, side, bad = build_k_lane(Ll, k, bad)
    r = margin_of(n, adj_of(n, E), side)
    if r:
        print("klane-L%dk%-13s N=%d beta=%d Gamma=%s V2=%s  margin=%s (>=0: %s)" % (
            Ll, str(k), r['n'], r['beta'], r['Gamma'], r['V2'], r['margin'], r['margin'] >= 0))
