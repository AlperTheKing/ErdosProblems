"""AUDIT 5.  Independent re-run of the bip <= |E|/5 exhaustive search (report Sec.6 / claim 10).
Uses geng directly, exact bitmask max-cut, exact integer comparison 5*bip vs |E|.
Also runs the min-degree>=2 case at n=11 and n=12 (which the report did NOT do) as far as time allows,
and the DISCONNECTED question (bip is additive so connected suffices).
"""
import subprocess
import sys

GENG = r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"


def g6_edges(line):
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


def maxcut(n, E):
    adjm = [0] * n
    for (u, v) in E:
        adjm[u] |= 1 << v
        adjm[v] |= 1 << u
    best = -1
    for mask in range(1 << (n - 1)):
        s = mask << 1
        c = 0
        for (u, v) in E:
            if ((s >> u) ^ (s >> v)) & 1:
                c += 1
        if c > best:
            best = c
    return best


def run(n, mindeg):
    p = subprocess.Popen([GENG, "-t", "-c", f"-d{mindeg}", str(n)],
                         stdout=subprocess.PIPE, text=True, stderr=subprocess.DEVNULL)
    cnt = 0
    bestnum, bestden, arg = 0, 1, None
    beats = []
    for line in p.stdout:
        if not line.strip():
            continue
        m, E = g6_edges(line)
        b = len(E) - maxcut(m, E)
        cnt += 1
        if 5 * b > len(E):
            beats.append((line.strip(), m, len(E), b))
        if len(E) and b * bestden > bestnum * len(E):
            bestnum, bestden, arg = b, len(E), (line.strip(), m, len(E), b)
    return cnt, bestnum, bestden, arg, beats


if __name__ == "__main__":
    for (n, d) in [(5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (11, 3), (12, 3), (11, 2)]:
        cnt, bn, bd, arg, beats = run(n, d)
        print(f"n={n} mindeg>={d}: {cnt} graphs; max bip/|E| = {bn}/{bd} "
              f"= {bn/bd if bd else 0:.6f}  at {arg};  #with 5*bip>|E| = {len(beats)}")
        if beats:
            print("   COUNTEREXAMPLES:", beats[:5])
        sys.stdout.flush()
