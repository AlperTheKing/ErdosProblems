from harness import *
results=[]
def rec(name,N,edges):
    edges=sorted(set((min(u,v),max(u,v)) for u,v in edges))
    b,e,mc,d,tf=evalone(N,edges)
    results.append((round(b/(N*N/25),3),name,N,e,b,d,tf,in_band(N,e)))
    return edges

# Generalized Petersen GP(n,k): outer cycle, inner cycle step k, spokes. Triangle-free for most n,k.
def GP(n,k):
    edges=[]
    for i in range(n):
        edges.append((i,(i+1)%n))           # outer
        edges.append((n+i, n+(i+k)%n))       # inner
        edges.append((i, n+i))               # spoke
    return 2*n, edges
for (n,k) in [(7,2),(8,3),(9,2),(10,2),(10,3),(11,2),(12,5),(7,3),(9,4),(11,3),(12,4)]:
    N,e=GP(n,k)
    # check triangle free first cheaply
    b,ee,mc,d,tf=evalone(N,e)
    if tf and in_band(N,ee):
        rec(f"GP({n},{k})",N,e)

# Mobius-Kantor = GP(8,3). Desargues=GP(10,3). Nauru=GP(12,5). Already covered.
# Heawood graph (bipartite, 14 vtx, girth 6) - bipartite => beta could be 0? maxcut=e. skip but test:
heawood=[]
# Heawood: vertices 0..13 cycle with chords; standard LCF [5,-5]^7
import itertools
n=14; lcf=[5,-5]*7
hw=[(i,(i+1)%n) for i in range(n)]
for i in range(n):
    hw.append((i,(i+lcf[i])%n))
rec("Heawood",14,hw)

for r in sorted(results,reverse=True): print(r)
