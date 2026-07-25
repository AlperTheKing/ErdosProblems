"""Final consistency checks for every numeric claim made in F1.md."""
import networkx as nx
from itertools import combinations
from f1_bip import g6_decode, bip_bruteforce, is_triangle_free

ok = True


def chk(name, cond, extra=""):
    global ok
    ok = ok and bool(cond)
    print(("PASS " if cond else "FAIL ") + name + (" " + str(extra) if extra else ""))


# --- 1. And(4) = C11(1,4) is one of the N=11 extremal graphs -----------------
And4 = nx.circulant_graph(11, [1, 4])
n, E = g6_decode("J?bFF`wN?{?")
G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(E)
chk("And(4)=C11(1,4) is the 4-regular extremal graph at N=11",
    nx.is_isomorphic(G, And4) and bip_bruteforce(11, list(And4.edges())) == 4)

# --- 2. Grotzsch graph is extremal at N=11 ----------------------------------
def mycielskian(H):
    M = nx.Graph(); nn = H.number_of_nodes()
    for u, v in H.edges():
        M.add_edge(u, v); M.add_edge(u, nn + v); M.add_edge(v, nn + u)
    for i in range(nn):
        M.add_edge(nn + i, 2 * nn)
    return M
GR = mycielskian(nx.cycle_graph(5))
n2, E2 = g6_decode("J?BD@g]Qvo?")
G2 = nx.Graph(); G2.add_nodes_from(range(n2)); G2.add_edges_from(E2)
chk("Grotzsch graph is extremal at N=11 (bip=4)",
    nx.is_isomorphic(G2, GR) and bip_bruteforce(11, list(GR.edges())) == 4)

# --- 3. C13(1,5) is extremal at N=13 ---------------------------------------
C13 = nx.circulant_graph(13, [1, 5])
chk("C13(1,5) triangle-free with bip=6=floor(169/25)",
    is_triangle_free(13, list(C13.edges())) and
    bip_bruteforce(13, list(C13.edges())) == 6 and 13 * 13 // 25 == 6)

# --- 4. N=14 unique extremal graph: bip=7, not C5-colourable ---------------
n4, E4 = g6_decode("M?AE@bH{AYN_LgBs?")
chk("a(14) witness: triangle-free, 32 edges, bip=7",
    is_triangle_free(14, E4) and len(E4) == 32 and bip_bruteforce(14, E4) == 7)

# --- 5. K_{m,m} diagonal cut: 1-locally optimal, uncut = N^2/8 -------------
for m in (4, 6, 8, 10):
    K = nx.complete_bipartite_graph(m, m)
    X = list(range(m)); Y = list(range(m, 2 * m))
    A = set(X[:m // 2]) | set(Y[:m // 2])
    B = set(K.nodes()) - A
    uncut = sum(1 for u, v in K.edges() if (u in A) == (v in A))
    # single-flip improvement?
    best_gain = 0
    for v in K.nodes():
        same = sum(1 for w in K[v] if (w in A) == (v in A))
        cross = K.degree(v) - same
        best_gain = max(best_gain, same - cross)
    N = 2 * m
    chk(f"K_{m},{m} diagonal cut 1-locally optimal, uncut={uncut}=N^2/8={N*N//8}",
        best_gain <= 0 and uncut == N * N // 8 and uncut * 25 > N * N)

# --- 6. counts of maximal triangle-free graphs (A006855) -------------------
counts = {5: 3, 6: 4, 7: 6, 8: 10, 9: 16, 10: 31, 11: 61, 12: 147, 13: 392,
          14: 1274, 15: 5036}
chk("h<=13 maximal triangle-free total = 670",
    sum(counts[h] for h in range(5, 14)) == 670,
    sum(counts[h] for h in range(5, 14)))

# --- 7. phi(N) <= N^2/25 and the closed form -------------------------------
def phi(N):
    best = -1
    for a in range(N + 1):
        for b in range(N + 1 - a):
            for c in range(N + 1 - a - b):
                for d in range(N + 1 - a - b - c):
                    t = (a, b, c, d, N - a - b - c - d)
                    best = max(best, min(t[i] * t[(i + 1) % 5] for i in range(5)))
    return best
bad = [N for N in range(1, 40)
       if phi(N) * 25 > N * N or
       phi(N) != (N // 5) ** 2 + ((N // 5) if N % 5 >= 3 else 0)]
chk("phi(N) closed form and phi(N)<=N^2/25 for N<=39", not bad, bad)

# --- 8. deletion inequality bip(G) <= bip(G-v) + floor(d(v)/2) -------------
import random
random.seed(3)
bad2 = 0
for trial in range(400):
    n = random.randint(5, 9)
    E = [(u, v) for u, v in combinations(range(n), 2) if random.random() < 0.4]
    if not is_triangle_free(n, E):
        continue
    b = bip_bruteforce(n, E)
    for v in range(n):
        Ev = [(u, w) for (u, w) in E if u != v and w != v]
        rel = {}
        for x in range(n):
            if x != v:
                rel[x] = len(rel)
        Ev = [(rel[u], rel[w]) for (u, w) in Ev]
        d = sum(1 for (u, w) in E if u == v or w == v)
        if b > bip_bruteforce(n - 1, Ev) + d // 2:
            bad2 += 1
chk("deletion inequality on 400 random triangle-free graphs", bad2 == 0, bad2)

print()
print("ALL CHECKS PASSED" if ok else "SOME CHECK FAILED")
