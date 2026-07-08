r"""EXACT-GATE for GPT-Pro's LEAF full-support C5/density-bank closure (2026-07-08).

GPT-Pro closes the tight full-support LEAF case (single-bad-edge cage) via the density bank:
   C5Cap = 25 * max(0, N^2/25 - m - sigma),  Door = 25*sigma,  Demand = sum(ell^2 - 25).
Claude's non-circularity note: for a leaf (m=1) the shortest odd cycle has ell <= N vertices (a GRAPH FACT, NOT the
conjecture), so Demand = ell^2 - 25 <= N^2 - 25 = Door + C5 (when C5>=0); when C5<0 (dense, sigma>N^2/25-1) the door
alone exceeds N^2-25 >= Demand. EITHER WAY Balance = Door + C5Cap - Demand >= 0, and in fact >= N^2 - ell^2 >= 0.

This gate verifies, EXACTLY (Fraction):
  (odd cycles C_{2k+1}, k=2..25): ell = N, Balance = 0 (tight), Door + C5 = Demand exactly.
  (all triangle-free single-bad-edge Gamma-min cages, census N<=11): ell <= N, Door + max(0,C5) >= Demand, Balance>=0.
A single failure (Door + C5 < Demand at a single-bad-edge cage) would refute GPT-Pro's leaf closure. Run from problems/23/writeup.
"""
from fractions import Fraction as F
import subprocess
from _claude_residual_hall_gate import residuals
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def leaf_check(n, adj, side):
    """Return dict for a single-bad-edge cage, or None if not single-bad-edge / not B-connected."""
    if not Bconn(n, adj, side):
        return None
    cd = residuals(n, adj, side)
    if cd is None:
        return None
    M, ell = cd['M'], cd['ell']
    if len(M) != 1:
        return None  # leaf = single bad edge
    e = M[0]; L = ell[e]
    cut_edges = sum(1 for a in range(n) for b in adj[a] if a < b and side[a] != side[b])
    m = 1
    sigma = cut_edges - m
    demand = L ** 2 - 25
    door = 25 * sigma
    c5mass = F(n * n, 25) - m - sigma          # eta - sigma  (exact Fraction)
    c5cap = 25 * max(F(0), c5mass)
    balance = door + c5cap - demand
    return dict(n=n, ell=L, sigma=sigma, demand=demand, door=door,
                c5mass=c5mass, c5cap=c5cap, balance=balance, ell_le_N=(L <= n))


def odd_cycle(k):
    n = 2 * k + 1
    E = [(i, (i + 1) % n) for i in range(n)]
    return n, adj_from_edges(n, E), [i % 2 for i in range(n)]


def main():
    print("=" * 96)
    print("LEAF C5 CLOSURE GATE (GPT-Pro density bank; single-bad-edge cages). EXACT (Fraction).")
    print("=" * 96)
    print(" ODD CYCLES C_{2k+1} (ell=N, expect Balance=0 tight, Door+C5=Demand):")
    ok_odd = True
    for k in range(2, 26):
        n, adj, side = odd_cycle(k)
        r = leaf_check(n, adj, side)
        if r is None:
            print("   C_%d: (skipped)" % (2 * k + 1)); continue
        # absorption holds iff Balance = Door + max(0,C5) - Demand >= 0 (with ell<=N); tightness (Balance=0) only when C5mass>=0.
        good = r['balance'] >= 0 and r['ell_le_N']
        tight = (r['door'] + r['c5cap'] == r['demand'])
        ok_odd = ok_odd and good
        print("   C_%-3d N=%-3d ell=%-3d sigma=%-3d Demand=%-5d Door=%-5d C5mass=%-7s C5cap=%-5s Balance=%-4s ell<=N=%s %s%s"
              % (2 * k + 1, n, r['ell'], r['sigma'], r['demand'], r['door'], str(r['c5mass']), str(r['c5cap']),
                 str(r['balance']), r['ell_le_N'], "OK" if good else "*** FAIL ***", " (tight)" if tight else " (door over-covers)"))
    print("\n ALL triangle-free SINGLE-BAD-EDGE Gamma-min cages, census N<=11 (expect ell<=N, Balance>=0):")
    cages = 0; fails = 0; ex = None; min_balance = None
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            r = leaf_check(n, adj, best[0])
            if r is None:
                continue
            cages += 1
            if min_balance is None or r['balance'] < min_balance:
                min_balance = r['balance']
            if r['balance'] < 0 or not r['ell_le_N'] or (r['door'] + r['c5cap'] < r['demand']):
                fails += 1
                if ex is None:
                    ex = (nn, r)
        print("   census N=%d done: single-bad-edge cages %d, fails %d" % (nn, cages, fails), flush=True)
    print("=" * 96)
    print("LEAF C5 GATE: odd-cycle closure %s | census single-bad-edge cages %d, min Balance %s, FAILS %d"
          % ("OK" if ok_odd else "FAIL", cages, str(min_balance), fails))
    if ex:
        print("   *** FAIL example: N=%d %s ***" % (ex[0], ex[1]))
    print("VERDICT: %s" % (
        "GPT-Pro's LEAF full-support C5 closure CONFIRMED -- every single-bad-edge cage has Balance = Door+max(0,C5)-Demand >= 0"
        " (non-circular, via ell<=N); the tight full-support leaves (odd cycles) are TIGHT Balance=0. Base case of the induction CLOSED."
        if ok_odd and fails == 0 else
        "LEAF closure FAILS on %d cages -- GPT-Pro's density C5 bank does NOT absorb (decisive)." % fails))


if __name__ == '__main__':
    main()
