"""Bridge check: rho(K) <= A via the PROVEN diag(T)-K >= L_omega >= 0.
For Perron x of K (Kx=rho x, x>=0): rho = x^T K x/||x||^2 <= [sum_v T x^2 - x^T L_omega x]/||x||^2.
So define  BR(x) := (sum_v T(v) x(v)^2 - x^T L_omega x)/||x||^2  evaluated at the Perron vector.
Claim-to-bridge: BR(perron) <= A even though max_v T(v) > A (the L_omega term redistributes).
Also report: does diag(T)-K >= L_omega actually hold exactly (PSD)? (the PROVEN local lemma).
Test on the max-T-failing fans + two-lane + C5[t]."""
from fractions import Fraction as F
import numpy as np
from _satzmu_conn import struct_for_side
from _h import Bconn, maxcut_all, bdist_restr

def a_bar(ell): return F(ell**3, 4*(ell*ell-2))

def gmins(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

def build(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return None
    N=n; m=len(M)
    # K
    K=[[F(0)]*n for _ in range(n)]
    Lom=[[F(0)]*n for _ in range(n)]
    for f in M:
        Ps=cyc[f]; k=len(Ps); L=ell[f]; ae=a_bar(L)
        pf={}
        for P in Ps:
            for v in P: pf[v]=pf.get(v,F(0))+F(1,k)
        it=list(pf.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
        # tau_f edges: f itself weight 1, geodesic edges weight 1/k each occurrence
        tau={}
        ef=(min(f),max(f)); tau[ef]=F(1)
        for P in Ps:
            for i in range(len(P)-1):
                e2=(min(P[i],P[i+1]),max(P[i],P[i+1])); tau[e2]=tau.get(e2,F(0))+F(1,k)
        for (u,v),w in tau.items():
            ww=ae*w
            Lom[u][u]+=ww; Lom[v][v]+=ww; Lom[u][v]-=ww; Lom[v][u]-=ww
    return K,Lom,T,N,m,ell,M

def analyze(name,n,adj,side):
    if not Bconn(n,adj,side): return
    r=build(n,adj,side)
    if r is None: return
    K,Lom,T,N,m,ell,M=r; A=N+N*N/25.0-m
    Kf=np.array([[float(x) for x in row] for row in K])
    Lf=np.array([[float(x) for x in row] for row in Lom])
    Df=np.diag([float(T[v]) for v in range(n)])
    # PROVEN: diag(T)-K-L_omega >= 0 ? check min eig
    R=Df-Kf-Lf
    minR=min(np.linalg.eigvalsh(R))
    # Perron of K
    w,V=np.linalg.eigh(Kf); rho=w[-1]; x=V[:,-1]; x=np.abs(x)
    nx2=float(x@x)
    diagpart=float(x@(Df@x))/nx2
    lompart=float(x@(Lf@x))/nx2
    BR=diagpart-lompart
    maxT=max(float(T[v]) for v in range(n))
    print(f"  {name}: N={n} m={m} A={A:.2f} | maxT={maxT:.2f}(>A:{maxT>A}) rho(K)={rho:.3f}(<=A:{rho<=A+1e-7}) "
          f"| Perron: diagT-part={diagpart:.3f} L_om-part={lompart:.3f} BR={BR:.3f}(<=A:{BR<=A+1e-7}) "
          f"| diag(T)-K-L_om PSD: minEig={minR:+.4f}")

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def build_two_lane(L):
    a=lambda i:(L+1)+i; b=lambda i:(L+1)+(L+1)+i
    n=3*(L+1); E=set()
    for i in range(L): E.add((i,i+1))
    for i in range(L+1):
        E.add((min(i,a(i)),max(i,a(i)))); E.add((min(i,b(i)),max(i,b(i))))
    for i in range(L):
        for u in (a(i),b(i)):
            for v in (a(i+1),b(i+1)): E.add((min(u,v),max(u,v)))
    for e in [(0,L-2),(0,L),(2,L-2),(2,L)]: E.add((min(e),max(e)))
    side=[0]*n
    for i in range(L+1): side[i]=i%2
    for i in range(L+1): side[a(i)]=1-(i%2); side[b(i)]=1-(i%2)
    return n,sorted(E),side

if __name__=="__main__":
    print("--- max-T-FAILING fans (maxT>A) : does L_omega rescue rho<=A and BR<=A? ---")
    for sizes in [[3,9,1,9,3],[2,10,1,10,2],[9,1,9,1,9]]:
        n,E=blowup(sizes); adj,cuts=gmins(n,E)
        for s in cuts[:1]: analyze("fan%s"%sizes,n,adj,s)
    print("--- two-lane ---")
    for L in (8,12,16):
        n,E,side=build_two_lane(L)
        adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        analyze("twolane%d"%L,n,adj,side)
    print("--- C5[t] (tight) ---")
    for t in (1,2,3):
        n,E=blowup([t]*5); adj,cuts=gmins(n,E)
        for s in cuts[:1]: analyze("C5[%d]"%t,n,adj,s)
