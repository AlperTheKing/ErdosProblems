"""Exact checks backing the write-up.

(A) Theorem A on random C_{2k+1}-colourable graphs: bip(G) <= min_j e(V_j,V_{j+1}) and
    bip(G) <= N^2/(2k+1)^2, verified against brute-force bip over all 2^(N-1) bipartitions.
(B) C7[n] has no 5-cycle yet bip = n^2 = N^2/49  (kills any bound by C5-count alone).
(C) delta5(G) := min over phi:V->Z5 of #edges whose Z5-difference is not +-1 satisfies
    delta5 <= bip (take the optimal bipartition and use colours {0,1}), so statement F3(iii)
    is WEAKER than Erdos #23 and is already known for N <= 200.
"""
import numpy as np, itertools, random
from beta import Template, explicit_blowup, bip_bruteforce

rng = random.Random(1)

print("=== (A) Theorem A: G -> C_{2k+1} ===")
for k in (2, 3, 4):
    L = 2 * k + 1
    for trial in range(6):
        sizes = [rng.randint(1, 3) for _ in range(L)]
        N = sum(sizes)
        if N > 15:
            continue
        off, s = [], 0
        for x in sizes:
            off.append(s); s += x
        E = []
        for i in range(L):
            j = (i + 1) % L
            for a in range(sizes[i]):
                for b in range(sizes[j]):
                    if rng.random() < 0.75:
                        E.append((off[i] + a, off[j] + b))
        if not E:
            continue
        ej = []
        for i in range(L):
            j = (i + 1) % L
            ej.append(sum(1 for (u, v) in E
                          if (off[i] <= u < off[i] + sizes[i] and off[j] <= v < off[j] + sizes[j])
                          or (off[j] <= u < off[j] + sizes[j] and off[i] <= v < off[i] + sizes[i])))
        b = bip_bruteforce(N, E)
        assert b <= min(ej), (b, ej)
        assert b * L * L <= N * N, (b, N, L)
        print("   L=%d N=%2d |E|=%2d  bip=%d  min_j e_j=%d  N^2/L^2=%.2f  OK"
              % (L, N, len(E), b, min(ej), N * N / L / L))

print("=== (B) C7[n]: no C5, bip = n^2 = N^2/49 ===")
C7 = (7, [(i, (i + 1) % 7) for i in range(7)])
t7 = Template(*C7)
for n in (1, 2, 3):
    N, E = explicit_blowup(7, C7[1], [n] * 7)
    adj = [set() for _ in range(N)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    # count 5-cycles
    c5 = 0
    for a, b, c, d, e in itertools.permutations(range(N), 5):
        if a == min(a, b, c, d, e) and b < e:
            if b in adj[a] and c in adj[b] and d in adj[c] and e in adj[d] and a in adj[e]:
                c5 += 1
    bb = t7.bip([n] * 7)[0]
    print("   n=%d N=%2d  #C5=%d  bip=%d  n^2=%d  N^2/49=%.3f  N^2/25=%.3f"
          % (n, N, c5, bb, n * n, N * N / 49, N * N / 25))

print("=== (C) delta5 vs bip ===")
def delta5(N, E, chunk=1 << 20):
    """exact min over phi:V->Z5 (phi(0)=0 wlog) of #edges with difference not in {+-1}"""
    eu = np.array([e[0] for e in E]); ev = np.array([e[1] for e in E])
    total = 5 ** (N - 1)
    best = len(E)
    pw = 5 ** np.arange(N - 1)
    for start in range(0, total, chunk):
        idx = np.arange(start, min(start + chunk, total), dtype=np.int64)
        digits = np.zeros((len(idx), N), dtype=np.int8)
        for i in range(N - 1):
            digits[:, i + 1] = (idx // pw[i]) % 5
        d = (digits[:, eu] - digits[:, ev]) % 5
        bad = ((d != 1) & (d != 4)).sum(axis=1)
        best = min(best, int(bad.min()))
        if best == 0:
            break
    return best

PET = (10, [(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),
            (5,7),(7,9),(9,6),(6,8),(8,5)])
for name, (N, E) in [("C5", (5, [(0,1),(1,2),(2,3),(3,4),(4,0)])),
                     ("C7", (7, C7[1])),
                     ("Petersen", PET)]:
    d5 = delta5(N, E)
    b = bip_bruteforce(N, E)
    print("   %-9s N=%2d |E|=%2d  delta5=%d  bip=%d  N^2/25=%.2f   delta5<=bip: %s"
          % (name, N, len(E), d5, b, N * N / 25, d5 <= b))
