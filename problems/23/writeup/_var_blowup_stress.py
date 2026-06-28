"""Stress Codex's variance strengthening n*(n-row) >= var on EXPLICIT UNBALANCED odd-cycle blow-ups
(moderate N, built directly so the exact gate runs without quotient subtlety). These are where ROWSUM-O is
near-tight and the load S is most non-uniform -- the most likely place for a variance strengthening to break,
mirroring how the band died on unbalanced C7. Exact Fraction."""
from fractions import Fraction as F
from _bdef_construct import Cn
from _stark1 import gmins
from _satzmu_conn import struct_for_side

def blowup(parts):
    """C_m blow-up with given part sizes; returns (n,E). Cycle 0-1-..-(m-1)-0, complete bipartite between
       consecutive parts."""
    m=len(parts); off=[0]*(m+1)
    for i in range(m): off[i+1]=off[i]+parts[i]
    n=off[m]; E=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]):
                E.append((min(a,b),max(a,b)))
    return n,E

def rows_var_all(n,E):
    adj,cuts=gmins(n,E)
    worst=None; fails=0; tot=0
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
        for f in M:
            d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
            mean=row/ll; var=sum(d[v]*(S[v]-mean)**2 for v in d)
            margin=F(n)*(F(n)-row)-var; tot+=1
            if margin<0: fails+=1
            if worst is None or margin<worst[0]: worst=(margin,f,str(row),str(var),''.join(map(str,s))[:40])
    return tot,fails,worst

if __name__=="__main__":
    print("=== variance strengthening on EXPLICIT unbalanced blow-ups (exact) ===",flush=True)
    configs=[
        [1,50,10,10,50],[1,40,4,40,4],[2,60,8,8,60],[1,30,30,3,30],
        [1,20,3,20,3,20,3],[2,40,5,40,5,40,5],[1,50,2,50,2,50,2],
        [1,15,2,15,2,15,2,15,2],[3,30,3,30,3,30,3,30,3],
        [1,25,5,5,25],[1,100,10,10,100],
    ]
    anyfail=False
    for parts in configs:
        n,E=blowup(parts)
        tot,fails,worst=rows_var_all(n,E)
        print(f"  C{len(parts)}{parts}: N={n} rows={tot} FAILS={fails} worst-margin={float(worst[0]):.2f} "
              f"(f={worst[1]} row={worst[2]} var={worst[3]})",flush=True)
        if fails: anyfail=True
    print(f"\n=== unbalanced blow-up stress: {'FAILURE FOUND' if anyfail else 'NO FAILURE (variance strengthening holds)'} ===",flush=True)
