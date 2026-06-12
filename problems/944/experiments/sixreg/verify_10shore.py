"""Independent recount for the 10-shore filter.

Input: graph6 stream from
    geng -c -D6 10 27:27

This mirrors enum_10shore.cpp in plain Python:
  B: b(v)=6-deg_A(v), sum b=6.
  C: every proper 3-colouring has allowed boundary vector.
  T: no comparable non-neighbour forced by a b=0 vertex.
  L: each b=0 vertex has at least one colouring of A-v with all colours
     appearing at least twice on N_A(v).
"""
import sys

N = 10
ALLOWED = {(6, 0, 0), (4, 1, 1), (3, 3, 0), (2, 2, 2)}


def g6_to_adj(s):
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        bits.extend((v >> k) & 1 for k in range(5, -1, -1))
    adj = [set() for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i].add(j)
                adj[j].add(i)
            idx += 1
    return n, adj


def all_colourings(adj, vertices):
    vertices = list(vertices)
    col = {}
    out = []

    def bt(i):
        if i == len(vertices):
            out.append(dict(col))
            return
        v = vertices[i]
        used = {col[u] for u in adj[v] if u in col}
        for c in range(3):
            if c not in used:
                col[v] = c
                bt(i + 1)
                del col[v]

    bt(0)
    return out


def local_ok(adj, b, v):
    cols = all_colourings(adj, [u for u in range(N) if u != v])
    for phi in cols:
        cnt = [0, 0, 0]
        for u in adj[v]:
            cnt[phi[u]] += 1
        if min(cnt) >= 2:
            return True
    return False


def classify(adj):
    deg = [len(adj[v]) for v in range(N)]
    b = [6 - d for d in deg]
    if any(x < 0 or x > 5 for x in b) or sum(b) != 6:
        return "badB"
    cols = all_colourings(adj, range(N))
    if not cols:
        return "not3col"
    for phi in cols:
        s = [0, 0, 0]
        for v in range(N):
            s[phi[v]] += b[v]
        if tuple(sorted(s, reverse=True)) not in ALLOWED:
            return "badvec"
    for u in range(N):
        if b[u] != 0:
            continue
        for v in range(N):
            if u == v or v in adj[u]:
                continue
            if (adj[u] - {v}) <= adj[v]:
                return "badcomp"
    for v in range(N):
        if b[v] == 0 and not local_ok(adj, b, v):
            return "badlocal"
    return "SURVIVOR"


counts = {}
survivors = []
for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith(">"):
        continue
    n, adj = g6_to_adj(line)
    assert n == N
    tag = classify(adj)
    counts[tag] = counts.get(tag, 0) + 1
    if tag == "SURVIVOR":
        survivors.append(line)

print("python recount:", counts)
print("survivors:", survivors)
