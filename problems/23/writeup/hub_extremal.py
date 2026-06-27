#!/usr/bin/env python3
"""Adversarial constructions near the Gamma=N^2 extremal regime, to maximize maxT/K with funneling.
Idea: ratio=1 needs Gamma~N^2. Build graphs where many bad-edge geodesics funnel through a hub
WHILE keeping Gamma high (close to N^2)."""
from fractions import Fraction as Fr
from hub_adv import report

def E_to_n(E):
    return (max(max(e) for e in E)+1) if E else 0

# odd cycle C_{2k+1}
def odd_cycle(k):
    n=2*k+1
    return [tuple(sorted((i,(i+1)%n))) for i in range(n)]

# Two odd cycles C5 sharing a single hub vertex (figure-eight); hub on both bad edges
def bowtie_C5(num):
    # num C5's all sharing vertex 0
    E=set(); nxt=1
    for c in range(num):
        # cycle 0 - a - b - c - d - 0
        a,b,cc,d=nxt,nxt+1,nxt+2,nxt+3; nxt+=4
        E.add((0,a));E.add((a,b));E.add((b,cc));E.add((cc,d));E.add((d,0))
    return sorted(tuple(sorted(e)) for e in E)

# C5 blow-up but with one "thin" class (asymmetric) to break symmetry and funnel
def C5_blowup_asym(sizes):
    # sizes = [t0,t1,t2,t3,t4]; class i connected fully to class i+1
    starts=[0];
    for t in sizes: starts.append(starts[-1]+t)
    n=starts[5]
    E=set()
    for i in range(5):
        for a in range(sizes[i]):
            for b in range(sizes[(i+1)%5]):
                u=starts[i]+a; v=starts[(i+1)%5]+b
                E.add(tuple(sorted((u,v))))
    return sorted(E)

# "pinched" C5 blow-up: classes sized t except one class is a single hub vertex
def C5_pinch(t):
    return C5_blowup_asym([1,t,t,t,t])

# Theta graph generalization: hub h, with m internally-disjoint paths between two poles, lengths giving odd cycles
def theta_pencil(m, half=2):
    # two poles s,t connected by m paths each of length 'half' on each side won't be odd; make each path produce a C5 with a shared edge through hub
    # build: shared edge s-t? no. Use shared path s-h-t (len2); m other paths s-x_i-y_i-t (len3) => C5 each
    E=set(); s,t,h=0,1,2; E.add((s,h));E.add((h,t)); nxt=3
    for i in range(m):
        x,y=nxt,nxt+1; nxt+=2
        E.add((s,x));E.add((x,y));E.add((y,t))
    return sorted(tuple(sorted(e)) for e in E)

if __name__=='__main__':
    print("=== odd cycles (extremal Gamma=N^2) ===")
    for k in range(2,10):
        E=odd_cycle(k); report("C%d"%(2*k+1), E_to_n(E), E)
    print("=== bowtie of C5's sharing one hub vertex ===")
    for num in range(1,5):
        E=bowtie_C5(num); report("bowtie%d"%num, E_to_n(E), E)
    print("=== pinched C5 blow-up [1,t,t,t,t] ===")
    for t in range(1,5):
        E=C5_pinch(t); report("pinch_t%d"%t, E_to_n(E), E)
    print("=== asymmetric C5 blow-up variants ===")
    for sizes in [[1,1,1,1,2],[1,2,2,2,1],[2,1,2,1,2],[1,1,2,2,3],[1,3,1,3,1],[2,2,2,2,1]]:
        E=C5_blowup_asym(sizes); report("blow_%s"%("_".join(map(str,sizes))), E_to_n(E), E)
    print("=== theta pencils ===")
    for m in range(2,9):
        E=theta_pencil(m); report("theta_m%d"%m, E_to_n(E), E)
