"""Sweep-structure probe for LOAD-PSC.

Dump, for a chosen witness, the full coarea table:
  level a_j, width w_j, |H_j|, delta_B(H_j), delta_M(H_j), sigma_j,
  and the running prefix for LOAD-PSC-25 and LOAD-PSC-5.

Goal: find the Abel/summation-by-parts invariant that keeps the prefix >=0
even though individual bands go very negative at high s.

Key algebraic facts we test here:
  * sum_j w_j * |H_j|      = sum_v T(v) = Gamma        (layer-cake for T)
  * sum_j w_j * sigma_j    = TV_B(T) - TV_M(T)         (coarea for signed TV)
  * sum_j w_j * 2 a_j |H_j| + sum_j w_j^2 |H_j| = sum_v T(v)^2
    (layer-cake for T^2, since int_0^T 2s ds = T^2; discrete a(a+w) per band)

We also test the monotonicity structure of sigma_j and |H_j| along the sweep.
"""
from fractions import Fraction as F
from _codex_psc50_scout import adj_of, build_two_lane, greedy_chords
from _wf_lrsbreak_0 import build_k_lane
from _satzmu_conn import struct_for_side


def sweep_table(n, edges, side):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    M, ell, T, _mu, _cyc = st
    T = [F(t) for t in T]
    m = len(M)
    D = F(n * n - 25 * m)
    L = F(n) + F(n * n, 25) - m
    cut_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    bad_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    levels = sorted(set([F(0)] + T))
    rows = []
    for a, b in zip(levels, levels[1:]):
        H = {i for i, t in enumerate(T) if t > a}
        w = b - a
        dB = sum(1 for u, v in cut_edges if (u in H) ^ (v in H))
        dM = sum(1 for u, v in bad_edges if (u in H) ^ (v in H))
        sigma = dB - dM
        rows.append(dict(a=a, b=b, w=w, H=len(H), dB=dB, dM=dM, sigma=sigma))
    return dict(n=n, m=m, D=D, L=L, T=T, rows=rows,
                Gamma=sum(t * t for t in T))


def prefix(rows, n, D, c):
    """Running prefix for LOAD-PSC-c.
    band_j = w_j*( c*(L?) ...). We use the coarea integrand for coefficient c:
    LOAD-PSC-c integrand at level s in band j (a=a_j, width w):
      capacity term derivative: c * d/ds[ a(L-a) ] integrated ... but we use the
      exact discrete band matching _codex_prefix_loadpsc_gate for c=25, and the
      general-c version.
    """
    # General-c band. LOAD-PSC-c: c*sum a(L-a) - N*(TV_B(a)-TV_M(a)) >=0.
    # d/dtau [c*sum a_tau(L-a_tau)] over band [a,b): for vertices with T>a (set H),
    #   a_tau=tau so term = c*(L-2*tau)*|H| integrated ds. plus a bad-count shift.
    # We reconstruct exactly from the c=25 script: band = w*(D*H -25*(2a+w-N)*H - N*sigma)
    # For general c the '25' multiplying (2a+w-N)*H is really c, and D*H is c*(N^2/25... )?
    # Cleanest: recompute capacity+tv directly. Do that in caller instead.
    raise NotImplementedError


def direct_prefix(tab, c):
    """Directly compute Phi(tau_k)=c*sum a(L-a) - N*(TV_B(a)-TV_M(a)) at each level."""
    n = tab["n"]
    L = tab["L"]
    T = tab["T"]
    rows = tab["rows"]
    levels = [F(0)] + [r["b"] for r in rows]
    out = []
    for tau in levels:
        a = [min(t, tau) for t in T]
        cap = sum(x * (L - x) for x in a)
        # TV via sweep: TV_B(a)-TV_M(a) = sum_{j: a_j < tau} w_j*sigma_j
        tv = F(0)
        for r in rows:
            if r["a"] < tau:
                w = min(r["b"], tau) - r["a"]
                tv += w * r["sigma"]
        phi = c * cap - F(n) * tv
        out.append((tau, cap, tv, phi))
    return out


def main():
    L = 18
    bad = greedy_chords(L, 5, 10)
    n, edges, side, _ = build_k_lane(L, 5, bad)
    tab = sweep_table(n, edges, side)
    print(f"n={n} m={tab['m']} D={tab['D']} L={tab['L']} Gamma={tab['Gamma']}")
    print("verify layer-cake identities:")
    Gsum = sum(r["w"] * r["H"] for r in tab["rows"])
    tvsum = sum(r["w"] * r["sigma"] for r in tab["rows"])
    print(f"  sum w*H = {Gsum}  (Gamma={tab['Gamma']})")
    print(f"  sum w*sigma = {tvsum}")
    print()
    print(" j |    a    w  |H|  dB  dM  sigma | cumH  cumSigma")
    cumH = 0
    cumS = 0
    for j, r in enumerate(tab["rows"]):
        cumH += r["w"] * r["H"]
        cumS += r["w"] * r["sigma"]
        print(f"{j:2d} | {str(r['a']):>5} {str(r['w']):>3} {r['H']:>4} {r['dB']:>3} {r['dM']:>3} {r['sigma']:>5} | {str(cumH):>6} {str(cumS):>6}")
    print()
    for c in (25, 5):
        pref = direct_prefix(tab, c)
        mn = min(p[3] for p in pref)
        print(f"LOAD-PSC-{c}: min prefix Phi = {mn}")
        for tau, cap, tv, phi in pref:
            flag = " <<<" if phi < 0 else ""
            print(f"   tau={str(tau):>5}  cap={str(cap):>8}  tv={str(tv):>6}  Phi={str(phi):>10}{flag}")


if __name__ == "__main__":
    main()
