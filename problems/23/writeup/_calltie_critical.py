"""Test: in any (hypothetical) Q-only K-component C containing a saturated vertex, is C forced critical (T==N)?
Since no Q-only nontrivial K-comp occurs in real graphs, we test the structural IMPLICATION on the
single load-bearing component restricted to Q (drop O and see what happens) -- and more usefully,
we test the KEY deficit inequality that a DIRECT proof would need:

For the load-bearing K-component L (which contains O in real graphs), compute:
   deficit_Q(L) := sum_{w in L, w in Q} (N - T(w))   [total underload in L\O]
   overload(L)  := sum_{o in L cap O} (T(o) - N)      [total overload in L]
and check the MASS BALANCE:  sum_{w in L} T(w) = Gamma_L, with Gamma_L = sum_{f: supp in L} ell^2.

The transport claim a direct C-alltie proof rests on:
   A saturated v (charge 0) cannot be 'surrounded' only by Q -- its K-mass N must be balanced,
   and the ONLY sink for the eigen-imbalance is O.  Quantify: leak(v) = sum_{o in O} K[v,o].
   Is leak(v) > 0 for the saturated v with dead nb?  (If yes for ALL, that's a DIRECT lever:
   saturated v with dead nb has positive K-mass directly to O.)

Also test STRONGER: does v have a bad edge f through it with the OTHER endpoint in O, OR
   K[v,o]>0 for some o in O (1-step K-adjacency to O)?
Exact Fraction, census N=11 all gamma-min cuts.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, geos
from _satzmu_conn import struct_for_side, kcomponents

def all_gmin(n, E):
    adj = [set() for _ in range(n)]
    for x, y in E: adj[x].add(y); adj[y].add(x)
    cuts = maxcut_all(n, adj); cand = []
    for side in cuts:
        if not Bconn(n, adj, side): continue
        Mloc = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        if not Mloc: continue
        G = 0; ok = True
        for (u, v) in Mloc:
            d = bdist_restr(adj, side, u, v)
            if d < 0: ok = False; break
            G += (d+1)**2
        if ok: cand.append((side, G))
    if not cand: return adj, []
    gm = min(G for _, G in cand)
    return adj, [s for s, G in cand if G == gm]

def buildK(n, side, adj, cyc):
    # exact p_f and K
    K = [[F(0)]*n for _ in range(n)]
    for f, Ps in cyc.items():
        nf = len(Ps); ellf = len(Ps[0])
        pf = [F(0)]*n
        for P in Ps:
            for v in P: pf[v] += F(ellf, nf) / ellf  # p_f(v) = (#geodesics through v)/nf
        # Actually p_f(v) = (# shortest paths through v)/(total #), independent of ell.
        # recompute properly:
        cnt = [0]*n
        for P in Ps:
            for v in P: cnt[v] += 1
        pf = [F(cnt[v], nf) for v in range(n)]
        for a in range(n):
            if pf[a] == 0: continue
            for b in range(n):
                if pf[b] == 0: continue
                K[a][b] += pf[a]*pf[b]
    return K

def cases(n, E):
    adj, sides = all_gmin(n, E)
    res = []
    for side in sides:
        st = struct_for_side(n, adj, side)
        if st is None: continue
        M, ell, T, mu, cyc = st
        N = n
        O = set(v for v in range(N) if T[v] > N)
        if not O: continue
        comp, find = kcomponents(n, cyc)
        K = buildK(n, side, adj, cyc)
        for v in range(N):
            if T[v] != N: continue
            deadnb = [z for z in adj[v] if side[z] != side[v] and T[z] == 0]
            if not deadnb: continue
            leak = sum(K[v][o] for o in O)               # K-mass from v directly to O
            kadjO = [o for o in O if K[v][o] > 0]         # 1-step K-adjacency to O
            badedge_to_O = [f for f in M if v in f and (f[0] in O or f[1] in O)]
            res.append(dict(v=v, leak=leak, kadjO=kadjO, badedge_to_O=badedge_to_O, O=sorted(O)))
    return res

def run():
    total = 0; leak_pos = 0; kadj1 = 0; minleak = None
    for nn in (11,):
        og = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in og:
            n, E = dec(g6)
            for c in cases(n, E):
                total += 1
                if c['leak'] > 0:
                    leak_pos += 1
                    if minleak is None or c['leak'] < minleak: minleak = c['leak']
                if c['kadjO']: kadj1 += 1
    print(f"  N=11 all gamma-min: cases={total}")
    print(f"    leak(v)=sum_o K[v,o] > 0  : {leak_pos}/{total}  (minleak={float(minleak) if minleak else 'NA'})")
    print(f"    v K-adjacent to O (1 step): {kadj1}/{total}")
    print(f"  => DIRECT lever 'saturated v w/ dead nb has positive K-mass to O' holds for ALL? {leak_pos==total}")

if __name__ == "__main__":
    print("=== Does a saturated v with dead nb have DIRECT K-leak to O? ===")
    run()
