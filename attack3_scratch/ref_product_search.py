import itertools, numpy as np, random
from scipy.optimize import linprog

def is_tf(adj,n):
    for u in range(n):
        for v in range(u+1,n):
            if adj[u][v]:
                for w in range(n):
                    if adj[u][w] and adj[v][w]: return False
    return True

def maxcut_exact(adj,n):
    best=-1; bS=None
    for mask in range(1<<n):
        S=frozenset(i for i in range(n) if mask&(1<<i))
        c=sum(1 for u in range(n) for v in range(u+1,n) if adj[u][v] and ((u in S)!=(v in S)))
        if c>best: best=c; bS=S
    return best,bS

def paths(A,n,s,t,maxlen=12):
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

# Petersen (known non-bipartite, girth 5, vertex-transitive) is the prime suspect for a SECOND
# tight-ish non-L1 family. Build Petersen and several odd-K5 subdivisions / Kneser-like graphs.
def petersen():
    verts=list(itertools.combinations(range(5),2)); n=10
    adj=[[0]*n for _ in range(n)]
    for i,a in enumerate(verts):
        for j,b in enumerate(verts):
            if i<j and not (set(a)&set(b)): adj[i][j]=adj[j][i]=1
    return n,adj

# C5 with all 5 chords subdivided -> the M-5-cycle from m5cycle (N=20). Already rho?
# Test a family: subdivide odd-K5 = K5 with each edge subdivided once (Petersen-ish?), check tf.

def subdivided_complete(k):
    # K_k with every edge subdivided once: bipartite? No—becomes bipartite incidence-like, girth depends.
    core=list(range(k)); n=k; adj=[[0]*(k+k*(k-1)//2) for _ in range(k+k*(k-1)//2)]
    nodes=k; edges=[]
    nxt=k
    for u in range(k):
        for v in range(u+1,k):
            m=nxt; nxt+=1
            adj[u][m]=adj[m][u]=1; adj[v][m]=adj[m][v]=1
    return nxt,adj

cases=[('Petersen',)+petersen(), ('subdivK5',)+subdivided_complete(5)]
worst=0; wc=None
for nm,n,adj in cases:
    if not is_tf(adj,n):
        print(nm,'NOT triangle-free -> skip'); continue
    if n>20:
        print(nm,'too big for exact maxcut'); continue
    mc,S=maxcut_exact(adj,n)
    r,m=rho_for(n,adj,S)
    if r is None or r==999:
        print(nm,'N=%d no M or disconnected B (m=%d)'%(n,m)); continue
    bound=max(1,n*n/(25*m)); prod=r*25*m/(n*n)
    print('%-12s N=%d m=%d rho=%.4f bound=%.4f  rho*25m/N^2=%.4f'%(nm,n,m,r,bound,prod))
    if prod>worst: worst=prod; wc=nm
print('worst product rho*25m/N^2 =',round(worst,4),'at',wc,'(>1 would break KEY LEMMA)')
