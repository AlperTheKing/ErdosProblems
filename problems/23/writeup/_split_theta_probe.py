"""Test the theta-split per-level structure for LOAD-PSC-5.

theta = (N+eta)/2 = L/2, where eta=N^2/25-|M|, L=N+eta.
At s=theta the capacity coefficient 5(L-2s) changes sign.

I5(s) = 5(L-2s)|H_s| - N*sigma_s.

CLAIM A (LOW half, s <= theta i.e. L-2s>=0):  I5(s) >= 0 TERMWISE.
   i.e. N*sigma_s <= 5(L-2s)|H_s| for every super-level with 2s <= L.
CLAIM B (HIGH half, s > theta): I5(s) may be < 0; must be paid by the bank
   accumulated in the low half (prefix). We test that the FULL prefix integral
   Phi5(tau) >= 0 for tau>theta reduces to: (bank at theta) >= (debt from theta to tau).

We scan census N<=10 + lanes and report:
  - CLAIM A termwise violations (should be 0 if the clean split holds), with worst.
  - For the HIGH half: max debt vs bank-at-theta.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords


def adj_of(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    return adj


def boundary(n, adj, side, Hset):
    dB = 0; dM = 0
    for u in Hset:
        for v in adj[u]:
            if v in Hset:
                continue
            if side[u] != side[v]:
                dB += 1
            else:
                dM += 1
    return dB, dM


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    N = F(n); m = len(M)
    Gamma = sum(t for t in T)
    eta = F(n * n, 25) - m
    L = N + eta
    theta = L / 2
    levs = sorted(set([F(0)] + [t for t in T]))
    for k in range(len(levs) - 1):
        s = levs[k]
        Hset = set(v for v in range(n) if T[v] > s)
        if not Hset:
            continue
        h = len(Hset)
        dB, dM = boundary(n, adj, side, Hset)
        sig = dB - dM
        I5 = 5 * (L - 2 * s) * h - N * sig
        acc['levels'] += 1
        if 2 * s <= L:  # LOW half (s <= theta): claim I5>=0 termwise
            acc['low_levels'] += 1
            if I5 < 0:
                acc['claimA_viol'] += 1
                if I5 < acc['claimA_worst'][0]:
                    acc['claimA_worst'] = (I5, name, n, m, str(s), h, str(sig), str(L), str(Gamma))
        else:  # HIGH half
            acc['high_levels'] += 1
            if I5 < 0:
                acc['high_neg'] += 1
        # also track alternate low-half cap: N*sig <= (N^2-Gamma)*h  (LOW-GAMMA-CAP)
        if 2 * s <= N:  # strict low band per note
            if N * sig > (F(n*n) - Gamma) * h:
                acc['lowgamma_viol'] += 1
                if acc['lowgamma_ex'] is None:
                    acc['lowgamma_ex'] = (name, n, m, str(s), h, str(sig))


def main():
    acc = dict(levels=0, low_levels=0, high_levels=0,
               claimA_viol=0, claimA_worst=(F(0), '', 0, 0, '', 0, '', '', ''),
               high_neg=0, lowgamma_viol=0, lowgamma_ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj, cuts = gmins(n, E)
            for side in cuts:
                scan_cut(f"cen{g6}", n, adj, side, acc)
        print(f"census N={nn}: claimA_viol={acc['claimA_viol']}", flush=True)
    for L in (8, 12, 16, 20):
        n, edges, side, _ = build_two_lane(L)
        scan_cut(f"two-lane-L{L}", n, adj_of(n, edges), side, acc)
    for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _bad = build_k_lane(Ll, k, bad)
        scan_cut(f"klane-L{Ll}k{k}", n, adj_of(n, edges), side, acc)

    print("\n=== theta-split per-level scan ===")
    print(f"levels={acc['levels']} low={acc['low_levels']} high={acc['high_levels']}")
    print(f"CLAIM A (LOW half s<=theta: I5>=0 termwise) violations = {acc['claimA_viol']}")
    print(f"  worst I5 in low half = {acc['claimA_worst'][0]} at {acc['claimA_worst'][1:]}")
    print(f"HIGH half levels with I5<0 (expected, paid by bank) = {acc['high_neg']}")
    print(f"LOW-GAMMA-CAP (2s<=N: N*sig<=(N^2-Gamma)h) violations = {acc['lowgamma_viol']} {acc['lowgamma_ex'] or ''}")


if __name__ == "__main__":
    main()
