"""F7: blow-up machinery for bip.

BLOW-UP CUT LEMMA.  For any graph H on [k] and any class sizes n_1..n_k >= 0,

    bip(H[n]) = min_{sigma : V(H) -> {+1,-1}}  sum_{ij in E(H), sigma_i = sigma_j} n_i n_j ,

i.e. some optimal bipartition of the blow-up puts every class entirely on one side.

Part 1 of this script VERIFIES that lemma by brute force (build the actual blow-up graph and
compute its bip by exhaustive cut enumeration) on many random (H, n).

Part 2 computes  B_k(N) = max over triangle-free H with |H| <= k, and over class sizes
n >= 1 summing to N, of bip(H[n]) -- the best blow-up of a base graph of order <= k.

Run:  python f7_blowup.py verify
      python f7_blowup.py table  <kmax> <Nmax>
"""
import itertools
import random
import subprocess
import sys
import os
import numpy as np
import networkx as nx
from networkx.readwrite.graph6 import from_graph6_bytes

HERE = os.path.dirname(os.path.abspath(__file__))
GENG = os.environ.get("GENG", r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe")


# ---------------------------------------------------------------- brute force
def bip_brute(G):
    V = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(V)}
    E = [(idx[u], idx[v]) for u, v in G.edges()]
    n = len(V)
    best = len(E)
    for mask in range(1 << (n - 1)):
        m = mask << 1
        c = 0
        for u, v in E:
            if ((m >> u) & 1) == ((m >> v) & 1):
                c += 1
                if c >= best:
                    break
        if c < best:
            best = c
    return best


def blowup_graph(H, n):
    """H[n]: class i replaced by independent set of size n_i."""
    G = nx.Graph()
    off = {}
    t = 0
    for i, v in enumerate(sorted(H.nodes())):
        off[v] = t
        for a in range(n[i]):
            G.add_node(t + a)
        t += n[i]
    for u, v in H.edges():
        iu, iv = sorted(H.nodes()).index(u), sorted(H.nodes()).index(v)
        for a in range(n[iu]):
            for b in range(n[iv]):
                G.add_edge(off[u] + a, off[v] + b)
    return G


# ---------------------------------------------------------------- lemma formula
def colourings(k):
    """All 2-colourings of [k] up to global flip: vertex 0 fixed to side 0."""
    for mask in range(1 << (k - 1)):
        yield (mask << 1)


def mono_masks(H):
    """Boolean matrix (num_colourings x num_edges): entry = edge is monochromatic."""
    V = sorted(H.nodes())
    idx = {v: i for i, v in enumerate(V)}
    E = [(idx[u], idx[v]) for u, v in H.edges()]
    k = len(V)
    rows = []
    for c in colourings(k):
        rows.append([(((c >> u) & 1) == ((c >> v) & 1)) for u, v in E])
    return np.array(rows, dtype=np.int64), E, k


def bip_blowup_formula(H, n):
    M, E, k = mono_masks(H)
    prods = np.array([n[u] * n[v] for u, v in E], dtype=np.int64)
    if len(E) == 0:
        return 0
    return int((M @ prods).min())


# ---------------------------------------------------------------- part 1
def verify(trials=250):
    random.seed(4242)
    bad = 0
    done = 0
    for _ in range(trials):
        k = random.randint(3, 6)
        p = random.uniform(0.3, 0.8)
        H = nx.gnp_random_graph(k, p, seed=random.randrange(10 ** 9))
        n = [random.randint(0, 3) for _ in range(k)]
        if sum(n) < 2 or sum(n) > 13:
            continue
        G = blowup_graph(H, n)
        if G.number_of_nodes() > 14 or G.number_of_nodes() < 1:
            continue
        b1 = bip_brute(G)
        b2 = bip_blowup_formula(H, n)
        done += 1
        if b1 != b2:
            bad += 1
            print("LEMMA FAILS", nx.to_graph6_bytes(H, header=False), n, "brute", b1, "formula", b2)
    print(f"blow-up cut lemma: {done} random (H,n) pairs tested, {bad} failures")
    return bad


# ---------------------------------------------------------------- part 2
def triangle_free_graphs(k):
    """All triangle-free graphs on exactly k vertices (unlabelled), via geng -t."""
    out = subprocess.run([GENG, "-t", "-q", str(k)], capture_output=True, text=True)
    for line in out.stdout.split():
        line = line.strip()
        if line:
            yield from_graph6_bytes(line.encode()), line


def compositions(N, k):
    """all n_1..n_k >= 1 with sum N"""
    if k == 1:
        yield (N,)
        return
    for first in range(1, N - k + 2):
        for rest in compositions(N - first, k - 1):
            yield (first,) + rest


def best_blowup(k, N):
    """max bip(H[n]) over triangle-free H on exactly k vertices and n>=1 summing to N."""
    comps = np.array(list(compositions(N, k)), dtype=np.int64)
    if len(comps) == 0:
        return 0, None, None
    best = -1
    bestH = None
    bestn = None
    for H, g6 in triangle_free_graphs(k):
        M, E, kk = mono_masks(H)
        if len(E) == 0:
            continue
        ei = np.array([u for u, v in E])
        ej = np.array([v for u, v in E])
        prods = comps[:, ei] * comps[:, ej]          # (P x E)
        vals = prods @ M.T                            # (P x C)
        b = vals.min(axis=1)
        i = int(b.argmax())
        if b[i] > best:
            best, bestH, bestn = int(b[i]), g6, tuple(int(t) for t in comps[i])
    return best, bestH, bestn


def table(kmax, Nmax):
    print(f"{'N':>3} " + " ".join(f"B_{k}(N)".rjust(8) for k in range(3, kmax + 1)))
    for N in range(5, Nmax + 1):
        row = []
        for k in range(3, kmax + 1):
            if k > N:
                row.append("-")
                continue
            b, g6, n = best_blowup(k, N)
            row.append(str(b))
        print(f"{N:>3} " + " ".join(s.rjust(8) for s in row))


def detail(kmax, Nmax):
    for N in range(5, Nmax + 1):
        best = -1
        arg = None
        for k in range(3, min(kmax, N) + 1):
            b, g6, n = best_blowup(k, N)
            if b > best:
                best, arg = b, (k, g6, n)
        print(f"N={N:3d} best blow-up bip={best}  base k={arg[0]} g6={arg[1]} sizes={arg[2]}"
              f"   N^2/25={N * N / 25:.2f}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if cmd == "verify":
        sys.exit(1 if verify() else 0)
    elif cmd == "table":
        table(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == "detail":
        detail(int(sys.argv[2]), int(sys.argv[3]))
