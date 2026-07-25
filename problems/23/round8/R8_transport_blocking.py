"""Exact minimum blocking family of induced C5s (bitmask version, fast).

If NO cut of H is optimal on every induced C5, we quantify how badly the
multiplicative certificate fails:  find the minimum number r of induced C5s
C_1..C_r such that every cut S has k_S(C_j) >= 3 for at least one j.  Then for
every probability distribution lambda over cuts,

    max_x prod_S nu_S(x)^{lambda_S}  >=  max_j (1/25) prod_S k_S(C_j)^{lambda_S}
                                     >=  (1/25) ( prod_j prod_S k_S(C_j)^{lambda_S} )^{1/r}
                                     =   (1/25) prod_S ( prod_j k_S(C_j) )^{lambda_S / r}
                                     >=  (1/25) * 3^{1/r} .
"""
import sys
from itertools import combinations

sys.path.insert(0, ".")
from R8_transport_lib import *   # noqa


def induced_c5s(G):
    out = []
    for verts in combinations(range(G.n), 5):
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
        if all(d == 2 for d in deg.values()):
            out.append((verts, e))
    return out


def run(G):
    cyc = induced_c5s(G)
    cuts = list(G.all_cuts())
    ncut = len(cuts)
    full = (1 << ncut) - 1
    cover = []          # cover[j] = bitmask of cuts S with k_S(C_j) >= 3
    perfect = full
    for (verts, es) in cyc:
        m = 0
        for idx, S in enumerate(cuts):
            k = sum(1 for u, v in es if ((S >> u) & 1) == ((S >> v) & 1))
            if k != 1:
                m |= 1 << idx
        cover.append(m)
        perfect &= ~m
    npf = bin(perfect).count("1")
    print("%-14s n=%2d |E|=%3d bip=%d  #indC5=%3d  #C5-perfect cuts=%d"
          % (G.name, G.n, G.m, G.bip(), len(cyc), npf), flush=True)
    if npf:
        return
    order = sorted(range(len(cyc)), key=lambda j: -bin(cover[j]).count("1"))
    for r in range(1, 6):
        for combo in combinations(order, r):
            u = 0
            for j in combo:
                u |= cover[j]
            if u == full:
                print("    minimum blocking family r=%d : %s" %
                      (r, [cyc[j][0] for j in combo]), flush=True)
                print("    ==> every lambda:  max_x prod nu_S^lambda >= 3^(1/%d)/25 = %.6f  (> 1/25 = 0.04)"
                      % (r, 3 ** (1.0 / r) / 25), flush=True)
                return
        print("    no blocking family of size %d" % r, flush=True)


if __name__ == "__main__":
    for G in [andrasfai(4), andrasfai(5), from_g6("M?AE@bH{AYN_LgBs?", "N14extremal")]:
        run(G)
