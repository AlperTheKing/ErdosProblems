"""R9: exact certificates for the SRG witnesses.

(1) Lambda = m/5 EXACTLY for every triangle-free graph in which every edge lies in the
    same number p of 5-cycles:
      cover   y == 1/5           feasible (odd girth 5)          cost m/5
      packing z_C == 1/p on the 5-cycles   load(e) = p/p = 1 <= 1  value #C5/p = m/5
    Two-sided, so Lambda = m/5 with no symmetry or automorphism input at all.
(2) bip is then pinned exactly between the spectral lower bound and an explicit cut.
(3) Guenin (contrapositive): gap > 1  =>  the graph HAS an odd-K5 minor.  No minor
    search needed; the LP gap itself certifies membership in the complement class.
"""
from fractions import Fraction as F
from R9_oddk5_lib import G, bip, odd_girth, maxcut_local, cut_value
import R9_oddk5_srg as S

def c5_per_edge(g):
    """for every edge, the number of 5-cycles through it (exact integers, bitset counting)"""
    n = g.n
    nb = [0] * n
    for (a, b) in g.E:
        nb[a] |= 1 << b
        nb[b] |= 1 << a
    cnt = {}
    for (u, v) in g.E:
        c = 0
        for x in g.adj[u]:
            if x == v:
                continue
            for z in g.adj[v]:
                if z == u or z == x:
                    continue
                mid = nb[x] & nb[z] & ~((1 << u) | (1 << v))
                c += bin(mid).count('1')
        cnt[(u, v)] = c
    return cnt

def certify(name, g, ls_iters=200, seed=11):
    par = S.srg_params(g)
    lmin = S.lambda_min_exact(par) if par else None
    m, n = g.m, g.n
    og = odd_girth(g)
    cnt = c5_per_edge(g)
    vals = set(cnt.values())
    uniform = (len(vals) == 1)
    p = next(iter(vals)) if uniform else None
    nC5 = sum(cnt.values()) // 5
    lam = F(m, 5) if (uniform and og == 5 and p > 0) else None
    lb = F(m, 2) + F(n * lmin, 4) if lmin is not None else None
    lb_int = -((-lb.numerator) // lb.denominator) if lb is not None else None
    cut, side = maxcut_local(g, iters=ls_iters, seed=seed)
    assert cut == cut_value(g, side)
    ub = m - cut
    exact_bip = lb_int if (lb_int is not None and lb_int == ub) else None
    print(f"{name:18s} n={n:4d} m={m:5d} oddgirth={og} 5-cycles/edge "
          f"{'==' + str(p) if uniform else str(sorted(vals))}  #C5={nC5}")
    if lam is not None:
        print(f"    Lambda = {lam} EXACT  (cover y=1/5 cost {lam}; packing z=1/{p} on {nC5} "
              f"pentagons, value {F(nC5,p)})")
        assert F(nC5, p) == lam
    print(f"    bip in [{lb_int}, {ub}]" + (f"  => bip = {exact_bip} EXACT" if exact_bip else ""))
    if lam and exact_bip:
        g_ratio = F(exact_bip) / lam
        print(f"    psi/Lambda = {g_ratio} = {float(g_ratio):.6f}   "
              f"{'=> odd-K5 minor EXISTS (Guenin, contrapositive)' if g_ratio > 1 else ''}")
        print(f"    psi(uniform) = {F(exact_bip, n*n)} = {float(F(exact_bip,n*n)):.6f} "
              f"vs 1/25 = 0.04  ->  {'below' if F(exact_bip,n*n) < F(1,25) else 'ABOVE!!'}")
        return g_ratio
    elif lam:
        print(f"    psi/Lambda in [{F(lb_int)/lam}, {F(ub)/lam}]")
    return None

if __name__ == "__main__":
    print("=" * 92)
    print("EXACT Lambda and bip for the triangle-free strongly regular graphs")
    print("=" * 92)
    ratios = {}
    for nm, g in [("Petersen", S.petersen()), ("Clebsch", S.clebsch()),
                  ("Hoffman-Singleton", S.hoffman_singleton()), ("Gewirtz", S.gewirtz()),
                  ("M22", S.m22_graph()), ("Higman-Sims", S.higman_sims())]:
        r = certify(nm, g)
        if r:
            ratios[nm] = r
        print()
    print("exact ratios:", {k: str(v) for k, v in ratios.items()})
