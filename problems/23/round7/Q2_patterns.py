"""Q2_patterns.py -- emit connected triangle-free patterns as adjacency matrices
for Q2_finite.exe.   usage: python Q2_patterns.py HMIN HMAX > patterns.txt"""
import sys, subprocess
GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"


def g6_decode(line):
    bs = [ord(c) - 63 for c in line.strip()]
    n = bs[0]
    bits = []
    for b in bs[1:]:
        for k in range(5, -1, -1):
            bits.append((b >> k) & 1)
    adj = [[0] * n for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i][j] = adj[j][i] = 1
            idx += 1
    return n, adj


def main():
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    out = []
    for h in range(lo, hi + 1):
        r = subprocess.run([GENG, "-t", "-c", str(h)], capture_output=True, text=True)
        for g6 in r.stdout.split():
            n, adj = g6_decode(g6)
            out.append(f"{n} {g6}")
            for i in range(n):
                out.append("".join(str(adj[i][j]) for j in range(n)))
    sys.stdout.write("\n".join(out) + "\n")


main()
