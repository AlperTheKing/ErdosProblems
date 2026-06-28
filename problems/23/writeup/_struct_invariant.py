"""Hunt the GLOBAL invariant. Identities (all exact-tested):
  sum_v S(v) = sum_f ell(f)         [since S = sum_f p_f, ||p_f||_1 = ell(f)]
  sum_f ROWSUM(f) = sum_v S(v)^2    [= 1^T O 1 = ||S||_2^2]
  ROWSUM(f) = <p_f, S> = sum_v p_f(v) S(v).
Per-edge: since 0<=p_f(v)<=1 and sum_v p_f(v)=ell(f),
  <p_f,S> <= (max over choices of ell(f) vertices) of sum S(v) restricted to f's geodesic-interval support.
The CRUCIAL local-vs-global gap: band budget bounds S(v) <= N/ell on a per-vertex basis, but that's FALSE
(some vertex overloads). The global truth must be that the SUM over f's support of S(v)*p_f(v) <= N because
high-S vertices are exactly the ones SHARED by many edges, and being shared means p_f(v)<1 there (the
geodesic load is split among the many g's that pass through v).

CONJECTURE TO TEST (the 'shared vertices are diluted' invariant):
  (DIL) For every bad edge f:  sum_v p_f(v) * S(v)  <=  sum_v p_f(v) * (ell(f) + deg_load(v))   ... vague.
Better, test these CLEAN candidate global inequalities EXACTLY:
  (C-A) <p_f,S> <= ell(f) + <p_f, S - p_f> and bound cross by:  for each v on f, S(v)-p_f(v) = load from OTHER edges.
        The vertices with big S(v) carry big OTHER load => those other edges g 'use up' budget at v.
  (C-B) KEY: sum_v p_f(v)*S(v) <= N  <=>  sum_v p_f(v)*S(v) <= sum_v S(v)/ell-ish? test ratio.
  (C-C) Cauchy-Schwarz-free: <p_f,S> <= sqrt(<p_f,p_f>) * sqrt(<S,S>)? too weak. test.
  (C-D) the WINNER candidate: <p_f,S> <= max_v S(v) * ell(f)? test margin.
  (C-E) <p_f,S> <= sum over LAYERS i of f of (layer-i total geodesic mass), where layer total <= N/ell.
We compute all these and report which (if any) is a TIGHT certificate (holds with the right margin)."""
from fractions import Fraction as F
from _h import dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side

def cut_data(n, adj, s):
    st = struct_for_side(n, adj, s)
    if st is None: return None
    M, ell, T, mu, cyc = st
    pf = {}; S = [F(0)]*n
    for g in M:
        Ps = cyc[g]; k = len(Ps); d = {}
        for P in Ps:
            for v in P: d[v] = d.get(v, F(0)) + F(1, k)
        pf[g] = d
        for v, pv in d.items(): S[v] += pv
    return dict(M=M, ell=ell, S=S, pf=pf, cyc=cyc, n=n)

def analyze(g6):
    n, E = dec(g6)
    adj = [set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    adj2, cuts = gmins(n, E)
    res = []
    for ci, s in enumerate(cuts):
        cd = cut_data(n, adj2, s)
        if cd is None: continue
        M, ell, S, pf = cd['M'], cd['ell'], cd['S'], cd['pf']
        sumS = sum(S); sumSS = sum(x*x for x in S)
        maxS = max(S)
        for f in M:
            d = pf[f]; L = ell[f]
            ROW = sum(pv*S[v] for v,pv in d.items())
            # (C-D) maxS * ell
            cD = maxS*L
            # (C-E) layer totals: for each layer i (B-distance from f[0]), total geodesic mass arriving = sum over
            # ALL edges g of (mass of g at vertices in that layer's "column")? define by f's own layers:
            # layer total of S along f's geodesic support per layer i:
            layer = {}
            for P in cd['cyc'][f]:
                for i,v in enumerate(P): layer[v]=i
            A = [F(0)]*L
            for v,pv in d.items(): A[layer[v]] += pv*S[v]
            res.append(dict(g6=g6, ci=ci, f=f, L=L, ROW=ROW, maxS=maxS,
                            sumS=sumS, sumSS=sumSS, cD=cD, A=A, S=S, N=n))
    return res, n

def test_all(graphs):
    print(f"{'graph':>14} {'cut':>3} {'f':>9} {'ROW':>7} {'N':>3} {'maxS':>6} {'maxS*ell':>9} {'sumSS':>8}")
    worst_margin = None
    # check candidate global bounds across the board
    cD_holds = True; cD_tight = None
    for g in graphs:
        res, n = analyze(g)
        for r in res:
            tag = ""
            if r['ROW'] > r['N']: tag = " <<< ROWSUM-O VIOLATION"
            print(f"{r['g6']:>14} {r['ci']:>3} {str(r['f']):>9} {float(r['ROW']):>7.3f} {r['N']:>3} {float(r['maxS']):>6.3f} {float(r['cD']):>9.3f} {float(r['sumSS']):>8.2f}{tag}")
            if r['cD'] < r['ROW']: cD_holds = False  # C-D would be false as an upper bound
            m = F(r['N']) - r['ROW']
            if worst_margin is None or m < worst_margin: worst_margin = m
    print(f"\n(C-D) maxS*ell >= ROWSUM always? {cD_holds}")
    print(f"worst margin N - ROWSUM over all = {worst_margin}={float(worst_margin):.4f}")

if __name__ == "__main__":
    test_all(["K??CE@A{?]Fc"])
