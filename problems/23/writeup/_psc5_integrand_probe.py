"""Exact LOAD-PSC-5 integrand and prefix.

Phi(tau) = 5*sum_v a(L-a) - N*(TV_B(a)-TV_M(a)),  a=min(T,tau).
Derivative over band {T>s}=H_s:  I(s) = 5*(L-2s)*|H_s| - N*sigma_s.
Phi(tau) = int_0^tau I(s) ds.

We dump I(s) and the prefix for the hardest witnesses, and test the Abel
identity Phi(tau) = int_0^tau I. We look for the monotone/telescoping invariant.

We also test the ENDPOINT statement (tau=maxT) which is theorem-sufficient:
  Phi(maxT) = 5*sum T(L-T) - N*(TV_B(T)-TV_M(T)) >= 0
equivalently 5*sum T^2 <= 5 L Gamma - N*(TV_B(T)-TV_M(T)), i.e. LRS-with-TV.
"""
from fractions import Fraction as F
from _codex_psc50_scout import adj_of, greedy_chords
from _wf_lrsbreak_0 import build_k_lane
from _satzmu_conn import struct_for_side


def table(n, edges, side):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    M, ell, T, _mu, _cyc = st
    T = [F(t) for t in T]
    m = len(M)
    L = F(n) + F(n * n, 25) - m
    cut = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    bad = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    levels = sorted(set([F(0)] + T))
    rows = []
    for a, b in zip(levels, levels[1:]):
        H = {i for i, t in enumerate(T) if t > a}
        w = b - a
        dB = sum(1 for u, v in cut if (u in H) ^ (v in H))
        dM = sum(1 for u, v in bad if (u in H) ^ (v in H))
        sigma = dB - dM
        rows.append(dict(a=a, w=w, H=len(H), sigma=sigma, dB=dB, dM=dM))
    return n, m, L, rows, T


def main():
    L = 20
    bad = greedy_chords(L, 6, 10)
    n, edges, side, _ = build_k_lane(L, 6, bad)
    n, m, Lval, rows, T = table(n, edges, side)
    print(f"n={n} m={m} L={Lval} maxT={max(T)} L/2={Lval/2}")
    print(" band [a,b): I(s)=5(L-2s)H - N*sigma over the band; integrate")
    print(" a      w   H  sigma   5(L-2a)H    5(L-2b)H   band_lo band_hi  cumPhi(a)  cumPhi(b)")
    cum = F(0)
    for r in rows:
        a, w, H, sigma = r["a"], r["w"], r["H"], r["sigma"]
        b = a + w
        # I is linear in s: I(s)=5(L-2s)H - N sigma. integrate over [a,b]:
        # int = 5H*( L*w - (b^2-a^2) ) - N*sigma*w = 5H*w*(L-(a+b)) - N*sigma*w
        band = 5 * H * w * (Lval - (a + b)) - F(n) * sigma * w
        Ia = 5 * (Lval - 2 * a) * H - F(n) * sigma
        Ib = 5 * (Lval - 2 * b) * H - F(n) * sigma
        cum_before = cum
        cum += band
        print(f"{str(a):>5} {str(w):>3} {H:>3} {sigma:>5} {str(Ia):>12} {str(Ib):>12} {str(band):>9} {str(cum_before):>10} {str(cum):>10}")
    print(f"final Phi(maxT) = {cum}   (must be >=0)")


if __name__ == "__main__":
    main()
