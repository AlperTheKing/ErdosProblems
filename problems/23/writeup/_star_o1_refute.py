"""Independently verify Codex's STAR-O1 refutation (block 93): non-uniform C5 blow-up parts (1,48,6,8,48), N=111,
   cut {V0,V2,V4}|{V1,V3}. Expect: STAR-O1 LB1(o)-D_o = -2133/9877 < 0 (FALSE), but full-g O-row margin > 0 (cond3 holds).
   Also add non-uniform odd-cycle blow-ups to the gate going forward."""
from fractions import Fraction as F
from _star_o1 import star_o1
from _opencap import opencap

def c5_blowup_nonuniform(sizes):
    # 5 parts in a C5; consecutive parts fully joined. sizes=[s0..s4].
    n=sum(sizes)
    start=[0]*5
    for i in range(1,5): start[i]=start[i-1]+sizes[i-1]
    part=[None]*n
    for i in range(5):
        for j in range(sizes[i]): part[start[i]+j]=i
    adj=[set() for _ in range(n)]
    E=[]
    for i in range(5):
        j=(i+1)%5
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                u=start[i]+a; v=start[j]+b
                adj[u].add(v); adj[v].add(u); E.append((u,v))
    # cut: parts {0,2,4} -> side 0 ; {1,3} -> side 1
    side=[0 if part[v] in (0,2,4) else 1 for v in range(n)]
    return n,E,adj,side,part,start

if __name__=="__main__":
    sizes=[1,48,6,8,48]
    n,E,adj,side,part,start=c5_blowup_nonuniform(sizes)
    print(f"N={n} parts={sizes}")
    # STAR-O1 on this exact cut
    d=star_o1(adj,side,n)
    if d is None:
        print("star_o1: not |O|=1 here (?)")
    else:
        ok,ratio,Do,LB1,o,terms=d
        print(f"STAR-O1: o={o} D_o={Do} LB1={LB1} LB1-D_o={LB1-Do} (float {float(LB1-Do):+.6f}) STAR-O1-OK={ok}")
        print(f"  expect LB1-D_o = -2133/9877 = {float(F(-2133,9877)):+.6f}; match={LB1-Do==F(-2133,9877)}")
    # full-g cond3 on this exact cut
    c=opencap(adj,side,n)
    print(f"full-g opencap: {c}")
