"""FAST probe (census<=10 + small blowups only, no N=23 Myc) for L1 / STRONG sublemmas + tightness map.
Also record, for the TIGHT rows (margin==0 or small), the structure: ell, k=|cyc|, <S>, Smax, Smin, n."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_var_0 import build

def blowup(parts):
    m=len(parts); off=[0]*(m+1)
    for i in range(m): off[i+1]=off[i]+parts[i]
    nn=off[m]; EE=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,EE

def cases():
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: yield (f"c{nn}:{g6}",n,adj,s)
    for parts in [[2,2,2,2,2],[3,3,3,3,3],[1,3,2,2,3],[2,3,2,3,2],[1,5,2,2,5],
                  [1,2,1,2,1,2,1],[2,2,2,2,2,2,2]]:
        nn,EE=blowup(parts); adj,cuts=gmins(nn,EE)
        for s in cuts: yield (f"blow{parts}",nn,adj,s)

if __name__=="__main__":
    print("=== FAST probe ===",flush=True)
    nrows=0; L1_fail=0; L1_worst=None; strong_fail=0; strong_worst=None; tight=[]
    for nm,n,adj,s in cases():
        b=build(n,adj,s)
        if b is None: continue
        M,ell,T,mu,cyc,S,pf=b
        for f in M:
            if len(cyc[f])<2: continue
            d=pf[f]; ll=sum(d.values())
            smean=sum(d[v]*S[v] for v in d)/ll
            Smax=max(S[v] for v in d); Smin=min(S[v] for v in d)
            sm=sum(d[v]*S[v]**2 for v in d)
            row=ll*smean; var=sm-row**2/ll
            margin=F(n)*(F(n)-row)-var
            nrows+=1
            for v in d:
                if S[v]>F(n,5):
                    L1_fail+=1; exc=S[v]-F(n,5)
                    if L1_worst is None or exc>L1_worst[0]: L1_worst=(exc,nm,f,v,str(S[v]),n)
                    break
            lhs=ll*smean*(Smax+F(n)-smean); slk=F(n)**2-lhs
            if slk<0:
                strong_fail+=1
                if strong_worst is None or slk<strong_worst[0]: strong_worst=(slk,nm,f,n,str(smean),str(Smax),str(ll))
            if margin<=F(1,1) and len(tight)<40:
                tight.append((str(margin),nm,f,n,str(ell[f]),len(cyc[f]),str(smean),str(Smax),str(Smin),str(row),str(var)))
    print("nonunique rows:",nrows)
    print(f"L1 (S<=n/5) fails:{L1_fail} worst:{L1_worst}")
    print(f"STRONG fails:{strong_fail} worst:{strong_worst}")
    print("TIGHT rows (margin<=1): margin,nm,f,n,ell,k,<S>,Smax,Smin,row,var")
    for t in tight: print("  ",t)
