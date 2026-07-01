"""Per-edge gradient vs flow candidates, to bound TV_B(T) and TV_M(T).

For a cut edge e=(u,v) in B, we test relationships between |T(u)-T(v)| and the
geodesic flow mu(e), and toward the endpoint bound
   5 sum_v T(L-T) >= N (TV_B(T)-TV_M(T)).

mu(e) = sum_f (ell(f)/|cyc[f]|) * (#geodesics of f through e).
sum_{e in B} mu(e) = sum_f ell(f)*(ell(f)-... )? Actually each geodesic has
ell(f) vertices => ell(f)-1 edges, all in B; so sum over B-edges of the per-f
contribution = ell(f)*(ell(f)-1)/... no: (ell(f)/|cyc|)*sum_{geo} (edges in geo)
= (ell(f)/|cyc|)*|cyc|*(ell(f)-1) = ell(f)*(ell(f)-1). So
   sum_{e in B} mu(e) = sum_f ell(f)*(ell(f)-1) = Gamma - sum_f ell(f).
Test candidates:
  (E1) |T(u)-T(v)| <= mu(e)           for e in B
  (E2) sum_{e in B}|T(u)-T(v)| <= sum_{e in B} mu(e) = Gamma - sum ell
  (E3) TV_B(T) <= 2*mu-sum ... etc.
Report failures & the max ratio |grad|/mu.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_psc50_scout import adj_of, build_two_lane, greedy_chords
from _wf_lrsbreak_0 import build_k_lane


def check(name, n, edges, side, acc):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, _cyc = st
    if not M:
        return
    T = [F(t) for t in T]
    cut = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    tvB = F(0)
    musumB = F(0)
    e1fail = 0
    for (u, v) in cut:
        g = abs(T[u] - T[v])
        me = mu.get((u, v), mu.get((v, u), F(0)))
        tvB += g
        musumB += me
        if g > me:
            e1fail += 1
            if me > 0:
                r = g / me
                if r > acc["maxr"][0]:
                    acc["maxr"] = (r, name, str(u), str(v), str(g), str(me))
            else:
                acc["maxr_infty"] += 1
    acc["e1fail"] += e1fail
    if tvB > musumB:
        acc["e2fail"].append((name, str(tvB), str(musumB)))
    acc["count"] += 1


def census(nmin, nmax, acc):
    for nn in range(nmin, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                check(f"cen{g6}", n, edges, side, acc)
        print(f"N={nn} e1fail={acc['e1fail']} e2fail={len(acc['e2fail'])}", flush=True)


def main():
    acc = {"count": 0, "e1fail": 0, "e2fail": [], "maxr": (F(0), "", "", "", "", ""), "maxr_infty": 0}
    for L in range(8, 22, 2):
        n, edges, side, _ = build_two_lane(L)
        check(f"two-lane-L{L}", n, edges, side, acc)
    for Ll, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8), (18, 5, 10), (20, 6, 10)):
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        check(f"k-lane-L{Ll}-k{k}", n, edges, side, acc)
    census(7, 10, acc)
    print("=== per-edge gradient vs flow ===")
    print(f"cuts={acc['count']}")
    print(f"(E1) |grad|<=mu(e) failures = {acc['e1fail']} (of which mu=0: {acc['maxr_infty']})")
    print(f"(E2) TV_B<=sum mu failures = {len(acc['e2fail'])}")
    print(f"max |grad|/mu (finite) = {float(acc['maxr'][0]):.4f} at {acc['maxr'][1:]}")
    if acc["e2fail"]:
        print("E2 ex:", acc["e2fail"][:5])


if __name__ == "__main__":
    main()
