"""Critical check: the C5 island in C5+Myc(C7)+bridge gives a Q-only bad-carrying K-component.
Is the loads()-cut actually a GAMMA-MIN connected max cut? Does the bridge get cut?
If the island {0..4} truly is a Q-only bad-carrying comp on a gamma-min cut, that REFUTES NO-Q-ONLY/C-alltie.
Recheck with full gamma-min enumeration (small enough? N=20 too big for maxcut_all). Use loads() + verify
manually that the cut is max and connected, then probe: is there a SMALLER-Gamma connected max cut?"""
from fractions import Fraction as F
from collections import deque
from _bdef_construct import loads, mycielski, union_disjoint, add_edges, Cn, build_K_T, Kcomponents

isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
n,E=union_disjoint(isl,g15); n,E=add_edges((n,E),[(0,5)])
adj=[set() for _ in range(n)]
for a,b in E: adj[a].add(b); adj[b].add(a)
info=loads(n,E)
if info is None:
    print("loads None"); raise SystemExit
N=info['n']; side=info['side']; T=info['T']
print("N=",N)
print("loads-cut side=",side)
# cut size and max
def cutsize(side):
    return sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
print("loads-cut cutsize=",cutsize(side))
# B-connected?
def Bconn(side):
    seen={0};q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v);q.append(v)
    return len(seen)==n
print("B-connected=",Bconn(side))
# is the bridge (0,5) cut or bad?
print("bridge (0,5): side0=",side[0]," side5=",side[5]," -> ",("CUT" if side[0]!=side[5] else "BAD"))
print("Gamma(loads)=",info['G'])
# Is the C5 island B-connected to the rest? The only inter-block edge is bridge (0,5).
# If bridge is CUT (in B), then removing it disconnects B into island{0..4} and rest.
# But B must be connected for a valid cut in this framework. Check.
print("T=",[str(T[v]) for v in range(N)])
O=[v for v in range(N) if T[v]>N]
print("O=",O)
# Now: the island {0,1,2,3,4} K-comp disjoint from O. Is this a valid gamma-min connected max cut?
# If yes -> NO-Q-ONLY is FALSE. Investigate whether a different cut gives smaller Gamma.
