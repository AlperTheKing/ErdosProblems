"""Identify the extremal graphs at N=12 (bip = 5) and test how they relate to blow-ups.

Re-runs the census in Python over the geng stream (exact, independent of the C++ pass),
collects EVERY graph attaining bip = 5, and reports structure: degree sequence,
independence number, whether it is a blow-up (i.e. has two vertices with identical
closed-neighbourhood-free twin structure), automorphism-orbit sizes via a cheap
refinement, and the 5-cycle count.
"""

import subprocess, sys
from itertools import combinations

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
N = 12
TARGET = 5


def g6_decode(s):
    b = [ord(c) - 63 for c in s]
    n = b[0]
    bits = []
    for byte in b[1:]:
        for k in range(5, -1, -1):
            bits.append((byte >> k) & 1)
    adj = [0] * n
    idx = 0
    m = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                m += 1
            idx += 1
    return n, adj, m


def maxcut(n, adj):
    """Gray-code exhaustive maxcut, vertex 0 fixed."""
    deg = [bin(a).count("1") for a in range(0)]  # placeholder
    deg = [bin(a).count("1") for a in adj]
    S = 1
    cut = deg[0]
    best = cut
    for k in range(1, 1 << (n - 1)):
        v = (k & -k).bit_length()  # ctz(k)+1
        a = bin(adj[v] & S).count("1")
        if S >> v & 1:
            cut += 2 * a - deg[v]
            S &= ~(1 << v)
        else:
            cut += deg[v] - 2 * a
            S |= 1 << v
        if cut > best:
            best = cut
    return best


def independence_number(n, adj):
    best = 0
    order = sorted(range(n), key=lambda v: -bin(adj[v]).count("1"))

    def rec(cand, size):
        nonlocal best
        if size + bin(cand).count("1") <= best:
            return
        if cand == 0:
            best = max(best, size)
            return
        v = (cand & -cand).bit_length() - 1
        # take v
        rec(cand & ~(1 << v) & ~adj[v], size + 1)
        # skip v
        rec(cand & ~(1 << v), size)

    rec((1 << n) - 1, 0)
    return best


def count_c5(n, adj):
    """Number of 5-cycles (unordered)."""
    cnt = 0
    for vs in combinations(range(n), 5):
        sub = list(vs)
        # count hamiltonian cycles of the induced subgraph on 5 vertices
        idx = {v: i for i, v in enumerate(sub)}
        e = [[False] * 5 for _ in range(5)]
        for i in range(5):
            for j in range(5):
                if i != j and (adj[sub[i]] >> sub[j]) & 1:
                    e[i][j] = True
        # fix start 0, permute rest, divide by 2 for direction
        from itertools import permutations
        h = 0
        for p in permutations(range(1, 5)):
            cyc = (0,) + p
            if all(e[cyc[i]][cyc[(i + 1) % 5]] for i in range(5)):
                h += 1
        cnt += h // 2
    return cnt


def twin_classes(n, adj):
    """Group vertices by identical neighbourhood (blow-up parts are exactly these)."""
    groups = {}
    for v in range(n):
        groups.setdefault(adj[v], []).append(v)
    return sorted((len(g) for g in groups.values()), reverse=True)


print(f"scanning connected triangle-free graphs on {N} vertices for bip = {TARGET} ...")
proc = subprocess.Popen([GENG, "-t", "-c", "-q", str(N)],
                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
hits = []
total = 0
for line in proc.stdout:
    line = line.strip()
    if not line:
        continue
    total += 1
    n, adj, m = g6_decode(line)
    b = m - maxcut(n, adj)
    if b >= TARGET:
        hits.append((line, adj, m, b))
proc.wait()
print(f"graphs scanned: {total}   graphs with bip >= {TARGET}: {len(hits)}")
print()

for g6, adj, m, b in hits:
    degs = sorted((bin(a).count("1") for a in adj), reverse=True)
    print(f"g6 = {g6}")
    print(f"  |E| = {m}   bip = {b}   maxcut = {m - b}")
    print(f"  degree sequence : {degs}")
    print(f"  independence no.: {independence_number(len(adj), adj)}")
    print(f"  twin-class sizes: {twin_classes(len(adj), adj)}  (a blow-up of H has these as its parts)")
    print(f"  number of C5s   : {count_c5(len(adj), adj)}")
    print(f"  bip*25 vs N^2   : {b*25} vs {len(adj)**2}   ratio = {b*25/len(adj)**2:.4f} of the bound")
    print()
