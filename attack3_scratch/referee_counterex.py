import networkx as nx
from referee_factored import is_triangle_free, all_max_cuts, analyze

# The counterexample found: graph6 'H?AFBo]' on N=9, with ells=[5,7].
G = nx.from_graph6_bytes(b'H?AFBo]')
G = nx.convert_node_labels_to_integers(G)
print("N =", G.number_of_nodes(), " edges =", G.number_of_edges())
print("triangle-free:", is_triangle_free(G))
print("edges:", sorted(tuple(sorted(e)) for e in G.edges()))
best, cuts, nodes = all_max_cuts(G)
print("maxcut value:", best, " #maxcuts:", len(cuts))
print()
seen=set()
for X in cuts:
    r = analyze(G, X)
    if r is None: continue
    key = (tuple(sorted(r['ells'])),)
    if key in seen: continue
    seen.add(key)
    print(f"  cut X={sorted(X)} |M|={r['M']} ells={sorted(r['ells'])} "
          f"L={r['L']} S={r['S']} Gamma={r['Gamma']} "
          f"L*S={r['LS']} (N^2={r['N2']}) "
          f"=> L*S<=N^2 ? {r['LS']<=r['N2']}   Gamma<=N^2 ? {r['Gamma']<=r['N2']}")
