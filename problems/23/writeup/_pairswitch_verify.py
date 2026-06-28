"""Direct verification that the paired switches {0,4},{1,5} repair the symmetric SPLIT-bad cut
J?b@b_wBuD? side 10000111100, preserving cut size, Gamma, and B-connectivity."""
from _h import dec, Bconn, bdist_restr
g6="J?b@b_wBuD?"; s=[1,0,0,0,0,1,1,1,1,0,0]
n,E=dec(g6)
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
def cutsize(ss): return sum(1 for u in range(n) for v in adj[u] if v>u and ss[u]!=ss[v])
def gamma(ss):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and ss[u]==ss[v]]
    G=0
    for (u,v) in M:
        d=bdist_restr(adj,ss,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G
base_c=cutsize(s); base_g=gamma(s)
print(f"base: cut={base_c} gamma={base_g} Bconn={Bconn(n,adj,s)}")
print(f"edge(0,4)? {4 in adj[0]}  edge(1,5)? {5 in adj[1]}  adj[0]={sorted(adj[0])} adj[5]={sorted(adj[5])}")
for pair in [(0,4),(1,5)]:
    s2=s[:]; s2[pair[0]]^=1; s2[pair[1]]^=1
    ok = cutsize(s2)==base_c and gamma(s2)==base_g and Bconn(n,adj,s2)
    print(f"flip {pair}: cut={cutsize(s2)} gamma={gamma(s2)} Bconn={Bconn(n,adj,s2)} -> {'GAMMA-PRESERVING-MAXCUT' if ok else 'NO'}")
