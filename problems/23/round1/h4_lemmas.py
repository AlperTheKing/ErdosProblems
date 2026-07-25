"""Randomised exact check of the two structural lemmas the H4 search reductions rest on.

L1 (monotonicity).  If G and G+e are both triangle-free then bip(G+e) >= bip(G).
    Proof.  Any cut of G+e restricted to G loses at most the single edge e, so
    maxcut(G+e) <= maxcut(G)+1, hence bip(G+e) = m+1-maxcut(G+e) >= m-maxcut(G) = bip(G).
    Consequence: a(N) = max over MAXIMAL triangle-free graphs on N vertices.

L2 (vertex deletion).  bip(G) <= bip(G-v) + floor(d(v)/2).
    Proof.  Take a maximum cut of G-v and place v on the side meeting fewer of its
    neighbours: it contributes >= ceil(d(v)/2) new cut edges, so
    maxcut(G) >= maxcut(G-v) + ceil(d(v)/2), and
    bip(G) = m'+d(v)-maxcut(G) <= bip(G-v) + d(v) - ceil(d(v)/2) = bip(G-v)+floor(d(v)/2).
    Consequence: bip(G) <= a(N-1) + floor(delta(G)/2), i.e. a lower bound on min degree.

Both are checked below on random triangle-free graphs with EXHAUSTIVE maxcut.
"""

import random
from h4_lib import maxcut_exact, num_edges, is_triangle_free, bip


def random_tf(n, rnd, p=0.5):
    adj = [0] * n
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rnd.shuffle(pairs)
    for (i, j) in pairs:
        if rnd.random() > p:
            continue
        if adj[i] & adj[j]:
            continue
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    return adj


def main():
    rnd = random.Random(20260725)
    n1 = n2 = 0
    for trial in range(4000):
        n = rnd.randint(5, 12)
        adj = random_tf(n, rnd, p=rnd.choice([0.3, 0.5, 0.8, 1.0]))
        b = bip(n, adj)

        # L1: add every legal edge, check bip does not drop
        for i in range(n):
            for j in range(i + 1, n):
                if (adj[i] >> j) & 1:
                    continue
                if adj[i] & adj[j]:
                    continue          # would make a triangle
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                b2 = bip(n, adj)
                assert b2 >= b, ("L1 FAIL", n, i, j, b, b2)
                n1 += 1
                adj[i] &= ~(1 << j)
                adj[j] &= ~(1 << i)

        # L2: delete every vertex
        for v in range(n):
            dv = bin(adj[v]).count("1")
            sub = [0] * (n - 1)
            relab = [x for x in range(n) if x != v]
            pos = {x: k for k, x in enumerate(relab)}
            for a in range(n):
                if a == v:
                    continue
                for bx in range(a + 1, n):
                    if bx == v:
                        continue
                    if (adj[a] >> bx) & 1:
                        sub[pos[a]] |= 1 << pos[bx]
                        sub[pos[bx]] |= 1 << pos[a]
            bd = bip(n - 1, sub) if n - 1 >= 2 else 0
            assert b <= bd + dv // 2, ("L2 FAIL", n, v, b, bd, dv)
            n2 += 1
    print(f"L1 verified on {n1} edge additions; L2 verified on {n2} vertex deletions; 0 failures")


if __name__ == "__main__":
    main()
