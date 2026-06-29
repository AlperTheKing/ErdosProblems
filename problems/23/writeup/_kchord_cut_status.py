"""CRITICAL: is the k-chord parity cut (used in all hub/descent gates) actually a connected-B MAXIMUM cut?
If not, its interval-Hall 'failures' are on cuts that never arise in the reduction (which only sees
connected-B max cuts), making the descent lemma's validation irrelevant. Check for k=3,6 clen=4,6:
 (a) cutsize(parity) vs global max cut; (b) Bconn(parity); (c) is parity in maxcut_all?; (d) triangle-free.
Exact."""
from _h import maxcut_all, Bconn, bdist_restr

def kchord(k, clen=4):
    pend=clen*k; E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def tri_free(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True

for clen in (4,6):
    for k in (3,6):
        n,E=kchord(k,clen); adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        s=[v%2 for v in range(n)]
        pc=cutsize(n,adj,s)
        mc=maxcut_all(n,adj)
        maxsize=cutsize(n,adj,list(mc[0])) if mc else None
        parity_is_max = any(list(m)==s for m in mc)
        # is there ANY max cut equal to parity up to global flip?
        sflip=[1-x for x in s]
        parity_or_flip_max = any(list(m)==s or list(m)==sflip for m in mc)
        print(f"k={k} clen={clen} N={n}: tri-free={tri_free(n,adj)} parity-cutsize={pc} GLOBAL-maxcut={maxsize} "
              f"parity-IS-max={pc==maxsize} Bconn(parity)={Bconn(n,adj,s)} parity-in-maxcut_all={parity_is_max or parity_or_flip_max} "
              f"#maxcuts={len(mc)}",flush=True)
