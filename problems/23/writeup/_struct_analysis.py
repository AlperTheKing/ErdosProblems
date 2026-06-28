"""Structural analysis of the ROWSUM-O witness K??CE@A{?]Fc (N=12) and other band-bad N=12 graphs.
For each gamma-min cut: compute per-bad-edge geometry, p_f(v), S(v), layer loads A_i, ROWSUM(f),
the band budget bound, and DECOMPOSE ROWSUM(f) = sum_g <p_f,p_g> into per-other-edge contributions
to see WHERE the overlap lives (which g's contribute, how much, and whether there is cancellation
between the inner band and the outer band that the per-band budget bound cannot see)."""
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn
from _stark1 import gmins
from _satzmu_conn import struct_for_side

def analyze_cut(n, adj, s, label=""):
    st = struct_for_side(n, adj, s)
    if st is None: return None
    M, ell, T, mu, cyc = st
    # p_f(v)
    pf = {}
    S = [F(0)]*n
    for g in M:
        Ps = cyc[g]; k = len(Ps); d = {}
        for P in Ps:
            for v in P: d[v] = d.get(v, F(0)) + F(1, k)
        pf[g] = d
        for v, pv in d.items(): S[v] += pv
    # S(v) == T(v)?  (T already = sum_g p_g(v) by construction in struct)
    rows = []
    for f in M:
        L = ell[f]; d = pf[f]
        # layer index along f's geodesic
        Ps = cyc[f]; layer = {}
        for P in Ps:
            for i, v in enumerate(P): layer[v] = i
        A = [F(0)]*L
        for v, pv in d.items(): A[layer[v]] += pv*S[v]
        ROW = sum(A)
        # decompose ROW = sum_g <p_f,p_g>
        contrib = {}
        for g in M:
            dg = pf[g]
            c = sum(pv*dg.get(v, F(0)) for v, pv in d.items())
            contrib[g] = c
        rows.append(dict(f=f, L=L, A=A, ROW=ROW, contrib=contrib, layer=layer, pf=d))
    return dict(M=M, ell=ell, T=T, S=S, pf=pf, rows=rows)

def report(g6, focus_only_worst=True):
    n, E = dec(g6)
    adj = [set() for _ in range(n)]
    for x, y in E: adj[x].add(y); adj[y].add(x)
    adj2, cuts = gmins(n, E)
    print(f"\n===== {g6} N={n} |E|={len(E)} cuts={len(cuts)} =====")
    # find the cut with the maximum ROWSUM
    best = None
    for ci, s in enumerate(cuts):
        a = analyze_cut(n, adj2, s)
        if a is None: continue
        mx = max(r['ROW'] for r in a['rows'])
        if best is None or mx > best[0]: best = (mx, ci, s, a)
    mx, ci, s, a = best
    print(f"worst ROWSUM = {mx} = {float(mx):.4f} at cut {ci} side={''.join(map(str,s))}  margin N-max = {F(n)-mx}")
    print(f"S(v) = T(v): {[str(x) for x in a['S']]}")
    M = a['M']
    print(f"bad edges M = {M}, ell = {[a['ell'][f] for f in M]}")
    for r in a['rows']:
        f = r['f']; L = r['L']
        print(f"\n  edge f={f} L={L} ROWSUM={r['ROW']}={float(r['ROW']):.4f}")
        print(f"    layer loads A_i = {[str(x) for x in r['A']]}  (sum={sum(r['A'])})")
        # band budget: outer t layers from each end vs 2t*N/L
        m = (L-1)//2
        for t in range(1, m+1):
            outer = sum(r['A'][i] for i in range(t)) + sum(r['A'][i] for i in range(L-t, L))
            budget = F(2*t*n, L)
            print(f"    band t={t}: outer-load={outer}={float(outer):.4f}  budget 2tN/L={budget}={float(budget):.4f}  slack={float(budget-outer):.4f}")
        # decompose contributions
        cs = sorted(r['contrib'].items(), key=lambda kv: -kv[1])
        print(f"    ROW = sum_g <p_f,p_g>:")
        for g, c in cs:
            tag = " (self)" if g == f else ""
            print(f"       g={g}: {c}={float(c):.4f}{tag}")

if __name__ == "__main__":
    report("K??CE@A{?]Fc")
