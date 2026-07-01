"""Pin down the EXACT low-band per-level cap and its proof mechanism.

Two candidate low-band caps for a super-level H=H_s={T>s}, sigma=dB(H)-dM(H):
  (LOW-D)     D*|H|      >= N*sigma,   D=N^2-25m
  (LOW-GAMMA) (N^2-Gamma)*|H| >= N*sigma
valid under a low-band condition on s. Find the SHARP threshold on s.

Structural identity (max-cut, undirected simple graph):
  |H|(N-|H|) = e_cut_across(H) + e_noncut_across(H)   [edges + non-edges from H to V\H, counted as pairs]
  Actually: #pairs (u in H, w notin H) = |H|(N-|H|).
  Among boundary EDGES: dB (cut) + dM (bad=monochromatic). So
     dB + dM + (nonedges across) = |H|(N-|H|).
  sigma = dB - dM = |H|(N-|H|) - 2*dM - nonedges_across.        (id-1)
So N*sigma = N|H|(N-|H|) - N(2 dM + noncross).
  (LOW-D): D|H| >= N sigma  <=>  (N^2-25m)|H| >= N|H|(N-|H|) - N(2dM+noncross)
        <=> N(2 dM + noncross) >= N|H|(N-|H|) - (N^2-25m)|H|
        <=> N(2 dM + noncross) >= |H|( N(N-|H|) - N^2 + 25m )
        <=> N(2 dM + noncross) >= |H|( 25m - N|H| ).
  RHS positive only when N|H| < 25m, i.e. |H| < 25m/N. Since m<=N^2/25, 25m/N<=N; and
  in low band |H| is large-ish? Let's just SCAN the sharp s-threshold empirically.

We report, per level, whether (LOW-D) holds, and the max s (as fraction of N) at which it
still holds, to find the exact band. Then test the pure structural inequality
   N(2 dM + noncross) >= |H|(25m - N|H|)         (STRUCT-D)
which is equivalent to (LOW-D) with NO band condition, and find where it fails.
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
    D = F(n * n) - 25 * m
    Gamma = sum(t for t in T)
    levs = sorted(set([F(0)] + [t for t in T]))
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
        # STRUCT-D equivalent form:  N(2 dM + noncross) >= h(25m - N h)
        noncross = h * (n - h) - dB - dM
        struct_lhs = N * (2 * dM + noncross)
        struct_rhs = h * (25 * m - N * h)
        holds_D = (D * h >= N * sig)
        holds_G = ((F(n*n) - Gamma) * h >= N * sig)
        # record: for cuts where LOW-D fails, at what s/N?
        if not holds_D:
            acc['D_fail'] += 1
            rN = F(s, n)  # s/N
            if rN < acc['D_fail_min_sN'][0]:
                acc['D_fail_min_sN'] = (rN, name, n, m, str(s), h, str(sig), str(struct_rhs))
        if not holds_G:
            acc['G_fail'] += 1
            rN = F(s, n)
            if rN < acc['G_fail_min_sN'][0]:
                acc['G_fail_min_sN'] = (rN, name, n, m, str(s), h, str(sig))
        # STRUCT-D sanity: holds_D <=> struct_lhs>=struct_rhs
        if holds_D != (struct_lhs >= struct_rhs):
            acc['struct_mismatch'] += 1
        acc['levels'] += 1


def main():
    acc = dict(levels=0, D_fail=0, G_fail=0, struct_mismatch=0,
               D_fail_min_sN=(F(10**9), '', 0, 0, '', 0, '', ''),
               G_fail_min_sN=(F(10**9), '', 0, 0, '', 0, ''))
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj, cuts = gmins(n, E)
            for side in cuts:
                scan_cut(f"cen{g6}", n, adj, side, acc)
        print(f"census N={nn}: D_fail={acc['D_fail']} G_fail={acc['G_fail']}", flush=True)
    print("\n=== low-band cap sharp-threshold scan ===")
    print(f"levels={acc['levels']} struct_mismatch={acc['struct_mismatch']}")
    print(f"LOW-D (D*h>=N*sig) fails {acc['D_fail']} times; MIN s/N at failure = "
          f"{acc['D_fail_min_sN'][0]} (={float(acc['D_fail_min_sN'][0]):.4f}) at {acc['D_fail_min_sN'][1:]}")
    print(f"LOW-GAMMA ((N^2-Gamma)*h>=N*sig) fails {acc['G_fail']} times; MIN s/N at failure = "
          f"{acc['G_fail_min_sN'][0]} (={float(acc['G_fail_min_sN'][0]):.4f}) at {acc['G_fail_min_sN'][1:]}")


if __name__ == "__main__":
    main()
