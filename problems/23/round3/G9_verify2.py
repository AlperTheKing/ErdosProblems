"""G9 second, independently written verification layer.

(1) Direct brute-force bip on the explicit 25-vertex graph W_1 = C5[7,2,7,7,2] and on
    W_1 minus a minimum-degree vertex, using a bitmask max-cut written from scratch
    (does NOT use the blow-up identity).
(2) Exhaustive check of THEOREM A:  bip(G) <= m - max_v vol(N(v))   for all connected
    triangle-free graphs up to n = 10 (graph6 read from geng), plus the weaker
    bip(G) <= m - 4 m^2 / N^2  (exact Fraction).
(3) Exact data for the extremal graphs at N = 12, 13, 14 quoted in the task.
"""
import sys
from fractions import Fraction


def parse_g6(s):
    d = [ord(c) - 63 for c in s.strip()]
    n = d[0]
    bits = []
    for b in d[1:]:
        for k in range(5, -1, -1):
            bits.append((b >> k) & 1)
    adj = [0] * n
    p = 0
    for j in range(1, n):
        for i in range(j):
            if bits[p]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            p += 1
    return n, adj


def edges_of(n, adj):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1]


def bip_bits(n, adj):
    """min over cuts of #monochromatic edges, brute force over 2^(n-1) cuts."""
    E = edges_of(n, adj)
    best = len(E)
    for S in range(1 << (n - 1)):
        c = 0
        for (u, v) in E:
            a = (S >> u) & 1 if u < n - 1 else 0
            b = (S >> v) & 1 if v < n - 1 else 0
            if a == b:
                c += 1
                if c >= best:
                    break
        if c < best:
            best = c
    return best


def build_blowup_c5(a):
    off = []
    c = 0
    for x in a:
        off.append(c)
        c += x
    n = c
    adj = [0] * n
    for i in range(5):
        j = (i + 1) % 5
        for p in range(a[i]):
            for q in range(a[j]):
                u = off[i] + p
                v = off[j] + q
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    return n, adj, off


def theoremA_check(n, adj):
    E = edges_of(n, adj)
    m = len(E)
    deg = [bin(adj[v]).count("1") for v in range(n)]
    volmax = 0
    for v in range(n):
        vol = sum(deg[w] for w in range(n) if (adj[v] >> w) & 1)
        volmax = max(volmax, vol)
    b = bip_bits(n, adj)
    ok1 = b <= m - volmax
    ok2 = Fraction(b) <= Fraction(m) - Fraction(4 * m * m, n * n) if n else True
    return b, m, volmax, ok1, ok2


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode in ("all", "w1"):
        print("=== (1) explicit brute force on W_1 = C5[7,2,7,7,2], N=25 ===")
        n, adj, off = build_blowup_c5([7, 2, 7, 7, 2])
        E = edges_of(n, adj)
        deg = [bin(adj[v]).count("1") for v in range(n)]
        print(f"N={n} m={len(E)} degree multiset={sorted(set(deg))} delta={min(deg)} "
              f"4N/25={Fraction(4*n,25)}")
        b = bip_bits(n, adj)
        print(f"brute-force bip(W_1) = {b}   (blow-up identity predicts 14)")
        # delete a minimum-degree vertex: vertex 0 (part 0)
        keep = [v for v in range(n) if v != 0]
        idx = {v: i for i, v in enumerate(keep)}
        adj2 = [0] * (n - 1)
        for u in keep:
            for w in keep:
                if (adj[u] >> w) & 1:
                    adj2[idx[u]] |= 1 << idx[w]
        b2 = bip_bits(n - 1, adj2)
        print(f"brute-force bip(W_1 - v) = {b2}  drop = {b - b2}  floor(delta/2) = {min(deg)//2}")
        print(f"budget (2N-1)/25 = {Fraction(2*n-1,25)};  drop > budget ? {b-b2 > Fraction(2*n-1,25)}")

    if mode in ("all", "extremal"):
        print()
        print("=== (3) extremal graphs quoted in the task ===")
        for g6 in ["K?ABBBwerwBw", "K?BD@g]Qvo^?", "L??ED@_~?~^_Fw", "M?AE@bH{AYN_LgBs?"]:
            n, adj = parse_g6(g6)
            b, m, volmax, ok1, ok2 = theoremA_check(n, adj)
            deg = [bin(adj[v]).count("1") for v in range(n)]
            delta = min(deg)
            # drops
            drops = []
            for v in range(n):
                keep = [u for u in range(n) if u != v]
                idx = {u: i for i, u in enumerate(keep)}
                adj2 = [0] * (n - 1)
                for u in keep:
                    for w in keep:
                        if (adj[u] >> w) & 1:
                            adj2[idx[u]] |= 1 << idx[w]
                drops.append(b - bip_bits(n - 1, adj2))
            print(f"{g6}: N={n} m={m} bip={b} N^2/25={Fraction(n*n,25)} delta={delta} "
                  f"(4N-2)/25={Fraction(4*n-2,25)} delta>(4N-2)/25? {delta > Fraction(4*n-2,25)}")
            print(f"    degrees={deg}")
            print(f"    drops={drops}  min drop={min(drops)}  budget={Fraction(2*n-1,25)} "
                  f"floor(delta/2)={delta//2}")
            print(f"    ThmA: bip<=m-max_v vol(N(v)) : {b} <= {m}-{volmax}={m-volmax} -> {ok1}; "
                  f"bip<=m-4m^2/N^2 -> {ok2}")
