"""Is A-alltie really about the value N, or is there a sharper local tradeoff?
For EVERY zero-mu B-edge uv (over census loads-cut), record (T(u),T(v)).
Plot the relation. Sub-claims to test exactly:
  (Q1) zero-mu edge with T(v)>0  =>  T(u) <= N-1 ? (i.e. saturation is the exact threshold)
  (Q2) zero-mu edge: min(T(u),T(v)) <= ??? ; max possible min(T(u),T(v)) over zero-mu edges (ZMU-HALF says <=N/2)
  (Q3) zero-mu edge with BOTH T(u)>0 and T(v)>0: what is the max of max(T(u),T(v))?  (the real obstruction)
Also: among zero-mu edges with T(u)>0 and T(v)>0, record T(u)+T(v) and T(u),T(v).
Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

if __name__=="__main__":
    print("=== zero-mu edges: (T(u),T(v)) relation over census loads-cut ===")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        max_min=F(0); max_min_wit=None         # max over zero-mu edges of min(Tu,Tv)
        max_maxboth=F(0); max_maxboth_wit=None  # max over BOTH-positive zero-mu edges of max(Tu,Tv)
        n_bothpos=0
        viol_Q1=0  # T(v)>0 and T(u)=N
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            T=info['T']; N=info['n']
            mu=mu_edges(info)
            for e,val in mu.items():
                if val!=0: continue
                u,v=tuple(e)
                mn=min(T[u],T[v]); mx=max(T[u],T[v])
                if mn>max_min: max_min=mn; max_min_wit=(g6,u,v,str(T[u]),str(T[v]),N)
                if T[u]>0 and T[v]>0:
                    n_bothpos+=1
                    if mx>max_maxboth: max_maxboth=mx; max_maxboth_wit=(g6,u,v,str(T[u]),str(T[v]),N)
                    if mn==N or mx==N: viol_Q1+=1  # one end saturated AND other positive
        print(f"  N={nn}: max min(Tu,Tv) over zero-mu={float(max_min)}={max_min} wit={max_min_wit}", flush=True)
        print(f"         both-positive zero-mu edges={n_bothpos}, max(max(Tu,Tv)) among them={float(max_maxboth)} wit={max_maxboth_wit}; (one-end-sat & other-pos)={viol_Q1}", flush=True)
