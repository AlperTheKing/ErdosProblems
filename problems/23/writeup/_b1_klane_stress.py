"""Stress B1 (R_load = sum T^2/Gamma <= 2N) on DENSER k-lane constructions (the family that broke B2 and pushed
R_load/N to 1.88). Question: can a denser k-lane push R_load/N to/over 2 (=> B1 dies, only LRS family survives)?
For each (L,k,gap): build k-lane + greedy chords, require CP-SAT GLOBAL max (parity), compute exact R_load/N,
maxT/N, |M|/(N^2/25), and the LRS-family slacks. Report max R_load/N reached + whether B1 ever fails."""
from fractions import Fraction as F
from _wf_lrsbreak_0 import build_k_lane, trifree, cutsize, cpmax, lrs_check
from _wf_lrsbreak_0c import greedy_chords
from _satzmu_conn import struct_for_side
from _h import Bconn

rows=[]
for k in (3,4,5,6):
    for L in (10,12,14,16,18):
        for gap in (4,6,8):
            if gap>L: continue
            try:
                bad=greedy_chords(L,k,gap)
                n,E,side,bad=build_k_lane(L,k,bad)
            except Exception:
                continue
            if n>120: continue
            adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            if not trifree(n,adj) or not Bconn(n,adj,side): continue
            pc=cutsize(n,adj,side)
            opt,bd,iso=cpmax(n,E,40)
            if not (pc==opt==bd):  # require global max
                continue
            st=struct_for_side(n,adj,side)
            if st is None: continue
            M,ell,T,mu,cyc=st
            if not M: continue
            Gamma=sum(ell[f]**2 for f in M); sumT2=sum(t*t for t in T)
            Rload=F(sumT2,Gamma); Tmax=max(T); m=len(M)
            b1=Rload<=2*n; b2=Tmax<=2*n
            rows.append((float(Rload/n),float(Tmax/n),m,float(F(m)/F(n*n,25)),n,k,L,gap,b1,b2))

rows.sort(reverse=True)
print("=== B1 stress on dense k-lanes (CP-SAT global-max) ===",flush=True)
print("  TOP by R_load/N (R/N, Tmax/N, |M|, |M|/(N^2/25), N, k, L, gap, B1ok, B2ok):",flush=True)
for r in rows[:16]: print("   ",tuple(round(x,4) if isinstance(x,float) else x for x in r),flush=True)
b1fail=[r for r in rows if not r[8]]
maxR=max((r[0] for r in rows), default=0)
print("\n  configs(global-max)=%d  B1 failures=%d  MAX R_load/N=%.4f"%(len(rows),len(b1fail),maxR),flush=True)
if b1fail: print("  *** B1 FAILS: %s ***"%(b1fail[:3],),flush=True)
print("  === %s ==="%("B1 BROKEN by dense k-lane -> only LRS family survives" if b1fail else "B1 (R_load<=2N) survives all dense k-lanes; max R_load/N=%.3f"%maxR),flush=True)
