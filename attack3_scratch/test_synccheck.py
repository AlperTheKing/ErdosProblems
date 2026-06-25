import itertools
from itertools import combinations, product
from collections import deque
import numpy as np
from scipy.optimize import linprog

def build_c5_of_paths():
    xs=list(range(5))
    idx={}
    c=5
    for i in range(5):
        for t in ['y','z','w']:
            idx[(t,i)]=c; c+=1
    n=c
    B=set(); M=set()
    for i in range(5):
        a,b=xs[i],xs[(i+1)%5]; M.add((min(a,b),max(a,b)))
    for i in range(5):
        path=[xs[i], idx[('y',i)], idx[('z',i)], idx[('w',i)], xs[(i+1)%5]]
        for a,b in zip(path,path[1:]):
            B.add((min(a,b),max(a,b)))
    return n,sorted(B),sorted(M)

def adj_from(n,B):
    A=[[0]*n for _ in range(n)]
    for u,v in B: A[u][v]=A[v][u]=1
    return A

def all_simple_paths(A,n,s,t,maxlen=12):
    res=[]
    def dfs(u,path,seen):
        if u==t:
            res.append(path[:]); return
        if len(path)>maxlen: return
        for w in range(n):
            if A[u][w] and w not in seen:
                seen.add(w); path.append(w); dfs(w,path,seen); path.pop(); seen.discard(w)
    dfs(s,[s],{s})
    return res

def rho_lp(n,B,M):
    A=adj_from(n,B)
    Bidx={e:i for i,e in enumerate(B)}
    nB=len(B)
    pathlists=[]
    for (u,v) in M:
        paths=all_simple_paths(A,n,u,v)
        pl=[]
        for P in paths:
            inc=np.zeros(nB)
            for a,b in zip(P,P[1:]):
                inc[Bidx[(min(a,b),max(a,b))]]+=1
            pl.append(inc)
        pathlists.append(pl)
    var_demand=[]; var_inc=[]
    for di,pl in enumerate(pathlists):
        for inc in pl:
            var_demand.append(di); var_inc.append(inc)
    nf=len(var_inc)
    c=np.zeros(nf+1); c[-1]=1.0
    A_ub=[]; b_ub=[]
    for ei in range(nB):
        row=np.zeros(nf+1)
        for j in range(nf): row[j]=var_inc[j][ei]
        row[-1]=-1.0
        A_ub.append(row); b_ub.append(0.0)
    A_eq=[]; b_eq=[]
    for di in range(len(M)):
        row=np.zeros(nf+1)
        for j in range(nf):
            if var_demand[j]==di: row[j]=1.0
        A_eq.append(row); b_eq.append(1.0)
    bounds=[(0,None)]*nf+[(0,None)]
    res=linprog(c,A_ub=np.array(A_ub),b_ub=np.array(b_ub),A_eq=np.array(A_eq),b_eq=np.array(b_eq),bounds=bounds,method='highs')
    return res.x[-1] if res.success else None

n,B,M=build_c5_of_paths()
m=len(M)
print(f"C5-of-paths: N={n}, |B|={len(B)}, m={m}, N^2/(25m)={n*n/(25*m):.4f}")
r=rho_lp(n,B,M)
if r is not None:
    print(f"  rho = {r:.4f}, bound max(1,N^2/(25m))={max(1,n*n/(25*m)):.4f}, QFC25 holds: {r<=max(1,n*n/(25*m))+1e-9}")
else:
    print("  LP failed")
