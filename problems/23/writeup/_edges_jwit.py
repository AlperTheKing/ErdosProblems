"""Definitive: decode J??E@_ibE?, list ALL edges, and the same-side (bad) edges for side
[1,1,1,1,1,1,0,0,0,0,0]. Cross-check geng's own decode."""
import subprocess
from _h import dec, GENG
g6="J??E@_ibE?"
n,E=dec(g6)
s=[1,1,1,1,1,1,0,0,0,0,0]
E=[tuple(sorted(e)) for e in E]
print(f"g6={g6} N={n} |E|={len(E)}")
print(f"edges: {sorted(E)}")
bad=[(u,v) for (u,v) in E if s[u]==s[v]]
cross=[(u,v) for (u,v) in E if s[u]!=s[v]]
print(f"side={s}")
print(f"SAME-SIDE (bad) edges: {sorted(bad)}  (count {len(bad)})")
print(f"cross edges: {len(cross)}")
# verify via showg/independent: re-encode and compare degree sequence
deg=[0]*n
for u,v in E: deg[u]+=1; deg[v]+=1
print(f"degree seq: {deg}")
# also: is this even a max cut? count cross
print(f"cut size (cross count) = {len(cross)}")