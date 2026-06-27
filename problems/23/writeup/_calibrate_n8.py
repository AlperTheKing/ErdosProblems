import io,contextlib
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    from census_GPI import dec, maxcut_all, gmin, geos
from fractions import Fraction as Fr
n,E=dec('G?`F`w')
adj=[set() for _ in range(n)]
for a,b in E: adj[a].add(b); adj[b].add(a)
r=gmin(n,adj,maxcut_all(n,adj)); side,G,M,ell=r
K=n+(n*n-G); defi=n*n-G
T=[Fr(0) for _ in range(n)]
for f in M:
    Ps=geos(adj,side,f[0],f[1]); nf=len(Ps); share=Fr(ell[f],nf)
    for P in Ps:
        for v in P: T[v]+=share
maxT=max(T); Uo=sum(max(Fr(0),t-n) for t in T); Uu=sum(max(Fr(0),n-t) for t in T)
print("n8 witness G?`F`w:  N=",n,"Gamma=",G,"K=",K,"deficit=",defi)
print("  max_w T =",maxT,"  K - max_w T =",K-maxT,"(<- the requested slack 12:",K-maxT==12,")")
print("  U_over =",Uo,"U_under=",Uu,"U_under-U_over=",Uu-Uo,"=deficit:",Uu-Uo==defi)
print("  total-overshoot lemma: U_over=",Uo,"<= deficit=",defi,":",Uo<=defi,"slack=",defi-Uo)
