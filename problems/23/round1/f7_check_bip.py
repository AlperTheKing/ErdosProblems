"""Cross-check the C++ exact bip engine against an independent Python brute force.

bip(G) = min over 2-colourings of the number of monochromatic edges.
Run:  python f7_check_bip.py
"""
import itertools, random, subprocess, sys, os
import networkx as nx
from networkx.readwrite.graph6 import to_graph6_bytes

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, "f7_bip.exe")


def bip_py(G):
    """Independent brute force: min monochromatic edges over all 2-colourings."""
    V = list(G.nodes())
    n = len(V)
    idx = {v: i for i, v in enumerate(V)}
    E = [(idx[u], idx[v]) for u, v in G.edges()]
    best = len(E)
    for mask in range(1 << (n - 1)):          # vertex 0 fixed on side 0
        m = mask << 1
        c = 0
        for u, v in E:
            if ((m >> u) & 1) == ((m >> v) & 1):
                c += 1
        if c < best:
            best = c
    return best


def g6(G):
    return to_graph6_bytes(G, header=False).decode().strip()


def main():
    random.seed(20260725)
    tests = []
    # named graphs
    tests.append(nx.cycle_graph(5))
    tests.append(nx.cycle_graph(7))
    tests.append(nx.cycle_graph(9))
    tests.append(nx.petersen_graph())
    tests.append(nx.complete_bipartite_graph(3, 4))
    # random triangle-free graphs on 6..12 vertices
    for n in range(5, 13):
        for _ in range(40):
            G = nx.gnp_random_graph(n, random.uniform(0.2, 0.55), seed=random.randrange(10 ** 9))
            # delete an edge from every triangle until triangle-free
            while True:
                tri = None
                for u, v, w in itertools.combinations(G.nodes(), 3):
                    if G.has_edge(u, v) and G.has_edge(v, w) and G.has_edge(u, w):
                        tri = (u, v)
                        break
                if tri is None:
                    break
                G.remove_edge(*tri)
            tests.append(G)

    lines = "\n".join(g6(G) for G in tests) + "\n"
    # feed one at a time so we can compare per-graph values
    bad = 0
    for G in tests:
        out = subprocess.run([EXE, "-1"], input=g6(G) + "\n", capture_output=True, text=True)
        # threshold -1 => report every graph with its exact bip
        parts = out.stdout.split()
        cpp = int(parts[1]) if len(parts) >= 2 else None
        py = bip_py(G)
        if cpp != py:
            bad += 1
            print("MISMATCH", g6(G), "cpp", cpp, "py", py)
    print(f"checked {len(tests)} graphs, mismatches: {bad}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
