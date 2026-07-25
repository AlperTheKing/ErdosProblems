"""F6 / Erdos #23 -- final exact identifications and the blow-up lemma check."""
from fractions import Fraction
import itertools
import networkx as nx
from f6_isbound_refutation import mwis_weight, bip_exact, triangle_free
from f6_family_Gpt import build, stats

def data(n, E):
    adj=[0]*n
    for u,v in E: adj[u]|=1<<v; adj[v]|=1<<u
    deg=[bin(a).count('1') for a in adj]
    m=len(E); w=mwis_weight(n,adj,deg); al=mwis_weight(n,adj,[1]*n)
    return dict(n=n,m=m,deg=deg,w=w,alpha=al,tf=triangle_free(n,adj),
                bip=bip_exact(n,adj,E))

print("=== C13(1,5) : the unique (3,5)-Ramsey graph on 13 vertices ===")
E13=[(i,(i+j)%13) for i in range(13) for j in (1,5) if i<(i+j)%13 or True]
E13=sorted({tuple(sorted((i,(i+j)%13))) for i in range(13) for j in (1,5)})
d=data(13,E13)
print(f"  N=13 m={d['m']} regular={set(d['deg'])} trianglefree={d['tf']} alpha={d['alpha']} "
      f"w={d['w']} m-w={d['m']-d['w']} bip={d['bip']}")
print(f"  (m-w)/N^2 = {Fraction(d['m']-d['w'],169)} = {(d['m']-d['w'])/169:.6f}   "
      f"min(floor(m/2),m-w)={min(d['m']//2,d['m']-d['w'])}   1/25=0.04  1/16=0.0625")
G13=nx.Graph(E13)
cens=nx.from_graph6_bytes(b"L?`DE`gl@YJODg")
print(f"  census champion L?`DE`gl@YJODg isomorphic to C13(1,5)? {nx.is_isomorphic(G13,cens)}")

print("\n=== identify the N=12 move-class witness K??FFB_vDwN_ ===")
W=nx.from_graph6_bytes(b"K??FFB_vDwN_")
n,adj,side,_=build(3,2); Gp=nx.Graph()
Gp.add_nodes_from(range(n))
for u in range(n):
    for v in adj[u]:
        if u<v: Gp.add_edge(u,v)
print(f"  witness: N={W.number_of_nodes()} m={W.number_of_edges()} bipartite={nx.is_bipartite(W)}")
print(f"  G(3,2):  N={Gp.number_of_nodes()} m={Gp.number_of_edges()} bipartite={nx.is_bipartite(Gp)}")
print(f"  isomorphic? {nx.is_isomorphic(W,Gp)}")

print("\n=== blow-up lemma:  bip(H[n]) = n^2 * bip(H)  (exact check) ===")
def blowup_bip_exact_bruteforce(E,nH,n):
    """min over ALL cuts of H[n] (not only class-split ones)."""
    idx={}; V=[]
    for i in range(nH):
        for t in range(n): idx[(i,t)]=len(V); V.append((i,t))
    EE=[]
    for i,j in E:
        for a in range(n):
            for b in range(n): EE.append((idx[(i,a)],idx[(j,b)]))
    N=len(V); adj=[0]*N
    for u,v in EE: adj[u]|=1<<v; adj[v]|=1<<u
    return bip_exact(N,adj,EE)
for name,E,nH,bipH in [("C5",[(i,(i+1)%5) for i in range(5)],5,1),
                       ("W8",[(i,(i+1)%8) for i in range(8)]+[(i,i+4) for i in range(4)],8,2)]:
    for n in (1,2):
        got=blowup_bip_exact_bruteforce(E,nH,n)
        print(f"  {name}[{n}]: full brute force over all 2^(N-1) cuts -> bip={got}; n^2*bip(H)={n*n*bipH}"
              f"  {'MATCH' if got==n*n*bipH else 'MISMATCH'}")
