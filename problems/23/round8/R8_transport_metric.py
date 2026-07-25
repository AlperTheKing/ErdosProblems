"""Metric-potential (distance level set) family, and the And(4) identification.

(a)  For A subset V let f = d(.,A) (1-Lipschitz), and take the cut f^{-1}(even).  Its
     monochromatic edges are exactly the HORIZONTAL edges {uv : f(u)=f(v)}.  We enumerate
     the whole family over all A and count how many distinct bipartitions it produces.
     On every test graph it produces ALL 2^{N-1} of them -> the metric formulation is a
     rename of psi, not a restriction.

(b)  graph6 output for And(4), to be compared with round1/base11.g6's J?bFF`wN?{? via
     nauty labelg (both canonicalise to  Js`@IStU`w? ).
"""
import sys
from collections import deque

sys.path.insert(0, ".")
from R8_transport_lib import *   # noqa


def distance_parity_cuts(G):
    n, out = G.n, set()
    for A in range(1, 1 << n):
        dist = [-1] * n
        q = deque()
        for v in range(n):
            if (A >> v) & 1:
                dist[v] = 0
                q.append(v)
        while q:
            v = q.popleft()
            for u in range(n):
                if (G.adj[v] >> u) & 1 and dist[u] < 0:
                    dist[u] = dist[v] + 1
                    q.append(u)
        if any(d < 0 for d in dist):
            continue
        S = 0
        for v in range(n):
            if dist[v] % 2 == 0:
                S |= 1 << v
        if (S >> 0) & 1:
            S = ((1 << n) - 1) ^ S           # normalise: vertex 0 outside
        out.add(S)
    return sorted(out)


def to_g6(G):
    n, bits = G.n, []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (G.adj[i] >> j) & 1 else 0)
    while len(bits) % 6:
        bits.append(0)
    return chr(n + 63) + "".join(
        chr(63 + int("".join(map(str, bits[k:k + 6])), 2)) for k in range(0, len(bits), 6))


if __name__ == "__main__":
    for G in [cycle(5), blowup(cycle(5), [2] * 5), wagner(), petersen(), grotzsch(),
              andrasfai(4), from_g6("M?AE@bH{AYN_LgBs?", "N14")]:
        D = distance_parity_cuts(G)
        best = min(len(G.mono_edges(S)) for S in D)
        print("%-12s distance-parity cuts = %5d of %5d   min mono = %d   bip = %d   %s"
              % (G.name, len(D), 1 << (G.n - 1), best, G.bip(),
                 "RENAME (family = all cuts)" if len(D) == 1 << (G.n - 1) else "proper subfamily"))
    print()
    print("And(4) graph6 =", to_g6(andrasfai(4)))
    print("round1/base11.g6 witness = J?bFF`wN?{?   ; labelg canonical form of both = Js`@IStU`w?")
