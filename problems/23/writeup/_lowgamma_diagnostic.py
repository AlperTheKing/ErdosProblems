"""Dump tight LOW-GAMMA-CAP rows.

For consecutive load bands [a,b] with 2*b <= N, LOW-GAMMA-CAP is

    |H| * (N^2 - Gamma) >= N * sigma(H),

where H={v:T(v)>a} and sigma=delta_B(H)-delta_M(H).

This script prints the smallest exact slacks and auxiliary pair/load data.
It is diagnostic only; it does not certify the theorem.
"""
import subprocess
from fractions import Fraction as F

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


def scan(name, n, adj, side, out, keep=20):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, T, _mu, _cyc = st
    if not M:
        return
    levels = sorted(set([F(0)] + [F(t) for t in T]))
    Gamma = sum(F(t) for t in T)
    for a, b in zip(levels, levels[1:]):
        if 2 * b > n:
            continue
        H = {v for v, tv in enumerate(T) if F(tv) > a}
        if not H:
            continue
        h = len(H)
        dB = dM = internalB = internalM = 0
        for u in range(n):
            for v in adj[u]:
                if v <= u:
                    continue
                sameH = (u in H) == (v in H)
                isB = side[u] != side[v]
                if sameH:
                    if u in H:
                        if isB:
                            internalB += 1
                        else:
                            internalM += 1
                    continue
                if isB:
                    dB += 1
                else:
                    dM += 1
        sigma = dB - dM
        slack = h * (n * n - Gamma) - n * sigma
        noncross = h * (n - h) - dB - dM
        sumH = sum(F(T[v]) for v in H)
        sumC = Gamma - sumH
        row = (
            slack,
            name,
            n,
            len(M),
            str(a),
            str(b),
            h,
            str(Gamma),
            dB,
            dM,
            sigma,
            noncross,
            str(sumH),
            str(sumC),
            internalB,
            internalM,
        )
        out.append(row)
        out.sort(key=lambda x: x[0])
        del out[keep:]


def main():
    rows = []
    for L in range(8, 102, 2):
        n, E, side, _ = build_two_lane(L)
        scan(f"two-lane-L{L}", n, adj_of(n, E), side, rows)
    for Ll, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8), (18, 5, 10), (20, 6, 10)):
        bad = greedy_chords(Ll, k, gap)
        n, E, side, _ = build_k_lane(Ll, k, bad)
        scan(f"k-lane-L{Ll}-k{k}", n, adj_of(n, E), side, rows)
    for nn in range(7, 12):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj, cuts = gmins(n, E)
            for side in cuts:
                scan(f"cen{g6}", n, adj, side, rows)
        print(f"census N={nn} done", flush=True)

    print("=== tight LOW-GAMMA-CAP rows (slack ascending) ===")
    print("slack | name n m [a,b] h Gamma dB dM sigma noncross sumH sumC intB intM")
    for row in rows:
        slack, name, n, m, a, b, h, Gamma, dB, dM, sigma, noncross, sumH, sumC, intB, intM = row
        print(
            f"{slack} | {name} {n} {m} [{a},{b}] h={h} Gamma={Gamma} "
            f"dB={dB} dM={dM} sig={sigma} non={noncross} "
            f"sumH={sumH} sumC={sumC} intB={intB} intM={intM}"
        )


if __name__ == "__main__":
    main()
