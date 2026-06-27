"""CROSS-ROUTE LINK TEST: is U_over (uniform-split overshoot, Step-1/(COUPLE)) <= D* (master-inequality residual
CD-defect, Step-2)?  If yes, Step-2's PROVEN-target master inequality Gamma+D*<=N^2 IMPLIES (COUPLE) U_over<=N^2-Gamma,
unifying the two routes rigorously.  D(C)=max_{S subset R=V\C} (delta_{M[R]}(S) - delta_{B[R]}(S))_+ ;  D*=min over
shortest bad-geodesic peels C of D(C).  Exact (Fractions for U_over, integer D*). Small N (2^|R| defect)."""
from fractions import Fraction as F
from itertools import combinations
import subprocess
from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG

def setup(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    return (adj,)+r  # adj,side,Gamma,M,ell

def Uover(n,adj,side,M,ell):
    T=[F(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return None
        sh=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=sh
    return sum((t-n) for t in T if t>n)

def DC(n,adj,side,M,C):
    """residual CD-defect after peeling vertex set C: max_{S subset R} (delta_M[R](S)-delta_B[R](S))_+ , R=V\C."""
    R=[v for v in range(n) if v not in C]; Rset=set(R)
    MR=[(u,v) for (u,v) in M if u in Rset and v in Rset]
    BR=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]!=side[v] and u in Rset and v in Rset]
    best=0
    if len(R)>20: return None
    for k in range(1,len(R)//1+1):
        for S in combinations(R,k):
            Sset=set(S)
            dM=sum(1 for (u,v) in MR if (u in Sset)!=(v in Sset))
            dB=sum(1 for (u,v) in BR if (u in Sset)!=(v in Sset))
            if dM-dB>best: best=dM-dB
    return best

def Dstar(n,adj,side,M,ell):
    best=None
    for f in M:
        for P in geos(adj,side,f[0],f[1]):
            d=DC(n,adj,side,M,set(P))
            if d is None: continue
            if best is None or d<best: best=d
    return best

def show(name,n,E):
    s=setup(n,E)
    if s is None: print(f"  {name}: no gmin"); return
    adj,side,G,M,ell=s
    uo=Uover(n,adj,side,M,ell); ds=Dstar(n,adj,side,M,ell)
    if uo is None or ds is None: print(f"  {name}: skip"); return
    defc=n*n-G
    print(f"  {name:7} N={n} Gamma={G} deficit={defc} | U_over={uo}({float(uo):.3f}) D*={ds} | U_over<=D*? {uo<=ds} | both<=deficit? {uo<=defc and ds<=defc}")
    return (float(uo), ds, uo<=ds)

print("=== U_over (uniform-split, COUPLE) vs D* (master-ineq residual CD-defect) ===")
for q in (2,3): show(f"C5[{q}]",*blow(q))
show("n8",*dec("G?\x60F\x60w")); show("N11a",*dec("J?BD@g]Qvo?")); show("N11b",*dec("J?AAD@ON@[?"))
print("--- census N=7..9: count U_over>D* (if 0, master-ineq IMPLIES COUPLE) ---")
for nn in (7,8,9):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    gt=0; nt=0
    for g6 in out:
        n,E=dec(g6); s=setup(n,E)
        if s is None: continue
        adj,side,G,M,ell=s
        uo=Uover(n,adj,side,M,ell); ds=Dstar(n,adj,side,M,ell)
        if uo is None or ds is None: continue
        nt+=1
        if uo>ds: gt+=1
    print(f"  N={nn}: configs={nt} | U_over>D* count={gt} (0 => master-ineq Gamma+D*<=N^2 IMPLIES COUPLE)",flush=True)
print("\nIf U_over<=D* everywhere: proving Step-2's master inequality ALSO proves (COUPLE) -- the routes are ONE.")
