"""Test structural monotonicity/decomposition facts needed for the sweep proof.

(1) Is sigma_s NON-INCREASING in s?  (H_s nested decreasing; does signed boundary shrink?)
    The note says 'Monotone sigma(H)/|H| over pre-theta levels: false'. Test sigma_s itself.
(2) Abel form: Phi5(tau) = int_0^tau [5(L-2s)h_s - N sigma_s] ds. Integrate by parts to move
    the s-weight onto a cumulative boundary term. Define
       Sig(s) = int_s^{maxT} sigma_r dr  (tail TV from s up) ... test whether
       Phi5 can be written as sum of nonneg pieces using (LOW-D low band) + (post-theta endpoint control).
(3) The clean split we CAN prove: for tau <= s0 where s0 = sharp low-band threshold,
    Phi5(tau) >= 0 termwise via LOW-D-like cap; report the sharp s0/N over battery
    where the integrand 5(L-2s)h - N sigma FIRST goes negative, vs the LOW-D failure threshold.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins


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
    eta = F(n * n, 25) - m
    L = N + eta
    Gamma = sum(t for t in T)
    levs = sorted(set([F(0)] + [t for t in T]))
    prev_sig = None
    first_I5neg = None
    for k in range(len(levs) - 1):
        s = levs[k]
        Hset = set(v for v in range(n) if T[v] > s)
        if not Hset:
            continue
        h = len(Hset)
        dB = dM = 0
        for u in Hset:
            for v in adj[u]:
                if v in Hset:
                    continue
                if side[u] != side[v]:
                    dB += 1
                else:
                    dM += 1
        sig = dB - dM
        I5 = 5 * (L - 2 * s) * h - N * sig
        # monotonicity of sigma
        if prev_sig is not None and sig > prev_sig:
            acc['sig_increase'] += 1
        prev_sig = sig
        # first s where I5<0
        if I5 < 0 and first_I5neg is None:
            first_I5neg = F(s, n)
        acc['levels'] += 1
    if first_I5neg is not None:
        if first_I5neg < acc['I5neg_min_sN'][0]:
            acc['I5neg_min_sN'] = (first_I5neg, name, n, m)


def main():
    acc = dict(levels=0, sig_increase=0, I5neg_min_sN=(F(10**9), '', 0, 0))
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj, cuts = gmins(n, E)
            for side in cuts:
                scan_cut(f"cen{g6}", n, adj, side, acc)
        print(f"census N={nn}: sig_increase={acc['sig_increase']}", flush=True)
    print("\n=== sigma monotone + I5-first-neg scan ===")
    print(f"levels={acc['levels']}")
    print(f"sigma_s INCREASES (violates monotone-decreasing) count = {acc['sig_increase']}")
    print(f"integrand I5 first goes negative at MIN s/N = {acc['I5neg_min_sN'][0]} "
          f"(={float(acc['I5neg_min_sN'][0]):.4f}) at {acc['I5neg_min_sN'][1:]}")


if __name__ == "__main__":
    main()
