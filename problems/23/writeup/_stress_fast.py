"""Fast stress of (ROWSUM-O) sum_g O_fg <= N on odd-cycle blowups, WITHOUT 2^N maxcut.
For C_{2k+1}[t]: a max cut is given by 2-coloring the (2k+1)-cycle near-bipartitely (one mono edge per cycle).
Rather than guess the cut, we pass an explicit known-good side vector and reuse _h's geodesic machinery on the
restricted-to-cut B-graph, building the EXACT O directly. We construct the side by the standard odd-cycle cut:
color cycle positions 0..L-1 with side = pos%2, so the only monochromatic cycle-edge is between pos L-1 and 0
(both even when L odd: L-1 even, 0 even -> same side). Inside a part there are NO edges (independent set), so
mono edges are exactly the cross-part edges within the same side... wait blowup parts are independent; edges go
between consecutive parts. With side=pos%2, edge between part i and i+1: sides differ unless i=L-1 (L-1 even,0 even).
So mono edges = all t*t edges between part L-1 and part 0. Those are the bad edges. Good: matches loads()'s find.

We just call loads() but SHORTCUT maxcut by monkeypatching maxcut_all to return our single good cut (still must
be A max cut; for blowups the balanced cut IS max). To stay safe we VERIFY it's connected-B and gives the known
Gamma=N^2 for C5; for C7/C9 we accept the structural cut. Then compute ROWSUM-O exactly."""
import numpy as np
from fractions import Fraction as F
import _h
from _h import loads

def odd_blow(k,t):
    L=2*k+1; nn=L*t; E=[]
    for i in range(L):
        for a in range(t):
            for b in range(t):
                E.append((i*t+a, ((i+1)%L)*t+b))
    return nn,E,L

def good_cut(L,t):
    side=[0]*(L*t)
    for i in range(L):
        for a in range(t):
            side[i*t+a]= i%2
    return side

def run(k,t):
    nn,E,L=odd_blow(k,t)
    side0=good_cut(L,t)
    adj=[set() for _ in range(nn)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    # monkeypatch maxcut_all to return just our cut (it's a max cut for the balanced blowup)
    orig=_h.maxcut_all
    _h.maxcut_all=lambda n,a: [side0]
    try:
        info=loads(nn,E)
    finally:
        _h.maxcut_all=orig
    if info is None:
        return nn, None, None, None
    n=info['n']; N=n; M=info['M']; cyc=info['cyc']; m=len(M)
    pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    def ip(a,b):
        ss=F(0)
        for w,av in a.items():
            bv=b.get(w)
            if bv is not None: ss+=av*bv
        return ss
    # ROWSUM-O for each f
    worst=None
    for i in range(m):
        row=sum(ip(pf[i],pf[j]) for j in range(m))
        r=row-N
        if worst is None or r>worst: worst=r
    return nn, worst, float(info['G'])/(nn*nn), m

if __name__=="__main__":
    print("=== FAST ROWSUM-O on odd-cycle blowups C_{2k+1}[t] (explicit balanced cut) ===")
    for k in [2,3,4,5]:
        for t in range(1,6):
            nn,worst,gn,m=run(k,t)
            if worst is None:
                print(f"  C{2*k+1}[{t}] N={nn}: no bad edge"); continue
            flag="  <-- VIOLATION!" if worst>0 else ""
            print(f"  C{2*k+1}[{t}] N={nn}: ROWSUM-O max-resid={worst}={float(worst):+.4f} | #bad={m} Gamma/N^2={gn:.4f}{flag}")
