"""Structural analysis of the exact extremal graphs at N = 12, 13 (and 14 when collected).

For each extremal graph, independently re-verifies bip by exhaustive maxcut, then reports the
invariants that any proof of the conjecture would have to be tight against:
  degree sequence, independence number, chromatic number, odd girth, number of C5s,
  twin classes (a C5 blow-up has exactly five, covering V), and -- the key test --
  whether the graph admits a homomorphism to C5, since G -> C5 already implies bip <= N^2/25
  by an elementary argument (see the note at the bottom of this file).
"""

from itertools import combinations, permutations
import sys


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
    deg = [bin(a).count("1") for a in adj]
    S, cut = 1, deg[0]
    best = cut
    for k in range(1, 1 << (n - 1)):
        v = (k & -k).bit_length()
        a = bin(adj[v] & S).count("1")
        if S >> v & 1:
            cut += 2 * a - deg[v]; S &= ~(1 << v)
        else:
            cut += deg[v] - 2 * a; S |= 1 << v
        if cut > best:
            best = cut
    return best


def independence_number(n, adj):
    best = 0
    def rec(cand, size):
        nonlocal best
        if size + bin(cand).count("1") <= best:
            return
        if cand == 0:
            best = max(best, size); return
        v = (cand & -cand).bit_length() - 1
        rec(cand & ~(1 << v) & ~adj[v], size + 1)
        rec(cand & ~(1 << v), size)
    rec((1 << n) - 1, 0)
    return best


def chromatic_number(n, adj):
    for k in range(2, n + 1):
        colour = [-1] * n
        def rec(v):
            if v == n:
                return True
            used = set()
            for c in range(k):
                if any((adj[v] >> u) & 1 and colour[u] == c for u in range(v)):
                    continue
                if c in used:
                    continue
                colour[v] = c
                if c not in used and rec(v + 1):
                    return True
                colour[v] = -1
                used.add(c)
                if c > max([colour[u] for u in range(v)] + [-1]) + 0:
                    pass
            return False
        if rec(0):
            return k
    return n


def hom_to_C5(n, adj):
    """Is there a homomorphism G -> C5?  (phi(u)-phi(v) = +-1 mod 5 on every edge.)"""
    phi = [-1] * n
    order = sorted(range(n), key=lambda v: -bin(adj[v]).count("1"))
    pos = {v: i for i, v in enumerate(order)}

    def ok(v, c):
        for u in range(n):
            if (adj[v] >> u) & 1 and phi[u] != -1:
                if (c - phi[u]) % 5 not in (1, 4):
                    return False
        return True

    def rec(i):
        if i == n:
            return True
        v = order[i]
        lo = 5 if i > 0 else 1          # fix phi of the first vertex to 0 (C5 is vertex-transitive)
        for c in range(lo if i == 0 else 5) if i == 0 else range(5):
            pass
        rng = [0] if i == 0 else range(5)
        for c in rng:
            if ok(v, c):
                phi[v] = c
                if rec(i + 1):
                    return True
                phi[v] = -1
        return False

    return rec(0)


def count_c5(n, adj):
    cnt = 0
    for vs in combinations(range(n), 5):
        e = [[bool((adj[vs[i]] >> vs[j]) & 1) for j in range(5)] for i in range(5)]
        h = 0
        for p in permutations(range(1, 5)):
            cyc = (0,) + p
            if all(e[cyc[i]][cyc[(i + 1) % 5]] for i in range(5)):
                h += 1
        cnt += h // 2
    return cnt


def odd_girth(n, adj):
    from collections import deque
    best = None
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        dq = deque([s])
        while dq:
            u = dq.popleft()
            for w in range(n):
                if (adj[u] >> w) & 1:
                    if dist[w] == -1:
                        dist[w] = dist[u] + 1
                        dq.append(w)
                    elif dist[w] == dist[u]:
                        c = 2 * dist[u] + 1
                        best = c if best is None else min(best, c)
    return best


def twin_classes(n, adj):
    g = {}
    for v in range(n):
        g.setdefault(adj[v], []).append(v)
    return sorted((len(x) for x in g.values()), reverse=True)


EXTREMAL = {
    12: ["K?ABBBwerwBw", "K?BD@g]Qvo^?"],
    13: ["L??ED@_~?~^_Fw", "L??EDB_~?~^_Fw", "L??EFB_~FwB{Fw", "L??FFB_~?~^_Fw",
         "L?`DAboU`w@{hS", "L?`DAboUdIF_Bo", "L?`DAboUdIF_Bw", "L?`DE`gl@YJODg"],
    14: ["M?AE@bH{AYN_LgBs?"],
}

for N in sorted(EXTREMAL):
    print("=" * 76)
    print(f"N = {N}   bound N^2/25 = {N*N}/25 = {N*N/25:.2f}   floor = {N*N//25}")
    print("=" * 76)
    for g6 in EXTREMAL[N]:
        n, adj, m = g6_decode(g6)
        mc = maxcut(n, adj)
        b = m - mc
        print(f"{g6}")
        print(f"   |E|={m}  maxcut={mc}  bip={b}   (bip*25={b*25} vs N^2={n*n})")
        print(f"   degrees        : {sorted((bin(a).count('1') for a in adj), reverse=True)}")
        print(f"   independence   : {independence_number(n, adj)}")
        print(f"   chromatic no.  : {chromatic_number(n, adj)}")
        print(f"   odd girth      : {odd_girth(n, adj)}")
        print(f"   # C5           : {count_c5(n, adj)}")
        print(f"   twin classes   : {twin_classes(n, adj)}")
        print(f"   hom -> C5 ?    : {hom_to_C5(n, adj)}   <-- if True, bip <= N^2/25 is elementary")
        print()

print("""
NOTE (elementary lemma, complete proof).
If phi: V(G) -> Z_5 is a homomorphism to C5 (every edge has phi-difference +-1), set
n_j = |phi^{-1}(j)| and E_j = the edges between classes j and j+1, so E = E_0 u ... u E_4 and
|E_j| <= n_j n_{j+1}. For each i take the cut A_i = phi^{-1}({i, i+2}). Inside A_i the only
possible edges are those between classes i and i+2, which have difference 2 and hence do not
exist; inside the complement phi^{-1}({i+1, i+3, i+4}) the only possible edges are those between
i+3 and i+4. Hence the cut A_i has exactly |E_{i+3}| monochromatic edges, so
   bip(G) <= min_i |E_i| <= min_i n_i n_{i+1} <= (prod_i n_i)^{2/5} <= ((N/5)^5)^{2/5} = N^2/25,
using AM-GM twice. So the conjecture is elementary for C5-colourable graphs, and the whole
difficulty lies with triangle-free graphs admitting NO homomorphism to C5.
""")
