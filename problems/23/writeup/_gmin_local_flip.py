"""ANGLE: exact LOCAL consequence of gamma-MINIMALITY at a vertex, vs the Hardy weight d(v)=L*_vv.

Setup (reusing shared infra; EXACT Fraction):
 - struct_for_side(n,adj,side) -> (M,ell,T,mu,cyc).  T[v]=load, cyc[f]=shortest blue geodesics for bad edge f.
 - Hardy diag d(v) := L*_{vv} = 2 * sum_f (beta_{L_f}/|cyc[f]|) * #{Q in cyc[f] : v in Q}
   (each vertex of a cycle Q has cycle-Laplacian degree 2).  (H) PSD REQUIRES diag>=0: T[v]-N <= d(v).
 - We separately MEASURE the gamma-min local content:
     * vertex type at v in a MAX cut: blue_deg(v)=#cut incident, bad_deg(v)=#uncut incident.
       Max-cut optimality => blue_deg>=bad_deg for ALL v.  v is NEUTRAL-FLIPPABLE iff blue_deg==bad_deg.
     * For a neutral-flippable v, flipping v gives another MAX cut; gamma-min => DeltaGamma(v)=Gamma(flip)-Gamma>=0.
       We compute Gamma(flip) EXACTLY (recompute all bad-edge blue-geodesic lengths on the flipped cut).
       (We do NOT assume the flipped cut is B-connected; Gamma is still sum_f L_f^2 with L_f=bad-restricted
        shortest blue-geodesic length; if some new bad edge has no blue geodesic we mark it +inf and skip.)

KEY QUESTIONS answered with exact data:
 (Q1) Hardy diag inequality  T[v]-N <= d(v)  -- does it hold at EVERY vertex, or only neutral-flippable ones?
       (this is the *necessary* diagonal condition for (H); if it can FAIL the per-vertex route is dead.)
 (Q2) Does gamma-min's neutral-flip DeltaGamma(v)>=0 give a per-vertex bound T[v]-N <= (incident cycle energy)?
       We test the candidate  T[v]-N <= DeltaGamma(v)/something? No -- we directly compare what gamma-min yields.
 (Q3) Characterize the vertices where T[v]>N (the "O" overloaded set) by their flip-type and d(v).

Battery: H?AFBo] gmin (N=9, Gamma=50), C5[2] (N=10), C5[3] (N=15 TIGHT), two census N=8/9, Myc(Grotzsch) N=23.
Run: python _gmin_local_flip.py
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
    """Exact Gamma = sum_{bad edge f} L_f^2 on the given cut, L_f = #vertices of shortest blue geodesic
       (= bad-restricted distance +1).  Returns (Gamma, ok) ; ok=False if some bad edge has no blue geodesic."""
    M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    G = F(0)
    for (u, v) in M:
        d = bdist_restr(adj, side, u, v)
        if d < 0:
            return None, False  # bad edge with no odd cycle -> not a valid competitor (skip)
        G += (d + 1) ** 2
    return G, True


def hardy_diag(n, M, ell, cyc):
    """d(v) = L*_{vv} = 2 * sum_f (beta_{L_f}/|cyc[f]|) * #{Q in cyc[f] : v in Q}  (exact rational, certified beta')."""
    d = [F(0)] * n
    for f in M:
        Qs = cyc[f]; L = ell[f]
        w = BETA[L] / len(Qs)
        for Q in Qs:
            for v in set(Q):
                d[v] += 2 * w  # cycle-Laplacian degree of any vertex on cycle Q is 2
    return d


def vertex_types(n, adj, side):
    """blue_deg, bad_deg per vertex; neutral-flippable iff equal."""
    bl = [0] * n; bd = [0] * n
    for u in range(n):
        for v in adj[u]:
            if side[u] != side[v]: bl[u] += 1
            else: bd[u] += 1
    return bl, bd


def analyze_cut(name, n, adj, side, acc, verbose=False):
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
    bl, bd = vertex_types(n, adj, side)
    G0, ok0 = gamma_of_cut(n, adj, side)
    acc['cuts'] += 1

    rows = []
    for v in range(n):
        flippable = (bl[v] == bd[v])  # neutral (max-cut-tight)
        strict = (bl[v] > bd[v])
        over = (T[v] > N)
        # Hardy diagonal inequality   T[v]-N <= d(v)
        hardy_lhs = T[v] - N          # want <= d[v]
        hardy_ok = (hardy_lhs <= d[v])
        acc['rows'] += 1
        if not hardy_ok:
            acc['hardy_fail'] += 1
            if acc['hardy_fail_ex'] is None:
                acc['hardy_fail_ex'] = (name, n, v, str(hardy_lhs), str(d[v]))
        # diag slack
        slack = d[v] - hardy_lhs
        if acc['min_diag_slack'] is None or slack < acc['min_diag_slack']:
            acc['min_diag_slack'] = slack; acc['min_diag_slack_ex'] = (name, n, v, float(slack))
        # gamma-min flip (only for neutral-flippable)
        dG = None
        if flippable:
            ns = side[:]; ns[v] ^= 1
            Gf, okf = gamma_of_cut(n, adj, side=ns)
            if okf:
                dG = Gf - G0
                acc['flip_tested'] += 1
                if dG < 0:
                    acc['flip_neg'] += 1
                    if acc['flip_neg_ex'] is None:
                        acc['flip_neg_ex'] = (name, n, v, str(dG))
                if acc['min_dG'] is None or dG < acc['min_dG']:
                    acc['min_dG'] = dG
        # tabulate over (T>N) vertices: are they neutral-flippable?
        if over:
            acc['over_total'] += 1
            if flippable: acc['over_flippable'] += 1
            if strict: acc['over_strict'] += 1
            # for over vertices test hardy on the over set explicitly
            if not hardy_ok:
                acc['over_hardy_fail'] += 1
        rows.append((v, bl[v], bd[v], flippable, over, str(T[v]), str(d[v]), str(hardy_lhs), hardy_ok, (str(dG) if dG is not None else '-')))

    if verbose:
        print(f"\n[{name}] N={n} Gamma={G0} (#bad={len(M)}) ")
        print("  v  bl bd flip over   T_v       d_v      T-N    Hok  dGamma")
        for (v, b, c, fl, ov, tv, dv, hl, hok, dg) in rows:
            print(f"  {v:2d} {b:3d}{c:3d}  {int(fl)}    {int(ov)}   {tv:>8} {dv:>9} {hl:>6}  {int(hok)}   {dg}")


def gfam(name, n, E, acc, verbose=False):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for i, side in enumerate(cuts):
        analyze_cut(name + (f"#{i}" if len(cuts) > 1 else ""), n, adj, side, acc, verbose=verbose)


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
    acc = dict(cuts=0, rows=0, hardy_fail=0, hardy_fail_ex=None, flip_tested=0, flip_neg=0,
               flip_neg_ex=None, min_dG=None, min_diag_slack=None, min_diag_slack_ex=None,
               over_total=0, over_flippable=0, over_strict=0, over_hardy_fail=0)

    # --- focused battery with verbose tables ---
    # H?AFBo] gmin (N=9, Gamma=50)
    n, E = dec("H?AFBo]")
    gfam("H?AFBo]_N9", n, E, acc, verbose=True)

    # C5[2] (N=10)
    n2, E2 = odd_blowup(5, [2, 2, 2, 2, 2])
    gfam("C5[2]_N10", n2, E2, acc, verbose=True)

    # C5[3] (N=15, TIGHT extremal)
    n3, E3 = odd_blowup(5, [3, 3, 3, 3, 3])
    gfam("C5[3]_N15_TIGHT", n3, E3, acc, verbose=True)

    # two census N=8 / N=9 graphs (first triangle-free connected with a valid gmin)
    cen_done = {8: 0, 9: 0}
    for nn in (8, 9):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            if cen_done[nn] >= 1:
                break
            n, E = dec(g6)
            before = acc['cuts']
            gfam(f"cen{nn}_{g6}", n, E, acc, verbose=True)
            if acc['cuts'] > before:
                cen_done[nn] += 1

    # Myc(Grotzsch) N=23 guardrail
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    adjm = [set() for _ in range(m2N)]
    for x, y in m2E:
        adjm[x].add(y); adjm[y].add(x)
    sidem = maxcut_ls(m2N, adjm)
    analyze_cut("MycGrotzsch_N23", m2N, adjm, sidem, acc, verbose=True)

    # --- broaden silently: census N=5..9 ALL gmin cuts, chains, blowups ---
    for nn in range(5, 10):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam(f"cen{nn}", n, E, acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(2,2,2,2,2),(3,3,3,3,3),(1,1,1,1,1)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 24:
            gfam(f"blow{sizes}", nn, EE, acc)
    grN, grE = mycielski(5, Cn(5)); gfam("Grotzsch_N11", grN, grE, acc)

    print("\n" + "=" * 70)
    print("TOTAL gmin cuts analyzed:", acc['cuts'], " vertex-rows:", acc['rows'])
    print("-" * 70)
    print("(Q1) HARDY DIAGONAL  T[v]-N <= d(v)=L*_vv  at EVERY vertex:")
    print("     FAILURES:", acc['hardy_fail'], "  first:", acc['hardy_fail_ex'])
    print("     min diagonal slack d(v)-(T-N):", acc['min_diag_slack'],
          "(float", (float(acc['min_diag_slack']) if acc['min_diag_slack'] is not None else None),
          ") at", acc['min_diag_slack_ex'])
    print("-" * 70)
    print("(Q3) OVERLOADED vertices (T[v]>N):", acc['over_total'],
          " of which neutral-flippable:", acc['over_flippable'], " strict(blue>bad):", acc['over_strict'])
    print("     overloaded vertices that VIOLATE hardy diag:", acc['over_hardy_fail'])
    print("-" * 70)
    print("(Q2) NEUTRAL-FLIP gamma-min content:")
    print("     neutral-flip DeltaGamma tested:", acc['flip_tested'], " NEGATIVE (gamma-min VIOLATION):", acc['flip_neg'],
          acc['flip_neg_ex'] or '')
    print("     min DeltaGamma over neutral flips:", acc['min_dG'])
    print("=" * 70)
    verdict_hardy = "HOLDS at every vertex" if acc['hardy_fail'] == 0 else "FAILS (per-vertex diag route needs flip-type restriction)"
    verdict_flip = "consistent (no neutral flip lowers Gamma)" if acc['flip_neg'] == 0 else "VIOLATED"
    print("VERDICT: Hardy diagonal", verdict_hardy, "| gamma-min neutral-flip", verdict_flip)


if __name__ == "__main__":
    main()
