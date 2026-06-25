#!/usr/bin/env python3
# Generate g6 for structured triangle-free candidate graphs on 5n vertices,
# to stress-test the per-graph Peeling Lemma pc(G) <= 2n-1.
import sys, itertools

def g6(n, edges):
    adj=[[0]*n for _ in range(n)]
    for u,v in edges:
        adj[u][v]=adj[v][u]=1
    bits=[]
    for j in range(1,n):
        for i in range(j):
            bits.append(adj[i][j])
    # pad to multiple of 6
    while len(bits)%6: bits.append(0)
    out=chr(n+63)
    for k in range(0,len(bits),6):
        val=0
        for b in bits[k:k+6]: val=(val<<1)|b
        out+=chr(val+63)
    return out

def triangle_free(n,edges):
    adj=[set() for _ in range(n)]
    for u,v in edges: adj[u].add(v); adj[v].add(u)
    for u,v in edges:
        if adj[u]&adj[v]: return False
    return True

def c5_blowup(sizes):
    # parts consecutive, complete bipartite between part i and i+1 mod 5
    n=sum(sizes);
    starts=[0]*5
    for i in range(1,5): starts[i]=starts[i-1]+sizes[i-1]
    def part_vertices(i): return range(starts[i], starts[i]+sizes[i])
    edges=[]
    for i in range(5):
        j=(i+1)%5
        for a in part_vertices(i):
            for b in part_vertices(j):
                edges.append((a,b))
    return n,edges

def cycle(n):
    return n,[(i,(i+1)%n) for i in range(n)]

def petersen():
    # outer C5 0-4, inner pentagram 5-9, spokes
    edges=[]
    for i in range(5): edges.append((i,(i+1)%5))
    for i in range(5): edges.append((5+i,5+((i+2)%5)))
    for i in range(5): edges.append((i,5+i))
    return 10,edges

def blowup(n0, edges0, t):
    # blow up each vertex into t copies; edge -> complete bipartite t x t
    n=n0*t
    def cp(v): return range(v*t,(v+1)*t)
    edges=[]
    for u,v in edges0:
        for a in cp(u):
            for b in cp(v): edges.append((a,b))
    return n,edges

def gen_petersen(n,k):
    # generalized Petersen GP(n,k): outer C_n, inner step-k, spokes. 2n vertices.
    edges=[]
    for i in range(n):
        edges.append((i,(i+1)%n))            # outer cycle
        edges.append((n+i, n+((i+k)%n)))     # inner
        edges.append((i, n+i))               # spoke
    return 2*n, edges

def dodecahedron():
    # dodecahedron = generalized Petersen GP(10,2), 20 vertices, girth 5
    return gen_petersen(10,2)

def mycielski(n0, edges0):
    # Mycielskian: vertices v0..v_{n-1}, u0..u_{n-1}, w.  n=2n0+1
    n=2*n0+1; w=2*n0
    adj=[set() for _ in range(n0)]
    for u,v in edges0: adj[u].add(v); adj[v].add(u)
    edges=list(edges0)
    for i in range(n0):
        for j in adj[i]:
            if i<j: pass
        for j in adj[i]:
            edges.append((n0+i, j))      # u_i ~ neighbors of v_i
    for i in range(n0):
        edges.append((n0+i, w))          # u_i ~ w
    # dedup
    ee=set()
    for a,b in edges:
        if a>b: a,b=b,a
        ee.add((a,b))
    return n,sorted(ee)

cands=[]
def add(name, nE):
    n,E=nE
    # dedup edges
    s=set()
    for a,b in E:
        if a==b: continue
        if a>b: a,b=b,a
        s.add((a,b))
    E=sorted(s)
    tf=triangle_free(n,E)
    cands.append((name,n,E,tf))

# 15-vertex (n=3) candidates
add("C5[3] balanced", c5_blowup([3,3,3,3,3]))
add("C5 unbal 1,2,3,4,5", c5_blowup([1,2,3,4,5]))
add("C5 unbal 2,2,3,4,4", c5_blowup([2,2,3,4,4]))
add("C5 unbal 1,3,3,4,4", c5_blowup([1,3,3,4,4]))
add("C5 unbal 2,3,3,3,4", c5_blowup([2,3,3,3,4]))
add("C15 cycle", cycle(15))
add("Mycielski(C5)=Grotzsch on11 + pad? ", mycielski(*cycle(5)))  # 11 vtx, will skip (not 15)

# 20-vertex (n=4) candidates
add("C5[4] balanced", c5_blowup([4,4,4,4,4]))
add("C5 unbal 2,4,4,5,5", c5_blowup([2,4,4,5,5]))
add("C5 unbal 3,3,4,5,5", c5_blowup([3,3,4,5,5]))
add("C5 unbal 1,4,5,5,5", c5_blowup([1,4,5,5,5]))
add("Petersen[2] blowup", blowup(*petersen(), 2))
add("C20 cycle", cycle(20))
add("Dodecahedron(listing)", dodecahedron())

# emit two files: 15-vertex and 20-vertex, only triangle-free ones with right n
f15=open("cand15.g6","w"); f20=open("cand20.g6","w"); meta=open("cand_meta.txt","w")
for name,n,E,tf in cands:
    meta.write(f"{name}\tn={n}\ttri_free={tf}\tedges={len(E)}\n")
    if not tf: continue
    line=g6(n,E)
    if n==15: f15.write(line+"\n")
    elif n==20: f20.write(line+"\n")
f15.close(); f20.close(); meta.close()
sys.stderr.write("wrote cand15.g6, cand20.g6, cand_meta.txt\n")
for name,n,E,tf in cands:
    sys.stderr.write(f"  {name}: n={n} tf={tf} e={len(E)}\n")
