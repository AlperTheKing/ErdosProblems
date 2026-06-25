import itertools
from itertools import combinations
from collections import deque
import numpy as np
from scipy.optimize import linprog

# For a given (B,M) instance, the dual MT25 worst metric ell* is the B-shortest-path
# metric realizing rho. Strategy 1 asks: decompose ell as nonneg comb of CUT metrics
# (indicator of delta_B(S)) plus an L1-residual. We compute, for the worst ell*,
# whether the *path metric* d^B_ell restricted to V is itself L1-embeddable, and if
# not, the L1-distortion. Here we just test the cleanest statement:
#   On the M-pairs, is sum_M d^B(u,v) <= rho * sum_b ell_b achievable with a CUT metric?
# i.e. is the binding ell* in the cut cone? If yes for all small instances -> the
# difficulty is only realized by graphs whose B-metric on M-pairs is non-L1.

def maxcut(adj,n):
    best=-1;bx=None
    for mask in range(1<<n):
        Xs=frozenset(i for i in range(n) if mask&(1<<i)); c=0
        for u in range(n):
            for v in range(u+1,n):
                if adj[u][v] and ((u in Xs)!=(v in Xs)): c+=1
        if c>best: best=c;bx=Xs
    return best,bx

def split(adj,n):
    mc,Xs=maxcut(adj,n)
    B=[];M=[]
    for u in range(n):
        for v in range(u+1,n):
            if adj[u][v]:
                if (u in Xs)!=(v in Xs): B.append((u,v))
                else: M.append((u,v))
    return B,M,Xs

def adj_from(n,B):
    A=[[0]*n for _ in range(n)]
    for u,v in B: A[u][v]=A[v][u]=1
    return A

def all_simple_paths(A,n,s,t,maxlen=10):
    res=[]
    def dfs(u,path,seen):
        if u==t: res.append(path[:]); return
        if len(path)>maxlen: return
        for w in range(n):
            if A[u][w] and w not in seen:
                seen.add(w);path.append(w);dfs(w,path,seen);path.pop();seen.discard(w)
    dfs(s,[s],{s})
    return res

def rho_lp(n,B,M):
    A=adj_from(n,B); Bidx={e:i for i,e in enumerate(B)}; nB=len(B)
    pathlists=[]
    for (u,v) in M:
        pl=[]
        for P in all_simple_paths(A,n,u,v):
            inc=np.zeros(nB)
            for a,b in zip(P,P[1:]): inc[Bidx[(min(a,b),max(a,b))]]+=1
            pl.append(inc)
        if not pl: return None
        pathlists.append(pl)
    var_demand=[];var_inc=[]
    for di,pl in enumerate(pathlists):
        for inc in pl: var_demand.append(di);var_inc.append(inc)
    nf=len(var_inc); c=np.zeros(nf+1);c[-1]=1.0
    A_ub=[];b_ub=[]
    for ei in range(nB):
        row=np.zeros(nf+1)
        for j in range(nf): row[j]=var_inc[j][ei]
        row[-1]=-1.0; A_ub.append(row);b_ub.append(0.0)
    A_eq=[];b_eq=[]
    for di in range(len(M)):
        row=np.zeros(nf+1)
        for j in range(nf):
            if var_demand[j]==di: row[j]=1.0
        A_eq.append(row);b_eq.append(1.0)
    bounds=[(0,None)]*nf+[(0,None)]
    res=linprog(c,A_ub=np.array(A_ub),b_ub=np.array(b_ub),A_eq=np.array(A_eq),b_eq=np.array(b_eq),bounds=bounds,method='highs')
    return res.x[-1] if res.success else None

# random triangle-free, take maxcut, compute rho, check max over instances where rho>1
import random
def is_tf(adj,n):
    for u in range(n):
        for v in range(u+1,n):
            if adj[u][v]:
                for w in range(n):
                    if adj[u][w] and adj[v][w]: return False
    return True

random.seed(7)
worst=0; worstinfo=None; count_rho_gt1=0; total=0
for n in range(7,11):
    edges=list(combinations(range(n),2))
    for _ in range(3000):
        adj=[[0]*n for _ in range(n)]
        order=edges[:]; random.shuffle(order)
        for (u,v) in order:
            adj[u][v]=adj[v][u]=1
            bad=False
            for w in range(n):
                if adj[u][w] and adj[v][w]: bad=True;break
            if bad: adj[u][v]=adj[v][u]=0
        B,M,Xs=split(adj,n)
        if not M: continue
        r=rho_lp(n,B,M)
        if r is None: continue
        total+=1
        m=len(M); bound=max(1.0,n*n/(25*m))
        if r>1.0001: count_rho_gt1+=1
        ratio=r/bound
        if ratio>worst: worst=ratio; worstinfo=(n,m,r,bound)
print(f"instances tested: {total}, with rho>1: {count_rho_gt1}")
print(f"worst rho/bound ratio = {worst:.4f}  (n,m,rho,bound)={worstinfo}")
print("QFC25 holds on all:", worst<=1.0+1e-6)
