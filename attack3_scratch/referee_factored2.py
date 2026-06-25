import networkx as nx
from referee_factored import is_triangle_free, all_max_cuts, analyze, report

# -------------------------------------------------------------------
# DECISIVE TEST (ii): the theta witness "c5paths20".
# One bad edge u-v, but in B the two B-paths from u to v have UNEQUAL
# lengths (4 and 6), i.e. there is no clean global 5-shell layering.
# A theta graph: two terminals joined by two internally disjoint paths
# of even length (so each closes an odd cycle with the chord uv).
# We must (a) keep it triangle-free, (b) make (X,Y) a MAXIMUM cut with
# u,v on the SAME side (so uv is bad), (c) B connected.
# Construct: chord uv, plus path u-a1-a2-a3-v (len 4) and
#            path u-b1-b2-b3-b4-b5-v (len 6). All internal disjoint.
# -------------------------------------------------------------------
def theta_witness(len1=4, len2=6):
    G = nx.Graph()
    u, v = 'u', 'v'
    G.add_edge(u, v)                      # the chord = candidate bad edge
    # path 1
    prev = u
    for k in range(len1-1):
        nd = ('a', k); G.add_edge(prev, nd); prev = nd
    G.add_edge(prev, v)
    # path 2
    prev = u
    for k in range(len2-1):
        nd = ('b', k); G.add_edge(prev, nd); prev = nd
    G.add_edge(prev, v)
    return nx.convert_node_labels_to_integers(G)

print("="*70)
print("THETA WITNESS c5paths20 : chord uv + B-paths of length 4 and 6")
print("="*70)
for (l1,l2) in [(4,6),(4,4),(4,8),(6,6),(4,10)]:
    G = theta_witness(l1,l2)
    N = G.number_of_nodes()
    print(f"\n--- theta({l1},{l2}) N={N} triangle-free={is_triangle_free(G)} ---")
    best, cuts, nodes = all_max_cuts(G)
    print(f"    maxcut value = {best}, #maxcuts = {len(cuts)}")
    seen = set()
    for ci, X in enumerate(cuts):
        r = analyze(G, X)
        if r is None: continue
        key = (r['N'], r['M'], tuple(sorted(r['ells'])))
        if key in seen: continue
        seen.add(key)
        flagLS = "VIOLATION" if r['LS']>r['N2'] else ("tight" if r['LS']==r['N2'] else "ok")
        flagG  = "VIOLATION" if r['Gamma']>r['N2'] else ("tight" if r['Gamma']==r['N2'] else "ok")
        print(f"    cut N={r['N']} |M|={r['M']} ells={sorted(r['ells'])} "
              f"L={r['L']} S={r['S']} Gamma={r['Gamma']} L*S={r['LS']} N^2={r['N2']} "
              f"[LS:{flagLS}][Gamma:{flagG}]")
