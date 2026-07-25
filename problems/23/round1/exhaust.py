"""
Exhaustive exact census of connected triangle-free graphs, N = 5..NMAX.

For each graph we compute, in EXACT arithmetic:
    bip(G)      : min # monochromatic edges over all bipartitions
    tau*(G)     : value of the fractional odd-cycle edge-cover LP
                  (= nu*(G), the fractional odd-cycle packing, by LP duality)

and we record
    * the maximum of bip(G)  and of bip(G)/N^2   (conjecture: <= 1/25)
    * every graph with tau*(G) < bip(G)   (odd-cycle LP integrality gap)
    * every graph with bip(G) * 25 >= N^2 (tight / near tight for the conjecture)
    * the maximum of tau*(G)/N^2

Usage:  python exhaust.py NMAX
"""
import subprocess, sys, os
from fractions import Fraction
from f5lib import parse_graph6, bip, tau_star, all_odd_cycles, verify_cover, verify_packing

GENG = os.environ.get("GENG", r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe")


def run(nmax):
    summary = []
    gaps = []
    tight = []
    for n in range(int(os.environ.get("NMIN","5")), nmax + 1):
        p = subprocess.run([GENG, "-tcq", str(n)], capture_output=True, text=True)
        lines = [l for l in p.stdout.split() if l]
        cnt = 0
        best_bip = -1
        best_bip_g = None
        best_ratio = Fraction(-1)
        best_ratio_g = None
        best_tau = Fraction(-1)
        best_tau_g = None
        n_nonbip = 0
        for g6 in lines:
            nn, edges = parse_graph6(g6)
            assert nn == n
            cnt += 1
            b = bip(n, edges)
            if b > best_bip:
                best_bip, best_bip_g = b, g6
            r = Fraction(b, n * n)
            if r > best_ratio:
                best_ratio, best_ratio_g = r, g6
            if b == 0:
                continue
            n_nonbip += 1
            cycles = all_odd_cycles(n, edges)
            t, y, z, _ = tau_star(n, edges, cycles)
            assert verify_cover(edges, cycles, y), g6
            assert verify_packing(len(edges), cycles, z), g6
            assert sum(y) == t and sum(z) == t, g6
            tr = t / (n * n)
            if tr > best_tau:
                best_tau, best_tau_g = tr, g6
            if t < b:
                gaps.append((n, g6, len(edges), b, t))
            if 25 * b >= n * n:
                tight.append((n, g6, len(edges), b, t))
        summary.append(dict(n=n, count=cnt, nonbip=n_nonbip,
                            best_bip=best_bip, best_bip_g=best_bip_g,
                            best_ratio=best_ratio, best_ratio_g=best_ratio_g,
                            best_tau_ratio=best_tau, best_tau_g=best_tau_g))
        s = summary[-1]
        print(f"n={n} graphs={cnt} nonbipartite={n_nonbip} "
              f"max bip={s['best_bip']} ({s['best_bip_g']}) "
              f"max bip/N^2={s['best_ratio']}={float(s['best_ratio']):.5f} "
              f"max tau*/N^2={s['best_tau_ratio']} "
              f"| 1/25={float(Fraction(1,25)):.5f}", flush=True)
    print()
    print("=== ODD-CYCLE LP INTEGRALITY GAPS (tau* < bip) ===")
    if not gaps:
        print("none found")
    for n, g6, m, b, t in gaps:
        print(f"  n={n} g6={g6} m={m} bip={b} tau*={t} gap={b - t}")
    print()
    print("=== GRAPHS WITH 25*bip >= N^2 ===")
    for n, g6, m, b, t in tight:
        print(f"  n={n} g6={g6} m={m} bip={b} tau*={t} N^2/25={Fraction(n*n,25)}")
    return summary, gaps, tight


if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    run(nmax)
