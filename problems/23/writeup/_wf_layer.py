"""Verify the LAYER decomposition of row_f and var_f EXACTLY.
For a nonunique bad edge f with geodesics cyc[f] each of ell vertices:
 layers I_i = {v : position i on the geodesic}.  By layer-uniformity sum_{v in I_i} p_f(v)=1.
 a_i := sum_{v in I_i} p_f(v) S(v)  (layer-i weighted avg of S, weight 1).
 w_i := sum_{v in I_i} p_f(v) (S(v)-a_i)^2  (within-layer var >=0).
 Claims to verify exactly:
   (C-rowlayer)  row_f = sum_i a_i
   (C-layerwt)   sum_{v in I_i} p_f(v) = 1  for each i
   (C-vardecomp) var_f = sum_i (a_i - <S>)^2 + sum_i w_i,  <S>=row/ell
Battery: census<=10 + small blowups.  Report any mismatch.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins

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
    for parts in [[2,2,2,2,2],[3,3,3,3,3],[1,5,2,2,5],[1,2,1,2,1,2,1]]:
        nn,EE=blowup(parts); adj,cuts=gmins(nn,EE)
        for s in cuts: yield (f"blow{parts}",nn,adj,s)

def build(n,adj,s):
    st=struct_for_side(n,adj,s)
    if st is None: return None
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    return M,ell,T,mu,cyc,S,pf

if __name__=="__main__":
    print("=== verify LAYER decomposition exactly ===",flush=True)
    nrows=0; bad_rowlayer=0; bad_layerwt=0; bad_vardecomp=0; ex=None
    for nm,n,adj,s in cases():
        b=build(n,adj,s)
        if b is None: continue
        M,ell,T,mu,cyc,S,pf=b
        for f in M:
            Ps=cyc[f]
            if len(Ps)<2: continue
            L=ell[f]
            d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); mean=row/ll
            var=sum(d[v]*(S[v]-mean)**2 for v in d)
            # build layers: position i -> set of vertices appearing at index i in some geodesic
            # weight of v in layer i = (#geodesics with v at index i)/k
            k=len(Ps)
            layer_w=[dict() for _ in range(L)]
            for P in Ps:
                for i,v in enumerate(P):
                    layer_w[i][v]=layer_w[i].get(v,F(0))+F(1,k)
            nrows+=1
            # C-layerwt
            okwt=all(sum(layer_w[i].values())==1 for i in range(L))
            if not okwt: bad_layerwt+=1
            # a_i, w_i
            a=[sum(layer_w[i][v]*S[v] for v in layer_w[i]) for i in range(L)]
            w=[sum(layer_w[i][v]*(S[v]-a[i])**2 for v in layer_w[i]) for i in range(L)]
            # C-rowlayer
            if sum(a)!=row: bad_rowlayer+=1
            # C-vardecomp
            rhs=sum((a[i]-mean)**2 for i in range(L))+sum(w)
            if rhs!=var:
                bad_vardecomp+=1
                if ex is None: ex=(nm,f,str(var),str(rhs))
    print("nonunique rows:",nrows)
    print(f"bad layer-weight (sum!=1): {bad_layerwt}")
    print(f"bad row=sum a_i: {bad_rowlayer}")
    print(f"bad var-decomp: {bad_vardecomp}  ex={ex}")
