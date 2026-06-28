"""Verify the clean characterization: given ROWSUM<=N, the integer SPLIT band-pair for t
   (OUT_t<=2tN/L AND CEN_t<=(L-2t)N/L) holds IFF R <= B_t <= 0, where B_t=OUT_t-2tN/L, R=ROWSUM-N.
   Check on census N<=11 (selected good cuts) that the two formulations agree exactly, per (t, bad edge)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def check(n, adj, s):
    st=struct_for_side(n,adj,s)
    if st is None: return 0,0
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    nchk=0; mism=0
    for f in M:
        L=ell[f]; Ps=cyc[f]; d=pf[f]; layer={}
        for P in Ps:
            for i,v in enumerate(P): layer[v]=i
        A=[F(0)]*L
        for v,pv in d.items(): A[layer[v]]+=pv*S[v]
        ROW=sum(A); R=ROW-F(n); mm=(L-1)//2
        if ROW>n: continue  # only test where ROWSUM-O holds
        for t in range(1,mm+1):
            out=sum(A[i] for i in range(t))+sum(A[i] for i in range(L-t,L))
            cen=sum(A[i] for i in range(t,L-t))
            bandpair = (out<=F(2*t*n,L)) and (cen<=F((L-2*t)*n,L))
            Bt=out-F(2*t*n,L)
            charact = (R<=Bt<=0)
            nchk+=1
            if bandpair!=charact: mism+=1
    return nchk,mism

if __name__=="__main__":
    print("=== verify SPLIT band-pair  <=>  R<=B_t<=0  (census N<=11, good cuts) ===",flush=True)
    tot=0; totm=0
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        c=0; m=0
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts:
                a,b=check(n,adj,s); c+=a; m+=b
        print(f"  N={nn}: (t,edge) checks={c} mismatches={m}",flush=True)
        tot+=c; totm+=m
    print(f"=== TOTAL checks={tot} mismatches={totm} -> characterization {'EXACT' if totm==0 else 'WRONG'} ===",flush=True)
