"""Audit Codex block 33: SAT-ZMU-CLASS is not invariant over all gamma-min cuts, but the reduction only needs it for
ONE chosen gamma-min cut. Construction: base J?AADBWM_}? + leaf 11 adjacent to vertex 8 (N=12).
(a) The loads()-chosen cut: does SAT-ZMU-CLASS hold? what is T[8], O, Gamma?
(b) Confirm the manual violating side [1,0,1,1,1,0,1,0,0,0,0,1] has T[8]=12=N, O=[10], edge (8,11) zero-mu.
Both equal-Gamma (75) => the reduction may pick the good (loads) cut. Exact Fraction."""
from fractions import Fraction as F
from _h import dec, loads
from _zmu import mu_edges

def satzmu_class_viol(info):
    N=info['n']; T=info['T']; Bset=info['Bset']
    O=[v for v in range(N) if T[v]>N]
    mu=mu_edges(info)
    viol=[]
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        for (a,b) in ((u,v),(v,u)):
            if T[a]==N and not (T[b]==0 and len(O)==0):
                viol.append((a,b,float(T[a]),float(T[b]),len(O)))
    return viol,O

# build construction
g6="J?AADBWM_}?"
n,E=dec(g6)
E2=list(E)+[(8,11)]   # leaf 11 adjacent to 8
n2=12
info=loads(n2,E2)
print("=== construction: J?AADBWM_}? + leaf 11~8, N=12 ===")
print(f"  loads()-cut: side={info['side']}")
print(f"  T={[float(t) for t in info['T']]}")
print(f"  O={[v for v in range(n2) if info['T'][v]>n2]}  Gamma={float(info['G'])}  M={info['M']}")
v,O=satzmu_class_viol(info)
print(f"  SAT-ZMU-CLASS violations on loads-cut: {v if v else 'NONE'}")
print(f"  T[8] on loads-cut = {info['T'][8]}  (saturated? {info['T'][8]==n2})")
