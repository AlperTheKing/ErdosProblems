"""Adversarial perturbation of the EXTREMAL C5[t]: try to create O (overload) by a tiny local change
while keeping a large near-saturated (T~N) Q-only K-component, to push deficit -> 0 with O nonempty.
Exact, brute max-cut N<=20.  Run from .../problems/23/writeup."""
from fractions import Fraction as F
from _h import loads
from _bdef_construct import (build_K_T, Kcomponents, is_triangle_free, report)

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
    print("=== perturbations of extremal C5[t] to create O while keeping near-saturated Q-comp ===")
    for t in [2,3]:
        n,E=c5blow(t)
        ES=set(map(lambda e:(min(e),max(e)),E))
        # baseline
        try_build(f"C5[{t}] baseline",n,list(ES))
        # add ONE extra vertex of degree 2 attached to two non-adjacent vertices to overload
        n2=n+1
        # attach new vertex n to two vertices in the SAME part (independent): e.g. 0 and 1 (both in class 0 of blow-up)
        E2=list(ES)+[(0,n),(1,n)] if t>=2 else None
        if E2: try_build(f"C5[{t}]+pendant(0,1)",n2,E2)
        # delete one edge to free a vertex then it becomes underloaded -> shifts O
        e0=sorted(ES)[0]
        E3=[e for e in ES if e!=e0]
        try_build(f"C5[{t}] minus {e0}",n,E3)
        # add a chord-ish extra vertex bridging classes to overload a hub
        E4=list(ES)+[(0,n)]  # degree-1 pendant
        try_build(f"C5[{t}]+pendant1(0)",n+1,E4)
