"""Targeted small-k (k=N-|C|) adversarial constructions, brute-force exact max-cut (N<=21).
Island = large odd-cycle blow-up (T high inside) while few outside vertices create O, keeping island a
separate K-comp. Minimize slack deficit-dB. Exact Fraction."""
from fractions import Fraction as F
from _h import loads
from _bdef_construct import (build_K_T, Kcomponents, Cn, union_disjoint, add_edges,
                              blow_g, mycielski, is_triangle_free, report, blow)

def cyc_blow(k, t, off=0):
    n=k*t; E=[]
    for i in range(k):
        for a in range(t):
            for b in range(t):
                E.append((off+i*t+a, off+((i+1)%k)*t+b))
    return n,E

def try_build(name, n, E):
    if not is_triangle_free(n,E):
        print(f"  {name}: NOT triangle-free"); return None
    info=loads(n,E)
    if info is None:
        print(f"  {name}: loads=None (no valid connected-B max cut w/ bad edges)"); return None
    return report(info,name)

if __name__=="__main__":
    print("=== small-k targeted constructions (exact, brute max-cut N<=21) ===")
    isl=cyc_blow(5,3)   # 15 verts, 0..14 ; internal extremal T=15
    for extra_struct, bridges, nm in [
        ((5,Cn(5)), [(0,15)], "C5[3]+C5 1br"),
        ((5,Cn(5)), [(0,15),(3,17)], "C5[3]+C5 2br"),
        ((7,Cn(7)), [(0,15)], "C5[3]+C7 1br"),
    ]:
        n,E=union_disjoint(isl, extra_struct)
        n,E=add_edges((n,E),bridges)
        try_build(nm,n,E)
    isl7=cyc_blow(7,2)  # 14 verts
    for extra_struct, bridges, nm in [
        ((5,Cn(5)), [(0,14)], "C7[2]+C5 1br"),
        ((7,Cn(7)), [(0,14)], "C7[2]+C7 1br"),
    ]:
        n,E=union_disjoint(isl7, extra_struct)
        n,E=add_edges((n,E),bridges)
        try_build(nm,n,E)
