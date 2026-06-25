import itertools, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h2_redteam2 import build, beta, has_triangle

def check(name, N, edges):
    am=build(N,edges)
    if has_triangle(N,am):
        print(f"{name:28s} INVALID(triangle)"); return
    bG=beta(N,am,list(range(N)))
    n=N//5; target=2*n-1
    mn=999; arg=None
    for S in itertools.combinations(range(N),5):
        rem=[v for v in range(N) if v not in S]
        d=bG-beta(N,am,rem)
        if d<mn: mn=d; arg=S
    print(f"{name:28s} N={N} E={len(set(tuple(sorted(e)) for e in edges)):2d} beta={bG} target={target} min5drop={mn} margin={mn-target:+d} {'VIOLATION' if mn>target else 'ok'}")

# 4 disjoint C5's on 20 vertices (max odd-cycle packing). beta should be 4.
e=[]
for b in range(4):
    for i in range(5): e.append((b*5+i, b*5+(i+1)%5))
check("4x disjoint C5", 20, e)

# Mobius-Kantor graph GP(8,3): 16 vtx, girth 6, bipartite -> beta 0. skip (not 20).
# Mobius-Kantor + C5? Instead: Wagner/Mobius-Kantor not 20. Use GP(10,2) = dodecahedron done.

# C5[4] with one edge deleted (break tightness?) 
def c5n(n):
    e=[]
    for p in range(5):
        q=(p+1)%5
        for j in range(n):
            for k in range(n): e.append((p*n+j,q*n+k))
    return e
e=c5n(4); e=[x for x in e if x!=(0,4) and x!=(4,0)]  # delete one cross edge
check("C5[4] minus 1 edge", 20, e)

# C5[4] plus a "diagonal" chord inside the blow-up that stays tri-free? 
# add edge between two vertices of same part (part0: 0,1,2,3): they share neighbors (part1,part4) -> triangle. so can't.
# add edge between part0 and part2 (distance-2 parts): vtx0(part0)-vtx8(part2). common nbr? part1 between them: 0~{4..7}, 8~{4..7} -> common -> triangle. can't either.
# C5[4] is edge-maximal triangle-free. confirms rigidity.

# Petersen (10) blown up by 2 = Kneser-like 20-vtx, tri-free? Petersen has girth 5, blow-up by 2 keeps tri-free (blow-up of tri-free is tri-free).
PET=[(0,1),(1,2),(2,3),(3,4),(4,0),(5,7),(7,9),(9,6),(6,8),(8,5),(0,5),(1,6),(2,7),(3,8),(4,9)]
e=[]
for (u,v) in PET:
    for a in range(2):
        for b in range(2): e.append((u*2+a, v*2+b))
check("Petersen[2] blowup", 20, e)
