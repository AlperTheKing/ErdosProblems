import networkx as nx, itertools as it
def find_hom(B,M):
    V=list(B.nodes())
    for lab in it.product(range(5),repeat=len(V)):
        phi=dict(zip(V,lab))
        if all(abs(phi[a]-phi[b])==1 for a,b in B.edges()) and all({phi[a],phi[b]}=={0,4} for a,b in M):
            return phi
    return None
X2={'w','wp','u1','m','v2'}; Y2={'a1','b1','a2','b2'}
B2=nx.Graph(); B2.add_nodes_from(X2|Y2)
for e in [('u1','a1'),('a1','w'),('w','b1'),('b1','m'),
          ('m','a2'),('a2','wp'),('wp','b2'),('b2','v2')]: B2.add_edge(*e)
M2=[('u1','m'),('m','v2')]
phi=find_hom(B2,M2)
print("chained labeling:",phi)
# verify the two bad edges
for a,b in M2: print(a,b,"->",phi[a],phi[b])
## The point: each chord independently is a path 0-1-2-3-4 or 4-3-2-1-0. m can be the "4" end of
## chord1 and the "0" end of chord2 ONLY IF chord2 is labeled 0(m)-1-2-3-4, requiring a2,wp,b2,v2 = 1,2,3,4.
## And chord1 labeled u1=0..m=4. That is consistent because the two chords use DISJOINT middle verts.
## So this particular glue is still globally layerable. The TRUE incompatibility needs a CYCLE of chords.
