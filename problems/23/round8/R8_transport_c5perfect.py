"""DECISIVE TEST for the multiplicative (geometric-mean / entropy) transport certificate.

Setting.  For a cut S write  nu_S(x) = sum over monochromatic uv of x_u x_v.
psi(H,x) = min_S nu_S(x).  Any distribution lambda over cuts gives the valid bound

        psi(H,x) <= prod_S nu_S(x)^{lambda_S}          (min <= weighted geometric mean)

and the certificate scheme asks for lambda with  max_{x in simplex} prod_S nu_S^{lambda_S} <= 1/25.
This is the *multiplicative* analogue of the (dead) arithmetic averaging family A6.

Necessary condition.  Let C be an induced C5 of H and x = uniform 1/5 on C, 0 elsewhere.
Then nu_S(x) = k_S(C)/25 where k_S(C) = # monochromatic edges of S inside C, an odd number >= 1.
So prod_S nu_S(x)^{lambda_S} = (1/25) * prod_S k_S(C)^{lambda_S} >= 1/25, with equality iff
k_S(C) = 1 for every S in the support of lambda.  Hence

    the certificate can succeed only if some cut S is simultaneously optimal
    on EVERY induced C5 of H  ("C5-perfect cut").

This script decides the existence of a C5-perfect cut exactly, by enumeration.
"""
from R8_transport_lib import *
from fractions import Fraction
from itertools import combinations


def induced_c5s(G):
    """all induced 5-cycles, as vertex tuples in cyclic order (each cycle once)."""
    out = []
    n = G.n
    for verts in combinations(range(n), 5):
        mask = 0
        for v in verts:
            mask |= 1 << v
        e = G.induced_edges(mask)
        if len(e) != 5:
            continue
        deg = {v: 0 for v in verts}
        for u, v in e:
            deg[u] += 1
            deg[v] += 1
        if any(d != 2 for d in deg.values()):
            continue
        # connected 2-regular on 5 vertices = C5
        out.append((verts, e))
    return out


def report(G):
    c5s = induced_c5s(G)
    perfect = []
    worst = None
    for S in G.all_cuts():
        ok = True
        mx = 0
        for verts, es in c5s:
            k = sum(1 for u, v in es if ((S >> u) & 1) == ((S >> v) & 1))
            mx = max(mx, k)
            if k != 1:
                ok = False
        if ok:
            perfect.append(S)
        if worst is None or mx < worst[0]:
            worst = (mx, S)
    print("%-16s N=%2d  #inducedC5=%4d  #C5-perfect cuts = %4d   best max_C k_S(C) = %d" %
          (G.name, G.n, len(c5s), len(perfect), worst[0] if c5s else 0))
    return c5s, perfect


if __name__ == "__main__":
    for G in testbed():
        report(G)
    print()
    for k in (2, 3, 4, 5):
        report(andrasfai(k))
