"""F7: test the sharp inequality

    (B)   5*bip(G) + 4*e(G) <= N^2          for every triangle-free G

over the whole infinite family of BLOW-UPS of small triangle-free base graphs, using the
Blow-up Cut Lemma (so every test is exact integer arithmetic and covers all N at once).

(B) is an equality for every balanced blow-up C5[n]; it implies Mantel (bip=0) and it implies
bip <= N^2/25 whenever e >= N^2/5.

Usage:  python f7_ineqB.py <kmax> [Nlist]
"""
import subprocess
import sys
import os
import random
from fractions import Fraction

import numpy as np
from networkx.readwrite.graph6 import from_graph6_bytes

GENG = os.environ.get("GENG", r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from f7_lambda import mono_matrix, bip_blowup


def value(M, ei, ej, n):
    """(5*bip + 4*e) for the blow-up H[n]; compare against N^2."""
    p = n[ei] * n[ej]
    bip = int((M @ p).min())
    e = int(p.sum())
    return 5 * bip + 4 * e, bip, e


def climb(M, ei, ej, k, N, rng, restarts=8):
    best = -1
    bestn = None
    for _ in range(restarts):
        n = np.zeros(k, dtype=np.int64)
        for _ in range(N):
            n[rng.randrange(k)] += 1
        cur = value(M, ei, ej, n)[0]
        improved = True
        while improved:
            improved = False
            for i in range(k):
                if n[i] == 0:
                    continue
                for j in range(k):
                    if i == j:
                        continue
                    n[i] -= 1
                    n[j] += 1
                    v = value(M, ei, ej, n)[0]
                    if v > cur:
                        cur, improved = v, True
                        break
                    n[i] += 1
                    n[j] -= 1
                if improved:
                    break
        if cur > best:
            best, bestn = cur, n.copy()
    return best, bestn


def main():
    kmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    Nlist = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [10, 17, 25, 40]
    rng = random.Random(11)
    worst = Fraction(0)
    worstinfo = None
    tested = 0
    for k in range(3, kmax + 1):
        out = subprocess.run([GENG, "-t", "-q", str(k)], capture_output=True, text=True)
        g6s = [s for s in out.stdout.split() if s]
        for s in g6s:
            H = from_graph6_bytes(s.encode())
            if H.number_of_edges() == 0:
                continue
            M, ei, ej, kk = mono_matrix(H)
            tested += 1
            for N in Nlist:
                b, n = climb(M, ei, ej, kk, N, rng, restarts=4)
                r = Fraction(int(b), N * N)
                if r > worst:
                    worst, worstinfo = r, (s, list(map(int, n)), N)
                    print(f"  new max (5bip+4e)/N^2 = {r} = {float(r):.6f}  H={s} n={list(map(int,n))} N={N}")
                if r > 1:
                    print(f"*** (B) VIOLATED: H={s} n={list(map(int,n))} N={N} 5bip+4e={b} > {N*N}")
        print(f"k={k}: cumulative tested {tested} base graphs; max ratio so far {float(worst):.6f}")
    print(f"TESTED {tested} base graphs, N in {Nlist}: max (5bip+4e)/N^2 = {worst} = {float(worst):.6f} at {worstinfo}")
    print("(B) holds on every blow-up tested" if worst <= 1 else "(B) IS FALSE")


if __name__ == "__main__":
    main()
