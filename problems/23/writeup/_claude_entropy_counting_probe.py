r"""ENTROPY / COUNTING angle probe for gap#1 (Gamma<=N^2 / Ell5SupportExpansion).  2026-07-08.

Grounding for a probabilistic/entropy/double-counting attack. EXACT (Fraction) only.

Establishes and tests, on C5[t] (the extremal) + census tri-free Gamma-min cages:
 (I)   LOAD IDENTITY:  Gamma = sum_v T[v]     (T[v]=sum_e ell(e) p_e(v), p_e geodesic fraction)
 (II)  SUM-R IDENTITY: sum_v R[v] = N*Gamma - sum_v T[v]^2 ,  R[v]=N T[v]-(K2 T)[v]
       => sum_v R[v] >= 0  <=>  sum T^2 <= N*Gamma  =(with CS)=>  Gamma<=N^2.
       (Confirms R>=0 is counterfactual-strength: its S=all sum IS the conjecture.)
 (III) VERTEX-HALL (VH): for every atom set S:  sum_{e in S} ell(e)^2  <=  N * |V(S)| ,
       V(S)=union of geodesic-support VERTICES. (Gale-Hoffman feasibility of routing ell^2/atom
       to support-vertices, cap N/vertex.)  S=all instance == Gamma<=N|V_all|<=N^2.
       -> min slack, binding S; tightness at C5[t].
 (IV)  COLUMN DEGREES d(c) over ell=5 edge-supports P_e (SUNFLOWER witness): max d(c), hist.
       Tests the naive counting suff. cond. "mindeg_atom(>=4) >= maxdeg_col" for edge-Hall.
 (V)   EDGE-HALL matching: does atoms(ell=5)->P_e have an atom-saturating matching? deficiency.

Run from problems/23/writeup:  python _claude_entropy_counting_probe.py
"""
from fractions import Fraction as F
from itertools import combinations
import subprocess
from _h import dec, maxcut_all, Bconn, GENG, gmin, blow
from _codex_k2t_switch_probe import adj_from_edges
from _claude_residual_hall_gate import residuals, geos_paths


def support_vertices(adj, side, e):
    Vs = set()
    for P in geos_paths(adj, side, e[0], e[1]):
        Vs.update(P)
    return frozenset(Vs)


def support_edges(adj, side, e):
    es = set()
    for P in geos_paths(adj, side, e[0], e[1]):
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]
            es.add((min(a, b), max(a, b)))
    return frozenset(es)


def analyze(name, n, adj, side, out):
    if not Bconn(n, adj, side):
        return None
    if not any(side[a] == side[b] for a in range(n) for b in adj[a] if a < b):
        return None
    cd = residuals(n, adj, side)
    if cd is None:
        return None
    M, ell, T = cd['M'], cd['ell'], cd['T']
    Gamma = sum(ell[e] ** 2 for e in M)
    # (I) load identity
    sumT = sum(T)
    id_I = (sumT == Gamma)
    # (II) sum-R identity
    sumR = sum(cd['R'])
    sumT2 = sum(t * t for t in T)
    id_II = (sumR == F(n) * Gamma - sumT2)
    R_nonneg = all(r >= 0 for r in cd['R'])
    # global comparison
    reserve = F(n) ** 2 - Gamma          # N^2 - Gamma ; <0 == deficient (never on real graphs)
    sumT2_le_NGamma = (sumT2 <= F(n) * Gamma)
    Vall = set()
    for e in M:
        Vall |= support_vertices(adj, side, e)
    # (III) VERTEX-HALL min slack (full enumeration if few atoms)
    Ve = {e: support_vertices(adj, side, e) for e in M}
    vh_min = None; vh_binding = None
    atoms = list(M)
    if len(atoms) <= 20:
        # enumerate all nonempty subsets
        for r in range(1, len(atoms) + 1):
            for S in combinations(atoms, r):
                dem = sum(ell[e] ** 2 for e in S)
                Vs = set()
                for e in S:
                    Vs |= Ve[e]
                slack = F(n) * len(Vs) - dem     # want >=0
                if vh_min is None or slack < vh_min:
                    vh_min = slack; vh_binding = (r, len(Vs), dem)
    else:
        # too many; test S=all and single-atoms and a greedy densest subset heuristic
        cand = [tuple(atoms)] + [(e,) for e in atoms]
        for S in cand:
            dem = sum(ell[e] ** 2 for e in S)
            Vs = set()
            for e in S:
                Vs |= Ve[e]
            slack = F(n) * len(Vs) - dem
            if vh_min is None or slack < vh_min:
                vh_min = slack; vh_binding = (len(S), len(Vs), dem)
    # (IV) column degrees on ell=5 edge-supports
    atoms5 = [e for e in M if ell[e] == 5]
    Pe = {e: support_edges(adj, side, e) for e in atoms5}
    dcol = {}
    for e in atoms5:
        for c in Pe[e]:
            dcol[c] = dcol.get(c, 0) + 1
    maxdcol = max(dcol.values()) if dcol else 0
    minPe = min((len(Pe[e]) for e in atoms5), default=0)
    # (V) edge-Hall matching for ell=5 atoms (Hopcroft-Karp)
    match_ok, defic = bipartite_saturates(atoms5, Pe)
    res = dict(name=name, n=n, m=len(M), m5=len(atoms5), Gamma=Gamma, reserve=reserve,
               id_I=id_I, id_II=id_II, R_nonneg=R_nonneg, sumT2_le_NGamma=sumT2_le_NGamma,
               vh_min=vh_min, vh_binding=vh_binding, Vall=len(Vall),
               maxdcol=maxdcol, minPe=minPe, match_ok=match_ok, defic=defic,
               maxell=max(ell.values()) if ell else 0)
    out.append(res)
    return res


def bipartite_saturates(atoms, Pe):
    """Return (saturates_all_atoms, deficiency=max_S(|S|-|N(S)|) lower bound via matching)."""
    if not atoms:
        return True, 0
    # Hopcroft-Karp-ish simple augmenting-path matching
    adjm = {e: list(Pe[e]) for e in atoms}
    matchC = {}   # cut-edge -> atom
    def try_aug(e, seen):
        for c in adjm[e]:
            if c in seen:
                continue
            seen.add(c)
            if c not in matchC or try_aug(matchC[c], seen):
                matchC[c] = e
                return True
        return False
    msize = 0
    for e in atoms:
        if try_aug(e, set()):
            msize += 1
    return (msize == len(atoms)), len(atoms) - msize


def run_family(getter, out):
    for name, n, adj, side in getter():
        analyze(name, n, adj, side, out)


def c5t_family():
    for t in range(1, 6):
        n, E = blow(t)
        adj = adj_from_edges(n, E)
        best = gmin(n, adj, maxcut_all(n, adj))
        if best is None:
            continue
        yield ('C5[%d]' % t, n, adj, best[0])


def census_family(nmax):
    for nn in range(5, nmax + 1):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            yield ('cen%d' % nn, n, adj, best[0])


def summarize(tag, out):
    print("\n==== %s : %d cages ====" % (tag, len(out)))
    bad_I = [r for r in out if not r['id_I']]
    bad_II = [r for r in out if not r['id_II']]
    print("  (I) load identity Gamma=sumT : %s" % ("ALL PASS" if not bad_I else "FAIL %s" % bad_I[:2]))
    print("  (II) sumR = N*Gamma-sumT^2   : %s" % ("ALL PASS" if not bad_II else "FAIL %s" % bad_II[:2]))
    rneg = [r for r in out if not r['R_nonneg']]
    st2 = [r for r in out if not r['sumT2_le_NGamma']]
    print("  R[v]>=0 pointwise: %d/%d cages fail | sumT^2<=N*Gamma: %d/%d fail (0 expected on real=non-deficient)"
          % (len(rneg), len(out), len(st2), len(out)))
    # VH slack
    vh = [r for r in out if r['vh_min'] is not None]
    if vh:
        worst = min(vh, key=lambda r: r['vh_min'])
        nneg = sum(1 for r in vh if r['vh_min'] < 0)
        print("  (III) VERTEX-HALL min slack over tested S: worst = %s at %s (%s) | negative-slack cages: %d"
              % (worst['vh_min'], worst['name'], worst['vh_binding'], nneg))
    # sunflowers
    md = max((r['maxdcol'] for r in out), default=0)
    ex = max(out, key=lambda r: r['maxdcol']) if out else None
    print("  (IV) SUNFLOWER max column-degree d(c) over ell5 supports: %d (%s, m5=%s) | min|P_e|=%s"
          % (md, ex['name'] if ex else '-', ex['m5'] if ex else '-', min((r['minPe'] for r in out if r['m5']), default='-')))
    sun = [r for r in out if r['maxdcol'] > 4]
    print("      cages with maxdcol>4 (naive mindeg>=maxdeg suff.cond FAILS): %d/%d" % (len(sun), len(out)))
    # edge-Hall
    nomatch = [r for r in out if not r['match_ok']]
    print("  (V) EDGE-HALL ell5 atom-saturating matching: %d/%d cages FAIL to saturate (deficiency>0)"
          % (len(nomatch), len(out)))
    if nomatch:
        print("      *** UNSATURATED (Hall fails on a REAL graph => would refute Ell5SupportExpansion): %s"
              % [(r['name'], r['n'], r['defic']) for r in nomatch[:3]])
    # reserve range
    print("  reserve N^2-Gamma range: min=%s max=%s (all >=0 expected on real graphs)"
          % (min(r['reserve'] for r in out), max(r['reserve'] for r in out)))


def main():
    print("ENTROPY/COUNTING probe -- exact grounding of the load identity, VH-Hall, sunflowers, edge-Hall")
    print("=" * 100)
    out5 = []
    run_family(c5t_family, out5)
    for r in out5:
        print("  %-7s N=%2d m=%3d m5=%3d Gamma=%5d N^2=%5d reserve=%4s vhmin=%5s maxdcol=%d match=%s"
              % (r['name'], r['n'], r['m'], r['m5'], r['Gamma'], r['n'] ** 2, r['reserve'],
                 r['vh_min'], r['maxdcol'], r['match_ok']))
    summarize("C5[t] EXTREMAL", out5)
    outc = []
    run_family(lambda: census_family(10), outc)
    summarize("CENSUS tri-free Gamma-min N<=10", outc)


if __name__ == '__main__':
    main()
