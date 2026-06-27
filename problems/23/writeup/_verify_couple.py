"""Independently EXACT-verify the proof-workflow's load-bearing claims before adopting (COUPLE) as the handoff:
  P1: sum_w T_uniform(w) = Gamma  (conservation)
  P2: U_under - U_over = N^2 - Gamma   where U_over=sum(T-N)_+, U_under=sum(N-T)_+
  COUPLE: sum_w (T(w)-N)_+ <= N^2 - Gamma   (the open lemma)  [equiv U_under >= 2 U_over]
on census N<=10 + witnesses + C5[q] anchor. Exact Fractions."""
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

def stats(n,E):
    res=loads(n,E)
    if res is None or res[0]=='disc': return None
    G,n2,T=res
    N=n2
    sumT=sum(T)
    Uover=sum((t-N) for t in T if t>N)
    Uunder=sum((N-t) for t in T if t<N)
    P1 = (sumT==G)
    P2 = (Uunder-Uover == N*N-G)
    COUPLE = (Uover <= N*N-G)
    return dict(G=G,N=N,P1=P1,P2=P2,COUPLE=COUPLE,Uover=Uover,Uunder=Uunder,deficit=N*N-G)

print("=== independent verify: P1 (sum T=Gamma), P2 (Uunder-Uover=N^2-Gamma), COUPLE (Uover<=N^2-Gamma) ===")
for q in (2,3,4):
    s=stats(*blow(q)); print(f"  C5[{q}]: P1={s['P1']} P2={s['P2']} COUPLE={s['COUPLE']} | Uover={s['Uover']} Uunder={s['Uunder']} deficit={s['deficit']}")
for nm,g in [("n8","G?\x60F\x60w"),("N11a","J?BD@g]Qvo?"),("N11b","J?AAD@ON@[?")]:
    s=stats(*dec(g)); print(f"  {nm}: P1={s['P1']} P2={s['P2']} COUPLE={s['COUPLE']} | Uover={s['Uover']} Uunder={s['Uunder']} deficit={s['deficit']}")
print("--- census N=5..10: count P1/P2 failures (MUST be 0) + COUPLE violations (MUST be 0) ---")
for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    p1f=p2f=cv=nt=0
    for g6 in out:
        n,E=dec(g6); s=stats(n,E)
        if s is None: continue
        nt+=1
        if not s['P1']: p1f+=1
        if not s['P2']: p2f+=1
        if not s['COUPLE']: cv+=1
    print(f"  N={nn}: configs={nt} | P1 fails={p1f} | P2 fails={p2f} | COUPLE violations={cv}",flush=True)
print("\nAll P1/P2 fails=0 and COUPLE violations=0 => the handoff lemma + scaffolding are exact-confirmed.")
