"""Examine the N=10 multi-geodesic TIGHT case I?rFf_{N? (worst ROW=10, #geo=8, margin 0).
Show how the fractional dilution makes ROW hit N exactly even with a multi-geodesic edge."""
from fractions import Fraction as F
from _h import dec
from _stark1 import gmins
from _corridor import cut_S
n,E=dec("I?rFf_{N?")
adj2,cuts=gmins(n,E)
print(f"N={n} cuts={len(cuts)}")
best=None
for ci,s in enumerate(cuts):
    M,ell,S,pf,cyc=cut_S(n,adj2,s)
    for f in M:
        ROW=sum(pv*S[v] for v,pv in pf[f].items())
        if best is None or ROW>best[0]: best=(ROW,ci,s,f,M,ell,S,pf,cyc)
ROW,ci,s,f,M,ell,S,pf,cyc=best
print(f"worst: cut{ci} side={''.join(map(str,s))} f={f} ROW={ROW}={float(ROW):.3f} ell={ell[f]} #geo={len(cyc[f])}")
print(f"M={M} ell={[ell[g] for g in M]}")
print(f"S = {[str(x) for x in S]}")
print(f"f geodesics ({len(cyc[f])}):")
for P in cyc[f]: print(f"   {P}")
print(f"\nper-vertex p_f, S, p_f*S:")
self_=F(0)
for v in sorted(pf[f]):
    print(f"  v={v}: p_f={pf[f][v]}={float(pf[f][v]):.3f}  S={S[v]}={float(S[v]):.3f}  p_f*S={float(pf[f][v]*S[v]):.3f}")
    self_+=pf[f][v]**2
print(f"self=<p_f,p_f>={self_}={float(self_):.3f}  cross=ROW-self={float(ROW-self_):.3f}  N-self={n-float(self_):.3f}")
print(f"UB (drop p_f->1) = sum_{{supp}} S = {float(sum(S[v] for v in pf[f]))}  (vs N={n})")
