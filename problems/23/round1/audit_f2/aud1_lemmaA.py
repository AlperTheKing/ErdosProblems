"""AUDIT 1.  Independent check of Lemma 1, Lemma 3, sigma(v)>=0, Lemma A (sharp star),
Corollary A1 (matching structure) and Corollary A2 (the proved bound), on
  * ALL connected triangle-free graphs on 3..8 vertices (geng -c -t), EVERY maximum cut;
  * additionally on every LOCALLY optimal cut (sigma(v)>=0 for all v) to see whether
    Lemma A needs more than vertex-local optimality.
"""
import os
import subprocess
import sys
from fractions import Fraction
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aud_core import sigma_set, sigma_by_recut, adj_of, cutsize

GENG = r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"


def g6(line):
    d = [ord(c) - 63 for c in line.strip()]
    n = d[0]
    bits = []
    for x in d[1:]:
        bits += [(x >> k) & 1 for k in range(5, -1, -1)]
    E, idx = [], 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                E.append((i, j))
            idx += 1
    return n, E


def check(n, E, side, want_max):
    adj = adj_of(n, E)
    B = [e for e in E if side[e[0]] != side[e[1]]]
    M = [e for e in E if side[e[0]] == side[e[1]]]
    sig = [sum(1 for w in adj[v] if side[w] != side[v]) -
           sum(1 for w in adj[v] if side[w] == side[v]) for v in range(n)]
    fails = []
    # Lemma 3
    if 4 * len(M) != 2 * len(E) - sum(sig):
        fails.append("L3")
    # Lemma 1 on all subsets + maximality
    for mask in range(1 << n):
        S = {i for i in range(n) if (mask >> i) & 1}
        s1 = sigma_set(S, E, side)
        if s1 != sigma_by_recut(S, E, side):
            fails.append("sigma-defn")
        eB = sum(1 for (u, v) in B if u in S and v in S)
        eM = sum(1 for (u, v) in M if u in S and v in S)
        if s1 != sum(sig[v] for v in S) - 2 * eB + 2 * eM:
            fails.append("L1")
        if want_max and s1 < 0:
            fails.append("not-max")
    # sigma(v)>=0
    if any(x < 0 for x in sig):
        fails.append("sigma_v")
    # Lemma A
    lemA_ok = True
    for v in range(n):
        NB = [a for a in adj[v] if side[a] != side[v]]
        if sum(max(2 - sig[a], 0) for a in NB) > sig[v]:
            lemA_ok = False
    if want_max and not lemA_ok:
        fails.append("LemmaA")
    # Corollary A1: B-edges inside Z={sigma<=1} form a matching, both ends sigma=1
    Z = [v for v in range(n) if sig[v] <= 1]
    Zs = set(Z)
    inner = [(u, v) for (u, v) in B if u in Zs and v in Zs]
    deg = {}
    a1_ok = True
    for (u, v) in inner:
        if sig[u] != 1 or sig[v] != 1:
            a1_ok = False
        deg[u] = deg.get(u, 0) + 1
        deg[v] = deg.get(v, 0) + 1
    if any(d > 1 for d in deg.values()):
        a1_ok = False
    if want_max and not a1_ok:
        fails.append("CorA1")
    # Corollary A2 : 4|M| <= 2|E| - sum_{Z0} d - sum_{Z1}(d+1)/2   (exact rationals)
    rhs = Fraction(2 * len(E))
    for a in range(n):
        d = len(adj[a])
        if sig[a] == 0:
            rhs -= Fraction(d)
        elif sig[a] == 1:
            rhs -= Fraction(d + 1, 2)
    if want_max and Fraction(4 * len(M)) > rhs:
        fails.append("CorA2")
    return fails, lemA_ok, a1_ok


def main():
    tot_g = tot_cuts = 0
    for n in range(3, 9):
        p = subprocess.run([GENG, "-c", "-t", str(n)], capture_output=True, text=True)
        lines = [l for l in p.stdout.splitlines() if l.strip()]
        cnt = 0
        for line in lines:
            m, E = g6(line)
            if not E:
                continue
            best, cuts = -1, []
            for mask in range(1 << (m - 1)):
                side = [0] + [(mask >> i) & 1 for i in range(m - 1)]
                c = cutsize(E, side)
                if c > best:
                    best, cuts = c, [side]
                elif c == best:
                    cuts.append(side)
            for side in cuts:
                f, _, _ = check(m, E, side, True)
                if f:
                    print("FAIL", n, line.strip(), side, f)
                    return
                tot_cuts += 1
            cnt += 1
        tot_g += cnt
        print(f"n={n}: {cnt} connected triangle-free graphs, all maximum cuts OK")
    print(f"TOTAL {tot_g} graphs, {tot_cuts} maximum cuts, 0 failures")

    # --- is Lemma A a consequence of vertex-local optimality alone? ---
    print("\n=== Lemma A at merely VERTEX-locally-optimal cuts (sigma(v)>=0 for all v) ===")
    bad = 0
    ex = None
    for n in range(3, 9):
        p = subprocess.run([GENG, "-c", "-t", str(n)], capture_output=True, text=True)
        for line in p.stdout.splitlines():
            if not line.strip():
                continue
            m, E = g6(line)
            adj = adj_of(m, E)
            for mask in range(1 << (m - 1)):
                side = [0] + [(mask >> i) & 1 for i in range(m - 1)]
                sig = [sum(1 for w in adj[v] if side[w] != side[v]) -
                       sum(1 for w in adj[v] if side[w] == side[v]) for v in range(m)]
                if any(x < 0 for x in sig):
                    continue                      # not vertex-locally optimal
                ok = True
                for v in range(m):
                    NB = [a for a in adj[v] if side[a] != side[v]]
                    if sum(max(2 - sig[a], 0) for a in NB) > sig[v]:
                        ok = False
                if not ok:
                    bad += 1
                    if ex is None:
                        ex = (line.strip(), m, E, side, sig)
    print(f"vertex-locally-optimal cuts VIOLATING Lemma A: {bad}")
    if ex:
        print("  example:", ex[0], "n=", ex[1], "side=", ex[3], "sigma=", ex[4])


if __name__ == "__main__":
    main()
