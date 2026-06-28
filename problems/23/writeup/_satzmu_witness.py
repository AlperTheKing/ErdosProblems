from fractions import Fraction as F
from _h import dec, loads
from _zmu import mu_edges
for g6 in ["J?AADBWeay?","J?ABBBWVCu?","J?`D@_w{EB?"]:
    n,E=dec(g6); info=loads(n,E); N=info['n']; T=info['T']; side=info['side']; adj=info['adj']
    sat=[v for v in range(N) if T[v]==N]
    mu=mu_edges(info); ze=[tuple(sorted(e)) for e,val in mu.items() if val==0]
    print(f"{g6} N={N}: O={[v for v in range(N) if T[v]>N]}")
    print(f"   saturated(T=N)={sat}; zero-mu edges={ze}")
    for v in sat:
        bn=[w for w in range(N) if w in adj[v] and side[w]!=side[v]]
        print(f"   T[{v}]={T[v]} (=N); B-neighbors of {v}={bn}; mu of those edges={[(v,w,float(mu.get(frozenset((v,w)),'na'))) for w in bn]}")
    for (u,w) in ze: print(f"   zero-mu ({u},{w}): T[{u}]={float(T[u])}, T[{w}]={float(T[w])}")
    print(f"   M={info['M']}; side={side}")
