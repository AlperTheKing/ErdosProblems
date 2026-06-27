#!/usr/bin/env python3
"""FAST candidate-inequality probe (N<=8 census + C5[q] + structured high-Gamma). Precompute everything
once per graph. Test a battery of COUPLED candidate upper bounds for T_uniform(w) and ell_max(w)*R(w),
looking for one that is (i) never violated, (ii) tight at C5[q]. EXACT Fractions.

Notation at binding vertex w (gamma-min cut, B connected):
  R(w)=sum_f p_f(w),  T(w)=sum_f ell(f) p_f(w),  L=ell_max(w),  Gamma=sum_f ell(f)^2, K=N+(N^2-Gamma).
  Per-edge: p_f(w) in (0,1].  CD holds.

Candidates (each must satisfy cand>=T(w) for all w; want equality at C5[q]):
  (T<=K)        : the target itself.
  (CS1)         : T(w) <= sqrt(R(w) * sum_f ell(f)^2 p_f(w))   [Cauchy-Schwarz on (sqrt p, ell sqrt p)]
  (CS2-global)  : T(w)^2 <= R(w) * Gamma     [since sum ell^2 p_f <= Gamma as p<=1]  -> T<=sqrt(R*Gamma)
  (avgL)        : T(w) = R(w)*Lbar(w) where Lbar=T/R is the p-weighted mean length.
  Probe whether  R(w) <= N/Lbar(w) + (N^2-Gamma)/(N)  ... measure residuals.
We MEASURE T,R,L,Lbar, Gamma/N, and the gap K-T, and tabulate to spot the law.
"""
import io, contextlib, subprocess
from fractions import Fraction as F
with contextlib.redirect_stdout(io.StringIO()):
    from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG

def per_graph(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    R=[F(0) for _ in range(n)]; T=[F(0) for _ in range(n)]
    Q2=[F(0) for _ in range(n)]   # sum_f ell^2 p_f(w)
    ellmax=[0]*n
    ok=True
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return None
        for P in Ps:
            for v in P:
                R[v]+=F(1,nf); T[v]+=F(ell[f],nf); Q2[v]+=F(ell[f]**2,nf)
                if ell[f]>ellmax[v]: ellmax[v]=ell[f]
    return dict(n=n,G=G,K=n+(n*n-G),R=R,T=T,Q2=Q2,ellmax=ellmax)

def scan(label, graphs, rows):
    for nm,(n,E) in graphs:
        d=per_graph(n,E)
        if d is None: continue
        n=d['n']; G=d['G']; K=d['K']
        for w in range(n):
            Rw=d['R'][w]
            if Rw==0: continue
            Tw=d['T'][w]; L=d['ellmax'][w]; Q2=d['Q2'][w]
            # candidate values
            cs2=Rw*G            # T^2 <= R*Gamma  ?
            rows.append((float(Tw), float(K), float(Rw), L, float(Tw/Rw), G, n,
                         float(Tw*Tw), float(cs2), float(L*Rw), nm, w))

def report(rows):
    # check (T<=K)
    vio=[r for r in rows if r[0]>r[1]+1e-9]
    print("rows:",len(rows)," T>K violations:",len(vio))
    # check CS2: T^2 <= R*Gamma
    cs2v=[r for r in rows if r[7]>r[8]+1e-9]
    print("CS2 (T^2<=R*Gamma) violations:",len(cs2v))
    # check L*R <= K
    lrv=[r for r in rows if r[9]>r[1]+1e-9]
    print("L*R<=K violations:",len(lrv))
    # tightness of CS2 at the binding rows (T near K)
    near=[r for r in rows if abs(r[0]-r[1])<1e-9]
    print("rows with T==K (extremal):",len(near))
    for r in near[:6]:
        tightcs2 = abs(r[7]-r[8])<1e-6
        print("   T=%.3f K=%.3f R=%.3f L=%d Lbar=%.3f Gamma=%d N=%d  T^2=%.2f R*Gamma=%.2f CS2tight=%s"
              %(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8], tightcs2))

if __name__=="__main__":
    rows=[]
    graphs=[(f"C5[{q}]",blow(q)) for q in (2,3,4,5,6)]
    graphs.append(("n8",dec("G?\x60F\x60w")))
    scan("witness",graphs,rows)
    for nn in range(5,9):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        scan(f"N{nn}",[(g6,dec(g6)) for g6 in out],rows)
    report(rows)
