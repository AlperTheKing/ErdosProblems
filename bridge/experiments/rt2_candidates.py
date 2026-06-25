import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h2_redteam2 import analyze, build, beta, has_triangle
import itertools

def conn_set(N, gens):
    S = set()
    for g in gens:
        S.add(g % N); S.add((-g) % N)
    S.discard(0); return S
def circ_edges(N, gens):
    S = conn_set(N, gens); edges=set()
    for v in range(N):
        for s in S:
            w=(v+s)%N
            e=(min(v,w),max(v,w)); edges.add(e)
    return sorted(edges)

CANDS = []

# === Family 1: vertex-transitive circulants on 15 ===
CANDS.append(("Cay(Z15,{1,4,6})", 15, circ_edges(15,(1,4,6))))   # degree 6
CANDS.append(("Cay(Z15,{2,3,7})", 15, circ_edges(15,(2,3,7))))   # degree 6 (other)
CANDS.append(("Cay(Z15,{1,4})", 15, circ_edges(15,(1,4))))       # degree 4
CANDS.append(("Cay(Z15,{2,7})", 15, circ_edges(15,(2,7))))       # degree 4
CANDS.append(("Cay(Z15,{1,6})", 15, circ_edges(15,(1,6))))

# === Family 1b: vertex-transitive circulants on 20 ===
CANDS.append(("Cay(Z20,{1,4,9})", 20, circ_edges(20,(1,4,9))))   # degree 6
CANDS.append(("Cay(Z20,{1,5,8})", 20, circ_edges(20,(1,5,8))))
CANDS.append(("Cay(Z20,{1,8,9})", 20, circ_edges(20,(1,8,9))))
CANDS.append(("Cay(Z20,{2,5,9})", 20, circ_edges(20,(2,5,9)) if False else circ_edges(20,(1,4,6))))

# === Family 2: C15 odd cycle as beta-witness, padded to 15 = just C15 ===
C15 = [(i,(i+1)%15) for i in range(15)]
CANDS.append(("C15 (single 15-cycle)", 15, C15))

# === Family 3: Petersen-based (non-C5-hom core) variants on 15 ===
PETERSEN = [(0,1),(1,2),(2,3),(3,4),(4,0),(5,7),(7,9),(9,6),(6,8),(8,5),(0,5),(1,6),(2,7),(3,8),(4,9)]
# Petersen (10 vtx) + C5 on 10..14, joined to make it denser triangle-free
def petersen_plus_c5():
    e = list(PETERSEN)
    # outer extra C5 on 10..14
    e += [(10,11),(11,12),(12,13),(13,14),(14,10)]
    # join the two: connect extra C5 to inner pentagram vertices avoiding triangles
    # inner verts 5..9. Add a perfect matching 10->? keep tri-free
    add = [(10,5),(11,6),(12,7),(13,8),(14,9)]  # may create triangles; will be filtered
    e += add
    return e
CANDS.append(("Petersen+C5+match", 15, petersen_plus_c5()))

# Kneser-ish: Petersen is Kneser(5,2). Try Petersen disjoint-union-ish.

# === Family 4: two odd cycles sharing structure: C9 + C5 + connections ===
# C9 on 0..8, C5 on 9..13, vertex 14 spare. Then add cross edges tri-free.
def c9_c5():
    e = [(i,(i+1)%9) for i in range(9)]
    e += [(9+i, 9+(i+1)%5) for i in range(5)]
    # connect 14 to alternate cycle vertices, tri-free
    e += [(14,0),(14,3),(14,6),(14,9),(14,11)]
    return e
CANDS.append(("C9+C5+hub14", 15, c9_c5()))

# === Family 5: C5[3] minus edges to create multiple disjoint odd cycles ===
def build_c5n(n):
    edges=[]
    for p in range(5):
        q=(p+1)%5
        for j in range(n):
            for k in range(n):
                edges.append((p*n+j, q*n+k))
    return edges
def c53_minus():
    e = set(tuple(sorted(x)) for x in build_c5n(3))
    # remove a near-perfect matching between parts to thin it but keep 3 odd cycles
    # remove edges (0,3),(1,4)... within part0->part1 mapping
    rm = [(0,3),(1,4),(2,5),(6,9),(7,10),(8,11),(12,0)]  # sample
    for r in rm:
        e.discard(tuple(sorted(r)))
    return sorted(e)
CANDS.append(("C5[3] minus matching", 15, c53_minus()))

# === Family 6: Cayley on Z20 sparser, degree 4, more rigid ===
CANDS.append(("Cay(Z20,{1,8})", 20, circ_edges(20,(1,8))))
CANDS.append(("Cay(Z20,{3,8})", 20, circ_edges(20,(3,8))))

# === Family 7: C5[4] reference (should be tight, sanity) ===
CANDS.append(("C5[4] (ref, tight)", 20, build_c5n(4)))
CANDS.append(("C5[3] (ref, tight)", 15, build_c5n(3)))

# Filter & report which are triangle-free quickly
from h2_redteam2 import build as bld, has_triangle as ht
print("name | N | edges | tri-free?")
for name,N,edges in CANDS:
    am = bld(N, edges)
    print(f"{name:30s} N={N} E={len(set(tuple(sorted(e)) for e in edges)):3d} trifree={not ht(N,am)}")
