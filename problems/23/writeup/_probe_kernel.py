"""On the tight extremal C5[3], characterize the kernel of GH=(H) under uniform c=beta_L (true beta, float),
   and verify the conductance cert is pinned: max uniform c keeping Local-SOS is beta_L, and the SDP-optimal
   per-edge c on the tight family is uniform. Also: is the GH kernel the C5[t] 'second-eigenvector' (the
   2-coloring-orthogonal mode)? That tells us (H) is tight precisely on the graphon C5 fixed point."""
import numpy as np, math
from fractions import Fraction as F
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup

def build_GH_float(n, M, ell, T, cyc, cfun):
    GH = np.zeros((n, n))
    for v in range(n):
        GH[v][v] = float(n) - float(T[v])
    for f in M:
        Qs = cyc[f]; L = ell[f]; w = 1.0 / len(Qs)
        for Q in Qs:
            Ql = list(Q)
            for i in range(L):
                a = Ql[i]; b = Ql[(i + 1) % L]
                c = cfun(L)
                GH[a][a] += w * c; GH[b][b] += w * c
                GH[a][b] -= w * c; GH[b][a] -= w * c
    return GH

def beta_true(L):
    return L / (2 + 2 * math.cos(math.pi / L))

for sizes, nm in [([3,3,3,3,3], "C5x3_N15"), ([2,2,2,2,2], "C5x2_N10"), ([4,4,4,4,4], "C5x4_N20")]:
    n, E = odd_blowup(5, sizes)
    adj, cuts = gmins(n, E)
    side = cuts[0]
    st = struct_for_side(n, adj, side)
    M, ell, T, mu, cyc = st
    GH = build_GH_float(n, M, ell, T, cyc, beta_true)
    ev, evec = np.linalg.eigh(GH)
    print(f"\n{nm} N={n}: GH eigenvalues (uniform true beta): {np.round(ev[:6],6)}")
    # kernel vector
    v0 = evec[:, 0]
    # which part each vertex belongs to (C5 blow-up): part index
    start = [0]*5
    for i in range(1,5): start[i]=start[i-1]+sizes[i-1]
    part = [None]*n
    for i in range(5):
        for j in range(sizes[i]): part[start[i]+j]=i
    print("  smallest eigenvalue =", round(ev[0],8))
    print("  kernel vec by part (avg per C5 part):")
    for p in range(5):
        vals = [v0[v] for v in range(n) if part[v]==p]
        print(f"    part {p}: mean={np.mean(vals):.4f} std={np.std(vals):.6f}  (C5 mode cos(4pi p/5)={math.cos(4*math.pi*p/5):.4f})")
