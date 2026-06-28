"""Pin down the LOCAL half (LC) of the rho(K)<=N sandwich, at its point of use.
   Per bad edge f (ell=ell(f)):   ell*diag(p_f) - p_f p_f^T - a_bar(ell) L_{tau_f}  ⪰ 0   (PSD, exact).
   Summed over f this gives M-K = diag(T)-L_omega-K ⪰ 0, but per-edge is the strictly stronger,
   point-of-use statement. Mechanism: each geodesic Q closed by f is an ell-cycle; circulant fact
   J_ell + a*_ell L_{C_ell} ⪯ ell I (a*_ell=ell/(2+2cos(pi/ell)) sharp); take E_Q, Jensen p_f p_f^T<=E[qq^T].
   Also: verify a_bar(ell) <= a*_ell for odd ell>=5 (so a_bar is a valid weaker rational coeff)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _gcd import is_psd_exact, a_bar
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski

def lc_per_edge_psd(adj, side, n):
    """Return (ok, nbad, worst_f) : ok = all per-bad-edge (LC) matrices PSD-exact."""
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    allok=True; worst=None; nb=0
    for f in M:
        nb+=1
        Ps=cyc[f]; k=len(Ps); L=ell[f]; ae=a_bar(L)
        # p_f(v)
        pf={}
        for P in Ps:
            for v in P: pf[v]=pf.get(v,F(0))+F(1,k)
        # tau_f(e): bad edge f -> 1; geodesic edges -> fraction
        tau={}
        ef=frozenset(f); tau[ef]=F(1)
        for P in Ps:
            for i in range(len(P)-1):
                e2=frozenset((P[i],P[i+1])); tau[e2]=tau.get(e2,F(0))+F(1,k)
        # support vertices (cycle vertices over all Q) + bad-edge endpoints
        supp=set(pf.keys()) | set(f)
        idx={v:i for i,v in enumerate(sorted(supp))}; m=len(idx)
        # A = ell*diag(p_f) - p_f p_f^T - ae*L_tau   on supp
        A=[[F(0)]*m for _ in range(m)]
        for v,pv in pf.items():
            A[idx[v]][idx[v]] += F(L)*pv
        items=list(pf.items())
        for a in range(len(items)):
            va,pa=items[a]
            for b in range(len(items)):
                vb,pb=items[b]; A[idx[va]][idx[vb]] -= pa*pb
        for e,w in tau.items():
            u,v=tuple(e)
            if u not in idx or v not in idx: continue
            A[idx[u]][idx[u]] -= ae*w; A[idx[v]][idx[v]] -= ae*w
            A[idx[u]][idx[v]] += ae*w; A[idx[v]][idx[u]] += ae*w
        if not is_psd_exact(A,m):
            allok=False; worst=worst or (f,L)
    return allok, nb, worst

def gmin_cuts(n,E):
    from _gcd import run_gmin   # reuse gamma-min cut selection
    return run_gmin(n,E)

def test_graph_lc(nm,n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    from _h import maxcut_all, Bconn, bdist_restr
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: print(f"  {nm} N={n}: no bad edges"); return
    gm=min(g for _,g in cand)
    tot=0; fails=0; wit=None
    for s,g in cand:
        if g!=gm: continue
        r=lc_per_edge_psd(adj,s,n)
        if r is None: continue
        ok,nb,worst=r; tot+=nb
        if not ok: fails+=1; wit=worst
    print(f"  {nm} N={n}: bad-edges-tested={tot} LC-PSD-FAILS={fails}{' WIT '+str(wit) if wit else ''}",flush=True)

if __name__=="__main__":
    print("=== (LC) per-bad-edge local PSD test (point of use) ===",flush=True)
    # circulant-fact closed form + a_bar<=a*_ell check (high precision, for the record)
    import math
    print("  --- a_bar(ell) <= a*_ell = ell/(2+2cos(pi/ell)) for odd ell ---")
    badcoef=0
    for L in range(5,52,2):
        astar=L/(2+2*math.cos(math.pi/L))
        ab=float(a_bar(L))
        # exact-equivalent test: a_bar<=a* <=> cos(pi/L) <= (L^2-4)/L^2
        lhs=math.cos(math.pi/L); rhs=(L*L-4)/(L*L)
        ok = lhs <= rhs + 1e-15
        if not ok: badcoef+=1
        if L<=11 or not ok:
            print(f"    ell={L}: a_bar={ab:.5f} a*={astar:.5f} cos(pi/L)={lhs:.6f} <= (L^2-4)/L^2={rhs:.6f} : {ok}")
    print(f"  a_bar<=a* violations (odd 5..51): {badcoef}  [proof: cos x <= 1-x^2/2+x^4/24, pi^2/2 - pi^4/(24*25) = {math.pi**2/2 - math.pi**4/(24*25):.4f} >= 4]")
    print("  --- per-bad-edge (LC) on the gate ---",flush=True)
    # Mycielski chain + named + census small
    cur=(5,Cn(5)); test_graph_lc("C5",*cur)
    for nm in ["Grotzsch=N11","Myc2(C5)=N23"]:
        cur=mycielski(*cur); test_graph_lc(nm,cur[0],cur[1])
    cur=(7,Cn(7)); test_graph_lc("C7",*cur)
    cur=mycielski(*cur); test_graph_lc("Myc(C7)=N15",cur[0],cur[1])
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); test_graph_lc(g6,n,E)
    # census N=7..9 all gamma-min cuts
    for nn in range(7,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; fails=0; wit=None
        from _h import maxcut_all, Bconn, bdist_restr
        for g6 in outg:
            n,E=dec(g6)
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
            cand=[]
            for s in cuts:
                Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
                if not Mb: continue
                G=0; ok=True
                for (u,v) in Mb:
                    d=bdist_restr(adj,s,u,v)
                    if d<0: ok=False; break
                    G+=(d+1)**2
                if ok: cand.append((s,G))
            if not cand: continue
            gm=min(g for _,g in cand)
            for s,g in cand:
                if g!=gm: continue
                r=lc_per_edge_psd(adj,s,n)
                if r is None: continue
                ok,nb,worst=r; tot+=nb
                if not ok: fails+=1; wit=wit or g6
        print(f"  census N={nn}: bad-edges-tested={tot} LC-PSD-FAILS={fails}{' WIT '+wit if wit else ''}",flush=True)
