"""Isolate the hard part. var = BV + WV, BV=sum_i (a_i-<S>)^2 (between), WV=sum_i w_i (within).
Test:
 (T-between)  n^2 >= BV + n*row   (target with WV dropped -- EASIER; if this fails sometimes, WV matters)
 (T-WV-bound) WV <= ?  measure max WV and max WV/(n^2-...).
 Also test STRONG-by-layer reformulation and a NEW candidate:
 (NEW) for each layer, a_i <= n  AND  the convexity:  sum_i a_i^2 <= (max_i a_i)*row <= n*row.
       Then BV = sum a_i^2 - row^2/ell <= n*row - row^2/ell.  target needs n^2>=BV+WV+n*row.
 (CORE) measure  Q := var + n*row   and  n^2,  and the gap; correlate gap with WV and amax.
Battery census<=10 + blowups.
"""
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
    for parts in [[2,2,2,2,2],[3,3,3,3,3],[1,5,2,2,5],[1,2,1,2,1,2,1],[1,6,2,2,6],[2,3,2,3,2]]:
        nn,EE=blowup(parts); adj,cuts=gmins(nn,EE)
        for s in cuts: yield (f"blow{parts}",nn,adj,s)

if __name__=="__main__":
    print("=== isolate within vs between layer variance ===",flush=True)
    nrows=0; f_between=0; wb=None; maxWV=None; f_amax=0
    f_between_strict=0
    for nm,n,adj,s in cases():
        b=build(n,adj,s)
        if b is None: continue
        M,ell,T,mu,cyc,S,pf=b
        for f in M:
            Ps=cyc[f]
            if len(Ps)<2: continue
            L=ell[f]; k=len(Ps)
            d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); mean=row/ll
            layer_w=[dict() for _ in range(L)]
            for P in Ps:
                for i,v in enumerate(P): layer_w[i][v]=layer_w[i].get(v,F(0))+F(1,k)
            a=[sum(layer_w[i][v]*S[v] for v in layer_w[i]) for i in range(L)]
            w=[sum(layer_w[i][v]*(S[v]-a[i])**2 for v in layer_w[i]) for i in range(L)]
            BV=sum((a[i]-mean)**2 for i in range(L)); WV=sum(w)
            nrows+=1
            # between-only target
            slk_b=F(n)**2-(BV+F(n)*row)
            if slk_b<0:
                f_between+=1
                if wb is None or slk_b<wb[0]: wb=(slk_b,nm,f,n,str(row),str(BV),str(WV))
            if maxWV is None or WV>maxWV[0]: maxWV=(WV,nm,f,n)
    print("nonunique rows:",nrows)
    print(f"BETWEEN-only target (n^2>=BV+n row) fails: {f_between} worst:{wb}")
    print(f"max WV (within-layer variance sum): {maxWV}")
