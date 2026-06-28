"""For a SINGLE-geodesic edge f (p_f in {0,1}), ROWSUM(f) = sum_{v in V_f} S(v) = sum_g <1_{V_f}, p_g>
 = ell(f) + sum_{g!=f} m(f,g),  where m(f,g) = <1_{V_f}, p_g> = geodesic-mass of g inside f's vertex set.
For the bound ROWSUM(f) <= N we need:  ell(f) + sum_{g!=f} m(f,g) <= N.
m(f,g) <= min(ell(f), ell(g)) trivially, and m(f,g) <= |V_f ∩ supp(g)|.
The KEY pairwise structure (test): how big can m(f,g) be? If g and f run through a common corridor of
c shared vertices, m(f,g) ~ c. The triangle-free + max-cut geometry should force: edges that overlap a lot
with f have endpoints near f's endpoints, limiting how MANY such g there can be (a packing bound).
EXACT-TEST the pairwise overlap matrix m(f,g) on the witness and see the structure:
  - Is m(f,g)=m(g,f)? NO in general (m(f,g) uses V_f, full mass of g; not symmetric unless both single-geo).
  - <p_f,p_g> IS symmetric. For single-geo f: <p_f,p_g> = sum_{v in V_f} p_g(v) = m(f,g).
  - So ROWSUM(f) = sum_g <p_f,p_g> and for single-geo f the cross part = sum_{g} m(f,g).
GLOBAL invariant candidate (MOAT/packing): for single-geo f,
  sum_{g!=f} <p_f,p_g>  <=  N - ell(f).
Equivalently sum over OTHER edges of their mass landing on V_f <= N-ell(f) = number of vertices OFF V_f.
Interpretation: the total geodesic mass of OTHER bad edges that lands inside the ell(f)-vertex corridor V_f
is at most the number of vertices outside V_f. This is a NON-LOCAL conservation: mass on the corridor is
budgeted by the complement size. TEST exactly."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
from _corridor import cut_S

def check(g6):
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    adj2,cuts=gmins(n,E)
    worst=None  # (margin, ci, f) for the cross<=N-ell test on single-geo edges
    rows=[]
    for ci,s in enumerate(cuts):
        M,ell,S,pf,cyc=cut_S(n,adj2,s)
        for f in M:
            if len(cyc[f])!=1: continue  # single-geodesic only
            Vf=set(pf[f].keys())
            cross=sum(S[v] for v in Vf)-ell[f]   # sum_{g!=f} mass on V_f
            margin=F(n)-ell[f]-cross            # want >=0
            rows.append((ci,f,ell[f],cross,margin))
            if worst is None or margin<worst[0]: worst=(margin,ci,f,ell[f],cross)
    return n,worst,rows

if __name__=="__main__":
    print("=== MOAT test (single-geo): sum_{g!=f}<p_f,p_g> <= N - ell(f)  i.e. cross-mass on corridor <= complement size ===")
    n,worst,rows=check("K??CE@A{?]Fc")
    print(f"witness N={n}: worst (margin,ci,f,ell,cross)={worst}")
    for ci,f,L,cr,m in rows[:8]:
        print(f"  cut{ci} f={f} ell={L} cross={cr}={float(cr):.3f} N-ell={n-L} margin={m}={float(m):.3f}")
    # census scan N<=11 (fast)
    for nn in range(5,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        fail=0; worst_m=None; first=None; ngraph=0
        for g6 in out:
            n2,w,_=check(g6)
            if w is None: continue
            ngraph+=1
            if w[0]<0: fail+=1; first=first or (g6,float(w[4]),w[3],n2)
            if worst_m is None or w[0]<worst_m: worst_m=w[0]
        print(f"  census N={nn}: single-geo graphs={ngraph} MOAT-FAILS={fail} worst margin={worst_m}={float(worst_m) if worst_m is not None else 0:.3f}"+(f" first={first}" if first else ""),flush=True)
