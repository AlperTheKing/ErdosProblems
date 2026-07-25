"""Search: is there a triangle-free graph with bip(G) > |E|/5 ?

(bip <= |E|/5 would be a natural sublemma; it implies the N^2/25 conjecture for every
triangle-free graph with |E| >= N^2/5.  It is exactly tight for C5 and for C5[n].)
Exhaustive over connected triangle-free graphs from nauty geng, exact max cut.
Run:  python edge_ratio_search.py
"""
import os
import subprocess
import sys

GENG = os.environ.get("GENG", r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe")


def graph6_to_edges(line):
    data = [ord(c) - 63 for c in line.strip()]
    n = data[0]
    bits = []
    for x in data[1:]:
        bits += [(x >> k) & 1 for k in range(5, -1, -1)]
    E, idx = [], 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                E.append((i, j))
            idx += 1
    return n, E


def bip(n, E):
    """|E| - maxcut, exact, brute force over 2^(n-1) bipartitions."""
    best = -1
    for mask in range(1 << (n - 1)):
        s = mask << 1
        c = 0
        for (u, v) in E:
            if ((s >> u) & 1) != ((s >> v) & 1):
                c += 1
        if c > best:
            best = c
    return len(E) - best


def run(n, mindeg):
    cmd = [GENG, "-t", "-c", f"-d{mindeg}", str(n)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True,
                         stderr=subprocess.DEVNULL)
    bestr, argb, cnt, beat = 0, None, 0, []
    for line in p.stdout:
        if not line.strip():
            continue
        m, E = graph6_to_edges(line)
        b = bip(m, E)
        cnt += 1
        if 5 * b > len(E):
            beat.append((line.strip(), m, len(E), b))
        if len(E) and b * 1.0 / len(E) > bestr:
            bestr, argb = b / len(E), (line.strip(), m, len(E), b)
    return cnt, bestr, argb, beat


if __name__ == "__main__":
    for (n, d) in [(5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (11, 3), (12, 3)]:
        cnt, bestr, argb, beat = run(n, d)
        print(f"n={n} (min degree>={d}): {cnt} graphs; max bip/|E| = {bestr:.6f} "
              f"(1/5 = 0.2) at {argb};  #graphs with 5*bip > |E| : {len(beat)}")
        if beat:
            print("   COUNTEREXAMPLES to bip <= |E|/5:", beat[:5])
        sys.stdout.flush()
