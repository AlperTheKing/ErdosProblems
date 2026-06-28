"""The CORRIDOR / overlap structure. For a single-geodesic edge f with vertex set V_f (|V_f|=ell(f)),
   ROWSUM(f) = sum_{v in V_f} S(v) = sum_{v in V_f} sum_g p_g(v) = sum_g |overlap of g with V_f| (weighted).
   = sum_g sum_{v in V_f} p_g(v) = sum_g <1_{V_f}, p_g>.
So ROWSUM(f) = sum_g (geodesic-mass of g landing inside f's vertex set).
For g=f this is ell(f). For g != f it is the f-V_f-mass of g.

CANDIDATE GLOBAL INVARIANT (the band misses):  for EVERY bad edge f and EVERY other bad edge g,
   <1_{V_f}, p_g>  +  <1_{V_g}, p_f>  <=  ell intersection budget.
The band charges each layer of f independently to N/ell; but the truth is that g's mass inside V_f is
'paid for' by V_f intersect V_g being a SHARED geodesic segment, and a shared segment of length L means
g and f run parallel => the two endpoints are close => contributes to BOTH but only counts once toward N.

EXACT-TESTABLE CONJECTURE (call it OVERLAP-N):
   For every bad edge f:  sum_g <1_{V_f}, p_g>  <=  N.
   Equivalently  sum_{v in V_f} S(v) <= N   when f is single-geodesic; for multi-geodesic f,
   ROWSUM(f) = sum_v p_f(v) S(v) <= sum_{v: p_f(v)>0} S(v) (drop p_f(v)<=1), call this UB(f).
   TEST whether UB(f) = sum over support of f of S(v) <= N. If UB <= N holds, that's a CLEAN bound
   STRONGER than ROWSUM-O (implies it), purely about the SUPPORT of f and the load there.
This is the key: does dropping p_f(v)->1 (i.e. taking the whole geodesic INTERVAL support) still stay <=N?"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
from _satzmu_conn import struct_for_side

def cut_S(n, adj, s):
    st = struct_for_side(n, adj, s)
    if st is None: return None
    M, ell, T, mu, cyc = st
    pf = {}; S = [F(0)]*n
    for g in M:
        Ps = cyc[g]; k = len(Ps); d = {}
        for P in Ps:
            for v in P: d[v] = d.get(v,F(0))+F(1,k)
        pf[g] = d
        for v,pv in d.items(): S[v] += pv
    return M, ell, S, pf, cyc

def check(g6, verbose=False):
    n, E = dec(g6)
    adj = [set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    adj2, cuts = gmins(n, E)
    worst_UB = None; worst_ROW = None; ub_fails = False
    for ci, s in enumerate(cuts):
        r = cut_S(n, adj2, s)
        if r is None: continue
        M, ell, S, pf, cyc = r
        for f in M:
            supp = set(pf[f].keys())   # geodesic-interval support of f
            UB = sum(S[v] for v in supp)
            ROW = sum(pv*S[v] for v,pv in pf[f].items())
            if UB > n: ub_fails = True
            if worst_UB is None or UB > worst_UB[0]: worst_UB = (UB, ci, f, len(supp))
            if worst_ROW is None or ROW > worst_ROW[0]: worst_ROW = (ROW, ci, f)
            if verbose and UB > n:
                print(f"   UB FAIL {g6} cut{ci} f={f}: UB={UB}={float(UB):.3f} > N={n}  (supp size {len(supp)})")
    return n, worst_UB, worst_ROW, ub_fails

if __name__ == "__main__":
    print("=== OVERLAP-N test: UB(f)=sum_{v in supp(f)} S(v) <= N ?  (stronger than ROWSUM-O) ===")
    n, wUB, wROW, fail = check("K??CE@A{?]Fc", verbose=True)
    print(f"witness K??CE@A{{?]Fc: N={n} worstUB={wUB} worstROW={float(wROW[0]):.3f} UB_fails={fail}")
    # census N<=12 full scan of UB-bound vs ROWSUM
    for nn in range(5,13):
        out = subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ub_fail_graphs = 0; row_fail_graphs = 0; first_ubfail=None
        worst_ub_margin = None
        for g6 in out:
            n,wUB,wROW,fail = check(g6)
            if wUB is None: continue
            if fail:
                ub_fail_graphs += 1
                if first_ubfail is None: first_ubfail=(g6,float(wUB[0]),wUB[3],n)
            if wROW[0] > n: row_fail_graphs += 1
            m = F(n)-wUB[0]
            if worst_ub_margin is None or m < worst_ub_margin: worst_ub_margin = m
        print(f"  census N={nn}: UB>N graphs={ub_fail_graphs}  ROWSUM>N graphs={row_fail_graphs}  worst UB-margin(N-UB)={worst_ub_margin}={float(worst_ub_margin):.3f}"+(f"  firstUBfail={first_ubfail}" if first_ubfail else ""), flush=True)
