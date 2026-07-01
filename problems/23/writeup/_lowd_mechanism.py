"""Verify the exact mechanism of LOW-D:  D*|H| >= N*sigma  (D=N^2-25m), equivalently
   N*(2 dM + noncross) >= |H|*(25m - N|H|).           (STRUCT-D)

Claimed proof ingredients (to verify hold at every level, esp. the nontrivial regime
25m > N|H|, i.e. |H| < 25m/N):
  (a) max-cut local optimality: every v in H has cut-degree >= deg(v)/2.
  (b) The load handshake / geodesic count bounds dM (bad boundary edges) and noncross.

We instead verify the *pure combinatorial* sufficient condition that would prove STRUCT-D
in the hard regime, testing several candidate lower bounds on the LHS:
  (C1)  each vertex v in H has >= (25m - N|H|)/(something) ... too vague.
Instead: directly measure, per level with 25m>N|H|, the SLACK
   slack = N*(2 dM + noncross) - |H|*(25m - N|H|)
and whether it correlates with a max-cut quantity. Report where STRUCT-D actually holds/fails
(should match LOW-D exactly) and, at the WORST (min-slack) nontrivial level, dump full data.
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
        noncross = h * (n - h) - dB - dM
        rhs = h * (25 * m - N * h)
        lhs = N * (2 * dM + noncross)
        slack = lhs - rhs
        nontrivial = (rhs > 0)   # 25m > N h
        acc['levels'] += 1
        if nontrivial:
            acc['nontrivial'] += 1
            if slack < acc['worst'][0]:
                acc['worst'] = (slack, name, n, m, str(s), h, dB, dM, noncross, str(rhs))
            if slack < 0:
                acc['fail'] += 1


def main():
    acc = dict(levels=0, nontrivial=0, fail=0,
               worst=(F(10**9), '', 0, 0, '', 0, 0, 0, 0, ''))
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj, cuts = gmins(n, E)
            for side in cuts:
                scan_cut(f"cen{g6}", n, adj, side, acc)
        print(f"census N={nn}: nontrivial={acc['nontrivial']} fail={acc['fail']}", flush=True)
    print("\n=== STRUCT-D (=LOW-D) mechanism scan ===")
    print(f"levels={acc['levels']} nontrivial(25m>Nh)={acc['nontrivial']} STRUCT-D fails={acc['fail']}")
    print(f"worst nontrivial slack = {acc['worst'][0]} at (name,n,m,s,h,dB,dM,noncross,rhs)={acc['worst'][1:]}")


if __name__ == "__main__":
    main()
