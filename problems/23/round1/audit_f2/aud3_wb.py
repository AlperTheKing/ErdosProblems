"""AUDIT 3.  W_b = P4[b+1,b,b,b+1] with cut V0 = P1 u P4, V1 = P2 u P3.
Independent verification of THEOREM 4.1, entirely from the explicit graph where feasible.
"""
import os
import sys
from itertools import product, combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aud_core import (blowup, sigma_set, sigma_by_recut, adj_of, is_triangle_free,
                      maxcut_brute, named_families, sharp_stars, independent_sets)

P4_EDGES = [(0, 1), (1, 2), (2, 3)]
COL = [0, 1, 1, 0]


def build(b):
    sizes = [b + 1, b, b, b + 1]
    N, E, part, start = blowup(P4_EDGES, sizes)
    side = [COL[part[v]] for v in range(N)]
    return N, E, part, side, sizes


def sigma_profile(s, sizes):
    tot = 0
    for (i, j) in P4_EDGES:
        eps = 1 if COL[i] != COL[j] else -1
        tot += eps * (s[i] * (sizes[j] - s[j]) + s[j] * (sizes[i] - s[i]))
    return tot


def report_formula(s, b):
    """(dagger) from the report: b(s1+s4)+s2+s3-2 s1 s2 + 2 s2 s3 - 2 s3 s4."""
    s1, s2, s3, s4 = s
    return b * (s1 + s4) + s2 + s3 - 2 * s1 * s2 + 2 * s2 * s3 - 2 * s3 * s4


def kappa_formula(b):
    return min((b * u) // (2 * u - 1) + 1 + u for u in range(1, b + 2))


def kappa_true(b):
    """Exhaustive over profiles: smallest |S| with sigma(S) < 0 (exact)."""
    sizes = [b + 1, b, b, b + 1]
    best = None
    for s in product(*[range(x + 1) for x in sizes]):
        if sigma_profile(s, sizes) < 0:
            t = sum(s)
            if best is None or t < best[0]:
                best = (t, s, sigma_profile(s, sizes))
    return best


def main():
    print("=== W_b basic data + formula cross-check ===")
    for b in range(2, 13):
        N, E, part, side, sizes = build(b)
        M = [e for e in E if side[e[0]] == side[e[1]]]
        assert is_triangle_free(N, E)
        # formula cross-check on all profiles
        bad = 0
        for s in product(*[range(x + 1) for x in sizes]):
            if sigma_profile(s, sizes) != report_formula(s, b):
                bad += 1
        print(f"  b={b:2d}: N={N:3d} |E|={len(E):4d} |M|={len(M):4d} (b^2={b*b})  "
              f"25|M|={25*len(M):5d} vs N^2={N*N:5d} -> {'BEATS' if 25*len(M)>N*N else 'no'}  "
              f"(dagger)-formula mismatches={bad}")

    print("\n=== sigma from profile == sigma from graph? (b=3, all 2^14 subsets) ===")
    b = 3
    N, E, part, side, sizes = build(b)
    bad = 0
    for mask in range(1 << N):
        S = {v for v in range(N) if (mask >> v) & 1}
        s = [0] * 4
        for v in S:
            s[part[v]] += 1
        if not (sigma_set(S, E, side) == sigma_profile(s, sizes) == sigma_by_recut(S, E, side)):
            bad += 1
    print(f"  b=3: mismatches over all {1<<N} subsets = {bad}")

    print("\n=== kappa(b): exhaustive vs report formula ===")
    for b in range(3, 41):
        kt = kappa_true(b)
        kf = kappa_formula(b)
        print(f"  b={b:2d}: exhaustive min|S| with sigma<0 = {kt[0]:3d} at {kt[1]} sigma={kt[2]:4d}"
              f"   report kappa(b) = {kf:3d}   {'OK' if kt[0] == kf else '*** MISMATCH ***'}"
              f"   N/8 = {(4*b+2)/8:.2f}")

    print("\n=== all named families on the EXPLICIT graph, b = 3..8 ===")
    for b in range(3, 9):
        N, E, part, side, sizes = build(b)
        worst = {}
        for name, S in named_families(N, E, side):
            v = sigma_set(S, E, side)
            if name not in worst or v < worst[name][0]:
                worst[name] = (v, sorted(S))
        for name, S in sharp_stars(N, E, side):
            v = sigma_set(S, E, side)
            if name not in worst or v < worst[name][0]:
                worst[name] = (v, sorted(S))
        # independent sets: enumerate by profile on independent supports {0,2},{1,3},{0,3}
        mn = None
        for T in ([0, 2], [1, 3], [0, 3]):
            for t in product(*[range(sizes[i] + 1) for i in T]):
                s = [0] * 4
                for k, i in enumerate(T):
                    s[i] = t[k]
                val = sigma_profile(s, sizes)
                if mn is None or val < mn[0]:
                    mn = (val, tuple(s))
        worst["independent set"] = mn
        # whole parts
        for i in range(4):
            s = [0] * 4
            s[i] = sizes[i]
            val = sigma_profile(s, sizes)
            if "one whole part" not in worst or val < worst["one whole part"][0]:
                worst["one whole part"] = (val, tuple(s))
        neg = {k: v for k, v in worst.items() if v[0] < 0}
        print(f"  b={b}: min sigma per family: " +
              ", ".join(f"{k}={v[0]}" for k, v in sorted(worst.items())) +
              ("   ALL >= 0" if not neg else f"   *** VIOLATED: {neg} ***"))

    print("\n=== explicit-graph brute force: min |S| with sigma<0, b=3,4 (all 2^N) ===")
    for b in (3, 4):
        N, E, part, side, sizes = build(b)
        found = None
        for k in range(1, N + 1):
            for S in combinations(range(N), k):
                if sigma_set(set(S), E, side) < 0:
                    found = (k, S)
                    break
            if found:
                break
        mc, _ = maxcut_brute(N, E)
        print(f"  b={b}: N={N} min|S| sigma<0 = {found[0]} (witness {found[1]})  "
              f"kappa(b)={kappa_formula(b)}  bip(G)=|E|-maxcut={len(E)-mc}")


if __name__ == "__main__":
    main()
