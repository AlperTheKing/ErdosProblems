"""Exact machine check of the three identities/inequalities proved in the report.

For every graph G in the test set and EVERY maximum cut of G we check
  (I1)  sigma(S) = sum_{v in S} sigma(v) - 2 e_B(S) + 2 e_M(S)      for all S   (identity)
  (I2)  4|M| = 2|E| - sum_v sigma(v)                                (identity)
  (L1)  sigma(v) >= 0                                               (vertex switch)
  (LA)  sum_{a in N_B(v)} max(2 - sigma(a), 0) <= sigma(v)          (SHARP STAR, Lemma A)
  (LA') sigma(v) + sum_{a in A} (sigma(a) - 2) >= 0 for every A subset N_B(v)  (equivalent form)
Test set: all connected triangle-free graphs on <= 8 vertices from nauty geng,
plus random triangle-free graphs.
"""
import os
import random
import subprocess
import sys
from itertools import combinations

GENG = os.environ.get("GENG", r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe")


def graph6_to_adj(line):
    line = line.strip()
    data = [ord(c) - 63 for c in line]
    n = data[0]
    bits = []
    for x in data[1:]:
        bits += [(x >> k) & 1 for k in range(5, -1, -1)]
    adj = [set() for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                adj[i].add(j); adj[j].add(i)
            idx += 1
    return n, adj


def check_graph(n, adj, verbose=False):
    E = [(u, v) for u in range(n) for v in adj[u] if u < v]
    if not E:
        return 0
    for (u, v) in E:                      # triangle-freeness
        assert not (adj[u] & adj[v])
    best, cuts = -1, []
    for mask in range(1 << (n - 1)):
        side = [0] + [(mask >> i) & 1 for i in range(n - 1)]
        c = sum(1 for (u, v) in E if side[u] != side[v])
        if c > best:
            best, cuts = c, [side]
        elif c == best:
            cuts.append(side)
    checked = 0
    for side in cuts:
        B = [e for e in E if side[e[0]] != side[e[1]]]
        M = [e for e in E if side[e[0]] == side[e[1]]]
        dB = [sum(1 for w in adj[v] if side[w] != side[v]) for v in range(n)]
        dM = [sum(1 for w in adj[v] if side[w] == side[v]) for v in range(n)]
        sig = [dB[v] - dM[v] for v in range(n)]
        assert 4 * len(M) == 2 * len(E) - sum(sig), "(I2) FAILED"
        for v in range(n):
            assert sig[v] >= 0, "(L1) FAILED"
        # (I1) and maximality on all subsets
        for mask in range(1 << n):
            S = {i for i in range(n) if (mask >> i) & 1}
            s1 = sum(1 for (u, v) in B if (u in S) != (v in S)) - \
                 sum(1 for (u, v) in M if (u in S) != (v in S))
            eB = sum(1 for (u, v) in B if u in S and v in S)
            eM = sum(1 for (u, v) in M if u in S and v in S)
            s2 = sum(sig[v] for v in S) - 2 * eB + 2 * eM
            assert s1 == s2, "(I1) FAILED"
            assert s1 >= 0, "max-cut property FAILED"
        # (LA) and (LA')
        for v in range(n):
            NB = [a for a in adj[v] if side[a] != side[v]]
            assert sum(max(2 - sig[a], 0) for a in NB) <= sig[v], "(LA) FAILED"
            for r in range(len(NB) + 1):
                for A in combinations(NB, r):
                    assert sig[v] + sum(sig[a] - 2 for a in A) >= 0, "(LA') FAILED"
        checked += 1
    return checked


def geng_stream(n, extra=("-c", "-t")):
    cmd = [GENG] + list(extra) + [str(n)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return [l for l in p.stdout.splitlines() if l.strip()]


def random_triangle_free(n, p, rng):
    adj = [set() for _ in range(n)]
    order = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(order)
    for (i, j) in order:
        if rng.random() < p and not (adj[i] & adj[j]):
            adj[i].add(j); adj[j].add(i)
    return adj


if __name__ == "__main__":
    tot_graphs = tot_cuts = 0
    for n in range(3, 9):
        lines = geng_stream(n)
        cnt = 0
        for line in lines:
            m, adj = graph6_to_adj(line)
            tot_cuts += check_graph(m, adj)
            cnt += 1
        tot_graphs += cnt
        print(f"n={n}: {cnt} connected triangle-free graphs -- all identities/inequalities hold")
    rng = random.Random(20260725)
    for trial in range(300):
        n = rng.randint(9, 13)
        adj = random_triangle_free(n, rng.uniform(0.2, 0.8), rng)
        tot_cuts += check_graph(n, adj)
        tot_graphs += 1
    print(f"random triangle-free graphs on 9..13 vertices: 300 graphs -- all hold")
    print(f"TOTAL: {tot_graphs} graphs, {tot_cuts} maximum cuts, 0 failures")
