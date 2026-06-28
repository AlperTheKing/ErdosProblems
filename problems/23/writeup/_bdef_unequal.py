"""Unequal-part C5 blow-up C5[a,b,c,d,e] (graphon-style realized as unweighted graph).
Tune part sizes so some vertices overload (T>N) and a near-saturated Q-only K-comp appears.
Exact, brute max-cut N<=20.  Run from .../problems/23/writeup."""
from fractions import Fraction as F
from _h import loads
from _bdef_construct import build_K_T, Kcomponents, is_triangle_free, report

def c5_unequal(parts):
    # parts = [a,b,c,d,e]; vertex classes 0..4 with given sizes; class i fully joined to class i+1 mod 5
    n=sum(parts); off=[0]*5
    for i in range(1,5): off[i]=off[i-1]+parts[i-1]
    E=[]
    for i in range(5):
        for a in range(parts[i]):
            for b in range(parts[(i+1)%5]):
                E.append((off[i]+a, off[(i+1)%5]+b))
    return n,E,off

def try_build(name,n,E):
    if not is_triangle_free(n,E):
        print(f"  {name}: NOT triangle-free"); return
    info=loads(n,E)
    if info is None:
        print(f"  {name}: loads=None"); return
    report(info,name)

if __name__=="__main__":
    print("=== unequal C5 blow-ups (exact, N<=20) ===")
    for parts in [
        [1,1,1,1,1],   # C5
        [2,1,2,1,1],   # asym
        [3,1,1,1,1],
        [2,2,2,1,1],
        [3,2,1,2,1],
        [1,4,1,1,1],
        [4,1,1,1,1],
        [3,3,1,1,1],
        [2,3,2,1,1],
        [3,1,3,1,1],
    ]:
        n,E,off=c5_unequal(parts)
        if n>20:
            print(f"  parts={parts}: N={n}>20 skip"); continue
        try_build(f"C5{parts} N={n}",n,E)
