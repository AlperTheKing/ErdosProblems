"""Reconstruct the FULL-ZMU counterexample (C5 + Myc(C7) glued, N=20) and examine the zero-mu edge with
both endpoints T>0. Confirm neither endpoint saturated (T<N), and contrast with A-alltie.
Also: search census + glued constructions for ANY zero-mu edge with both T>0 (FULL-ZMU violation) and record
max(T(u),T(v)) -- to see how close it gets to N (A-alltie requires =N forces 0)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def scan_loads(g6list, label=""):
    out=[]
    for g6 in g6list:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        N=info['n']; T=info['T']; mu=mu_edges(info)
        for e,val in mu.items():
            if val!=0: continue
            u,v=tuple(e)
            if T[u]>0 and T[v]>0:
                out.append((g6,N,(u,v),str(T[u]),str(T[v]),max(T[u],T[v])/N))
    return out

if __name__=="__main__":
    print("=== FULL-ZMU violations (zero-mu edge, both T>0) on loads-cut; how saturated? ===")
    # census loads-cut
    worst=F(0); worstrec=None; nviol=0
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        recs=scan_loads(outg)
        for r in recs:
            nviol+=1
            ratio=r[5]
            if ratio>worst: worst=ratio; worstrec=r
        print(f"  census N={nn} loads-cut: FULL-ZMU-violating zero-mu edges (both T>0) = {len(recs)}",flush=True)
    print(f"  TOTAL census FULL-ZMU viol (loads-cut) = {nviol}")
    print(f"  worst max(T(u),T(v))/N over census = {float(worst)}  rec={worstrec}")
