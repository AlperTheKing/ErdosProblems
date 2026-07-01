"""Per-level coarea probe for LOAD-PSC-5.

For each tested cut, sweep s over the distinct load values; for each super-level
set H_s = {v : T(v) > s} compute
  |H_s|,
  delta_B(H_s), delta_M(H_s), sigma_s = delta_B - delta_M,
  the LOAD-PSC-25 integrand  I25(s) = (D + 25N - 50 s)|H_s| - 5N*sigma_s,
  the LOAD-PSC-5  integrand  I5(s)  = (D + 5N - 10 s)|H_s| - N*sigma_s,   (see derivation below)
and the running prefix integrals Phi25(tau), Phi5(tau) over piecewise-constant bands.

Derivation of the LOAD-PSC-5 per-level integrand:
  LOAD-PSC-5 LHS = 5 * sum_v a(L-a).  d/d(band) of sum a(L-a) with a=min(T,tau):
  for a band (s,s+ds) the vertices in H_s each have a increasing at rate 1, contributing
  (L - 2 a) = (L - 2 s) per vertex (since on H_s, a=s at threshold s). Times 5:
  5*(L-2s)|H_s|.  With L = N + D/25:  5L = 5N + D/5 ... hmm keep symbolic. RHS pressure term:
  N * d/dtau (TV_B - TV_M) at level s = N * sigma_s.  So the LOAD-PSC-5 band integrand is
      I5(s) = 5*(L - 2 s)|H_s| - N*sigma_s.
  The note's LOAD-PSC-25 integrand (D+25N-50s)|H_s| - 5N sigma_s equals 5*I5 with L=N+D/25:
      5*(L-2s) = 5N + D/5 - 10 s ... times 5 gives 25N + D - 50 s = (D+25N-50s). YES matches, and
      5*N sigma = 5N sigma. So note's I25 = 5 * I5. Good, consistent.

We report:
  - min over s of I5(s)  (pointwise): expect NEGATIVE on two-lane at high s.
  - min over tau of Phi5(tau) (prefix integral): expect >= 0 always (that's LOAD-PSC-5).
  - the sign pattern of sigma_s across the sweep.
"""
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _h import Bconn
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


def probe(name, n, adj, side):
    if not Bconn(n, adj, side):
        print(f"{name}: not Bconn"); return
    st = struct_for_side(n, adj, side)
    if st is None:
        print(f"{name}: struct None"); return
    M, ell, T, mu, cyc = st
    if not M:
        print(f"{name}: no bad edges"); return
    m = len(M)
    N = F(n)
    D = F(n * n) - 25 * m
    L = N + D / 25
    Gamma = sum(t for t in T)
    # sweep levels: distinct load values, ascending; band (levels[k], levels[k+1])
    levs = sorted(set([F(0)] + [t for t in T]))
    maxT = max(T)
    # extend one dummy top so last band closes at maxT
    print(f"\n=== {name}  N={n} m={m} D={D} L={L} Gamma={Gamma} maxT={maxT} ===")
    print("  s(band lo) | |H_s| |  dB  dM  sigma |   I5(s)          |  band width")
    Phi5 = F(0)
    minI5 = None
    minPhi5 = F(0)
    running_min_Phi = F(0)
    # bands between consecutive distinct load levels, using lower endpoint s as representative
    for k in range(len(levs) - 1):
        s = levs[k]
        width = levs[k + 1] - levs[k]
        Hset = set(v for v in range(n) if T[v] > s)
        if not Hset:
            continue
        h = len(Hset)
        dB, dM = boundary(n, adj, side, Hset)
        sigma = dB - dM
        I5 = 5 * (L - 2 * s) * h - N * sigma
        Phi5 += I5 * width
        if minI5 is None or I5 < minI5:
            minI5 = I5
        if Phi5 < running_min_Phi:
            running_min_Phi = Phi5
        flag = " <-- I5<0" if I5 < 0 else ""
        print(f"  {str(s):>10} | {h:5} | {dB:3} {dM:3} {str(sigma):>4} | {str(I5):>16} | {str(width):>6}{flag}")
    print(f"  ==> min pointwise I5 = {minI5}   (negative pointwise means pure per-level FAILS)")
    print(f"  ==> Phi5(top) = {Phi5}  (= 5*sum a(L-a) - N*(TVB-TVM) at tau=maxT, must be >=0)")
    print(f"  ==> min running prefix Phi5(tau) = {running_min_Phi}  (LOAD-PSC-5 prefix, must be >=0)")


def main():
    for L in (8, 12, 16, 20):
        n, edges, side, _ = build_two_lane(L)
        probe(f"two-lane-L{L}", n, adj_of(n, edges), side)
    for Ll, k, gap in [(12, 4, 6), (14, 4, 8)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _bad = build_k_lane(Ll, k, bad)
        probe(f"klane-L{Ll}k{k}", n, adj_of(n, edges), side)


if __name__ == "__main__":
    main()
