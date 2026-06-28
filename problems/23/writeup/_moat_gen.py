"""Generalized MOAT (covers multi-geodesic too): ROWSUM-O is EXACTLY
   <p_f,p_f> + sum_{g!=f}<p_f,p_g> <= N.
Two clean sub-claims to test SEPARATELY (a decomposition of ROWSUM-O):
  (SELF)  <p_f,p_f> <= ell(f)                          [proven: p_f(v)<=1, sum=ell]
  (CROSS) sum_{g!=f} <p_f,p_g> <= N - <p_f,p_f>         [the real content]
We already saw CROSS holds for single-geo f as N-ell(f). Test CROSS for ALL f (multi too).
Also test the SHARPER single quantity that the band misses: define corridor-complement
  comp_load(f) = sum_{v} (1 - p_f(v)) * p_f(v) ??? no.
Cleanest equivalent of ROWSUM-O:  <p_f, S - p_f>  <=  N - <p_f,p_f>
  i.e. <p_f, S>  <= N. (tautology). So CROSS == ROWSUM-O. The POINT: test whether the
band's per-layer N/ell budget is what fails, while the GLOBAL corridor budget
  sum_{v in supp(f)} p_f(v)*(S(v)-p_f(v)) <= N - sum p_f(v)^2 holds with the dilution intact.
Report: max over census of ROWSUM, and whether worst is single-geo, plus the per-edge
identity ROWSUM = <p_f,p_f> + CROSS and margins."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
from _corridor import cut_S

def scan(g6):
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    adj2,cuts=gmins(n,E)
    worstROW=None
    for ci,s in enumerate(cuts):
        M,ell,S,pf,cyc=cut_S(n,adj2,s)
        for f in M:
            self_=sum(pv*pv for pv in pf[f].values())
            ROW=sum(pv*S[v] for v,pv in pf[f].items())
            ng=len(cyc[f])
            if worstROW is None or ROW>worstROW[0]:
                worstROW=(ROW,ci,f,ng,self_)
    return n,worstROW

if __name__=="__main__":
    for nn in range(5,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        worst=None; worst_is_single=None; rowfail=0
        for g6 in out:
            n,w=scan(g6)
            if w is None: continue
            if w[0]>n: rowfail+=1
            if worst is None or w[0]-n>worst[0]-worst[1]:  # closest to N (largest ROW-N)
                worst=(float(w[0]),n,g6,w[3])
        # worst[0]-worst[1] = ROW-N ; track max
        print(f"  census N={nn}: ROWSUM-O fails={rowfail}  worst ROW={worst[0]:.4f} (N={worst[1]}, #geo={worst[3]}, {worst[2]})  margin={worst[1]-worst[0]:.4f}",flush=True)
