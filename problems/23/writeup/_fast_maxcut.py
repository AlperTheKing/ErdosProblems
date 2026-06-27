import numpy as np
def maxcut_all_fast(n, adj):
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    if not edges:
        # no edges: every assignment is max-cut with 0; but our use needs M nonempty so irrelevant
        return [[0]*n]
    M=1<<(n-1)
    # bit matrix: side[k][u]
    idx=np.arange(M, dtype=np.uint32)
    bits=np.zeros((M,n), dtype=np.uint8)
    for u in range(n-1):
        bits[:,u]=((idx>>u)&1).astype(np.uint8)
    # vertex n-1 fixed to 0
    eu=np.array([e[0] for e in edges]); ev=np.array([e[1] for e in edges])
    cutcount=(bits[:,eu]!=bits[:,ev]).sum(axis=1)
    best=cutcount.max()
    sel=np.where(cutcount==best)[0]
    return [bits[k].tolist() for k in sel]
