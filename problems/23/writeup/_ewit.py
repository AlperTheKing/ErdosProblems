"""Find E-test witnesses: zero-mu B-edge uv with T(u)>0 AND T(v)>0.
For each, record T(u),T(v),N. Confirm: in EVERY such witness, neither endpoint is saturated (T<N).
This isolates exactly what 'saturation' buys A-alltie: a zero-mu edge can have both endpoints loaded,
but NOT if one is saturated.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def run(nmin=10,nmax=11, show=5):
    for nn in range(nmin,nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        maxminT=F(-1); shown=0; nwit=0; sat_among=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            N=info['n']; T=info['T']; mu=mu_edges(info)
            for e,val in mu.items():
                if val!=0: continue
                u,v=tuple(e)
                if T[u]>0 and T[v]>0:
                    nwit+=1
                    mn=min(T[u],T[v]); mx=max(T[u],T[v])
                    if mx==N: sat_among+=1
                    if mx>maxminT: maxminT=mx
                    if shown<show:
                        print(f"  {g6} N={N}: zero-mu edge ({u},{v}) T(u)={T[u]} T(v)={T[v]} (max={mx})")
                        shown+=1
        print(f"  ==> N={nn}: E-witnesses (both T>0)={nwit}, with a SATURATED endpoint (T=N)={sat_among}, "
              f"max-endpoint-T over all witnesses={maxminT} (N={nn})", flush=True)

if __name__=="__main__":
    print("=== E-test witnesses: zero-mu edge, both endpoints loaded ===")
    run(10,11)
