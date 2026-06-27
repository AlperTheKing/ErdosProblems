#!/usr/bin/env python3
"""Construct adversarial hub graphs and test the uniform-split load claim U exactly."""
import itertools
from hub_adv import report

def E_to_n(E):
    return (max(max(e) for e in E)+1) if E else 0

# ---- 1. Pentagon pencil: m pentagons sharing a common 2-path a-h-b ----
# Each pentagon: a-h-b plus a-x_i-y_i-b (so cycle a-h-b-y_i-x_i-a length 5). Triangle-free.
def pentagon_pencil(m):
    # vertices: h=0, a=1, b=2, then x_i,y_i
    E=set(); h,a,b=0,1,2
    E.add((a,h)); E.add((h,b))
    nxt=3
    for i in range(m):
        x=nxt; y=nxt+1; nxt+=2
        E.add((a,x)); E.add((x,y)); E.add((y,b))
    return sorted(tuple(sorted(e)) for e in E)

# ---- 1b. Pentagon pencil sharing a 3-path a-h1-h2-b, two-hub funnel ----
def pentagon_pencil_share3(m):
    # cycle: a-h1-h2-b plus a-x_i-b ... need length5: a-h1-h2-b (len3 path) + b-z-a? that is 5-cycle a h1 h2 b z.
    E=set(); a,h1,h2,b=0,1,2,3
    E.add((a,h1)); E.add((h1,h2)); E.add((h2,b))
    nxt=4
    for i in range(m):
        z=nxt; nxt+=1
        E.add((b,z)); E.add((z,a))
    return sorted(tuple(sorted(e)) for e in E)

# ---- 2. K_{2,m} extended: hub pair u,w each connected to m middles; close odd cycles ----
def k2m_odd(m):
    # u=0,w=1 ; middles c_i. add path u-c_i, w-c_i gives 4-cycles. To make 5-cycles add hub h.
    E=set(); u,w=0,1
    nxt=2
    mids=[]
    for i in range(m):
        c=nxt; nxt+=1; mids.append(c)
        E.add((u,c)); E.add((w,c))
    # connect u-w via length-3 path u-p-q-w to make odd cycles u-c_i-w-q-p-u length5
    p=nxt; q=nxt+1; nxt+=2
    E.add((u,p)); E.add((p,q)); E.add((q,w))
    return sorted(tuple(sorted(e)) for e in E)

# ---- named graphs by edge list ----
def petersen():
    # outer 0-4 pentagon, inner 5-9 pentagram, spokes
    E=set()
    for i in range(5):
        E.add((i,(i+1)%5))
        E.add((i,i+5))
        E.add((5+i,5+(i+2)%5))
    return sorted(tuple(sorted(e)) for e in E)

def heawood():
    # Heawood graph N=14, incidence graph of Fano plane, bipartite girth 6
    E=set()
    n=14
    # standard LCF [5,-5]^7
    lcf=[5,-5]*7
    for i in range(n):
        E.add((i,(i+1)%n))
    for i in range(n):
        E.add((i,(i+lcf[i])%n))
    return sorted(tuple(sorted(e)) for e in E)

def pappus():
    # Pappus graph N=18, LCF [5,7,-7,7,-7,-5]^3
    E=set(); n=18
    lcf=[5,7,-7,7,-7,-5]*3
    for i in range(n): E.add((i,(i+1)%n))
    for i in range(n): E.add((i,(i+lcf[i])%n))
    return sorted(tuple(sorted(e)) for e in E)

def desargues():
    # Desargues graph N=20, LCF [5,-5,9,-9]^5
    E=set(); n=20
    lcf=[5,-5,9,-9]*5
    for i in range(n): E.add((i,(i+1)%n))
    for i in range(n): E.add((i,(i+lcf[i])%n))
    return sorted(tuple(sorted(e)) for e in E)

def mcgee():
    # McGee graph N=24, LCF [12,7,-7]^8 girth 7
    E=set(); n=24
    lcf=[12,7,-7]*8
    for i in range(n): E.add((i,(i+1)%n))
    for i in range(n): E.add((i,(i+lcf[i])%n))
    return sorted(tuple(sorted(e)) for e in E)

def dodecahedron():
    # N=20 girth 5, LCF [10,7,4,-4,-7,10,-4,7,-7,4]^2
    E=set(); n=20
    lcf=[10,7,4,-4,-7,10,-4,7,-7,4]*2
    for i in range(n): E.add((i,(i+1)%n))
    for i in range(n): E.add((i,(i+lcf[i])%n))
    return sorted(tuple(sorted(e)) for e in E)

if __name__=='__main__':
    results=[]
    print("=== Pentagon pencils (share 2-path a-h-b), hub h ===")
    for m in range(2,9):
        results.append(("pencil2_m%d"%m, report("pencil2_m%d"%m, E_to_n(pentagon_pencil(m)), pentagon_pencil(m))))
    print("=== Pentagon pencils (share 3-path a-h1-h2-b) ===")
    for m in range(2,9):
        results.append(("pencil3_m%d"%m, report("pencil3_m%d"%m, E_to_n(pentagon_pencil_share3(m)), pentagon_pencil_share3(m))))
    print("=== K_{2,m} odd gadgets ===")
    for m in range(2,8):
        results.append(("k2m_m%d"%m, report("k2m_m%d"%m, E_to_n(k2m_odd(m)), k2m_odd(m))))
    print("=== Named cages / cubic graphs ===")
    named=[("Petersen",petersen()),("Heawood",heawood()),("Pappus",pappus()),
           ("Desargues",desargues()),("Dodecahedron",dodecahedron())]
    for nm,E in named:
        results.append((nm, report(nm, E_to_n(E), E)))
    # mcgee N=24 maxcut 2^23 ~ 8M, feasible-ish but slow; try
    print("=== McGee N=24 (slow maxcut) ===")
    results.append(("McGee", report("McGee", 24, mcgee())))

    print("\n=== SUMMARY ===")
    best=None
    for nm,r in results:
        if r is None: continue
        if best is None or r['ratio']>best[1]['ratio']: best=(nm,r)
        if r['viol']: print("VIOLATION:",nm)
    if best: print(f"max ratio maxT/K = {best[1]['ratio']:.4f} at {best[0]}")
