import itertools, numpy as np, random
from scipy.optimize import linprog

def maxcut(adj,n):
    best=-1; allb=[]
    for mask in range(1<<n):
        S=frozenset(i for i in range(n) if mask&(1<<i))
        c=sum(1 for u in range(n) for v in range(u+1,n) if adj[u][v] and ((u in S)!=(v in S)))
        if c>best: best=c; allb=[S]
        elif c==best: allb.append(S)
    return best,allb

def is_tf(adj,n):
    for u in range(n):
        for v in range(u+1,n):
            if adj[u][v]:
                for w in range(n):
                    if adj[u][w] and adj[v][w]: return False
    return True

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
        pl=paths(A,n,u,v)
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

random.seed(3)
maxrho=0; found=0; total=0; worst=None
for n in range(5,10):
    edges=list(itertools.combinations(range(n),2))
    for _ in range(4000):
        adj=[[0]*n for _ in range(n)]
        order=edges[:]; random.shuffle(order)
        for u,v in order:
            adj[u][v]=adj[v][u]=1
            ok=True
            for w in range(n):
                if adj[u][w] and adj[v][w]: ok=False;break
            if not ok: adj[u][v]=adj[v][u]=0
        if not is_tf(adj,n): continue
        mc,cuts=maxcut(adj,n)
        for S in cuts[:6]:
            r,m=rho_for(n,adj,S)
            if r is None or r==999: continue
            total+=1
            if r>1.0001:
                found+=1
                if r>maxrho: maxrho=r; worst=(n,m,r,max(1,n*n/(25*m)))
print('n in 5..9 random TF: maxcut-decomps tested=%d, with rho>1: %d, max rho=%.4f, worst=%s'%(total,found,maxrho,worst))
