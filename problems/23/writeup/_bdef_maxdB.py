"""Adversarial: MAXIMIZE dB (B-edges leaving island) while keeping a C5 island a SEPARATE Q-only K-comp.
deficit for a pure C5 island carrying one ell=5 bad edge is 5N-25. To violate need dB>5N-25.
Strategy: C5 island (0-4); attach many outside vertices each joined to island vertices, plus an overload core.
Brute-force exact max-cut, N<=21. Report whether island stays separate Q-only K-comp and slack."""
from fractions import Fraction as F
from _h import loads
from _bdef_construct import (Cn, union_disjoint, add_edges, is_triangle_free, report,
                             build_K_T, Kcomponents)

def try_build(name,n,E):
    if not is_triangle_free(n,E):
        print(f"  {name}: NOT triangle-free"); return
    info=loads(n,E)
    if info is None:
        print(f"  {name}: loads=None"); return
    report(info,name)

if __name__=="__main__":
    print("=== maximize dB on a C5 island (exact, N<=21) ===")
    # C5 island 0-4. Outside: a set S of vertices, each adjacent to TWO non-adjacent island verts
    # (triangle-free needs outside vertex's island-neighbors to be a C5 independent set, max size 2).
    # Build: island 0-4 (C5). Add m outside 'pendant-pair' verts, each joined to {0,2} (independent in C5).
    base_n=5; base_E=Cn(5)
    for m in [2,3,4,5,6,8,10,12]:
        n=base_n+m; E=list(base_E)
        for j in range(m):
            v=5+j
            E.append((v,0)); E.append((v,2))   # each outside vertex -> {0,2} (independent in C5)
        # also connect outside verts into an odd cycle among themselves to create overload? keep triangle-free
        if n>21:
            print(f"  m={m}: N={n}>21 skip"); continue
        try_build(f"C5+{m}x(0,2)-pendants",n,E)
    # Variation: outside vertices form their own C5/odd structure to overload, attached to island
    for m,struct,nm in [
        (5, [(5+i,5+(i+1)%5) for i in range(5)], "C5+C5out each->0,2"),
    ]:
        n=5+m; E=list(base_E)+list(struct)
        for j in range(m):
            E.append((5+j,0)); E.append((5+j,2))
        if not is_triangle_free(n,E):
            print(f"  {nm}: not trifree"); continue
        try_build(nm,n,E)
