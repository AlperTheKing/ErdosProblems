"""Inspect SDP-optimal c vs local vertex quantities (deficit N-T, overload) to find closed form."""
from fractions import Fraction as F
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _cond_cert import cycle_edges, sdp_optimize
import numpy as np

def report(name, n, E):
    adj, cuts = gmins(n, E)
    side = cuts[0]
    st = struct_for_side(n, adj, side)
    M, ell, T, mu, cyc = st
    print(f"\n##### {name} N={n}  deficit R_v = N - T_v #####")
    R = {v: F(n) - T[v] for v in range(n)}
    for v in range(n):
        tag = "OVER" if T[v] > n else ("def" if T[v] < n else "tie")
        print(f"  v={v}: T={T[v]} R=N-T={R[v]} [{tag}]")
    res = sdp_optimize(name, n, adj, side, verbose=False)
    if res is None:
        print("  SDP failed"); return
    cval = res['cval']
    print(f"  t* = {res['t']:.6f}")
    print("  edge-wise c (SDP) with endpoint deficits:")
    for Q, ce, p in res['Sblocks']:
        for k, (a, b) in enumerate(ce):
            c = cval[p + k]
            print(f"    Q={Q} edge {a}-{b}: c={c:.5f}  R_a={float(R[a]):.2f} R_b={float(R[b]):.2f}  "
                  f"min(R_a,R_b)={float(min(R[a],R[b])):.2f}")
        break  # one cycle per family is enough to see pattern (symmetric)

if __name__ == "__main__":
    n, E = dec("H?AFBo]"); report("HAFBo_N9", n, E)
    n, E = odd_blowup(5, [2, 1, 2, 1, 2]); report("C5_blow21212_N8", n, E)
    n, E = odd_blowup(5, [3, 2, 3, 2, 3]); report("C5_blow32323_N13", n, E)
