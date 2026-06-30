"""ADVERSARIAL VERIFY of route 'crossterm' (CX) for (CV). Fully independent re-implementation.
DO NOT import _cv_gate or any prior gate's struct beyond the shared primitives in _h / _satzmu_conn /
_stark1.gmins / _bdef_construct / two-lane / k-lane builders (these are the GRAPH builders, reused as the
prompt instructs). The LOAD/geodesic/struct computation here is RE-DERIVED from scratch in mystruct().

CLAIM under test:
  (CX) per bad edge f:  R_f := sum_v p_f(v) * T(v)  <=  (N+eta) * ell_f * |cyc_f|
       where p_f(v) = INTEGER count of shortest alternating geodesics of f through v,
             T(v)   = sum_g w_g p_g(v),  w_g = ell_g / |cyc_g|,
             eta    = N^2/25 - beta,  beta = |M|.
  Equivalently R_f / (ell_f * |cyc_f|) <= N + eta.
  Summing w_f*(CX) over f in a K-component c gives  w^T O_c w <= (N+eta) Gamma_c = (CV).

This gate:
  (1) Re-derives M, ell, |cyc|, p_f(v), T(v) from scratch (own BFS-geodesic enumeration).
  (2) CROSS-CHECKS its T against _satzmu_conn.struct_for_side (independent path) -- must match exactly.
  (3) CROSS-CHECKS the implication numerically: for each K-component, verifies
        w^T O_c w == sum_f w_f R_f   and   (min_f (CX margin)>=0)  ==>  (CV margin)>=0,
      and reports whether (CV) could hold while some (CX) FAILS (i.e. CX strictly stronger).
  (4) Hunts (CX) violations on the FULL battery, exact Fraction. Reports min (CX) margin, binding edge.
"""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, Bconn
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords
# import the OTHER struct purely as an independent cross-check oracle (NOT as the gate's source of truth)
from _satzmu_conn import struct_for_side as OTHER_struct, kcomponents as OTHER_kcomp

# ---------- independent geodesic enumeration (re-derived, do not call _h.geos) ----------
def my_geos(adj, side, s, t):
    """All shortest ALTERNATING (cut-edge only) paths s->t in the bipartite-boundary graph B."""
    dist = {s: 0}; layer = [s]; preds = {s: []}
    while layer:
        nxt = []
        for u in layer:
            du = dist[u]
            for v in adj[u]:
                if side[u] == side[v]:
                    continue  # only traverse B (cut) edges
                if v not in dist:
                    dist[v] = du + 1; preds[v] = [u]; nxt.append(v)
                elif dist[v] == du + 1:
                    preds[v].append(u)
        layer = nxt
    if t not in dist:
        return []
    paths = []
    def back(v, suff):
        if v == s:
            paths.append([s] + suff[::-1]); return
        for p in preds[v]:
            back(p, suff + [v])
    back(t, [])
    return paths

def mystruct(n, adj, side):
    """Independent: returns (M, ell, ncyc, pcount, T) where
       M = list of monochromatic (bad) edges (u<v),
       ell[f] = geodesic length in VERTICES (= edges+1),
       ncyc[f] = number of shortest alternating geodesics of f,
       pcount[f] = dict v -> INTEGER #geodesics of f through v,
       T[v] = sum_f (ell[f]/ncyc[f]) * pcount[f][v].
       Returns None if any bad edge has no alternating geodesic (degenerate cut)."""
    M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    if not M:
        return None
    ell = {}; ncyc = {}; pcount = {}
    T = [F(0)] * n
    for f in M:
        Ps = my_geos(adj, side, f[0], f[1])
        if not Ps:
            return None
        L = len(Ps[0])            # vertices on a shortest alternating geodesic
        # sanity: all listed geodesics have equal length
        for P in Ps:
            if len(P) != L:
                raise RuntimeError("non-uniform geodesic length")
        ell[f] = L; ncyc[f] = len(Ps)
        cnt = {}
        for P in Ps:
            for v in P:
                cnt[v] = cnt.get(v, 0) + 1
        pcount[f] = cnt
        w = F(L, len(Ps))
        for v, c in cnt.items():
            T[v] += w * c
    return M, ell, ncyc, pcount, T

# ---------- independent K-component union-find over geodesic paths ----------
def my_kcomp(n, adj, side, M):
    par = list(range(n))
    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    def uni(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: par[ra] = rb
    for f in M:
        for P in my_geos(adj, side, f[0], f[1]):
            for i in range(1, len(P)):
                uni(P[0], P[i])
    comp = {}
    for v in range(n):
        comp.setdefault(find(v), []).append(v)
    return comp, find

# ---------- the (CX) check on one cut ----------
def chk(name, n, adj, side, acc, do_crosscheck=False):
    if not Bconn(n, adj, side):
        return
    st = mystruct(n, adj, side)
    if st is None:
        return
    M, ell, ncyc, pcount, T = st
    beta = len(M)
    eta = F(n * n, 25) - F(beta)
    A = F(n) + eta                      # N + eta
    # ---- per-edge (CX) ----
    comp, find = my_kcomp(n, adj, side, M)
    cid = {v: find(v) for v in range(n)}
    for f in M:
        R_f = sum(F(c) * T[v] for v, c in pcount[f].items())   # sum_v p_f(v) T(v)
        rhs = A * F(ell[f]) * F(ncyc[f])                        # (N+eta) * ell_f * |cyc_f|
        margin = rhs - R_f                                      # >=0 means (CX) holds
        acc['ne'] += 1
        if margin < acc['minm'][0]:
            acc['minm'] = (margin, name, n, beta, f, str(ell[f]), str(ncyc[f]),
                           str(R_f), str(rhs))
        if margin < 0:
            acc['viol'] += 1
            if acc['first'] is None:
                acc['first'] = (name, n, beta, f, str(R_f), str(rhs), str(margin),
                                ''.join(map(str, side)))
    # ---- independent cross-check of the IMPLICATION: per component, w^T O_c w vs (N+eta)Gamma_c ----
    if do_crosscheck:
        # build O_c directly from pcount, w from ell/ncyc; verify sum_f w_f R_f == w^T O w and the (CV) link
        comps = {}
        for v in range(n):
            comps.setdefault(cid[v], []).append(v)
        for croot, vs in comps.items():
            Mc = [f for f in M if cid[f[0]] == croot]   # bad edges whose path lies in this comp
            if not Mc:
                continue
            w = {f: F(ell[f], ncyc[f]) for f in Mc}
            # O[f,g] = sum_v p_f(v) p_g(v)
            def Ofg(f, g):
                s = F(0)
                # iterate over smaller support
                pf = pcount[f]; pg = pcount[g]
                if len(pf) > len(pg):
                    pf, pg = pg, pf
                for v, c in pf.items():
                    if v in pg:
                        s += F(c) * F(pg[v])
                return s
            wOw = F(0)
            for f in Mc:
                for g in Mc:
                    wOw += w[f] * Ofg(f, g) * w[g]
            # sum_f w_f R_f  (R_f restricted to this comp's mass = full T since support is in comp)
            sum_wR = F(0)
            for f in Mc:
                R_f = sum(F(c) * T[v] for v, c in pcount[f].items())
                sum_wR += w[f] * R_f
            Gamma_c = sum(F(ell[f]) ** 2 for f in Mc)
            # T-based component Gamma must equal ell^2 sum (the prompt identity)
            Gamma_T = sum(T[v] for v in vs)
            S2 = sum(T[v] * T[v] for v in vs)
            cv_margin = A * Gamma_c - wOw          # (CV) in w^T O w form
            cv_margin_T = A * Gamma_T - S2          # (CV) in second-moment form
            acc['xc'] += 1
            # invariant 1: sum_f w_f R_f == w^T O w
            if sum_wR != wOw:
                acc['xc_bad_identity'].append((name, croot, str(sum_wR), str(wOw)))
            # invariant 2: Gamma_c (=sum ell^2) == Gamma_T (=sum T) -- prompt identity
            if Gamma_c != Gamma_T:
                acc['xc_bad_gamma'].append((name, croot, str(Gamma_c), str(Gamma_T)))
            # invariant 3: the two (CV) forms agree
            if cv_margin != cv_margin_T:
                acc['xc_bad_cvform'].append((name, croot, str(cv_margin), str(cv_margin_T)))
            if cv_margin < acc['cv_minm'][0]:
                acc['cv_minm'] = (cv_margin, name, n, beta, len(vs), str(Gamma_c))
            if cv_margin < 0:
                acc['cv_viol'] += 1

# ---------- cross-check our T against the OTHER independent struct ----------
def crosscheck_T(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    mine = mystruct(n, adj, side)
    other = OTHER_struct(n, adj, side)
    if mine is None and other is None:
        return
    if (mine is None) != (other is None):
        acc['T_mismatch'].append((name, "None-disagreement", mine is None, other is None))
        return
    M, ell, ncyc, pcount, T = mine
    M2, ell2, T2, mu2, cyc2 = other
    if T != T2:
        # locate first differing vertex
        diff = [(v, str(T[v]), str(T2[v])) for v in range(n) if T[v] != T2[v]]
        acc['T_mismatch'].append((name, diff[:4]))

def adj_of(n, E):
    a = [set() for _ in range(n)]
    for x, y in E:
        a[x].add(y); a[y].add(x)
    return a

def bridge(b1, b2, u, v):
    nn, E = union_disjoint(b1, b2); n1 = b1[0]
    return nn, E + [(u, n1 + v)]

def blowup(parts):
    mm = len(parts); off = [0] * (mm + 1)
    for i in range(mm):
        off[i + 1] = off[i] + parts[i]
    nn = off[mm]; EE = []
    for i in range(mm):
        j = (i + 1) % mm
        for a in range(off[i], off[i + 1]):
            for b in range(off[j], off[j + 1]):
                EE.append((min(a, b), max(a, b)))
    return nn, sorted(set(EE))

if __name__ == "__main__":
    acc = {'ne': 0, 'viol': 0, 'first': None,
           'minm': (F(10 ** 18), '', '', '', '', '', '', '', ''),
           'xc': 0, 'cv_viol': 0, 'cv_minm': (F(10 ** 18), '', '', '', '', ''),
           'xc_bad_identity': [], 'xc_bad_gamma': [], 'xc_bad_cvform': [],
           'T_mismatch': []}

    print("=== (CX) crossterm ADVERSARIAL re-verification (independent struct) ===", flush=True)

    # ---- two-lane L=8..20 ----
    for L in range(8, 21, 2):
        n, E, side, _ = build_two_lane(L)
        adj = adj_of(n, E)
        crosscheck_T("two-lane-L%d" % L, n, adj, side, acc)
        chk("two-lane-L%d" % L, n, adj, side, acc, do_crosscheck=True)
    print("  two-lane done: CXviol=%d  Tmismatch=%d" % (acc['viol'], len(acc['T_mismatch'])), flush=True)

    # ---- k-lane dense ----
    for (Ll, k, gap) in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
        bad = greedy_chords(Ll, k, gap)
        n, E, side, bad = build_k_lane(Ll, k, bad)
        adj = adj_of(n, E)
        crosscheck_T("klane-L%dk%d" % (Ll, k), n, adj, side, acc)
        chk("klane-L%dk%d" % (Ll, k), n, adj, side, acc, do_crosscheck=True)
    print("  k-lane done: CXviol=%d" % acc['viol'], flush=True)

    # ---- C5/C7/C9 blow-ups, uniform ----
    for c in (5, 7, 9):
        for t in range(1, 6):
            n, E = blowup([t] * c)
            if n > 26:
                continue
            adj, cuts = gmins(n, E)
            for s in (cuts[:2] if cuts else []):
                chk("C%d[%d]" % (c, t), n, adj, s, acc, do_crosscheck=True)

    # ---- non-uniform blow-ups ----
    for parts in [[2, 2, 2, 2, 3], [1, 5, 2, 2, 5], [1, 4, 2, 4, 2, 4, 2],
                  [3, 3, 3, 3, 2], [1, 3, 2, 2, 3], [1, 1, 1, 1, 8], [8, 1, 1, 1, 1],
                  [1, 6, 1, 6, 1], [2, 5, 1, 1, 5], [1, 7, 1, 1, 7]]:
        n, E = blowup(parts)
        if n > 30:
            continue
        adj, cuts = gmins(n, E)
        for s in (cuts[:2] if cuts else []):
            chk("nu%s" % parts, n, adj, s, acc, do_crosscheck=True)
    print("  blow-ups done: CXviol=%d  minCXmargin=%s" % (acc['viol'], float(acc['minm'][0])), flush=True)

    # ---- Grotzsch, Mycielskians, glued bridges ----
    grot = mycielski(5, Cn(5)); mycg = mycielski(grot[0], grot[1])
    cases = [("Grotzsch", grot), ("Myc(Grotzsch)", mycg),
             ("M(C7)", mycielski(7, Cn(7))), ("M(C9)", mycielski(9, Cn(9))),
             ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
             ("C9|C9", bridge((9, Cn(9)), (9, Cn(9)), 0, 0)),
             ("C5|C7", bridge((5, Cn(5)), (7, Cn(7)), 0, 0)),
             ("C5|C9", bridge((5, Cn(5)), (9, Cn(9)), 0, 0)),
             ("C7|C7", bridge((7, Cn(7)), (7, Cn(7)), 0, 0)),
             ("Grot|Grot", bridge(grot, grot, 0, 0))]
    for nm, (nn, E) in cases:
        adj, cuts = gmins(nn, E)
        for s in cuts[:3]:
            chk(nm, nn, adj, s, acc, do_crosscheck=True)
    print("  Mycielski+glued done: CXviol=%d" % acc['viol'], flush=True)

    # ---- census geng -tc N=7..11, ALL gamma-min cuts ----
    for nn in range(7, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        v0 = acc['viol']; t0 = len(acc['T_mismatch'])
        for g6 in outg:
            n, E = dec(g6); adj, cuts = gmins(n, E)
            for s in cuts:
                # cross-check T on first cut only (cheap, catches struct bugs)
                if s is cuts[0]:
                    crosscheck_T("cen%s" % g6, n, adj, s, acc)
                chk("cen%s" % g6, n, adj, s, acc, do_crosscheck=(nn <= 9))
        print("  census N=%d done (CXviol+%d, Tmismatch+%d)" % (nn, acc['viol'] - v0,
              len(acc['T_mismatch']) - t0), flush=True)

    # ---- REPORT ----
    print("\n  ===== RESULTS =====", flush=True)
    print("  edges (CX) tested = %d" % acc['ne'], flush=True)
    print("  (CX) violations   = %d" % acc['viol'], flush=True)
    mm = acc['minm']
    print("  MIN (CX) margin   = %s  (=%s) at name=%s N=%s beta=%s edge=%s ell=%s ncyc=%s R_f=%s rhs=%s"
          % (mm[0], float(mm[0]), mm[1], mm[2], mm[3], mm[4], mm[5], mm[6], mm[7], mm[8]), flush=True)
    if acc['first']:
        print("  FIRST (CX) violation: %s" % (acc['first'],), flush=True)
    print("  --- independent implication cross-checks ---", flush=True)
    print("  components cross-checked = %d" % acc['xc'], flush=True)
    print("  (CV) violations (w^T O w form) = %d   min (CV) margin = %s"
          % (acc['cv_viol'], float(acc['cv_minm'][0])), flush=True)
    print("  identity sum_f w_f R_f == w^T O w broken on = %d comps %s"
          % (len(acc['xc_bad_identity']), acc['xc_bad_identity'][:3]), flush=True)
    print("  Gamma_c(=sum ell^2)==Gamma_T(=sum T) broken on = %d comps %s"
          % (len(acc['xc_bad_gamma']), acc['xc_bad_gamma'][:3]), flush=True)
    print("  two (CV) forms disagree on = %d comps %s"
          % (len(acc['xc_bad_cvform']), acc['xc_bad_cvform'][:3]), flush=True)
    print("  T-cross-check mismatches vs _satzmu_conn = %d %s"
          % (len(acc['T_mismatch']), acc['T_mismatch'][:3]), flush=True)
    print("\n  === (CX) R_f <= (N+eta)*ell_f*|cyc_f| : %s ==="
          % ("HOLDS (0 viol)" if not acc['viol'] else "FAILS"), flush=True)
    print("  === implication (CX all f in c) => (CV) for c : %s ==="
          % ("CONFIRMED (identity exact, both forms agree)" if not acc['xc_bad_identity']
             and not acc['xc_bad_gamma'] and not acc['xc_bad_cvform'] else "BROKEN"), flush=True)
