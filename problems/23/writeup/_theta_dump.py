import numpy as np
from _h import dec, loads
from _kktcore2 import setup, maximizeL
from _theta import Omat, comps
for g6 in ["J?AAD?cuDs?"]:  # the N=11 (2)-failure
    n,E=dec(g6); info=loads(n,E); L,nn,M=setup(info); O,P=Omat(L)
    gmax,ystar=maximizeL(L,nn,restarts=30)
    def adj2(a,b):
        return (set(M[a])&set(M[b])) or O[a,b]>=1.0-1e-9
    c2=comps(len(M),adj2)
    best2=-1; bc=None
    for comp in c2:
        allowed=set()
        for ei in comp: allowed|=set(L[ei][2].keys())
        v,_=maximizeL(L,nn,allowed=allowed,restarts=12)
        if v>best2: best2=v; bc=comp
    supp=sorted(v for v in range(nn) if ystar[v]>1e-7)
    print(f"{g6} N={nn} |M|={len(M)} Gamma={info['G']}")
    print(f"  high-effort maxL={gmax:.5f}  best (2)-component maxL={best2:.5f}  gap={gmax-best2:+.5f}")
    print(f"  (2)-components (edge ids): {c2}")
    print(f"  bad edges M={list(enumerate(M))}")
    print(f"  overlap matrix O_fg:")
    for a in range(len(M)): print(f"    {M[a]}: {[round(O[a,b],3) for b in range(len(M))]}")
    print(f"  global y* support vertices = {supp}")
    # which (2)-components are 'active' (intersect supp)
    for ci,comp in enumerate(c2):
        sv=set()
        for ei in comp: sv|=set(L[ei][2].keys())
        act=sorted(sv & set(supp))
        print(f"    comp{ci} edges {[M[e] for e in comp]}: supp-vertices in y* = {act}")
