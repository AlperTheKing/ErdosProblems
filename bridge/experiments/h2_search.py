import itertools
from h2_redteam import is_triangle_free, min5drop, beta_sub

def edgeset(edges):
    return sorted(set(tuple(sorted(e)) for e in edges))

def cayley_z15(conn):
    E=[]
    for v in range(15):
        for s in conn:
            E.append((v,(v+s)%15))
    return edgeset(E)

def tf_quick(n, edges):
    adj=[0]*n
    for (u,v) in edges:
        adj[u]|=1<<v; adj[v]|=1<<u
    for (u,v) in edges:
        if adj[u]&adj[v]:
            return False
    return True

# 1) Exhaustive over all Cayley connection sets on Z15 (subsets of {1..7})
print("=== Cayley Z15 sweep ===")
best_break=[]
for r in range(1,8):
    for conn in itertools.combinations(range(1,8), r):
        E=cayley_z15(list(conn))
        if not tf_quick(15,E):
            continue
        md,S,bG = min5drop(15,E)
        thr=5
        if bG>=6:
            flag = "BREAK" if md>thr else ""
            if md>=4 and bG>=8:
                print(f"conn={conn} m={len(E)} beta={bG} min5drop={md} {flag}")
            if md>thr:
                best_break.append((conn,bG,md))
print("Cayley breakers:", best_break)
