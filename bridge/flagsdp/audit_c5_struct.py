#!/usr/bin/env python3
"""Structural check: at the C5 graphon (d_mono = 2/25 = c exactly, so d-c=0), the BEST fixed-cut deficit
sum per type, orbit-weighted, must be >= 0 for any valid balanced cert. If sum_sigma orbit_sigma*min_p g_sigma > 0
STRICTLY at C5, then max_band G >= that positive value => no balanced FIXED-cut cert is tight at C5 => not repairable."""
import numpy as np, itertools, random
import flag_engine as fe, cpp_precompute as cpp

def c5_blowup(b):
    cyc = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    n = 5 * b; A = [0] * n
    part = lambda v: v // b
    edge = set()
    for (p, q) in cyc:
        edge.add((p, q)); edge.add((q, p))
    for u in range(n):
        for w in range(u + 1, n):
            if (part(u), part(w)) in edge:
                A[u] |= 1 << w; A[w] |= 1 << u
    return (n, A)

def orbit_size(k, Asig):
    seen = set()
    for perm in itertools.permutations(range(k)):
        key = []
        for i in range(k):
            row = 0
            for j in range(k):
                if i != j and (Asig[perm[i]] >> perm[j]) & 1:
                    row |= (1 << j)
            key.append(row)
        seen.add(tuple(key))
    return len(seen)

def main():
    cpp.compile_cpp()
    t = 0.08
    types7 = fe.enumerate_graphs(7, triangle_free=True)
    for b in [2, 3]:
        st = [c5_blowup(b)]
        n = st[0][0]
        e = sum(1 for u in range(n) for v in range(u + 1, n) if (st[0][1][u] >> v) & 1)
        de = e / (n * (n - 1) / 2)
        Ssum = 0.0; best_sum = 0.0
        for ti, (k, A) in enumerate(types7):
            E, S, cls = cpp.precompute_type_cpp(st, 7, A, nthreads=16)
            E = E[0]; S = S[0]; nc = E.shape[0]
            osz = orbit_size(7, A)
            Ssum += osz * S
            if S < 1e-15:
                continue
            best = 1e18
            if nc <= 18:
                for p in itertools.product((0, 1), repeat=nc):
                    same = 0.0
                    for a in range(nc):
                        for bb in range(a, nc):
                            if p[a] == p[bb]:
                                same += E[a, bb]
                    g = same - t * S
                    if g < best:
                        best = g
            else:
                for _ in range(400):
                    p = [random.randint(0, 1) for _ in range(nc)]
                    imp = True
                    while imp:
                        imp = False
                        for a in range(nc):
                            sw = sum(E[min(a, b2), max(a, b2)] for b2 in range(nc) if b2 != a and p[b2] == p[a])
                            ow = sum(E[min(a, b2), max(a, b2)] for b2 in range(nc) if b2 != a and p[b2] != p[a])
                            if ow < sw:
                                p[a] ^= 1; imp = True
                    same = 0.0
                    for a in range(nc):
                        for bb in range(a, nc):
                            if p[a] == p[bb]:
                                same += E[a, bb]
                    g = same - t * S
                    if g < best:
                        best = g
            best_sum += osz * best
        print(f"C5 blowup b={b} n={n} d_edge={de:.4f}: sum_sigma orbit*min_p g = {best_sum:+.6e}  (Sigma=sum orbit*S={Ssum:.6f})", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
