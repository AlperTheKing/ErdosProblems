"""Glue a LARGE near-saturated island (C5[2], internal T=10) to a SMALL O-creating gadget (G?`F`w N=8),
to push deficit per island vertex as low as possible while O survives. Exact, brute max-cut N<=20.
Island C5[2] internal T=10; if island stays a separate Q-only K-comp with T~10 and N=18, deficit/v ~ 8.
Try many bridge choices; report best (smallest slack) coexisting bad-carrying Q-only comp."""
from fractions import Fraction as F
from _h import dec, loads
from _bdef_construct import (build_K_T, Kcomponents, union_disjoint, add_edges,
                             is_triangle_free, report)

def c5blow(t):
    n=5*t; E=[]
    for i in range(5):
        for a in range(t):
            for b in range(t):
                E.append((i*t+a,((i+1)%5)*t+b))
    return n,E

def try_build(name,n,E):
    if not is_triangle_free(n,E):
        print(f"  {name}: NOT triangle-free"); return
    info=loads(n,E)
    if info is None:
        print(f"  {name}: loads=None"); return
    report(info,name)

if __name__=="__main__":
    print("=== big island C5[2] + small O-gadget (exact, N<=20) ===")
    isl=c5blow(2)          # 10 verts, 0..9
    gn,gE=dec("G?`F`w")    # N=8 gadget with O at its {6,7}
    # gadget vertices become 10..17
    n0,E0=union_disjoint(isl,(gn,gE))
    # the gadget's overloaded vertices are 10+6=16, 10+7=17. Bridge island to a LOW-load gadget vertex
    # (not the overloaded ones) so O persists. Gadget low-load verts: 10..15.
    for bridges in [[(0,10)],[(0,11)],[(0,12)],[(0,10),(5,12)],[(0,10),(2,11),(4,13)],
                    [(0,10),(1,11),(2,12),(3,13)]]:
        n,E=add_edges((n0,E0),bridges)
        try_build(f"C5[2]+G?`F`w br{bridges}",n,E)
