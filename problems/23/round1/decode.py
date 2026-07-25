"""Decode graph6 strings and identify structure (exact, integer only)."""
import sys, itertools
import networkx as nx

def g6(s):
    return nx.from_graph6_bytes(s.encode())

def bip_exact(G):
    V = list(G.nodes()); n = len(V); idx = {v:i for i,v in enumerate(V)}
    E = [(idx[u],idx[v]) for u,v in G.edges()]
    best = len(E)
    for mask in range(1 << (n-1)):
        m2 = mask << 1
        c = sum(1 for u,v in E if ((m2>>u)&1)==((m2>>v)&1))
        if c < best: best = c
    return best

def report(name, s):
    G = g6(s)
    n = G.number_of_nodes(); m = G.number_of_edges()
    degs = sorted(d for _,d in G.degree())
    b = bip_exact(G)
    print(f"{name}: g6={s}  N={n} m={m} degseq={degs} bip={b}  25*bip={25*b} N^2={n*n}")
    print(f"    edges: {sorted(tuple(sorted(e)) for e in G.edges())}")
    # test: is it a blow-up of C5?
    for k in [5,7]:
        Ck = nx.cycle_graph(k)
        print(f"    hom to C{k}? ", has_hom(G, Ck))
    print(f"    girth={nx.girth(G) if m else '-'}  connected={nx.is_connected(G)}  chromatic-ish clique={nx.graph_clique_number(G) if hasattr(nx,'graph_clique_number') else max(len(c) for c in nx.find_cliques(G))}")
    return G

def has_hom(G, H):
    """exact backtracking homomorphism test G -> H"""
    V = sorted(G.nodes(), key=lambda v: -G.degree(v))
    Hn = list(H.nodes())
    f = {}
    def bt(i):
        if i == len(V): return True
        v = V[i]
        for h in Hn:
            ok = True
            for u in G[v]:
                if u in f and not H.has_edge(f[u], h):
                    ok = False; break
            if ok:
                f[v] = h
                if bt(i+1): return True
                del f[v]
        return False
    return bt(0)

if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        if line:
            report("G", line)
