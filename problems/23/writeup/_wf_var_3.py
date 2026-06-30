"""Spectral/Gram analysis of FAN-AVERAGING variance inequality n(n-row_f)>=var_f for NONUNIQUE f.

Setup per (graph, gamma-min connected-B max cut, side):
  M = bad (monochromatic) edges; for g in M, cyc[g] = list of B-geodesics, ell[g]=#vertices/geodesic.
  p_g(v) = (# geodesics of g through v)/|cyc(g)|.  P[g,v]=p_g(v).
  ell_g = sum_v p_g(v) (=#vertices on a geodesic; all geodesics equal length).
  S(v) = sum_g p_g(v)   (column sum).
  row_f = sum_v p_f(v) S(v) = sum_g K_{fg},  K = P P^T  (K_{fg}=sum_v p_f(v)p_g(v)).
  var_f = sum_v p_f(v)(S(v)-row_f/ell_f)^2 = Q_f - row_f^2/ell_f,  Q_f = sum_v p_f(v) S(v)^2.
Target: n(n-row_f) >= var_f, i.e. n^2 - n row_f >= Q_f - row_f^2/ell_f.

We test several candidate sub-lemmas EXACTLY (Fraction) on the standing gate.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def build(n, adj, side):
    """Return (M, ell, cyc, P, S, K, Kdiag) or None.  P[g] = dict v->p_g(v)."""
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    P = {}
    S = [F(0)]*n
    for g in M:
        Ps = cyc[g]; k = len(Ps); d = {}
        for Ppath in Ps:
            for v in Ppath: d[v] = d.get(v, F(0)) + F(1, k)
        P[g] = d
        for v, pv in d.items(): S[v] += pv
    return M, ell, cyc, P, S

def rowstats(n, M, ell, cyc, P, S, f):
    d = P[f]
    ll = sum(d.values())                       # ell_f
    row = sum(d[v]*S[v] for v in d)
    Q = sum(d[v]*S[v]*S[v] for v in d)
    var = Q - row*row/ll
    return ll, row, Q, var

# ---- candidate sub-lemma evaluators (return tuples of exact quantities) ----

def analyze_side(n, adj, side, acc):
    b = build(n, adj, side)
    if b is None: return
    M, ell, cyc, P, S = b
    N = F(n)
    for f in M:
        if len(cyc[f]) < 2: continue          # NONUNIQUE only
        ll, row, Q, var = rowstats(n, M, ell, cyc, P, S, f)
        margin = N*(N-row) - var
        # decomposition pieces
        ellf = ll
        # S(v)<=N claim?  (column sum bounded by N)
        maxS = max((S[v] for v in P[f]), default=F(0))    # max over support of f
        maxS_all = max(S) if S else F(0)
        # Q_f <= maxS_on_support * row  (since Q=sum p_f S^2 <= (max S) sum p_f S = maxS*row)
        rec = dict(n=n, f=f, ellf=ellf, row=row, Q=Q, var=var, margin=margin,
                   maxS_supp=maxS, maxS_all=maxS_all)
        acc.append(rec)

def run_graph(n, E, acc):
    adj, cuts = gmins(n, E)
    for s in cuts:
        analyze_side(n, adj, s, acc)

def battery():
    accs = []
    # census
    for nn in range(7, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        acc = []
        for g6 in outg:
            n, E = dec(g6); run_graph(n, E, acc)
        accs.append((f"census N={nn}", acc))
    # extras
    def blowup(parts):
        m=len(parts); off=[0]*(m+1)
        for i in range(m): off[i+1]=off[i]+parts[i]
        nn=off[m]; EE=[]
        for i in range(m):
            j=(i+1)%m
            for a in range(off[i],off[i+1]):
                for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
        return nn,EE
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("M(C7)",)+mycielski(7,Cn(7)),
           ("M(C9)",)+mycielski(9,Cn(9)),
           ("M(C11)",)+mycielski(11,Cn(11)),
           ("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0),
           ("C5[2]",)+blowup([2,2,2,2,2]),
           ("C5[3]",)+blowup([3,3,3,3,3]),
           ("C5unbal",)+blowup([1,5,2,2,5]),
           ("C7unbal",)+blowup([1,4,2,4,2,4,2]),
           ("C5[1,6,2,2,6]",)+blowup([1,6,2,2,6])]
    for it in extra:
        name=it[0]; n=it[1]; E=it[2]
        acc=[]; run_graph(n,E,acc); accs.append((name,acc))
    return accs

if __name__ == "__main__":
    accs = battery()
    # SUBLEMMA TESTS
    print("=== sub-lemma audit on standing gate (NONUNIQUE rows) ===", flush=True)
    g_margin_min=None; g_var_min=None
    # L1: S(v) <= N for all v anywhere
    L1_fail=0; L1_worst=None
    # L2: maxS on support of f  <= N  (weaker, only support)
    # L3: row_f <= ell_f  ?  (would be nice)   and row_f<=N
    L3a_fail=0; L3b_fail=0
    # L4: Q_f <= N * row_f   (Q<= maxS_supp*row, so implies if maxS_supp<=N)
    L4_fail=0; L4_worst=None
    # main margin
    main_fail=0
    nrows=0
    for name, acc in accs:
        for r in acc:
            nrows+=1
            if g_margin_min is None or r['margin']<g_margin_min[0]:
                g_margin_min=(r['margin'],name,r)
            if r['var']>0 and (g_var_min is None or (F(r['n'])-r['row'])/r['var']<g_var_min[0]):
                g_var_min=((F(r['n'])-r['row'])/r['var'],name,r)
            N=F(r['n'])
            if r['maxS_all']>N: L1_fail+=1; L1_worst=(r['maxS_all'],N,name)
            if r['row']>r['ellf']: L3a_fail+=1
            if r['row']>N: L3b_fail+=1
            if r['Q']>N*r['row']:
                L4_fail+=1
                if L4_worst is None: L4_worst=(name,r)
            if r['margin']<0: main_fail+=1
    print(f"total nonunique rows tested: {nrows}", flush=True)
    print(f"MAIN n(n-row)>=var  fails: {main_fail}  worst-margin: {g_margin_min[0]} @ {g_margin_min[1]}", flush=True)
    print(f"L1  S(v)<=N (all v) fails: {L1_fail}  worst: {L1_worst}", flush=True)
    print(f"L3a row_f<=ell_f    fails: {L3a_fail}", flush=True)
    print(f"L3b row_f<=N        fails: {L3b_fail}", flush=True)
    print(f"L4  Q_f<=N*row_f    fails: {L4_fail}  worst: {L4_worst}", flush=True)
    r=g_margin_min[2]
    print(f"worst-margin row detail: n={r['n']} f={r['f']} ellf={r['ellf']} row={r['row']} Q={r['Q']} var={r['var']} maxS_supp={r['maxS_supp']} maxS_all={r['maxS_all']}", flush=True)
