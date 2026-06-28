"""Verify Codex's SAT-ZMU-CLASS structure correction (block 31) on I??CF@wFo:
the T=0 endpoint of a saturated-zero-mu edge is a NON-leaf dead B-subnetwork (zero load, zero traffic),
and deleting T=0 vertices is unstable (gamma-min Gamma changes). Exact."""
from fractions import Fraction as F
from _h import dec, loads, maxcut_all, gmin
from _zmu import mu_edges

g6="I??CF@wFo"
n,E=dec(g6); info=loads(n,E); N=info['n']; T=info['T']; side=info['side']; adj=info['adj']
print(f"{g6} N={N}")
print(f"  T={[float(t) for t in T]}")
print(f"  side={side}  M={info['M']}  Gamma={float(info['G'])}")
sat=[v for v in range(N) if T[v]==N]; T0=[v for v in range(N) if T[v]==0]
print(f"  saturated(T=N)={sat}  T0-vertices={T0}")
mu=mu_edges(info); ze=[tuple(sorted(e)) for e,val in mu.items() if val==0]
print(f"  zero-mu edges={ze}")
for v in T0:
    bd=[w for w in range(N) if w in adj[v] and side[w]!=side[v]]
    print(f"  T=0 vertex {v}: B-degree={len(bd)} (B-neighbors {bd})  => {'LEAF' if len(bd)==1 else 'NON-leaf dead-net'}")
# delete all T=0 vertices and recompute gamma-min Gamma
keep=[v for v in range(N) if T[v]!=0]
relabel={v:i for i,v in enumerate(keep)}
E2=[(relabel[a],relabel[b]) for (a,b) in E if a in relabel and b in relabel]
n2=len(keep)
info2=loads(n2,E2)
print(f"  after deleting T=0 vertices {T0}: N'={n2}, Gamma'={float(info2['G']) if info2 else 'loads=None'}")
print(f"  => Gamma {float(info['G'])} -> {float(info2['G']) if info2 else 'NA'} : deletion {'CHANGES' if info2 and info2['G']!=info['G'] else 'preserves'} Gamma (so simple deletion is NOT load/Gamma-stable)")
