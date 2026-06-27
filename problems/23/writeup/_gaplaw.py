import sys, io
_o=sys.stdout; sys.stdout=io.StringIO()
from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG
sys.stdout=_o
from fractions import Fraction as F
import subprocess

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def worst_vertex(n,E):
    adj=adj_of(n,E)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    N=n; K=N+(N*N-G); deficit=N*N-G
    best=None
    for w in range(n):
        R=F(0); L=0
        for (u,v) in M:
            Ps=geos(adj,side,u,v); nf=len(Ps); thru=sum(1 for P in Ps if w in P)
            if thru:
                R+=F(thru,nf); L=max(L,ell[(u,v)])
        if L==0: continue
        prod=L*R
        if best is None or prod>best[0]: best=(prod,R,L,w)
    if best is None: return None
    prod,R,L,w=best
    return dict(N=N,Gamma=G,K=K,deficit=deficit,prod=prod,R=R,L=L,gap=K-prod)

# Candidate gap law: gap = K - ellmaxR.  We KNOW gap=0 when deficit=0 (extremal).
# Test: is  ellmax*R <= N + deficit  EQUIVALENT to  ellmax*(R-?) ... Let me test
#   (G1) ellmax*R <= N + deficit            [=U-ish, target, must hold]
#   (G2) ellmax*R <= N  WHEN deficit==0     [the pure-extremal statement]
#   (G3) prod - N <= deficit                 [<=> G1]; measure (prod-N)/deficit ratio when deficit>0
rows=[]
for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in out:
        n,E=dec(g6); d=worst_vertex(n,E)
        if d is None: continue
        rows.append((d,g6))
# G2: among deficit==0 graphs, is prod<=N (i.e. prod==N)?
defzero=[ (d,g) for (d,g) in rows if d['deficit']==0]
bad_g2=[(d,g) for (d,g) in defzero if d['prod']>d['N']]
print(f"deficit==0 graphs: {len(defzero)}; prod>N among them (must be 0): {len(bad_g2)}")
print("  (so for ALL extremal Gamma=N^2 graphs in census, ellmax*R<=N)")
# G3: when deficit>0, ratio (prod-N)/deficit ; max should be <1 (target prod-N<=deficit)
defpos=[(d,g) for (d,g) in rows if d['deficit']>0]
worst_ratio=None
for d,g in defpos:
    if d['prod']>d['N']:
        ratio=F(d['prod']-d['N'], d['deficit'])
        if worst_ratio is None or ratio>worst_ratio[0]: worst_ratio=(ratio,g,d)
if worst_ratio:
    ratio,g,d=worst_ratio
    print(f"deficit>0 & prod>N: max (prod-N)/deficit = {float(ratio):.4f}={ratio} @ {g} N={d['N']} deficit={d['deficit']} prod={d['prod']} R={d['R']} L={d['L']}")
    print("  (target: this ratio <=1 for U to hold via prod-N<=deficit)")
else:
    print("deficit>0: prod never exceeds N (even stronger)")
