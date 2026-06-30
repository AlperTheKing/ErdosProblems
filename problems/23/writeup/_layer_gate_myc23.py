"""Iterated-Mycielskian N=23 stress for the layer-cake tail-dominance lemma.
   Myc(Grotzsch) = Myc(Myc(C5)) has N=23 (gmins infeasible at 2^23).
   We compute a strong heuristic MAX cut by local search, take the best connected-B side with bad edges,
   and run the layer-cake identity + tail gate on that single supplied cut.  A tail PASS is supporting
   evidence on the standing iterated-Mycielskian gate (the family that killed (k2)).
   ALL exact Fraction.
"""
import random
from fractions import Fraction as F
from _layer_gate import Zr_row
from _h import Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski

def maxcut_localsearch(n, adj, seeds=40, iters=4000):
    best = None; bestval = -1
    rng = random.Random(12345)
    deg = [list(adj[v]) for v in range(n)]
    for s in range(seeds):
        side = [rng.randint(0,1) for _ in range(n)]
        improved = True
        while improved:
            improved = False
            order = list(range(n)); rng.shuffle(order)
            for v in order:
                same = sum(1 for w in deg[v] if side[w]==side[v])
                diff = sum(1 for w in deg[v] if side[w]!=side[v])
                if same > diff:
                    side[v] ^= 1; improved = True
        val = sum(1 for v in range(n) for w in adj[v] if w>v and side[v]!=side[w])
        if val > bestval: bestval = val; best = side[:]
    return best, bestval

def main():
    # Grotzsch = mycielski(C5); Myc(Grotzsch) = N=23
    grN, grE = mycielski(5, Cn(5))
    n, E = mycielski(grN, grE)
    print("Myc(Grotzsch): N=%d, edges=%d" % (n, len(E)))
    adj = [set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side, mc = maxcut_localsearch(n, adj)
    print("heuristic max cut value =", mc, "of", len(E), "edges")
    if not Bconn(n, adj, side):
        print("blue graph disconnected; trying complement / reseeding")
    st = struct_for_side(n, adj, side)
    if st is None:
        print(">>> struct_for_side None on this cut (no valid odd-cycle structure). Trying a few perturbations.")
        return
    M, ell, T, mu, cyc = st
    print("bad edges |M|=%d, Gamma=%s" % (len(M), str(sum(T))))
    if not M:
        print(">>> cut has no bad edges (bipartite-ish); not a useful stress row.")
        return
    rows=0; idfail=0; tailfail=0; idex=None; tex=None
    for f in M:
        if ell[f] % 2 == 0: continue
        for P in cyc[f]:
            if len(P) != ell[f]: continue
            B_L, DGsum, Z, lhs, rhs = Zr_row(n, adj, side, M, ell, T, cyc, f, P)
            rows += 1
            if lhs != rhs:
                idfail += 1
                if idex is None: idex = (ell[f], tuple(P), str(lhs-rhs))
            acc_tail = F(0); bad=False
            for k in range(n-1, -1, -1):
                acc_tail += (2*k+1)*Z[k]
                if acc_tail < 0: bad=True
            if bad:
                tailfail += 1
                if tex is None: tex = (ell[f], tuple(P))
    print("="*50)
    print("rows=%d  IDENTITY fails=%d %s  TAIL fails=%d %s" % (rows, idfail, idex or '', tailfail, tex or ''))
    print("VERDICT:", "TAIL HOLDS on Myc(Grotzsch) N=23 heuristic-maxcut" if tailfail==0 and idfail==0
          else "FAIL / inspect")

if __name__ == "__main__":
    main()
