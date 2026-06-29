"""Is Codex's block-192 two-sided-detour example a GLOBAL MAX cut? If non-max, (M) survives (its
interior-overlap is not on a max cut). Reconstruct (base nested N=26 + two cut-paths 0->3 + two cut-paths
8->5), then: (a) check parity is locally max (no single flip improves); (b) strong local-search max-cut
(many random restarts + 1-flip hill climb) to find best cut; compare to parity. If best > parity => NON-MAX."""
import random
from _tail_positive_extra_counterexample import add_cut_leaves, add_cut_path
from _M_tailswitch_gate import build_pd, tri_free
from _h import Bconn
from _satzmu_conn import struct_for_side

def adj_from(n,edges):
    adj=[set() for _ in range(n)]
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    return adj
def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def hillclimb(n,adj,s):
    s=s[:]; improved=True
    while improved:
        improved=False
        for v in range(n):
            d=sum(1 for w in adj[v] if s[w]==s[v])-sum(1 for w in adj[v] if s[w]!=s[v])
            if d>0: s[v]^=1; improved=True
    return s

# build base + two-sided detours (exactly Codex's construction)
n,edges=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]
for _ in range(2):
    n,edges,side=add_cut_path(n,edges,side,0,3,5)
    n,edges,side=add_cut_path(n,edges,side,8,5,5)
edges=sorted(set(edges)); adj=adj_from(n,edges)
print(f"N={n} tri-free={tri_free(n,adj)} Bconn(parity)={Bconn(n,adj,side)}")
pc=cutsize(n,adj,side); print(f"parity cutsize={pc}")
# (a) single-flip local max?
sf=[(v,cutsize(n,adj,[side[i]^(i==v) for i in range(n)])) for v in range(n)]
imp=[(v,c) for v,c in sf if c>pc]
print(f"single-vertex improving flips: {imp[:5]}{'...' if len(imp)>5 else ''} (count={len(imp)})")
# (b) strong local search for global max (random restarts)
random.seed(12345)
best=pc; bestmoves=0
for trial in range(400):
    s0=[random.randint(0,1) for _ in range(n)]
    s1=hillclimb(n,adj,s0); c=cutsize(n,adj,s1)
    if c>best: best=c
# also hillclimb from parity
sp=hillclimb(n,adj,side); cp=cutsize(n,adj,sp)
print(f"hillclimb-from-parity cutsize={cp}  (parity was {pc})")
print(f"BEST cut found (400 restarts) = {best}")
print(f"=== {'NON-MAX: parity '+str(pc)+' < found '+str(best)+' => two-sided-detour example is NOT global max => does NOT refute (M)' if best>pc else 'parity may be max (heuristic found nothing bigger) -- need exact solver, FLAG'} ===")
