import numpy as np
from scipy.optimize import linprog
from mycielskian_check import mycielskian, edges_of, gamma_min_cut, all_shortest_geos

def uniform_Tv(N,adj,side,M):
    Tv=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        h=len(geos[0])
        for P in geos:
            for x in P: Tv[x]+=h/len(geos)
    return Tv

def lp_Tv(N,adj,side,M):
    paths=[];pe=[];he=[];edge_paths=[]
    for ei,(u,v) in enumerate(M):
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        h=len(geos[0]); he.append(h); idxs=[]
        for P in geos:
            idxs.append(len(paths)); paths.append(P); pe.append(ei)
        edge_paths.append(idxs)
    nvar=len(paths)+1; tau=len(paths)
    c=np.zeros(nvar); c[tau]=1.0
    Aeq=np.zeros((len(M),nvar)); beq=np.ones(len(M))
    for ei,idxs in enumerate(edge_paths):
        for k in idxs: Aeq[ei,k]=1.0
    Aub=np.zeros((N,nvar))
    for k,P in enumerate(paths):
        w=he[pe[k]]
        for v in P: Aub[v,k]+=w
    for v in range(N): Aub[v,tau]=-1.0
    res=linprog(c,A_ub=Aub,b_ub=np.zeros(N),A_eq=Aeq,b_eq=beq,bounds=[(0,None)]*nvar,method="highs")
    if not res.success: return None
    x=res.x[:len(paths)]; return Aub[:,:len(paths)].dot(x), res.fun

def report(name,N,adj,side,G,M):
    K=N+(N*N-G)
    Tu=uniform_Tv(N,adj,side,M)
    print("\n=== %s N=%d beta=%d Gamma=%d N^2=%d deficit=%d K=%d ==="%(name,N,len(M),G,N*N,N*N-G,K))
    if Tu is not None:
        Ou=np.maximum(0,Tu-N).sum(); Uu=np.maximum(0,N-Tu).sum()
        idok=abs((N-Tu).sum()-(N*N-G))<1e-6
        print("  UNIFORM: sumT=%.3f(Gamma?%s) maxT=%.4f O=%.4f U=%.4f 2O<=U?%s slack=%.4f AMI(O<=def)?%s idok=%s"%(
            Tu.sum(),abs(Tu.sum()-G)<1e-6,Tu.max(),Ou,Uu,2*Ou<=Uu+1e-9,Uu-2*Ou,Ou<=N*N-G+1e-9,idok))
    r=lp_Tv(N,adj,side,M)
    if r is not None:
        Tl,tau=r
        Ol=np.maximum(0,Tl-N).sum(); Ul=np.maximum(0,N-Tl).sum()
        print("  LP     : tau*=%.4f<=K?%s maxT=%.4f O=%.4f U=%.4f 2O<=U?%s AMI(O<=def)?%s"%(
            tau,tau<=K+1e-6,Tl.max(),Ol,Ul,2*Ol<=Ul+1e-9,Ol<=N*N-G+1e-9))

def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; side=[0]*n; adj=[set() for _ in range(n)]
    for i in range(5):
        for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
    M=[(vid(4,a),vid(0,b)) for a in range(q) for b in range(q)]; G=25*len(M)
    return n,adj,side,G,M

for q in (2,3,4,5,8):
    n,adj,side,G,M=C5q(q); report("C5[%d]"%q,n,adj,side,G,M)

pet_adj=[set() for _ in range(10)]
for i in range(5):
    for (a,b) in [(i,(i+1)%5),(5+i,5+(i+2)%5),(i,5+i)]: pet_adj[a].add(b); pet_adj[b].add(a)
N,adj=mycielskian(10,edges_of(pet_adj))
res,mc=gamma_min_cut(N,adj,edges_of(adj))
if res:
    side,G,M=res; report("M(Petersen)",N,adj,side,G,M)

C5=[(i,(i+1)%5) for i in range(5)]
gN,gadj=mycielskian(5,C5)
N,adj=mycielskian(gN,edges_of(gadj))
res,mc=gamma_min_cut(N,adj,edges_of(adj))
if res:
    side,G,M=res; report("M(Grotzsch)",N,adj,side,G,M)
print("\nDONE")
