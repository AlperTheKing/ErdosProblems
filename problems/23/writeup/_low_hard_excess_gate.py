"""Exact gate for the near-extremal residue of LOW-GAMMA-CAP.

For a full-low band [a,b] with 2b <= N, H={T>a}, h=|H|,
sigma=delta_B(H)-delta_M(H), and Gamma=sum_f ell(f)^2, LOW-GAMMA-CAP is

    h * (N^2 - Gamma) >= N * sigma.

The easy split is:
  * if Gamma <= N*h, the trivial pair bound proves LOW-GAMMA-CAP;
  * if Gamma > N*h, the exact-gated LOW-HARD-P5 says sigma <= 5h.

When Gamma <= N(N-5), LOW-HARD-P5 proves LOW-GAMMA-CAP.  This script gates
the remaining hard-excess rewrite:

    N * (5h - sigma) >= h * (Gamma - N(N-5))

under Gamma > N*h and Gamma > N(N-5).  Algebraically this is LOW-GAMMA-CAP
on the near-extremal hard side, but its terms isolate the proof mechanism:
the spare C5-scale boundary slack must pay the square-deficit excess.
"""

import argparse
import subprocess
from fractions import Fraction as F

from _bdef_construct import Cn, mycielski, union_disjoint
from _h import Bconn, GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords


def adj_of(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def boundary_counts(adj, side, H):
    dB = dM = 0
    for u in H:
        for v in adj[u]:
            if v in H:
                continue
            if side[u] != side[v]:
                dB += 1
            else:
                dM += 1
    return dB, dM


def chk(name, n, adj, side, acc, stop_first=False):
    if not Bconn(n, adj, side):
        return False
    st = struct_for_side(n, adj, side)
    if st is None:
        return False
    M, ell, T, _mu, _cyc = st
    if not M:
        return False

    Gamma = sum(ell[f] ** 2 for f in M)
    levels = [F(0)] + sorted(set(F(t) for t in T if t > 0))
    for a, b in zip(levels, levels[1:]):
        if 2 * b > n:
            continue
        H = {v for v in range(n) if F(T[v]) > a}
        if not H:
            continue

        h = len(H)
        dB, dM = boundary_counts(adj, side, H)
        sigma = dB - dM
        acc["low"] += 1

        if Gamma <= n * h:
            acc["trivial"] += 1
            continue

        acc["hard"] += 1
        p5_slack = 5 * h - sigma
        if p5_slack < acc["min_p5"][0]:
            acc["min_p5"] = (p5_slack, name, n, len(M), Gamma, h, sigma, str(a), str(b), dB, dM)
        if p5_slack < 0:
            acc["p5_viol"] += 1
            if acc["first"] is None:
                acc["first"] = ("P5", name, "".join(map(str, side)), n, len(M), Gamma, h, sigma, str(a), str(b), dB, dM, p5_slack)
            if stop_first:
                return True

        if Gamma <= n * (n - 5):
            acc["p5_suffices"] += 1
            continue

        acc["excess"] += 1
        square_excess = Gamma - n * (n - 5)
        margin = F(n) * p5_slack - F(h) * square_excess
        low_gamma_margin = F(h) * (n * n - Gamma) - F(n) * sigma

        if margin != low_gamma_margin:
            raise AssertionError((name, n, Gamma, h, sigma, margin, low_gamma_margin))

        if margin < acc["min_excess"][0]:
            acc["min_excess"] = (margin, name, n, len(M), Gamma, h, sigma, str(a), str(b), dB, dM, p5_slack, square_excess)

        denom = F(n) * p5_slack
        if denom > 0:
            ratio = F(h) * square_excess / denom
            if ratio > acc["max_ratio"][0]:
                acc["max_ratio"] = (ratio, name, n, len(M), Gamma, h, sigma, str(a), str(b), dB, dM, p5_slack, square_excess)
        elif square_excess > 0:
            acc["zero_slack_excess"] += 1

        if margin < 0:
            acc["excess_viol"] += 1
            if acc["first"] is None:
                acc["first"] = ("EXCESS", name, "".join(map(str, side)), n, len(M), Gamma, h, sigma, str(a), str(b), dB, dM, margin)
            if stop_first:
                return True
    return False


def blowup(parts):
    offsets = [0]
    for part in parts:
        offsets.append(offsets[-1] + part)
    n = offsets[-1]
    edges = []
    for i in range(len(parts)):
        j = (i + 1) % len(parts)
        for u in range(offsets[i], offsets[i + 1]):
            for v in range(offsets[j], offsets[j + 1]):
                edges.append((min(u, v), max(u, v)))
    return n, sorted(set(edges))


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=7)
    parser.add_argument("--max-n", type=int, default=11)
    parser.add_argument("--two-lane-max", type=int, default=100)
    parser.add_argument("--blowup-t", type=int, default=5)
    parser.add_argument("--blowup-nmax", type=int, default=26)
    parser.add_argument("--fast", action="store_true", help="Skip named blowup/Myc/glued extras.")
    parser.add_argument("--stop-first", action="store_true")
    args = parser.parse_args()

    acc = {
        "low": 0,
        "trivial": 0,
        "hard": 0,
        "p5_suffices": 0,
        "excess": 0,
        "p5_viol": 0,
        "excess_viol": 0,
        "zero_slack_excess": 0,
        "first": None,
        "min_p5": (10**18, None),
        "min_excess": (F(10**18), None),
        "max_ratio": (F(0), None),
    }

    for L in range(8, args.two_lane_max + 1, 2):
        n, edges, side, _bad = build_two_lane(L)
        if chk(f"two-lane-L{L}", n, adj_of(n, edges), side, acc, args.stop_first):
            break

    for L, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8), (18, 5, 10), (20, 6, 10)):
        bad = greedy_chords(L, k, gap)
        n, edges, side, _bad = build_k_lane(L, k, bad)
        if chk(f"k-lane-L{L}-k{k}", n, adj_of(n, edges), side, acc, args.stop_first):
            break

    print(f"  lane diagnostics done: p5_viol={acc['p5_viol']} excess_viol={acc['excess_viol']}", flush=True)

    for n0 in range(args.min_n, args.max_n + 1):
        outg = subprocess.run([GENG, "-tc", str(n0)], capture_output=True, text=True).stdout.split()
        before = (acc["p5_viol"], acc["excess_viol"])
        for g6 in outg:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                if chk(f"cen{g6}", n, adj, side, acc, args.stop_first):
                    break
            if args.stop_first and acc["first"] is not None:
                break
        after = (acc["p5_viol"], acc["excess_viol"])
        print(f"  census N={n0} (p5+{after[0]-before[0]} excess+{after[1]-before[1]})", flush=True)
        if args.stop_first and acc["first"] is not None:
            break

    if not args.fast:
        for cyc in (5, 7, 9):
            for t in range(1, args.blowup_t + 1):
                n, edges = blowup([t] * cyc)
                if n > args.blowup_nmax:
                    continue
                adj, cuts = gmins(n, edges)
                for side in cuts[:2]:
                    chk(f"C{cyc}[{t}]", n, adj, side, acc, args.stop_first)

        for parts in ([2, 2, 2, 2, 3], [1, 5, 2, 2, 5], [1, 4, 2, 4, 2, 4, 2], [3, 3, 3, 3, 2], [1, 3, 2, 2, 3]):
            n, edges = blowup(parts)
            if n > args.blowup_nmax:
                continue
            adj, cuts = gmins(n, edges)
            for side in cuts[:2]:
                chk(f"nu{parts}", n, adj, side, acc, args.stop_first)

        grot = mycielski(5, Cn(5))
        mycg = mycielski(grot[0], grot[1])
        named = [
            ("Grotzsch", grot),
            ("Myc(Grotzsch)", mycg),
            ("M(C7)", mycielski(7, Cn(7))),
            ("M(C9)", mycielski(9, Cn(9))),
            ("C7|Grotzsch", bridge((7, Cn(7)), grot, 0, 0)),
            ("C9|C9", bridge((9, Cn(9)), (9, Cn(9)), 0, 0)),
            ("C5|C7", bridge((5, Cn(5)), (7, Cn(7)), 0, 0)),
        ]
        for name, (n, edges) in named:
            adj, cuts = gmins(n, edges)
            for side in cuts[:3]:
                chk(name, n, adj, side, acc, args.stop_first)
        print("  blow-ups + Mycielskians + glued done", flush=True)

    print("\n=== LOW-HARD-EXCESS gate ===")
    print(f"  low bands={acc['low']} trivial(Gamma<=Nh)={acc['trivial']} hard={acc['hard']}")
    print(f"  hard where P5 alone suffices={acc['p5_suffices']} hard-excess rows={acc['excess']}")
    print(f"  LOW-HARD-P5 violations={acc['p5_viol']} hard-excess violations={acc['excess_viol']} zero-slack-excess={acc['zero_slack_excess']}")
    print(f"  min P5 slack = {acc['min_p5'][0]} at {acc['min_p5'][1:]}")
    print(f"  min hard-excess margin = {acc['min_excess'][0]} at {acc['min_excess'][1:]}")
    print(f"  max excess/payment ratio = {acc['max_ratio'][0]} at {acc['max_ratio'][1:]}")
    if acc["first"]:
        print(f"  first violation: {acc['first']}")
    print(f"  === LOW-HARD-EXCESS {'HOLDS' if not acc['p5_viol'] and not acc['excess_viol'] else 'FAILS'} ===")


if __name__ == "__main__":
    main()
