"""Iterated-Mycielskian + island gluings (the family that broke sibling (k2)), exact, N<=21.
Goal: keep O nonempty AND realize a Q-only K-component; minimize slack. Also test islands of size 7, 9."""
from fractions import Fraction as F
from _h import loads
from _bdef_construct import (Cn, union_disjoint, add_edges, is_triangle_free, report,
                             mycielski, build_K_T, Kcomponents)

def try_build(name,n,E):
    if not is_triangle_free(n,E):
        print(f"  {name}: NOT triangle-free"); return
    info=loads(n,E)
    if info is None:
        print(f"  {name}: loads=None"); return
    report(info,name)

if __name__=="__main__":
    print("=== Mycielskian+island gluings (exact, N<=21) ===")
    g15=mycielski(7,Cn(7))   # Myc(C7), N=15, has O
    # island C5 (|C|=5): vary bridge endpoints to keep O after re-cut
    for isl,isln,bridges,nm in [
        ((5,Cn(5)),5,[(0,5)],"C5 + MycC7 br@5"),
        ((5,Cn(5)),5,[(0,6)],"C5 + MycC7 br@6"),
        ((5,Cn(5)),5,[(0,7)],"C5 + MycC7 br@7"),
        ((5,Cn(5)),5,[(0,14)],"C5 + MycC7 br@14(apex)"),
        ((7,Cn(7)),7,[(0,5)],"C7 + MycC7 br@5"),  # N=22
    ]:
        n,E=union_disjoint(isl,g15); n,E=add_edges((n,E),bridges)
        try_build(nm,n,E)
    # Grotzsch (N=11) has O too; glue C5 island, keep O. N=16.
    g11=mycielski(5,Cn(5))
    for bridges,nm in [([(0,5)],"C5+Grotzsch br@5"),([(0,10)],"C5+Grotzsch br@10"),([(0,15)],"C5+Grotzsch br@apex")]:
        n,E=union_disjoint((5,Cn(5)),g11); n,E=add_edges((n,E),bridges)
        try_build(nm,n,E)
