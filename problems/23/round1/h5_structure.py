"""Identify the structure of the known extremal graphs at N=11..14 (Grotzsch, C13(1,5),
the N=12 and N=14 records) so the mechanism can be transplanted to N=49/51/74/76."""
from itertools import combinations
from h5_core import from_g6, edges_from_adj, maxcut_exhaustive, is_triangle_free

KNOWN = {
    "N12": "K?ABBBwerwBw",
    "N13": "L??ED@_~?~^_Fw",
    "N14": "M?AE@bH{AYN_LgBs?",
}


def circulant(n, S):
    adj = [0] * n
    for v in range(n):
        for s in S:
            for d in (s, n - s):
                adj[v] |= 1 << ((v + d) % n)
    return n, adj


def canon_deg_seq(n, adj):
    return sorted(bin(a).count("1") for a in adj)


def independence_number(n, adj):
    best = 0
    def ext(cand, size):
        nonlocal best
        if size + bin(cand).count("1") <= best:
            return
        if cand == 0:
            best = max(best, size)
            return
        v = (cand & -cand).bit_length() - 1
        ext(cand & ~(1 << v) & ~adj[v], size + 1)   # take v
        ext(cand & ~(1 << v), size)                 # skip v
    ext((1 << n) - 1, 0)
    return best


def girth(n, adj):
    from collections import deque
    best = 10 ** 9
    for s in range(n):
        dist = [-1] * n
        par = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            for u in range(n):
                if (adj[v] >> u) & 1:
                    if dist[u] == -1:
                        dist[u] = dist[v] + 1
                        par[u] = v
                        q.append(u)
                    elif u != par[v]:
                        best = min(best, dist[v] + dist[u] + 1)
    return best


def iso_circulant_search(n, adj):
    """Is this graph isomorphic to a circulant on Z_n?  Brute force over connection sets."""
    from networkx import Graph, is_isomorphic
    G = Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges_from_adj(n, adj))
    half = n // 2
    for r in range(1, half + 1):
        for S in combinations(range(1, half + 1), r):
            cn, cadj = circulant(n, S)
            if sum(bin(a).count("1") for a in cadj) != 2 * G.number_of_edges():
                continue
            C = Graph()
            C.add_nodes_from(range(n))
            C.add_edges_from(edges_from_adj(cn, cadj))
            if is_isomorphic(G, C):
                return S
    return None


def main():
    for name, s in KNOWN.items():
        n, adj = from_g6(s)
        m = len(edges_from_adj(n, adj))
        mc, _ = maxcut_exhaustive(n, adj)
        print(f"{name} {s}: N={n} m={m} maxcut={mc} bip={m-mc} trifree={is_triangle_free(n,adj)}")
        print(f"   degseq={canon_deg_seq(n,adj)} alpha={independence_number(n,adj)} girth={girth(n,adj)}")
        S = iso_circulant_search(n, adj)
        print(f"   circulant? {('C%d%s' % (n, S)) if S else 'NO'}")
        print()

    # a few named comparisons
    print("--- named triangle-free graphs ---")
    for label, (n, adj) in {
        "C13(1,5)": circulant(13, (1, 5)),
        "C13(1,3)": circulant(13, (1, 3)),
        "C11(1,4)": circulant(11, (1, 4)),   # Andrasfai And(4)
        "C8(1,4) Wagner": circulant(8, (1, 4)),
    }.items():
        m = len(edges_from_adj(n, adj))
        mc, _ = maxcut_exhaustive(n, adj)
        print(f"{label}: N={n} m={m} maxcut={mc} bip={m-mc} "
              f"trifree={is_triangle_free(n,adj)} 25bip={25*(m-mc)} N^2={n*n}")


if __name__ == "__main__":
    main()
