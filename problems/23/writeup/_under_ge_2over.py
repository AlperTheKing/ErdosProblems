import io,contextlib,subprocess
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG
from fractions import Fraction as Fr
def getT(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    T=[Fr(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps); share=Fr(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=share
    return n,G,T
# verify identity Uunder - Uover = N^2-Gamma, and ratio Uunder/Uover.
worst_ratio=None; viol=0
for nn in range(5,11):
    o=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in o:
        r=getT(*dec(g6))
        if r is None: continue
        n,G,T=r
        Uo=sum(max(Fr(0),t-n) for t in T)
        Uu=sum(max(Fr(0),n-t) for t in T)
        assert Uu-Uo==n*n-G, (g6,Uu-Uo,n*n-G)
        if Uo>0:
            ratio=Uu/Uo
            if ratio<2: viol+=1; print("RATIO<2 VIOL",g6,float(ratio))
            if worst_ratio is None or ratio<worst_ratio[0]: worst_ratio=(ratio,g6,float(Uu),float(Uo),n,G)
print("identity Uunder-Uover=deficit: OK")
print("U_under >= 2 U_over: violations",viol,"tightest ratio",None if worst_ratio is None else (float(worst_ratio[0]),)+worst_ratio[1:])
