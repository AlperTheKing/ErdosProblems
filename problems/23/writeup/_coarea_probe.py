from fractions import Fraction as F
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _wf_deficit_farkas import deltas, flip, gamma_of
from _coarea_mr import Kcomp, cyclic_intervals, interval_Iir

g6="H?AFBo]"; n,E=dec(g6)
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
side=[int(c) for c in "000000111"]
st=struct_for_side(n,adj,side); M,ell,T,mu,cyc=st
Gamma=sum(T)
print("M:",[(g,ell[g]) for g in M])
for g in M:
    print("  cyc[%s]:"%(g,), cyc[g])
f=(6,8); P=[6,1,7,3,8]
K=Kcomp(n,M,cyc,set(P)); print("K(P)=",sorted(K))
cycles=[]
for g in M:
    for Q in cyc[g]:
        if set(Q)<=K: cycles.append((g,list(Q)))
print("geodesic-cycles in K:")
for g,o in cycles: print("   g=%s order=%s"%(g,o))
import itertools
# I=full path (r>=2): W = path ∪ S, S subset {0,2,4,5}.  Exhaustive over S, check arc-consistency + (c).
nonpath=[v for v in sorted(K) if v not in set(P)]
print("non-path K vertices:",nonpath)
cyc_arcsets=[(g,o,set(o),cyclic_intervals(o)) for g,o in cycles]
nfeasible=0
for k in range(len(nonpath)+1):
    for S in itertools.combinations(nonpath,k):
        W=set(P)|set(S)
        # arc consistency on every cycle
        ok=all(frozenset(W&Vq) in arcs for (g,o,Vq,arcs) in cyc_arcsets)
        if not ok: continue
        s2=flip(side,W); bc=Bconn(n,adj,s2); g1=gamma_of(n,adj,s2)
        dB,dM=deltas(n,adj,side,W)
        C25=(g1-Gamma)+25*(dB-dM) if g1 is not None else None
        tag="FEASIBLE(c)" if (bc and g1 is not None) else "rej(c)"
        if bc and g1 is not None: nfeasible+=1
        print("  S=%s arc_ok=Y Bconn=%s valid=%s q=%s C25=%s %s"%(S,bc,g1 is not None,dB-dM,C25,tag))
print("=> I=full-path: feasible-(c) W count =",nfeasible)
# also: drop (c), just min C25 over arc-consistent W (to see if removing connectivity helps)
best=None
for k in range(len(nonpath)+1):
    for S in itertools.combinations(nonpath,k):
        W=set(P)|set(S)
        if not all(frozenset(W&Vq) in arcs for (g,o,Vq,arcs) in cyc_arcsets): continue
        s2=flip(side,W); g1=gamma_of(n,adj,s2)
        if g1 is None: continue
        C25=(g1-Gamma)+25*(deltas(n,adj,side,W)[0]-deltas(n,adj,side,W)[1])
        if best is None or C25<best: best=C25
print("=> I=full-path: min C25 over arc-consistent struct-valid W (NO Bconn req) =",best)
