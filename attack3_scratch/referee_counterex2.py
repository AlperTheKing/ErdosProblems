import networkx as nx

G = nx.from_graph6_bytes(b'H?AFBo]')
G = nx.convert_node_labels_to_integers(G)
N = G.number_of_nodes()

# Independent brute-force max cut
edges = list(G.edges())
best=-1; bestmasks=[]
for mask in range(1<<N):
    c=sum(1 for u,v in edges if ((mask>>u)&1)!=((mask>>v)&1))
    if c>best: best=c; bestmasks=[mask]
    elif c==best: bestmasks.append(mask)
print("max cut value =", best, " (#max cuts =", len(bestmasks), ")")

# Pick the failing cut X={0,1,2,3,4}
X = {0,1,2,3,4}
side = {v:(v in X) for v in range(N)}
cutval = sum(1 for u,v in edges if side[u]!=side[v])
print("cut value for X={0,1,2,3,4}:", cutval, "(== max?", cutval==best, ")")

B = nx.Graph(); B.add_nodes_from(range(N))
M=[]
for u,v in edges:
    if side[u]!=side[v]: B.add_edge(u,v)
    else: M.append((u,v))
print("B connected:", nx.is_connected(B))
print("bad edges M:", M)
dist = dict(nx.all_pairs_shortest_path_length(B))
for (u,v) in M:
    d = dist[u][v]
    print(f"  bad edge {u}-{v}: d_B={d} ell={d+1}  (even d => odd cycle len {d+1})")

# Confirm ell=7 edge has no shorter ODD cycle in the whole graph G that would lower its 'shortest odd cycle' length.
# In the open-problem definition ell(uv)=d_B(u,v)+1 is by the cut-graph B distance (fixed). We report it.
print()
print("Independent: girth / shortest odd cycle through each bad edge in G:")
for (u,v) in M:
    # shortest odd cycle through edge uv in G = 1 + shortest even path u..v in G-{edge uv}
    H = G.copy(); H.remove_edge(u,v)
    # shortest path u->v of EVEN length: BFS on layered graph (parity)
    from collections import deque
    INF=10**9
    d2={(u,0):0}; dq=deque([(u,0)])
    while dq:
        x,par=dq.popleft()
        for y in H[x]:
            st=(y,1-par)
            if st not in d2:
                d2[st]=d2[(x,par)]+1; dq.append(st)
    even_len = d2.get((v,0),INF)   # path of even length closes odd cycle with uv
    print(f"  bad edge {u}-{v}: shortest even u-v path in G\\e = {even_len} => shortest odd cycle len = {even_len+1}")
