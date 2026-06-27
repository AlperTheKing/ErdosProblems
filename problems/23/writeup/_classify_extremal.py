import sys, io
_o=sys.stdout; sys.stdout=io.StringIO()
from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG
sys.stdout=_o
from fractions import Fraction as F
import subprocess
from collections import deque

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def is_oddcycle_blowup(n,adj):
    """Return (k,sizes) if G is a balanced/unbalanced blow-up of an odd cycle C_{2k+1}, else None.
    Blow-up of C_m (m odd): vertex set partitions into m classes V_0..V_{m-1}, each an independent set,
    with complete bipartite between consecutive classes (cyclically) and NO other edges."""
    # quotient by 'same neighborhood' (true twins have same closed nbhd? here use open-nbhd equivalence,
    # since blow-up classes are modules with identical open neighborhoods)
    # group vertices by frozenset(neighbors)
    from collections import defaultdict
    groups=defaultdict(list)
    for v in range(n):
        groups[frozenset(adj[v])].append(v)
    # classes are the groups; each class must be independent and have identical nbhd (by construction true)
    classes=list(groups.values())
    m=len(classes)
    if m<3 or m%2==0: return None
    # build class-level adjacency
    cid={}
    for i,c in enumerate(classes):
        for v in c: cid[v]=i
    cadj=[set() for _ in range(m)]
    for v in range(n):
        for u in adj[v]:
            if cid[u]!=cid[v]: cadj[cid[v]].add(cid[u])
    # each class independent?
    for c in classes:
        for v in c:
            for u in c:
                if u in adj[v]: return None
    # class graph must be exactly a cycle C_m: every class degree 2, connected
    if any(len(cadj[i])!=2 for i in range(m)): return None
    # check single cycle
    seen={0}; prev=None; cur=0; order=[0]
    for _ in range(m-1):
        nxts=[x for x in cadj[cur] if x!=prev]
        if not nxts: return None
        nxt=nxts[0] if nxts[0] not in seen else (nxts[1] if len(nxts)>1 else None)
        # simpler: pick neighbor not equal prev
        cand=[x for x in cadj[cur] if x!=prev]
        nxt=cand[0]
        if nxt in seen and nxt!=0: return None
        prev,cur=cur,nxt; seen.add(cur); order.append(cur)
    if len(seen)!=m: return None
    # complete bipartite between consecutive classes: check by counting
    return (m, [len(c) for c in classes])

bad=[]
for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in out:
        n,E=dec(g6); adj=adj_of(n,E)
        r=gmin(n,adj,maxcut_all(n,adj))
        if r is None: continue
        side,G,M,ell=r
        if G==n*n:  # extremal
            bw=is_oddcycle_blowup(n,adj)
            if bw is None:
                bad.append((g6,n,G))
print("Extremal (Gamma=N^2) census graphs that are NOT odd-cycle blow-ups (must be 0 for rigidity):")
print("  count:",len(bad))
for g6,n,G in bad[:20]: print("   ",g6,"N=",n,"Gamma=",G)
print("If 0 => rigidity backbone (Gamma=N^2 => odd-cycle blow-up) holds across census N<=10.")
