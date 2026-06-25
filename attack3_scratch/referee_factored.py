import itertools, networkx as nx
from itertools import product

# ---------------------------------------------------------------
# Build the open-problem objects exactly as stated:
#  G triangle-free, (X,Y) a MAXIMUM cut, B = bipartite graph of cut edges,
#  M = monochromatic ("bad") edges (both endpoints same side),
#  ell(uv) = d_B(u,v)+1.  We require B connected on all N vertices.
#  L = max ell, S = sum ell, Gamma = sum ell^2.
# Claim under test:  L*S <= N^2   (=> Gamma <= N^2).
# ---------------------------------------------------------------

def is_triangle_free(G):
    for u in G:
        Nu = set(G[u])
        for v in Nu:
            if v <= u: continue
            if Nu & set(G[v]):
                return False
    return True

def all_max_cuts(G):
    """Return list of all maximum cuts as frozenset(X). Brute force (small N)."""
    nodes = list(G.nodes()); n = len(nodes)
    edges = [(nodes.index(u), nodes.index(v)) for u,v in G.edges()]
    best = -1; cuts = []
    for mask in range(1 << n):
        c = 0
        for (a,b) in edges:
            if ((mask>>a)&1) != ((mask>>b)&1): c += 1
        if c > best:
            best = c; cuts = [mask]
        elif c == best:
            cuts.append(mask)
    res = []
    for mask in cuts:
        X = frozenset(nodes[i] for i in range(n) if (mask>>i)&1)
        res.append(X)
    return best, res, nodes

def analyze(G, X):
    """Given a max cut X, build B, M, ell. Return dict or None if B not connected / no M."""
    nodes = list(G.nodes())
    side = {v: (v in X) for v in nodes}
    B = nx.Graph(); B.add_nodes_from(nodes)
    M = []
    for u,v in G.edges():
        if side[u] != side[v]:
            B.add_edge(u,v)            # cut edge
        else:
            M.append((u,v))            # bad / monochromatic edge
    if not nx.is_connected(B):
        return None
    if not M:
        return None
    # shortest path distances in B
    dist = dict(nx.all_pairs_shortest_path_length(B))
    ells = []
    ok = True
    for (u,v) in M:
        if v not in dist[u]:
            ok = False; break
        d = dist[u][v]
        # d must be even (odd cycle through uv has length d+1, odd) ; ell = d+1 >=5
        ells.append(d+1)
    if not ok:
        return None
    N = len(nodes)
    L = max(ells); S = sum(ells); Gamma = sum(e*e for e in ells)
    return dict(N=N, M=len(M), ells=ells, L=L, S=S, Gamma=Gamma,
                LS=L*S, N2=N*N)

def report(name, G, verbose=True):
    if not is_triangle_free(G):
        print(f"[{name}] NOT triangle-free, skip"); return []
    best, cuts, nodes = all_max_cuts(G)
    rows = []
    for ci, X in enumerate(cuts):
        r = analyze(G, X)
        if r is None: continue
        r['cut'] = ci
        rows.append(r)
    if not rows:
        if verbose: print(f"[{name}] no connected-B max cut with bad edges")
        return rows
    # worst over cuts (the claim must hold for the max cut; if multiple maxcuts, all must satisfy)
    for r in rows:
        flagLS  = "VIOLATION" if r['LS'] > r['N2'] else ("tight" if r['LS']==r['N2'] else "ok")
        flagG   = "VIOLATION" if r['Gamma'] > r['N2'] else ("tight" if r['Gamma']==r['N2'] else "ok")
        if verbose:
            print(f"[{name}] cut#{r['cut']} N={r['N']} |M|={r['M']} L={r['L']} S={r['S']} "
                  f"Gamma={r['Gamma']} | L*S={r['LS']} N^2={r['N2']} [LS:{flagLS}] [Gamma:{flagG}]  ells={sorted(r['ells'])}")
    return rows

# ---------------- C5[q] balanced blow-up ----------------
def C5_blowup(q):
    G = nx.Graph()
    groups = [[(i,k) for k in range(q)] for i in range(5)]
    for g in groups:
        for v in g: G.add_node(v)
    for i in range(5):
        for a in groups[i]:
            for b in groups[(i+1)%5]:
                G.add_edge(a,b)
    return G

if __name__ == "__main__":
    print("="*70)
    print("C5[q] extremal family (must be tight: L*S = N^2):")
    print("="*70)
    for q in range(1,6):
        report(f"C5[{q}]", C5_blowup(q))

    print()
    print("="*70)
    print("Odd cycles C_{2k+1} (must be tight: L=S=N, kappa*=1):")
    print("="*70)
    for k in range(2,7):
        n = 2*k+1
        report(f"C{n}", nx.cycle_graph(n))
