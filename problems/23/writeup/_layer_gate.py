"""GPT-Pro LAYER-CAKE gate (route A, analytic).  Exact identity:
     B_L(P) - DG(x_0) - DG(x_{L-1}) = sum_{r=0}^{N-1} (2r+1) * Z_r(P),
   Z_r(P) = L*(1-m_r) + 25*(L-a_r(P))/(2r+1) - chi_P(r) - delta_P*1_{r<L}.
   m_r = #{bad g: L_g>r};  a_r = sum_{g:L_g>r} a_g(P), a_g(P)=sum_i p_g(x_i), p_g(v)=through-frac;
   delta_P = (S/L)^2 - q;  chi_P(r)=chi_{x0}(r)+chi_{xL-1}(r) layer profile of the DG closed form
   (0 if that endpoint flip is non-neutral / disconnecting).
   PORT-LAYER DOMINANCE LEMMA candidates:  (1) pointwise Z_r>=0;  (2) tail sum_{r>=k}(2r+1)Z_r>=0;
   (3) interval sum_{a..b}(2r+1)Z_r>=0.  On DG=0 rows (99.76%) chi_P=0 so this DIRECTLY decomposes B_L.
   ALL exact Fraction.  Verifies the identity first (sanity), then gates dominance.
"""
import subprocess, sys
from collections import deque
from fractions import Fraction as F
from _dgamma_formula import bfs_H, Dport
from _wf_deficit_farkas import deltas, flip, gamma_of, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint
INF = 10**9

def chi_profile(n, adj, side, v, M, Nlayers):
    """Layer profile chi_v(r), r=0..Nlayers-1, of the DG closed form. Returns None if flip invalid
       (-> caller treats chi=0). Only valid for neutral+connected flips."""
    s2 = flip(side, [v])
    if not Bconn(n, adj, s2): return None
    dB, dM = deltas(n, adj, side, {v})
    if dB != dM: return None
    g1 = gamma_of(n, adj, s2)
    if g1 is None: return None
    A = [w for w in adj[v] if side[w] != side[v]]
    C = [w for w in adj[v] if side[w] == side[v]]
    need = set(A) | set(C)
    for e in M: need.add(e[0]); need.add(e[1])
    distfrom = {s: bfs_H(n, adj, side, v, s) for s in need}
    chi = [0]*Nlayers
    def add(thresh, sign):
        # contributes sign at layers r < thresh
        t = min(thresh, Nlayers)
        for r in range(t): chi[r] += sign
    ok = True
    for (x, y) in M:
        if x == v or y == v: continue
        DC = Dport(x, y, distfrom, C); DA = Dport(x, y, distfrom, A)
        if DC >= INF or DA >= INF: return None
        add(DC+1, +1); add(DA+1, -1)
    for a in A:
        mn = min((distfrom[c][a] for c in C), default=INF)
        if mn >= INF: return None
        add(2+mn, +1)
    for c in C:
        mn = min((distfrom[a][c] for a in A), default=INF)
        if mn >= INF: return None
        add(2+mn, -1)
    # sanity: sum (2r+1) chi == g1 - Gamma
    return chi, g1

def Zr_row(n, adj, side, M, ell, T, cyc, f, P):
    L = ell[f]; N = F(n); Gamma = sum(T)
    x = P
    # p_g, a_g, m_r, a_r
    pg = {}
    for g in M:
        Q = cyc[g]; cnt = {}
        for path in Q:
            for vtx in path: cnt[vtx] = cnt.get(vtx, 0)+1
        k = len(Q)
        pg[g] = {vtx: F(cnt[vtx], k) for vtx in cnt}
    def p(g, v): return pg[g].get(v, F(0))
    a_g = {g: sum(p(g, x[i]) for i in range(L)) for g in M}
    Lg = {g: ell[g] for g in M}
    m = [0]*n; a = [F(0)]*n
    for r in range(n):
        for g in M:
            if Lg[g] > r:
                m[r] += 1; a[r] += a_g[g]
    # delta_P
    h = [T[x[i]]/N for i in range(L)]; S = sum(h); q = min(h[i]*h[(i+1) % L] for i in range(L))
    deltaP = (S/L)**2 - q
    # chi profile of endpoints
    chiP = [0]*n
    DGsum = F(0)
    for end in (x[0], x[-1]):
        res = chi_profile(n, adj, side, end, M, n)
        if res is not None:
            chi, g1 = res
            for r in range(n): chiP[r] += chi[r]
            DGsum += (g1 - Gamma)
    # Z_r
    Z = []
    for r in range(n):
        zr = L*(1-m[r]) + F(25*(L-a[r]), 2*r+1) - chiP[r] - (deltaP if r < L else F(0))
        Z.append(zr)
    # B_L and identity check
    C_L = S*S - (L*L)*q
    B_L = L*(N*N-Gamma) - 25*sum(T[x[i]]-N for i in range(L)) - C_L
    lhs = B_L - DGsum
    rhs = sum((2*r+1)*Z[r] for r in range(n))
    return B_L, DGsum, Z, lhs, rhs

def gate(name, n, E, acc):
    adj, cuts = gmins(n, E)
    for side in cuts:
        st = struct_for_side(n, adj, side)
        if st is None: continue
        M, ell, T, cyc = st[0], st[1], st[2], st[4]
        for f in M:
            if ell[f] % 2 == 0: continue
            for P in cyc[f]:
                if len(P) != ell[f]: continue
                B_L, DGsum, Z, lhs, rhs = Zr_row(n, adj, side, M, ell, T, cyc, f, P)
                acc['rows'] += 1
                if lhs != rhs:
                    acc['idfail'] += 1
                    if acc['idex'] is None: acc['idex'] = (name, n, ell[f], tuple(P), str(lhs-rhs))
                # pointwise
                neg = [r for r in range(n) if Z[r] < 0]
                if neg:
                    acc['ptfail'] += 1
                    if acc['ptex'] is None:
                        acc['ptex'] = (name, n, ell[f], tuple(P), neg[:3], [str(Z[r]) for r in neg[:3]])
                # tail
                tailbad = False
                acc_tail = F(0)
                for k in range(n-1, -1, -1):
                    acc_tail += (2*k+1)*Z[k]
                    if acc_tail < 0: tailbad = True
                if tailbad:
                    acc['tailfail'] += 1
                    if acc['tailex'] is None: acc['tailex'] = (name, n, ell[f], tuple(P))

def main():
    acc = dict(rows=0, idfail=0, ptfail=0, tailfail=0, idex=None, ptex=None, tailex=None)
    for nn in range(5, 10):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gate("cen%d" % nn, n, E, acc)
        print("census N=%d done: rows=%d idfail=%d ptfail=%d tailfail=%d"
              % (nn, acc['rows'], acc['idfail'], acc['ptfail'], acc['tailfail']), flush=True)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2),(1,1,1,1,1)]:
        n, E = odd_blowup(5, list(sizes)); gate("C5%s" % (sizes,), n, E, acc)
    n5, E5 = 5, Cn(5); n7, E7 = 7, Cn(7); n, E = union_disjoint((n5, E5), (n7, E7)); E = E+[(0, n5)]
    gate("glue_C5|C7", n, E, acc)
    n, E = dec("H?AFBo]"); gate("thw-H", n, E, acc)
    print("="*60)
    print("rows:", acc['rows'])
    print("IDENTITY fails:", acc['idfail'], acc['idex'])
    print("POINTWISE Z_r>=0 fails:", acc['ptfail'], acc['ptex'])
    print("TAIL sum_{r>=k}(2r+1)Z_r>=0 fails:", acc['tailfail'], acc['tailex'])

if __name__ == "__main__":
    main()
