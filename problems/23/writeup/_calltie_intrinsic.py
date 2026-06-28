"""Intrinsic load bound for a single K-component (K-closed).
For a K-component C, maxT_C := max_{v in C} T(v) and Gamma_C = sum T.
These are INTRINSIC (depend only on C's geodesics, not N or rest of graph).

We compute, over single-component instances (standalone graphs whose load-bearing K-graph
is connected), the ratios:
   maxT_C / |C|,   Gamma_C / |C|,   maxT_C  vs  |C|.

C-alltie / NO-Q-ONLY contrapositive needs: a Q-only comp C with a SATURATED vertex
T(v)=N while O lives elsewhere. Since N >= |C| + 5(k-1) >= |C|+5 (k>=2 loaded comps),
T(v)=N >= |C|+5 means maxT_C >= |C|+5. So a NECESSARY condition for C-alltie failure:
   a loaded K-component with maxT_C >= |C| + 5  AND that comp Q-only.
Test: does maxT_C - |C| ever reach +5 in a Q-only loaded comp?
And more basically: what is sup (maxT_C - |C|) over ALL loaded comps?
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _calltie_glue import components_from_info

def scan(nn, stride=1, badonly=True):
    gs=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
    best_excess=F(-10**9); best_g=None
    best_ratio=F(0); best_rg=None
    qonly_sat_excess=[]   # (excess, |C|, maxT) for Q-only loaded comps where maxT>=|C|
    for g6 in gs:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        T=info['T']; N=info['n']
        O=set(v for v in range(N) if T[v]>N)
        comps=components_from_info(info)
        for Cc in comps:
            gc=sum(T[v] for v in Cc)
            if gc==0: continue
            mx=max(T[v] for v in Cc); sz=len(Cc)
            excess=mx-sz
            if excess>best_excess: best_excess=excess; best_g=(g6,sz,mx)
            r=F(mx,sz)
            if r>best_ratio: best_ratio=r; best_rg=(g6,sz,mx)
            # Q-only loaded comp (disjoint from O)
            if not (Cc & O) and excess>0:
                qonly_sat_excess.append((g6,float(excess),sz,float(mx),bool(O)))
    print(f"N={nn}: max(maxT_C - |C|)={float(best_excess):+.3f} at {best_g}; "
          f"max(maxT_C/|C|)={float(best_ratio):.3f} at {best_rg}")
    if qonly_sat_excess:
        print(f"   Q-only comps with maxT_C>|C| (excess, |C|, maxT, O-nonempty): "
              f"{sorted(qonly_sat_excess,key=lambda x:-x[1])[:5]}")
    return best_excess

if __name__=="__main__":
    print("=== intrinsic load excess maxT_C - |C| over single K-components ===")
    for nn in range(5,12):
        scan(nn, stride=1)
