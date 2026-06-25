import itertools, math
from collections import deque
from scipy.optimize import linprog
import numpy as np

def maxcut(adj,n):
    best=-1;bx=None
    for mask in range(1<<n):
        Xs=frozenset(i for i in range(n) if mask&(1<<i)); c=0
        for u in range(n):
            for v in range(u+1,n):
                if adj[u][v] and ((u in Xs)!=(v in Xs)): c+=1
        if c>best: best=c;bx=Xs
    return best,bx

def all_odd_cycles(adj,n):
    seen=set(); out=[]
    def dfs(start,u,path,ps):
        for w in range(n):
            if not adj[u][w]: continue
            if w==start and len(path)>=3 and len(path)%2==1:
                es=frozenset(frozenset((path[i],path[(i+1)%len(path)])) for i in range(len(path)))
                if es not in seen: seen.add(es); out.append((tuple(path),es))
            elif w not in ps and w>start and len(path)<n:
                path.append(w); ps.add(w); dfs(start,w,path,ps); path.pop(); ps.discard(w)
    for s in range(n): dfs(s,s,[s],{s})
    return out

def edges_of(adj,n):
    return [(u,v) for u in range(n) for v in range(u+1,n) if adj[u][v]]

def nu_star(adj,n):
    E=edges_of(adj,n); cyc=all_odd_cycles(adj,n)
    if not cyc: return 0.0,[],None
    eidx={frozenset(e):i for i,e in enumerate(E)}; nC=len(cyc); nE=len(E)
    Aub=np.zeros((nE,nC))
    for j,(_,es) in enumerate(cyc):
        for e in es: Aub[eidx[e],j]=1.0
    res=linprog(-np.ones(nC),A_ub=Aub,b_ub=np.ones(nE),bounds=[(0,None)]*nC,method="highs")
    return -res.fun,cyc,res.x

def nu_int(adj,n):
    E=edges_of(adj,n); cyc=all_odd_cycles(adj,n)
    if not cyc: return 0,[]
    eidx={frozenset(e):i for i,e in enumerate(E)}; nC=len(cyc); nE=len(E)
    Aub=np.zeros((nE,nC))
    for j,(_,es) in enumerate(cyc):
        for e in es: Aub[eidx[e],j]=1.0
    res=linprog(-np.ones(nC),A_ub=Aub,b_ub=np.ones(nE),bounds=[(0,1)]*nC,method="highs",integrality=np.ones(nC))
    return int(round(-res.fun)),res.x

def greedy_pack(adj,n,M,Bset):
    Badj=[[1 if (adj[u][v] and ((min(u,v),max(u,v)) in Bset)) else 0 for v in range(n)] for u in range(n)]
    used_edges=set(); cycles=[]; Mrem=list(M)
    while Mrem:
        mu,mv=Mrem.pop(0)
        if (min(mu,mv),max(mu,mv)) in used_edges: continue
        dist=[math.inf]*n; par=[-1]*n; dist[mu]=0; q=deque([mu])
        while q:
            x=q.popleft()
            for y in range(n):
                if Badj[x][y] and (min(x,y),max(x,y)) not in used_edges and dist[y]==math.inf:
                    dist[y]=dist[x]+1; par[y]=x; q.append(y)
        if dist[mv]==math.inf: continue
        path=[]; x=mv
        while x!=-1: path.append(x); x=par[x]
        path=path[::-1]
        ces=set([(min(mu,mv),max(mu,mv))])
        for a,b in zip(path,path[1:]): ces.add((min(a,b),max(a,b)))
        used_edges|=ces
        cycles.append(path)
    return cycles

def analyze(name,adj,n):
    mc,Xs=maxcut(adj,n)
    M=[(u,v) for u in range(n) for v in range(u+1,n) if adj[u][v] and ((u in Xs)==(v in Xs))]
    Bset=set((u,v) for u in range(n) for v in range(u+1,n) if adj[u][v] and ((u in Xs)!=(v in Xs)))
    m=len(M)
    nus,_,_=nu_star(adj,n)
    nui,_=nu_int(adj,n)
    target=25*m*m/(n*n)
    gp=greedy_pack(adj,n,M,Bset)
    p_greedy=len(gp)
    print("=== %s: N=%d, m=tau=%d, MaxCut=%d ==="%(name,n,m,mc))
    print("   nu*(frac)=%.4f  nu_int(max edge-disjoint odd packing)=%d"%(nus,nui))
    print("   STRATEGY target p >= 25*tau^2/N^2 = %.4f"%target)
    print("   greedy region-grow extracted p = %d  cycle lengths %s"%(p_greedy,[len(c) for c in gp]))
    Tbound=(n/5)*math.sqrt(nus)
    print("   (T) tau <= (N/5)sqrt(nu*): %d <= %.4f -> %s"%(m,Tbound,"OK" if m<=Tbound+1e-9 else "FAIL"))
    print("   greedy meets target? p=%d >= %.4f? %s"%(p_greedy,target,"YES" if p_greedy>=target-1e-9 else "NO  <<<<<<"))
    print("   nu_int meets target?  %d >= %.4f? %s"%(nui,target,"YES" if nui>=target-1e-9 else "NO  <<<<<<"))
    print()

def grid3():
    n=9; adj=[[0]*n for _ in range(n)]
    def idx(r,c): return r*3+c
    for r in range(3):
        for c in range(3):
            if c<2: a,b=idx(r,c),idx(r,c+1); adj[a][b]=adj[b][a]=1
            if r<2: a,b=idx(r,c),idx(r+1,c); adj[a][b]=adj[b][a]=1
    adj[0][8]=adj[8][0]=1; adj[2][6]=adj[6][2]=1
    return adj,n

def gpt_k23():
    N=13; adj=[[0]*N for _ in range(N)]
    def add(u,v): adj[u][v]=adj[v][u]=1
    for i in (0,1):
        for j in (2,3,4): add(i,j)
    nxt=5
    for (x,y) in [(0,1),(2,3),(2,4),(3,4)]:
        a,b=nxt,nxt+1; nxt+=2; add(x,a); add(a,b); add(b,y)
    return adj,N

def c5blow(k):
    n=5*k; adj=[[0]*n for _ in range(n)]
    def grp(g,i): return g*k+i
    for g in range(5):
        h=(g+1)%5
        for i in range(k):
            for j in range(k):
                a,b=grp(g,i),grp(h,j); adj[a][b]=adj[b][a]=1
    return adj,n

analyze("3x3-grid-obstruction",*grid3())
analyze("K23-N13",*gpt_k23())
analyze("C5[2]",*c5blow(2))
analyze("C5[1]=C5",*c5blow(1))
