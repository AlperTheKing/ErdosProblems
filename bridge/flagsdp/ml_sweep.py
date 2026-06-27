#!/usr/bin/env python3
"""Exhaustive check of GPT's condition-(iii) marginal-loss reduction over ALL connected-B tri-free max-cut
configs N<=Nmax. For each, find the MIN-OVERSHOOT shortest-geodesic peel C (min L(C)-bound over connected
geodesics). Check: (iii) L<=bound; (A') A(C)<=2(N-h); (LEP) H(C)<=Delta(C). Report any config where the
min-overshoot peel FAILS (iii) [a real problem] or where (A')/(LEP) fail [decomposition gap, (iii) may still hold]."""
import sys
from collections import deque
import flag_engine as fe

def bdistB(n,adj,side,src,banned):
    d={src:0}; q=deque([src])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in banned and v not in d: d[v]=d[u]+1; q.append(v)
    return d
def Bconnected(n,adj,side):
    seen={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
    return len(seen)==n
def maxcut_all(n,E):
    best=-1; cuts=[]
    for mask in range(1<<(n-1)):
        c=sum(1 for (u,v) in E if ((mask>>u)&1)!=((mask>>v)&1))
        if c>best: best=c; cuts=[mask]
        elif c==best: cuts.append(mask)
    return best,cuts
def gamma_min_cut(n,adj,E):
    mc,cuts=maxcut_all(n,E); best=None
    for mask in cuts:
        side=[(mask>>u)&1 for u in range(n)]
        if not Bconnected(n,adj,side): continue
        M=[(u,v) for (u,v) in E if side[u]==side[v]]
        G=0; ok=True
        for (u,v) in M:
            d=bdistB(n,adj,side,u,set()).get(v,-1)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok and (best is None or G<best[1]): best=(side,G,M)
    return best
def all_geos(n,adj,side,s,t):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    out=[]
    def rec(v,acc):
        if v==s: out.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[]); return out

def ml_for_config(n,adj,side,G,M):
    ellG={(min(x,y),max(x,y)): bdistB(n,adj,side,x,set())[y]+1 for (x,y) in M}
    best=None
    for (u,v) in M:
        peeled=(min(u,v),max(u,v))
        for C in all_geos(n,adj,side,u,v):
            Cset=set(C); h=len(C); mu=0; Delta=0; conn=True
            for f in M:
                key=(min(f),max(f))
                if f[0] in Cset or f[1] in Cset: mu+=ellG[key]**2
                else:
                    nd=bdistB(n,adj,side,f[0],Cset).get(f[1],-1)
                    if nd<0: conn=False; break
                    Delta+=(nd+1)**2-ellG[key]**2
            if not conn: continue
            L=mu-Delta; bound=2*h*n-h*h; ov=L-bound
            if best is None or ov<best[0]:
                F=[f for f in M if (f[0] in Cset or f[1] in Cset) and (min(f),max(f))!=peeled]
                A=sum(ellG[(min(f),max(f))] for f in F)
                H=sum(max(0,ellG[(min(f),max(f))]**2-h*ellG[(min(f),max(f))]) for f in F)
                best=(ov,L,bound,h,A,H,Delta,2*(n-h))
    return best

def run(Nmax,Nmin=5):
    for N in range(Nmin,Nmax+1):
        gs=fe.enumerate_graphs(N,triangle_free=True); nconf=0
        iii_viol=0; Aviol=0; LEPviol=0; min_iii_slack=10**9
        ovm_viol=0; max_ov_minus_deficit=-10**9   # test ov(C_min) <= N^2-Gamma (unconditional cond-iii master)
        for (n,A0) in gs:
            adj=[set(v for v in range(n) if (A0[u]>>v)&1) for u in range(n)]
            E=[(u,v) for u in range(n) for v in adj[u] if v>u]
            res=gamma_min_cut(n,adj,E)
            if res is None: continue
            side,G,M=res
            if len(M)<2: continue
            nconf+=1
            b=ml_for_config(n,adj,side,G,M)
            if b is None: continue
            ov,L,bound,h,A,H,Delta,twoNh=b
            min_iii_slack=min(min_iii_slack,-ov)
            deficit=n*n-G
            if ov-deficit>max_ov_minus_deficit: max_ov_minus_deficit=ov-deficit
            if ov>deficit:
                ovm_viol+=1
                print(f"   OV-MASTER-VIOLATION N={n} Gamma={G} deficit={deficit} ov={ov} > deficit (ov-deficit={ov-deficit}) A0={A0}",flush=True)
            if ov>0:
                iii_viol+=1
                print(f"   (iii)-VIOLATION N={n} Gamma={G} N^2={n*n} deficit={deficit} (tight={G>=n*n}) ov={ov} L={L} bound={bound} h={h} A={A}<=2(N-h)={twoNh}? H={H}<=Delta={Delta}? A0={A0}",flush=True)
            if A>twoNh:
                Aviol+=1
                print(f"   (A')-VIOLATION  N={n} Gamma={G} deficit={deficit} A={A}>2(N-h)={twoNh} h={h} A0={A0}",flush=True)
            if H>Delta:
                LEPviol+=1
                print(f"   (LEP)-VIOLATION N={n} Gamma={G} deficit={deficit} H={H}>Delta={Delta} h={h} A0={A0}",flush=True)
        print(f"N={N}: connected-B m>=2 configs={nconf} | (iii) min-overshoot FAIL(ov>0)={iii_viol} (min slack={min_iii_slack}) | (A') fail={Aviol} | (LEP) fail={LEPviol} | OV-MASTER ov(Cmin)<=N^2-Gamma viol={ovm_viol} (max ov-deficit={max_ov_minus_deficit})",flush=True)
    print("DONE",flush=True)

if __name__=="__main__":
    a=[int(x) for x in sys.argv[1:]] or [10]
    run(a[0], a[1] if len(a)>1 else 5)
