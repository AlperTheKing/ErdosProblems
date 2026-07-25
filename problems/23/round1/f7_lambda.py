"""F7: the blow-up Lagrangian

    lambda(H) = max_{x in simplex}  min_{sigma : V(H)->{+-1}}  sum_{ij in E, sigma_i=sigma_j} x_i x_j

By the Blow-up Cut Lemma, lambda(H) = sup_n bip(H[n]) / (sum n)^2, so lambda(H) > 1/25 for a
single triangle-free H would DISPROVE the Erdos conjecture (blow up H and take n large).
Conversely lambda(H) >= bip(H)/|H|^2 (uniform weights), so sup_H lambda(H) = the conjecture's
constant: the search below is a genuine (if long-shot) attack.

lambda is computed as an exact rational LOWER bound by integer hill-climbing over class-size
vectors n with sum n = N, using exact integer arithmetic:  bip(H[n]) = min_sigma sum_mono n_i n_j.

Usage:
  python f7_lambda.py named
  python f7_lambda.py scan <file-of-graph6>     (one g6 per line)
"""
import sys
import os
import random
from fractions import Fraction

import numpy as np
import networkx as nx
from networkx.readwrite.graph6 import from_graph6_bytes, to_graph6_bytes

TARGET = Fraction(1, 25)


# ---------------------------------------------------------------- core
def mono_matrix(H):
    """(C x E) 0/1 matrix of monochromatic-edge incidence over all 2-colourings (v0 pinned),
    reduced to the inclusion-MINIMAL rows (the minimal bipartite-ising edge sets)."""
    V = sorted(H.nodes())
    idx = {v: i for i, v in enumerate(V)}
    E = [(idx[u], idx[v]) for u, v in H.edges()]
    k = len(V)
    rows = set()
    for mask in range(1 << (k - 1)):
        c = mask << 1
        r = tuple(1 if (((c >> u) & 1) == ((c >> v) & 1)) else 0 for u, v in E)
        rows.add(r)
    rows = sorted(rows, key=sum)
    minimal = []
    for r in rows:
        rs = set(i for i, t in enumerate(r) if t)
        if not any(m <= rs for m in minimal):
            minimal.append(rs)
    M = np.zeros((len(minimal), len(E)), dtype=np.int64)
    for a, m in enumerate(minimal):
        for i in m:
            M[a, i] = 1
    ei = np.array([u for u, v in E], dtype=np.int64)
    ej = np.array([v for u, v in E], dtype=np.int64)
    return M, ei, ej, k


def bip_blowup(M, ei, ej, n):
    p = n[ei] * n[ej]
    return int((M @ p).min())


def hill_climb(M, ei, ej, k, N, rng, restarts=6, start=None):
    """max over integer n>=0, sum n = N, of bip(H[n]) -- local search, exact integers."""
    best = -1
    bestn = None
    for r in range(restarts + (1 if start is not None else 0)):
        if start is not None and r == 0:
            n = np.array(start, dtype=np.int64)
        else:
            n = np.zeros(k, dtype=np.int64)
            for _ in range(N):
                n[rng.randrange(k)] += 1
        cur = bip_blowup(M, ei, ej, n)
        improved = True
        while improved:
            improved = False
            order = list(range(k))
            rng.shuffle(order)
            for i in order:
                if n[i] == 0:
                    continue
                for j in range(k):
                    if i == j:
                        continue
                    n[i] -= 1
                    n[j] += 1
                    v = bip_blowup(M, ei, ej, n)
                    if v > cur:
                        cur = v
                        improved = True
                        break
                    n[i] += 1
                    n[j] -= 1
                if improved:
                    break
        if cur > best:
            best, bestn = cur, n.copy()
    return best, bestn


def lambda_lower(H, schedule=(10, 20, 40, 80, 160), seed=1, restarts=6):
    """Exact rational lower bound for lambda(H), plus the witnessing class sizes."""
    M, ei, ej, k = mono_matrix(H)
    rng = random.Random(seed)
    best = Fraction(0)
    bestn = None
    prev = None
    for N in schedule:
        start = None
        if prev is not None:
            scale = N // sum(prev)
            if scale >= 1:
                s = prev * scale
                s[0] += N - int(s.sum())
                if (s >= 0).all():
                    start = s
        b, n = hill_climb(M, ei, ej, k, N, rng, restarts=restarts, start=start)
        val = Fraction(int(b), N * N)
        if val > best:
            best, bestn = val, n
        prev = n
    return best, bestn, k


# ---------------------------------------------------------------- named graphs
def wagner():
    return nx.circulant_graph(8, [1, 4])


def grotzsch():
    return nx.mycielskian(nx.cycle_graph(5))


def gen_mycielskian(G, m):
    """generalised Mycielskian M_m(G) (m levels), triangle-free if G is."""
    n = G.number_of_nodes()
    V = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(V)}
    M = nx.Graph()
    for lev in range(m):
        for i in range(n):
            M.add_node((lev, i))
    M.add_node("z")
    for u, v in G.edges():
        M.add_edge((0, idx[u]), (0, idx[v]))
    for lev in range(1, m):
        for u, v in G.edges():
            M.add_edge((lev, idx[u]), (lev - 1, idx[v]))
            M.add_edge((lev, idx[v]), (lev - 1, idx[u]))
    for i in range(n):
        M.add_edge("z", (m - 1, i))
    return nx.convert_node_labels_to_integers(M)


def kneser(n, k):
    import itertools
    V = list(itertools.combinations(range(n), k))
    G = nx.Graph()
    G.add_nodes_from(range(len(V)))
    for a in range(len(V)):
        for b in range(a + 1, len(V)):
            if not (set(V[a]) & set(V[b])):
                G.add_edge(a, b)
    return G


def named_graphs():
    g = {}
    g["C5"] = nx.cycle_graph(5)
    g["C7"] = nx.cycle_graph(7)
    g["C9"] = nx.cycle_graph(9)
    g["C11"] = nx.cycle_graph(11)
    g["Wagner V8 = C8(1,4)"] = wagner()
    g["Petersen"] = nx.petersen_graph()
    g["Grotzsch = M(C5)"] = grotzsch()
    g["C13(1,5)"] = nx.circulant_graph(13, [1, 5])
    g["C11(1,3)"] = nx.circulant_graph(11, [1, 3])
    g["C13(1,3)"] = nx.circulant_graph(13, [1, 3])
    g["C13(1,4)"] = nx.circulant_graph(13, [1, 4])
    g["C14(1,4)"] = nx.circulant_graph(14, [1, 4])
    g["C16(1,6)"] = nx.circulant_graph(16, [1, 6])
    g["M2(C5) gen-Mycielski"] = gen_mycielskian(nx.cycle_graph(5), 2)
    g["Kneser(7,3)"] = kneser(7, 3)
    g["C5[2] (=blow-up)"] = nx.complete_multipartite_graph  # placeholder removed below
    del g["C5[2] (=blow-up)"]
    return g


def report(name, H, schedule, seed=1, restarts=6):
    import itertools
    tri = any(H.has_edge(a, b) and H.has_edge(b, c) and H.has_edge(a, c)
              for a, b, c in itertools.combinations(H.nodes(), 3))
    k = H.number_of_nodes()
    if tri:
        print(f"{name:26s} SKIPPED (has a triangle)")
        return None
    if k > 20:
        print(f"{name:26s} SKIPPED (k={k} too large for 2^(k-1) colourings)")
        return None
    val, n, kk = lambda_lower(H, schedule=schedule, seed=seed, restarts=restarts)
    flag = "  *** > 1/25 ***" if val > TARGET else ""
    print(f"{name:26s} k={k:3d} e={H.number_of_edges():3d}  lambda >= {val} = {float(val):.6f}"
          f"   (1/25 = 0.04)  sizes={list(n)}{flag}")
    return val


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "named"
    if cmd == "named":
        sched = (10, 20, 40, 80, 160, 320)
        for name, H in named_graphs().items():
            report(name, H, sched)
    elif cmd == "scan":
        path = sys.argv[2]
        sched = tuple(int(x) for x in (sys.argv[3].split(",") if len(sys.argv) > 3 else "20,60,120".split(",")))
        best = Fraction(0)
        bestg = None
        cnt = 0
        for line in open(path):
            s = line.strip()
            if not s:
                continue
            H = from_graph6_bytes(s.encode())
            val, n, k = lambda_lower(H, schedule=sched, seed=7, restarts=4)
            cnt += 1
            if val > best:
                best, bestg = val, (s, list(n))
                print(f"  new best: {s} lambda >= {val} = {float(val):.6f} sizes={list(n)}")
            if val > TARGET:
                print(f"*** COUNTEREXAMPLE CANDIDATE {s} lambda >= {val} > 1/25, sizes={list(n)}")
        print(f"scanned {cnt} graphs; best lambda lower bound {best} = {float(best):.6f} at {bestg}")
