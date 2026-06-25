import numpy as np
from itertools import combinations
from scipy.optimize import linprog

def gpt_k23():
    N=13; adj=[[0]*N for _ in range(N)]
    def add(u,v): adj[u][v]=adj[v][u]=1
    for i in (0,1):
        for j in (2,3,4): add(i,j)
    nxt=5
    for (x,y) in [(0,1),(2,3),(2,4),(3,4)]:
        a,b=nxt,nxt+1; nxt+=2; add(x,a); add(a,b); add(b,y)
    return N,adj

def maxcut(adj,n):
    best=-1;bx=None
    for mask in range(1<<n):
        Xs=frozenset(i for i in range(n) if mask&(1<<i)); c=0
        for u in range(n):
            for v in range(u+1,n):
                if adj[u][v] and ((u in Xs)!=(v in Xs)): c+=1
        if c>best: best=c;bx=Xs
    return best,bx

def all_simple_paths(A,n,s,t,maxlen=12):
    res=[]
    def dfs(u,path,seen):
        if u==t: res.append(path[:]);return
        if len(path)>maxlen: return
        for w in range(n):
            if A[u][w] and w not in seen:
                seen.add(w);path.append(w);dfs(w,path,seen);path.pop();seen.discard(w)
    dfs(s,[s],{s});return res

N,adj=gpt_k23()
mc,Xs=maxcut(adj,N)
B=[];M=[]
for u in range(N):
    for v in range(u+1,N):
        if adj[u][v]:
            if (u in Xs)!=(v in Xs): B.append((u,v))
            else: M.append((u,v))
m=len(M)
print(f"K23-N13: N={N}, maxcut={mc}, |B|={len(B)}, m={m}, N^2/(25m)={N*N/(25*m):.4f}")
Bi={e:i for i,e in enumerate(B)}; nB=len(B)
A=[[0]*N for _ in range(N)]
for u,v in B: A[u][v]=A[v][u]=1
pls=[]
for (u,v) in M:
    pl=[]
    for P in all_simple_paths(A,N,u,v):
        inc=np.zeros(nB)
        for a,b in zip(P,P[1:]): inc[Bi[(min(a,b),max(a,b))]]+=1
        pl.append(inc)
    pls.append(pl)
vd=[];vi=[]
for di,pl in enumerate(pls):
    for inc in pl: vd.append(di);vi.append(inc)
nf=len(vi);c=np.zeros(nf+1);c[-1]=1
Aub=[];bub=[]
for ei in range(nB):
    row=np.zeros(nf+1)
    for j in range(nf): row[j]=vi[j][ei]
    row[-1]=-1;Aub.append(row);bub.append(0)
Aeq=[];beq=[]
for di in range(m):
    row=np.zeros(nf+1)
    for j in range(nf):
        if vd[j]==di: row[j]=1
    Aeq.append(row);beq.append(1)
res=linprog(c,A_ub=np.array(Aub),b_ub=np.array(bub),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=[(0,None)]*nf+[(0,None)],method='highs')
print(f"  rho = {res.x[-1]:.4f}  (this is the genuine rho>1 obstruction)")
print(f"  bound max(1,N^2/(25m)) = {max(1,N*N/(25*m)):.4f}, slack = {max(1,N*N/(25*m))-res.x[-1]:.4f}")
