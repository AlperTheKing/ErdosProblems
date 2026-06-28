"""SELECTED-cut gate for the fractional SPLIT: for each graph, does SOME gamma-min connected-B max cut satisfy
   the fractional SPLIT for ALL its bad edges? Count graphs with NO good cut (would kill SPLIT even as selected-cut).
   The reduction only needs ONE gamma-min cut, so selected-cut universality is the right metric."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def frac_ok_cut(n, adj, s):
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
    for f in M:
        L=ell[f]; Ps=cyc[f]; d=pf[f]; layer={}
        for P in Ps:
            for i,v in enumerate(P): layer[v]=i
        A=[F(0)]*L
        for v,pv in d.items(): A[layer[v]]+=pv*S[v]
        R=sum(A)-F(n); m=(L-1)//2
        Bs=[(sum(A[i] for i in range(t))+sum(A[i] for i in range(L-t,L)))-F(2*t*n,L) for t in range(1,m+1)]
        if not (R<=0 and min(Bs)<=0 and max(Bs)>=R): return False
    return True

if __name__=="__main__":
    print("=== SELECTED-cut fractional SPLIT gate: graphs with NO good gamma-min cut ===",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        graphs_with_cuts=0; nogood=0; witness=None
        for g6 in outg:
            n,E=dec(g6)
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            adj2,cuts=gmins(n,E)
            if not cuts: continue
            graphs_with_cuts+=1
            if not any(frac_ok_cut(n,adj2,s) for s in cuts):
                nogood+=1; witness=witness or g6
        print(f"  census N={nn}: graphs-with-gamma-min-cuts={graphs_with_cuts} NO-GOOD-CUT={nogood}{' WIT '+witness if witness else ''}",flush=True)
