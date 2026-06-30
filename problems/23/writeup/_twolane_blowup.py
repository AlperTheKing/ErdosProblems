"""SHARPEST SBC stress: BLOW UP the two-lane (which has high rho(O)/N) by factor q -> high rho AND high |M|
simultaneously (the only regime that could break SBC: rho(O)+|M| both large). Blow-up of triangle-free is
triangle-free; inherited side. Verify GLOBAL max cut via CP-SAT, then EXACT rational-LDL SBC: (N+N^2/25-|M|)I-O PSD.
Also report SBC-row max_f (O1)_f + |M| <= N+N^2/25 (stronger per-edge form)."""
from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side
from _verify_two_lane import build_two_lane
from ortools.sat.python import cp_model

def blowup_graph(n0,E0,side0,q):
    # vertex v -> copies v*q..v*q+q-1 ; edge (u,v) -> complete bipartite between groups
    n=n0*q
    E=set()
    for (u,v) in E0:
        for i in range(q):
            for j in range(q):
                a=u*q+i; b=v*q+j; E.add((min(a,b),max(a,b)))
    side=[0]*n
    for v in range(n0):
        for i in range(q): side[v*q+i]=side0[v]
    return n,sorted(E),side

def cpmax(n,edges,tl=60):
    m=cp_model.CpModel(); x=[m.NewBoolVar("x%d"%i) for i in range(n)]; t=[]
    for a,b in edges:
        z=m.NewBoolVar("e%d_%d"%(a,b)); m.AddBoolXOr([x[a],x[b],z.Not()]); t.append(z)
    m.Maximize(sum(t)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=tl
    st=s.Solve(m); return int(s.ObjectiveValue()), s.BestObjectiveBound()

def build_O(n,M,cyc):
    pf=[]
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf.append(d)
    m=len(M); O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        for j in range(i,m):
            s=F(0); di=pf[i]; dj=pf[j]
            for v,pv in di.items():
                if v in dj: s+=pv*dj[v]
            O[i][j]=s; O[j][i]=s
    return O

def is_psd(A):
    m=len(A); Aw=[r[:] for r in A]
    for k in range(m):
        piv=Aw[k][k]
        if piv<0: return False
        if piv==0:
            for j in range(m):
                if Aw[k][j]!=0: return False
            continue
        for i in range(k+1,m):
            if Aw[i][k]==0: continue
            f=Aw[i][k]/piv
            for j in range(k,m): Aw[i][j]-=f*Aw[k][j]
    return True

def analyze(L,q):
    n0,E0,side0,bad=build_two_lane(L)
    n,E,side=blowup_graph(n0,E0,side0,q)
    if n>96: print("L=%d q=%d N=%d too big"%(L,q,n)); return
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    bc=Bconn(n,adj,side)
    cut=sum(1 for x,y in E if side[x]!=side[y])
    opt,bd=cpmax(n,E)
    glob = (cut==opt==bd)
    st=struct_for_side(n,adj,side)
    if st is None: print("L=%d q=%d struct None"%(L,q)); return
    M,ell,T,mu,cyc=st; m=len(M); O=build_O(n,M,cyc)
    Gamma=sum(T); c=F(n)+F(n*n,25)-m
    A=[[ (c-O[i][j]) if i==j else (-O[i][j]) for j in range(m)] for i in range(m)]
    sbc_ok=is_psd(A)
    rowsums=[sum(O[i][j] for j in range(m)) for i in range(m)]
    maxrow=max(rowsums) if rowsums else F(0)
    sbcrow = (maxrow + m <= F(n)+F(n*n,25))
    # lower bound rho >= sumT^2/Gamma
    sumT2=sum(t*t for t in T); rho_lb=sumT2/Gamma if Gamma>0 else F(0)
    print("L=%2d q=%d N=%2d cut=%d global-max=%s Bconn=%s |M|=%d Gamma=%d N^2=%d Gamma<=N^2:%s"%(
        L,q,n,cut,glob,bc,m,Gamma,n*n,Gamma<=n*n))
    print("    rho_lb=sumT^2/Gamma=%s  c=N+N^2/25-|M|=%s   SBC (c*I-O PSD): %s   SBC-row: %s   maxrowO=%s"%(
        str(float(rho_lb))[:7],str(float(c))[:7],"HOLDS" if sbc_ok else "*** FAILS ***","HOLDS" if sbcrow else "FAILS",str(maxrow)))

if __name__=="__main__":
    for (L,q) in [(8,2),(8,3),(12,2),(8,4),(12,3),(16,2)]:
        analyze(L,q)
