"""Verify (COUPLE) <=> Sum_w |T(w)-N| <= 3(N^2-Gamma) [L1 form], and probe the energy Sum T^2 / Sum(T-N)^2 to test
whether a second-moment (Cauchy-Schwarz) bound can give the L1 bound. Exact Fractions."""
from fractions import Fraction as F
import subprocess
from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG

def loads(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    T=[F(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return ('disc',)
        sh=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=sh
    return (G,n,T)

def info(name,n,E):
    res=loads(n,E)
    if res is None or res[0]=='disc': print(f"  {name}: skip"); return
    G,N,T=res
    deficit=N*N-G
    L1=sum(abs(t-N) for t in T)
    Uover=sum((t-N) for t in T if t>N)
    sq=sum((t-N)*(t-N) for t in T)   # Sum(T-N)^2
    couple = Uover<=deficit
    l1form = L1 <= 3*deficit
    # Cauchy-Schwarz: L1 <= sqrt(N * Sum(T-N)^2). Is sqrt(N*sq) <= 3*deficit? (i.e. N*sq <= 9 deficit^2)
    cs_ok = (N*sq <= 9*deficit*deficit) if deficit>0 else (sq==0)
    print(f"  {name:7} N={N} Gamma={G} deficit={deficit} | Uover={float(Uover):.3f} L1={float(L1):.3f} | COUPLE={couple} L1form(<=3def)={l1form} (match={couple==l1form}) | Sum(T-N)^2={float(sq):.2f} | CauchySchwarz N*sq<=9def^2? {cs_ok}")

print("=== (COUPLE) <=> Sum|T-N|<=3(N^2-Gamma) ; energy Sum(T-N)^2 + Cauchy-Schwarz test ===")
for q in (2,3): info(f"C5[{q}]",*blow(q))
info("n8",*dec("G?\x60F\x60w")); info("N11a",*dec("J?BD@g]Qvo?")); info("N11b",*dec("J?AAD@ON@[?")); info("N11c",*dec("J?AAD@WM_{?"))
print("--- census N=8,9: L1form matches COUPLE? + how often Cauchy-Schwarz energy bound suffices ---")
for nn in (8,9):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    mism=0; csfail=0; nt=0
    for g6 in out:
        n,E=dec(g6); res=loads(n,E)
        if res is None or res[0]=='disc': continue
        G,N,T=res; nt+=1; deficit=N*N-G
        Uover=sum((t-N) for t in T if t>N); L1=sum(abs(t-N) for t in T); sq=sum((t-N)*(t-N) for t in T)
        if (Uover<=deficit)!=(L1<=3*deficit): mism+=1
        cs_ok = (N*sq<=9*deficit*deficit) if deficit>0 else (sq==0)
        if not cs_ok: csfail+=1
    print(f"  N={nn}: configs={nt} | L1<=>COUPLE mismatches={mism} (MUST be 0) | Cauchy-Schwarz energy bound FAILS in {csfail} (if 0, energy bound PROVES it!)",flush=True)
print("\nIf CS energy bound fails often => second-moment too weak (expected, like other decoupled bounds). If 0 => a proof!")
