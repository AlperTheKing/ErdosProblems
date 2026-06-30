"""Dissect C5unbal=[1,5,2,2,5] N=15, the row f=(6,8) where S3' fails (ell*Smax=20>15)
but BD-TARGET holds. Print full S, supp, a,b,mu,row,var,bd,target for ALL nonunique rows.
Goal: see WHY BD-TARGET survives despite ell*Smax>N -> reveals correct lemma."""
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for x in range(off[i],off[i+1]):
            for y in range(off[j],off[j+1]): EE.append((min(x,y),max(x,y)))
    return nn,EE

n,E=blowup([1,5,2,2,5])
adj,cuts=gmins(n,E)
print("N=",n,"ncuts=",len(cuts))
for s in cuts:
    st=struct_for_side(n,adj,s)
    if st is None: continue
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    print("side=",s)
    print("S=",[str(x) for x in S])
    for f in M:
        if len(cyc[f])<2: continue
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); m=row/ll
        var=sum(d[v]*(S[v]-m)**2 for v in d)
        Sv=[S[v] for v in d]; a=min(Sv); b=max(Sv)
        bd=ll*(b-m)*(m-a); tgt=F(n)*(F(n)-row)
        print(f"  f={f} ell={ll} row={row} mu={m} a={a} b={b} var={var} bd={bd} tgt={tgt} bd<=tgt? {bd<=tgt}")
        print(f"     supp S-values={[str(S[v]) for v in sorted(d)]}")
    break
