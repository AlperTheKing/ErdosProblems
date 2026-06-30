"""Focused push: find a CP-SAT GLOBAL-max case that ALSO breaks ROW/PATH-LRS.
Vary L, k, chord gap. Report only global-max cases and any breaker."""
from fractions import Fraction as F
from _wf_lrsbreak_0 import build_k_lane, trifree, cutsize, cpmax, lrs_check
from _h import Bconn

def greedy_chords(L,k,gap):
    base_n,base_E,_,_=build_k_lane(L,k,[])
    adj=[set() for _ in range(base_n)]
    for a,b in base_E: adj[a].add(b); adj[b].add(a)
    chords=[]
    cand=[(a,b) for a in range(0,L+1) for b in range(a+gap,L+1) if (a%2)==(b%2)]
    for (a,b) in cand:
        if b in adj[a] or (adj[a]&adj[b]): continue
        adj[a].add(b);adj[b].add(a);chords.append((a,b))
    return chords

globalmax_breakers=[]
for L in range(8,19,2):
    for k in (3,4):
        for gap in (4,6,8):
            bad=greedy_chords(L,k,gap)
            if not bad: continue
            n,E,side,bad=build_k_lane(L,k,bad)
            adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            if not trifree(n,adj) or not Bconn(n,adj,side): continue
            pc=cutsize(n,adj,side)
            opt,bd,iso=cpmax(n,E,60)
            gm=(pc==opt==bd) and iso
            r=lrs_check(n,adj,side)
            if r is None: continue
            broken=[nm for nm,ok in [('B2',r['B2_ok']),('PATH-LRS',r['PATH_ok']),('ROW-LRS',r['ROW_ok']),('LRS',r['LRS_ok'])] if not ok]
            tag = "GLOBALMAX" if gm else ("not-max(opt%d>cut%d)"%(opt,pc))
            print("L=%d k=%d gap=%d N=%d |M|=%d ratioM=%.3f maxT/2N=%.3f %s broken=%s ROWslack=%.2f"%(
                L,k,gap,n,r['absM'],float(r['ratioM']),float(r['maxT']/(2*n)),tag,broken,float(r['rowworst'][0])),flush=True)
            if gm and broken:
                globalmax_breakers.append((L,k,gap,broken,r))
print("=== GLOBALMAX breakers ===", [(L,k,gap,b) for (L,k,gap,b,_) in globalmax_breakers])
