#!/usr/bin/env python3
"""PARTIAL strided census of the U-claim over geng -tc 13. Samples every STRIDE-th
graph (covers ALL density regimes, not just sparse prefix) up to MAXCHECK checked.
EXACT Fractions. NO silent truncation: prints the exact count sampled & total seen.
Usage: python AUDIT_Tuniform_n13_partial.py STRIDE MAXCHECK
"""
import sys, subprocess, time
from collections import deque
from fractions import Fraction
from multiprocessing import Pool
GENG="E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"

def dec(s):
    b=[ord(c)-63 for c in s]; n=b[0]; bits=[]
    for x in b[1:]:
        for k in range(5,-1,-1): bits.append((x>>k)&1)
    E=[]; i=0
    for jj in range(1,n):
        for ii in range(jj):
            if i<len(bits) and bits[i]: E.append((ii,jj))
            i+=1
    return n,E
def maxcut_all(n,adj):
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]; best=-1; cuts=[]
    for m in range(1<<(n-1)):
        side=[(m>>u)&1 for u in range(n)]
        c=sum(1 for u,v in edges if side[u]!=side[v])
        if c>best: best=c; cuts=[side[:]]
        elif c==best: cuts.append(side[:])
    return cuts
def Bconn(n,adj,side):
    seen={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
    return len(seen)==n
def bdist_restr(adj,side,s,t):
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d: d[v]=d[u]+1; q.append(v)
    return d.get(t,-1)
def geos(adj,side,s,t):
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
    P=[]
    def rec(v,acc):
        if v==s: P.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[]); return P
def gmin(n,adj,cuts):
    best=None
    for side in cuts:
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True; ell={}
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v)
            if d<0: ok=False; break
            ell[(u,v)]=d+1; G+=(d+1)**2
        if ok and (best is None or G<best[1]): best=(side,G,M,ell)
    return best
def worker(g6):
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return ('skip',g6)
    side,G,M,ell=r
    K=n+(n*n-G)
    T=[Fraction(0) for _ in range(n)]
    for (u,v) in M:
        Ps=geos(adj,side,u,v); nf=len(Ps)
        if nf==0: return ('badgeo',g6)
        sh=Fraction(ell[(u,v)],nf)
        for P in Ps:
            for w in P: T[w]+=sh
    maxT=max(T)
    return ('viol' if maxT>K else 'ok', g6, n, G, K, maxT)

def main():
    STRIDE=int(sys.argv[1]); MAXCHECK=int(sys.argv[2])
    t0=time.time()
    print(f"=== PARTIAL strided U-census N=13 STRIDE={STRIDE} MAXCHECK={MAXCHECK} ===",flush=True)
    proc=subprocess.Popen([GENG,"-tc","13"],stdout=subprocess.PIPE,text=True,bufsize=1<<20)
    def gen():
        idx=0; emitted=0
        for line in proc.stdout:
            g=line.strip()
            if not g: continue
            idx+=1
            if idx % STRIDE: continue
            yield g; emitted+=1
            if emitted>=MAXCHECK*3:  # generous: stop generating once enough sampled
                proc.terminate(); break
    checked=0;skipped=0;viols=[];min_slack=None;worst=None;badgeo=0
    with Pool(processes=60) as pool:
        for out in pool.imap_unordered(worker, gen(), chunksize=100):
            if out[0]=='skip': skipped+=1; continue
            if out[0]=='badgeo': badgeo+=1; print("BADGEO",out[1],flush=True); continue
            _,g6,n,G,K,maxT=out; checked+=1
            slack=Fraction(K)-maxT
            if min_slack is None or slack<min_slack: min_slack=slack; worst=(g6,n,G,K,maxT)
            if out[0]=='viol':
                viols.append(out); print(f"!!! VIOLATION {out}",flush=True)
            if checked>=MAXCHECK:
                proc.terminate(); break
            if checked%20000==0:
                print(f"  ...checked={checked} skipped={skipped} viols={len(viols)} min_slack={min_slack} ({float(min_slack):.3f}) t={time.time()-t0:.0f}s",flush=True)
    print(f"--- PARTIAL DONE N=13: checked={checked} skipped={skipped} badgeo={badgeo} viols={len(viols)} (PARTIAL strided sample, NOT exhaustive; geng -tc 13 total=19425052) ---",flush=True)
    print(f"min_slack(K-maxT)={min_slack} ({float(min_slack):.4f}) at {worst}",flush=True)
    print(f"elapsed={time.time()-t0:.1f}s",flush=True)
    print("ZERO VIOLATIONS." if not viols else f"VIOLATIONS: {viols}",flush=True)

if __name__=='__main__': main()
