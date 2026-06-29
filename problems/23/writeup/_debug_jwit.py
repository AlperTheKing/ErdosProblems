"""Debug the J??E@_ibE? discrepancy: print gmin cuts, find side [1,1,1,1,1,1,0,0,0,0,0], its bad edges,
and whether f=(6,8) is unique-geodesic there + its geodesics + S, to reconcile with Codex's d=[0,1/2,1/2,1/2,1]."""
from fractions import Fraction as F
from _h import dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
g6="J??E@_ibE?"
n,E=dec(g6); adj,cuts=gmins(n,E)
print(f"g6={g6} N={n} #gmin-cuts={len(cuts)}")
target=[1,1,1,1,1,1,0,0,0,0,0]
for idx,cut in enumerate(cuts):
    if list(cut)==target:
        print(f"  side {target} is gmin-cut index {idx}")
        st=struct_for_side(n,adj,cut)
        M,ell,T,mu,cyc=st
        print(f"  bad edges M={sorted(M)}")
        print(f"  f=(6,8) in M? {(6,8) in M}; #geodesics={len(cyc[(6,8)]) if (6,8) in M else 'n/a'}")
        if (6,8) in M:
            print(f"  geodesics of (6,8): {cyc[(6,8)]}")
        # S over all bad edges
        S=[F(0)]*n;
        for g in M:
            Ps=cyc[g]; k=len(Ps); seen={}
            for P in Ps:
                for v in P: seen[v]=seen.get(v,F(0))+F(1,k)
            for v,pv in seen.items(): S[v]+=pv
        if (6,8) in M and len(cyc[(6,8)])==1:
            P_f=cyc[(6,8)][0]
            print(f"  P_f={P_f}  S on P_f={[str(S[v]) for v in P_f]}  d={[str(S[v]-1) for v in P_f]}")
        break
else:
    print(f"  side {target} NOT among gmin cuts! (Codex may use a different cut). Listing cuts:")
    for idx,cut in enumerate(cuts): print(f"   idx{idx}: {''.join(map(str,cut))}")
