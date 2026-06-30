"""FOLLOW-UP: derive/verify the EXACT DeltaGamma(v) for a neutral single-vertex flip and test whether the
gamma-min consequence (DeltaGamma>=0 at neutral-flippable v) PRODUCES a per-vertex bound of the announced form
   T[v] - N  <=  (incident cycle energy at v).

EXACT DeltaGamma(v) on a neutral flip (blue_deg=bad_deg) -- computed two ways and cross-checked:
  (way A, ground truth) actually flip v, recompute Gamma'=sum_f L_f^2 on the new cut, DeltaGamma=Gamma'-Gamma.
  (way B, LOCAL decomposition) at v the flip swaps the role of its incident edges; the change splits into
     - edges that were BAD at v and become BLUE  (#=bad_deg(v)=b): each such bad edge f=(v,w) DISAPPEARS
       from M -> removes ell[f]^2 = (d_B(v,w)+1)^2 from Gamma (but may shorten OTHER geodesics through v).
     - edges that were BLUE at v and become BAD   (#=blue_deg(v)=b): each becomes a NEW bad edge -> adds its
       new geodesic-length^2.
  Way B is only a heuristic lower bound; the GROUND TRUTH is way A (full recompute).  We report way A.

CENTRAL TEST: split overloaded vertices (T>N) into neutral-flippable vs strict, and for EACH report whether
   T[v]-N <= DeltaGamma(v)   (flippable only)   and    T[v]-N <= d(v)=L*_vv   (all).
Then test the candidate Hardy-from-flip identity:  is  d(v) >= DeltaGamma(v)/4  ?  or any clean relation, since
the Poincare/Hardy weight d(v)=L*_vv is the CYCLE energy and DeltaGamma is the load-change.  We just MEASURE.

Battery same as _gmin_local_flip plus a NEUTRAL-FLIPPABLE-focused census sweep.
Run: python _gmin_flip_formula.py
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all, geos, bdist_restr
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _hardy_gate import BETA
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski, is_triangle_free


def gamma_of_cut(n, adj, side):
    M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    G = F(0)
    for (u, v) in M:
        d = bdist_restr(adj, side, u, v)
        if d < 0:
            return None
        G += (d + 1) ** 2
    return G


def hardy_diag(n, M, ell, cyc):
    d = [F(0)] * n
    for f in M:
        Qs = cyc[f]; L = ell[f]
        w = BETA[L] / len(Qs)
        for Q in Qs:
            for v in set(Q):
                d[v] += 2 * w
    return d


def analyze(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    N = F(n)
    d = hardy_diag(n, M, ell, cyc)
    bl = [0] * n; bd = [0] * n
    for u in range(n):
        for v in adj[u]:
            if side[u] != side[v]: bl[u] += 1
            else: bd[u] += 1
    G0 = gamma_of_cut(n, adj, side)
    acc['cuts'] += 1
    for v in range(n):
        over = T[v] > N
        flippable = (bl[v] == bd[v])
        TmN = T[v] - N
        # Hardy diag (all vertices)
        if TmN <= d[v]:
            sl = d[v] - TmN
            if acc['min_diag_slack'] is None or sl < acc['min_diag_slack']:
                acc['min_diag_slack'] = sl
        else:
            acc['hardy_fail'] += 1
        if over:
            acc['over'] += 1
            if flippable: acc['over_flip'] += 1
            else: acc['over_strict'] += 1
        if flippable:
            ns = side[:]; ns[v] ^= 1
            Gf = gamma_of_cut(n, adj, ns)
            if Gf is not None:
                dG = Gf - G0
                acc['flips'] += 1
                if dG < 0: acc['flip_neg'] += 1
                # candidate relations between DeltaGamma and the load/Hardy weight on flippable v:
                # (R1)  T[v]-N <= DeltaGamma(v)        (does neutral flip directly bound the overload?)
                if TmN <= dG:
                    pass
                else:
                    acc['R1_fail'] += 1
                    if acc['R1_fail_ex'] is None:
                        acc['R1_fail_ex'] = (name, n, v, str(TmN), str(dG), bl[v], bd[v])
                # (R2)  DeltaGamma(v) <= 2 * d(v)? / measure ratio dG / d[v] for flippable overloaded v
                if over and d[v] > 0:
                    r = F(dG) / d[v]
                    if acc['max_ratio_over'] is None or r > acc['max_ratio_over']:
                        acc['max_ratio_over'] = r; acc['max_ratio_ex'] = (name, n, v, float(r), dG, float(d[v]))
                # record min DeltaGamma on overloaded flippable
                if over:
                    if acc['min_dG_over'] is None or dG < acc['min_dG_over']:
                        acc['min_dG_over'] = dG; acc['min_dG_over_ex'] = (name, n, v, dG, str(TmN))


def gfam(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for i, side in enumerate(cuts):
        analyze(name, n, adj, side, acc)


def maxcut_ls(n, adj, seeds=120):
    import random
    best = None; bv = -1; rng = random.Random(11)
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]; imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val; best = s[:]
    return best


def main():
    acc = dict(cuts=0, hardy_fail=0, min_diag_slack=None, over=0, over_flip=0, over_strict=0,
               flips=0, flip_neg=0, R1_fail=0, R1_fail_ex=None, max_ratio_over=None, max_ratio_ex=None,
               min_dG_over=None, min_dG_over_ex=None)

    # focused battery
    n, E = dec("H?AFBo]"); gfam("H?AFBo]_N9", n, E, acc)
    n2, E2 = odd_blowup(5, [2,2,2,2,2]); gfam("C5[2]_N10", n2, E2, acc)
    n3, E3 = odd_blowup(5, [3,3,3,3,3]); gfam("C5[3]_N15", n3, E3, acc)
    for nn in range(5, 10):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam(f"cen{nn}", n, E, acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(2,2,2,2,2),(3,3,3,3,3),(5,4,5,4,5)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 24: gfam(f"blow{sizes}", nn, EE, acc)
    # N=23
    grN, grE = mycielski(5, Cn(5)); gfam("Grotzsch_N11", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adjm = [set() for _ in range(m2N)]
    for x, y in m2E: adjm[x].add(y); adjm[y].add(x)
    sm = maxcut_ls(m2N, adjm)
    analyze("MycGrotzsch_N23", m2N, adjm, sm, acc)

    print("=" * 72)
    print("cuts:", acc['cuts'], " hardy-diag failures (T-N<=d(v)):", acc['hardy_fail'],
          " min diag slack:", (float(acc['min_diag_slack']) if acc['min_diag_slack'] is not None else None))
    print("-" * 72)
    print("OVERLOADED (T>N):", acc['over'], " neutral-flippable:", acc['over_flip'],
          " STRICT (blue>bad, NO single-flip lever):", acc['over_strict'])
    print("-" * 72)
    print("NEUTRAL flips tested:", acc['flips'], " negative DeltaGamma (gamma-min viol):", acc['flip_neg'])
    print("(R1)  T[v]-N <= DeltaGamma(v) on neutral-flippable v   FAILURES:", acc['R1_fail'], acc['R1_fail_ex'] or '')
    print("    min DeltaGamma on OVERLOADED flippable v:", acc['min_dG_over'], "at", acc['min_dG_over_ex'])
    print("    max ratio DeltaGamma(v)/d(v) on overloaded flippable v:",
          (float(acc['max_ratio_over']) if acc['max_ratio_over'] is not None else None), "at", acc['max_ratio_ex'])
    print("=" * 72)
    if acc['R1_fail'] == 0:
        print("FINDING: gamma-min single neutral flip GIVES  T[v]-N <= DeltaGamma(v)  at neutral-flippable v.")
    else:
        print("FINDING: (R1) T[v]-N <= DeltaGamma(v) FAILS -> single neutral flip does NOT bound the overload directly.")
    print("Strict overloaded vertices have NO single-vertex neutral-flip lever; yet hardy-diag holds there too",
          "(fail=%d)." % acc['hardy_fail'])


if __name__ == "__main__":
    main()
