## FINAL: can we run the AM-GM globally with AGGREGATE quantities?
## Define global potential phi (B-distance from a fixed reference set) giving 5 layers
## L0..L4 = level sets, BUT now layers need not be cleanly ordered for every bad edge.
## Test on the two-chords-shared-w and chained-chords: is there a single map to {0,1,2,3,4}
## with B-edges going +-1 and bad edges spanning 0<->4 ? (a C5-homomorphism / 5-colouring)
import networkx as nx, itertools
def try_C5_hom(B,M,X,Y):
    # search a labeling phi:V->Z5 with B-edges consecutive (diff +-1 mod5) and bad edges diff 2 (chord)
    # Actually for the cut decomposition the right target is: B-edge => |phi_i - phi_j|=1 (no wrap to
    # make it a PATH 0..4) OR a genuine C5 hom with wrap. The bad edge has B-dist 4 => path-labels 0,4.
    # We test PATH labeling: phi in {0..4}, B-edge => |diff|=1, bad edge => {0,4}.
    V=list(B.nodes())
    import itertools as it
    # brute over labelings (small)
    for lab in it.product(range(5),repeat=len(V)):
        phi=dict(zip(V,lab))
        ok=True
        for a,b in B.edges():
            if abs(phi[a]-phi[b])!=1: ok=False;break
        if not ok: continue
        for a,b in M:
            if {phi[a],phi[b]}!={0,4}: ok=False;break
        if ok: return phi
    return None

# instance 1
X={'w','u1','v1','u2','v2'}; Y={'a1','b1','a2','b2'}
B=nx.Graph(); B.add_nodes_from(X|Y)
for e in [('u1','a1'),('a1','w'),('w','b1'),('b1','v1'),
          ('u2','a2'),('a2','w'),('w','b2'),('b2','v2')]: B.add_edge(*e)
M=[('u1','v1'),('u2','v2')]
print("shared-w: path-C5-hom exists?", try_C5_hom(B,M,X,Y) is not None)

# instance 2: GENUINE obstruction = M (the bad-edge graph) contains an ODD CYCLE.
# (The previous "chained 2-chord" instance was NOT an obstruction: its M = u1-m-v2 is a PATH, hence
#  bipartite, so a {0,4} path-layering DOES exist, e.g. m=4, u1=v2=0 -- try_C5_hom returns a labeling.)
# Here M = C5: bad edges m0-m1-...-m4-m0, each with its own length-4 B-geodesic m_i-a_i-w_i-b_i-m_{i+1}
# (fresh internal vertices => triangle-free, every d_B(bad)=4; cf. m5cycle.py).
B2=nx.Graph(); M2=[]
ms=[f"m{i}" for i in range(5)]
for i in range(5):
    u,v=ms[i],ms[(i+1)%5]; a,w,b=f"a{i}",f"w{i}",f"b{i}"
    for e in [(u,a),(a,w),(w,b),(b,v)]: B2.add_edge(*e)
    M2.append((u,v))
B2.add_nodes_from(ms)
# A global {0,4} path-layering phi:V->{0..4} (B-edges |diff|=1, each bad edge spanning {0,4}) would force
# every m_i into {0,4} with adjacent m_i,m_{i+1} differing -- i.e. a proper 2-colouring of M. Since M is an
# ODD cycle (C5), it is NOT bipartite, so NO such layering exists. (try_C5_hom's brute force is infeasible
# at this size (N=20); the obstruction IS the non-bipartiteness of M, checked directly.)
Mg=nx.Graph(); Mg.add_edges_from(M2)
print("M-5-cycle: M (bad-edge graph) bipartite?", nx.is_bipartite(Mg), "(False => no {0,4} path-layering)")
print("-> M contains an ODD CYCLE => the instance has NO global path-layer labeling.")
print("   This is the genuine geodesic-incompatibility (cf. m5cycle.py / frustrated.py).")
