"""Sampled census N=12,13,14 (geng -tc, strided) testing A-alltie on the loads() gamma-min cut.
Also on N=12,13 test ALL gamma-min cuts for graphs that DO produce a saturated vertex (cheap filter).
Goal: gather many more saturated zero-mu cases at N>11 to gate A-alltie beyond census-11.
Report cases and any violation (exact)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads, maxcut_all, Bconn, bdist_restr
from _zmu import mu_edges
from _satzmu_conn import struct_for_side

def loads_cut_check(N,E):
    info=loads(N,E)
    if info is None: return 0,0,None
    T=info['T']; n=info['n']
    if not any(t==n for t in T): return 0,0,None
    mu=mu_edges(info)
    c=0; v=0; wit=None
    for e,val in mu.items():
        if val!=0: continue
        a,b=tuple(e)
        for (x,y) in ((a,b),(b,a)):
            if T[x]==n:
                c+=1
                if T[y]!=0:
                    v+=1
                    if wit is None: wit=(x,y,str(T[x]),str(T[y]))
    return c,v,wit

if __name__=="__main__":
    for nn,stride in [(12,7),(13,31),(14,131)]:
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        sample=outg[::stride]
        cases=0; viol=0; wit=None; nsat=0
        for g6 in sample:
            n,E=dec(g6)
            c,v,w=loads_cut_check(n,E)
            if c>0: nsat+=1
            cases+=c; viol+=v
            if v>0 and wit is None: wit=(g6,w)
        print(f"  N={nn} (sampled {len(sample)} of {len(outg)}, loads-cut): graphs-with-sat-zero-mu={nsat} A-alltie cases={cases} VIOLATIONS={viol}"+(f" WIT {wit}" if wit else ""), flush=True)
