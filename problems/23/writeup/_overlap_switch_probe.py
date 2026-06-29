"""Inspect cut-improving switches for P-contained chord interior-overlap.

Claude's max-cut mechanism (M): a global maximum connected-B cut should not
have two P-contained bad chords whose intervals interior-overlap on a unique
geodesic P_f.  This probe finds small non-max witnesses, brute-forces the best
cut-improving subset, and prints the geometry.
"""

import subprocess

from _h import dec, GENG, maxcut_all, Bconn
from _satzmu_conn import struct_for_side


def cutsize(n, adj, side):
    return sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])


def interior_pair(intervals):
    for i in range(len(intervals)):
        p1, q1, g1 = intervals[i]
        for j in range(i + 1, len(intervals)):
            p2, q2, g2 = intervals[j]
            lo = max(p1, p2)
            hi = min(q1, q2)
            if lo < hi:
                return (p1, q1, g1, p2, q2, g2, lo, hi)
    return None


def contained_intervals(M, cyc, f, P):
    pos = {x: i for i, x in enumerate(P)}
    Pset = set(P)
    intervals = []
    for g in M:
        if g == f:
            continue
        for Q in cyc[g]:
            if not set(Q) <= Pset:
                continue
            pp = sorted(pos[v] for v in Q)
            if pp[-1] - pp[0] == len(pp) - 1:
                intervals.append((pp[0], pp[-1], g))
                break
    return intervals


def best_subset(n, adj, side):
    base = cutsize(n, adj, side)
    best = (0, ())
    # Up to N=9 in this probe, brute force is cheap.
    for mask in range(1, 1 << n):
        side2 = side[:]
        subset = []
        for v in range(n):
            if (mask >> v) & 1:
                side2[v] ^= 1
                subset.append(v)
        gain = cutsize(n, adj, side2) - base
        if gain > best[0]:
            best = (gain, tuple(subset))
    return best


def first_witness():
    for nn in range(6, 10):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj = [set() for _ in range(n)]
            for a, b in E:
                adj[a].add(b)
                adj[b].add(a)
            mx = cutsize(n, adj, list(maxcut_all(n, adj)[0]))
            for mask in range(1 << (n - 1)):
                side = [(mask >> v) & 1 for v in range(n)]
                if cutsize(n, adj, side) == mx:
                    continue
                if not Bconn(n, adj, side):
                    continue
                st = struct_for_side(n, adj, side)
                if st is None:
                    continue
                M, _ell, _T, _mu, cyc = st
                for f in M:
                    if len(cyc[f]) != 1:
                        continue
                    P = cyc[f][0]
                    intervals = contained_intervals(M, cyc, f, P)
                    pair = interior_pair(intervals)
                    if pair is None:
                        continue
                    gain, subset = best_subset(n, adj, side)
                    return g6, n, sorted(E), "".join(map(str, side)), cutsize(n, adj, side), mx, f, P, intervals, pair, gain, subset
    return None


if __name__ == "__main__":
    w = first_witness()
    print("=== INTERIOR-OVERLAP SWITCH PROBE ===", flush=True)
    if w is None:
        print("no witness", flush=True)
    else:
        (
            g6,
            n,
            edges,
            side,
            cut,
            mx,
            f,
            P,
            intervals,
            pair,
            gain,
            subset,
        ) = w
        print(f"g6={g6} n={n} side={side} cut={cut} max={mx}", flush=True)
        print(f"edges={edges}", flush=True)
        print(f"f={f} P={P}", flush=True)
        print(f"contained intervals={intervals}", flush=True)
        print(f"first interior pair={pair}", flush=True)
        print(f"best gain={gain} subset={subset}", flush=True)
