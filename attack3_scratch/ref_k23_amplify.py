import itertools, numpy as np, random
from scipy.optimize import linprog
from collections import deque

def is_tf(adj,n):
    for u in range(n):
        for v in range(u+1,n):
            if adj[u][v]:
                for w in range(n):
                    if adj[u][w] and adj[v][w]: return False
    return True

def maxcut(adj,n):
    # heuristic + exact for small; for larger use repeated local search
    if n<=20:
        best=-1; bS=None
        for mask in range(1<<n):
            S=frozenset(i for i in range(n) if mask&(1<<i))
            c=sum(1 for u in range(n) for v in range(u+1,n) if adj[u][v] and ((u in S)!=(v in S)))
            if c>best: best=c; bS=S
        return best,bS
    # local search
    best=-1;bS=None
    for _ in range(400):
        S=set(i for i in range(n) if random.random()<0.5)
        improved=True
        while improved:
            improved=False
            for v in range(n):
                d=sum(1 for w in range(n) if adj[v][w] and (w in S))
                dn=sum(1 for w in range(n) if adj[v][w] and (w not in S))
                if (v in S and d>dn) or (v not in S and dn>d):
                    if v in S: S.discard(v)
                    else: S.add(v)
                    improved=True
        c=sum(1 for u in range(n) for v in range(u+1,n) if adj[u][v] and ((u in S)!=(v in S)))
        if c>best: best=c;bS=frozenset(S)
    return best,bS

def paths(A,n,s,t,maxlen=10):
    res=[]
    def dfs(u,p,seen):
        if u==t: res.append(p[:]); return
        if len(p)>maxlen: return
        for w in range(n):
            if A[u][w] and w not in seen:
                seen.add(w);p.append(w);dfs(w,p,seen);p.pop();seen.discard(w)
    dfs(s,[s],{s}); return res

def rho_for(n,adj,S):
    B=[(u,v) for u in range(n) for v in range(u+1,n) if adj[u][v] and ((u in S)!=(v in S))]
    M=[(u,v) for u in range(n) for v in range(u+1,n) if adj[u][v] and ((u in S)==(v in S))]
    if not M: return None,0
    A=[[0]*n for _ in range(n)]
    for u,v in B: A[u][v]=A[v][u]=1
    Bidx={(min(u,v),max(u,v)):i for i,(u,v) in enumerate(B)}; nB=len(B)
    vd=[];vi=[]
    for di,(u,v) in enumerate(M):
        pl=paths(A,n,u,v,maxlen=12)
        if not pl: return 999,len(M)
        for P in pl:
            inc=np.zeros(nB)
            for a,b in zip(P,P[1:]): inc[Bidx[(min(a,b),max(a,b))]]+=1
            vd.append(di); vi.append(inc)
    nf=len(vi); c=np.zeros(nf+1); c[-1]=1.0
    Aub=[];bub=[]
    for ei in range(nB):
        row=np.zeros(nf+1)
        for j in range(nf): row[j]=vi[j][ei]
        row[-1]=-1.0; Aub.append(row); bub.append(0.0)
    Aeq=[];beq=[]
    for di in range(len(M)):
        row=np.zeros(nf+1)
        for j in range(nf):
            if vd[j]==di: row[j]=1.0
        Aeq.append(row); beq.append(1.0)
    res=linprog(c,A_ub=np.array(Aub),b_ub=np.array(bub),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=[(0,None)]*nf+[(0,None)],method='highs')
    return (res.x[-1] if res.success else None),len(M)

# The K23 gadget on a base odd-K5-style structure.
# K23-N13: vertices 0,1 (the "2" side), 2,3,4 (the "3" side), each pair (0,1),(2,3),(2,4),(3,4)
#   joined by a length-3 B-path (x-a-b-y) so that the odd edge becomes a d_B=4 bad chord.
# This realizes the K_{2,3} 'odd-K5 minor' phenomenon. rho=1.333.
# AMPLIFY idea 1: BLOW UP each of the 5 core vertices into an independent set of size k.
def k23_blowup(k):
    # core K23: parts P2={A,B}, P3={C,D,E}; all P2-P3 edges. blow each to size k.
    # then add the 4 'odd-edge' gadgets between pairs that are non-adjacent in core but get a bad chord.
    # We replicate the exact N=13 gadget but with each of the 5 'core' roles a k-set, gadget verts shared?
    # Simplest faithful blow-up: take t disjoint copies of K23-N13 sharing nothing -> rho stays 1.333, m=4t, N=13t.
    pass

# Approach: t DISJOINT copies of K23 (independent gadgets). rho = max = 1.333 (disjoint),
#   m=4t, N=13t, bound = max(1, (13t)^2/(25*4t)) = 169t/100 -> grows with t, so bound gets EASIER. Not useful.
# Approach: OVERLAP copies to keep N small while m grows. Build a 'cycle' of K23 gadgets.

def build_k23():
    N=13; adj=[[0]*N for _ in range(N)]
    def add(u,v): adj[u][v]=adj[v][u]=1
    for i in (0,1):
        for j in (2,3,4): add(i,j)
    nxt=5
    for (x,y) in [(0,1),(2,3),(2,4),(3,4)]:
        a,b=nxt,nxt+1; nxt+=2; add(x,a); add(a,b); add(b,y)
    return N,adj

# t disjoint K23 copies sharing the SAME 5 core vertices? Core {0,1,2,3,4} reused, only gadget chains fresh.
# That would create more bad chords among the same 5 vertices -> but bad chords are the odd edges; reusing
# core means multiple parallel gadgets -> multi-edges. Instead, chain via shared core vertices in a path.

def chain_k23(t):
    # t copies, copy i uses core vertices c_i0..c_i4, and we IDENTIFY c_{i,1} with c_{i+1,0} to share.
    # Keep it simple: t fully disjoint copies but then add cross bad-edges? Risky for triangle-free.
    # Just do disjoint and report (sanity: rho stays 1.333, bound grows).
    blocks=[]; off=0; adjbig={};
    N,adj=build_k23()
    big=[]
    total=0
    cells=[]
    for i in range(t):
        cells.append((total,total+N)); total+=N
    A=[[0]*total for _ in range(total)]
    for i in range(t):
        base=cells[i][0]
        for u in range(N):
            for v in range(u+1,N):
                if adj[u][v]: A[base+u][base+v]=A[base+v][base+u]=1
    return total,A

for t in [1,2,3]:
    n,adj=chain_k23(t)
    mc,S=maxcut(adj,n)
    r,m=rho_for(n,adj,S)
    print('disjoint K23 x%d: N=%d m=%d rho=%s bound=%.4f'%(t,n,m,('%.4f'%r if r else r), max(1,n*n/(25*m)) if m else 0))
