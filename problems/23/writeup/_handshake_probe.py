"""Handshake probe: relate sigma_s (signed boundary of H_s) to geodesic structure.

For each bad edge f with geodesics cyc[f], ell[f], the load T(v)=sum_f ell[f] p_f(v).
Consider H_s={T>s}. A geodesic path P (a shortest B-path a..b closing bad edge f) is a
sequence of CUT edges. As we walk P, T changes; P enters/leaves H_s.

KEY: TV_B(a_tau) for a=min(T,tau) counts, per cut edge uv, |a_u - a_v|. Summed over the
geodesic edges this is a telescoping-like quantity. And the bad edges themselves (endpoints
a,b of f) contribute to TV_M.

We test the GEODESIC HANDSHAKE candidate:
  For the truncated load a=min(T,tau),
  sum_{cut uv} (a_u - a_v)^+ type ... instead we directly verify per-level:
  sigma_s = dB(H_s)-dM(H_s) counts boundary cut edges minus boundary bad edges of H_s.

CANDIDATE (max-cut local): every vertex v in H_s has cut-degree dcut(v) >= deg(v)/2, and
its boundary cut edges leaving H_s are <= dcut(v). We test the AGGREGATE bound
  dB(H_s) <= sum_{v in H_s} (dcut(v) restricted to boundary)
and see if a load-weighted version gives sigma_s <= (const)*sum_{v in H_s} something.

Actually the productive object: does each boundary CUT edge of H_s carry a geodesic that
also crosses the boundary, letting us charge dB to the load drop? Measure:
  boundary cut edges of H_s that lie on some geodesic  vs  total boundary cut edges.
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


def probe(name, n, adj, side):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    N = F(n)
    # collect geodesic edges (cut edges on some shortest geodesic) and geodesic vertices
    geo_edges = set()
    for f in M:
        for P in cyc[f]:
            for i in range(len(P) - 1):
                a, b = P[i], P[i + 1]
                geo_edges.add((min(a, b), max(a, b)))
    levs = sorted(set([F(0)] + [t for t in T]))
    print(f"\n=== {name} N={n} m={len(M)} ===")
    print("  s | h | dB | dB_on_geo dB_off_geo | dM | sig | sum_Hs dcut_boundary")
    for k in range(min(len(levs) - 1, 8)):
        s = levs[k]
        Hset = set(v for v in range(n) if T[v] > s)
        if not Hset:
            continue
        h = len(Hset)
        dB = dM = 0
        dB_geo = dB_off = 0
        for u in Hset:
            for v in adj[u]:
                if v in Hset:
                    continue
                e = (min(u, v), max(u, v))
                if side[u] != side[v]:
                    dB += 1
                    if e in geo_edges:
                        dB_geo += 1
                    else:
                        dB_off += 1
                else:
                    dM += 1
        sig = dB - dM
        print(f"  {str(s):>5} | {h:3} | {dB:3} | {dB_geo:3} {dB_off:3} | {dM:3} | {str(sig):>4}")


def main():
    for L in (8,):
        n, edges, side, _ = build_two_lane(L)
        probe(f"two-lane-L{L}", n, adj_of(n, edges), side)
    for Ll, k, gap in [(12, 4, 6)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _bad = build_k_lane(Ll, k, bad)
        probe(f"klane-L{Ll}k{k}", n, adj_of(n, edges), side)


if __name__ == "__main__":
    main()
