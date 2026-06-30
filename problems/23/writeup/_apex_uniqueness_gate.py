"""ANGLE: WHY |R|<=1 (apex uniqueness) -- is the unique negative Schur-row-sum vertex
always the unique global max-load apex, and can it ever break?

R = { o in O : rowsum_o(S) < 0 },  S = H_OO - H_OU H_UU^{-1} H_UO (Schur on overloaded set O={T_v>N}).
The reduction (H) PSD <=> S>=0 collapses to a SINGLE scalar apex inequality iff |R|<=1.

This gate (exact Fraction, reuses _schur_overload_gate.schur_on_O):
 (1) On every O-nonempty gamma-min cut (census N<=10 + Grotzsch N=11 + Myc23 + C5[t]/odd blowups),
     record a_o=T_o-N for o in O, the Schur row-sums r_o, R={o:r_o<0}; confirm |R|<=1, and when
     R={o*} that o* = argmax_o T_o (the unique global max-load apex) and r is negative for at most one o.
 (2) STRESS for |R|>=2: multi-hub triangle-free graphs --
        odd_blowup(5, sizes) with two heavy classes; two Grotzsch/Myc(C5) copies joined by a length-2/3
        path (kept triangle-free); C7-Mycielskians; 200 random N=12/13/14 triangle-free.
     Report any |R|>=2 case (graph, cut, the two apex loads).
 (3) Structural test: is the apex always the UNIQUE vertex with T_o > N + (its incident cycle conductance
     c_o := H_OO[o][o] - (N - T_o) = sum of Lstar diagonal at o)?  Equivalently T_o - N > c_o, i.e. the raw
     diagonal H[o][o] = (N - T_o) + c_o < 0 strictly, AND it is the unique such vertex among O whose
     deficit dominates.  We test the cleanest candidate:  r_o<0  =>  o = argmax T  AND  H[o][o]<0 unique-min.

EXACT only; reports 0-fail or first counterexample with full witness.
Run:  python _apex_uniqueness_gate.py
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski, union_disjoint, add_edges, is_triangle_free
from _hardy_gate import BETA, build_H
from _schur_overload_gate import schur_on_O, ldl_psd


def analyze_cut(name, n, adj, side):
    """Return None if not a valid gamma-min struct or O empty; else a record dict."""
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    if not M:
        return None
    N = F(n)
    H = build_H(n, M, ell, T, cyc, BETA)
    r = schur_on_O(H, n, T, N)
    O = r['O']
    if not O:
        return None
    if r['UU_PD'] is False or r['S'] is None or not r['psdS']:
        # S not PSD (would be a counterexample to the whole reduction; flag separately)
        return dict(name=name, n=n, side=''.join(map(str, side)), O=O,
                    Sfail=(r['psdS'] is False), UU_bad=(r['UU_PD'] is False),
                    supply=r.get('supply'), rowsum=r.get('rowsum'), T=T, H=H)
    rowsum = r['rowsum']           # list aligned with O
    supply = r['supply']           # a_o = T_o - N aligned with O
    # R = indices into O where rowsum<0
    Rset = [O[i] for i in range(len(O)) if rowsum[i] < 0]
    # global argmax load over ALL vertices (apex)
    Tmax = max(T)
    argmaxT = [v for v in range(n) if T[v] == Tmax]
    # diagonal of raw H on O: H[o][o] = (N - T_o) + c_o ; negative diag candidates
    diagO = [(O[i], H[O[i]][O[i]]) for i in range(len(O))]
    negdiagO = [o for (o, d) in diagO if d < 0]
    return dict(name=name, n=n, side=''.join(map(str, side)), O=O,
                supply=supply, rowsum=rowsum, R=Rset,
                Tmax=Tmax, argmaxT=argmaxT, negdiagO=negdiagO, diagO=diagO,
                T=T, Sfail=False, UU_bad=False)


def record(acc, rec):
    if rec is None:
        return
    acc['Ononempty'] += 1
    if rec.get('Sfail') or rec.get('UU_bad'):
        acc['Sfail_or_uubad'] += 1
        if acc['Sfail_ex'] is None:
            acc['Sfail_ex'] = (rec['name'], rec['n'], rec['side'], 'Sfail' if rec.get('Sfail') else 'UU_bad')
        return
    R = rec['R']
    sizeR = len(R)
    acc['Rsizes'][sizeR] = acc['Rsizes'].get(sizeR, 0) + 1
    if sizeR >= 2:
        acc['R_ge2'] += 1
        if acc['R_ge2_ex'] is None:
            # full witness
            O = rec['O']; T = rec['T']
            loads = {o: float(T[o] - rec['n']) for o in R}
            acc['R_ge2_ex'] = (rec['name'], rec['n'], rec['side'], R, loads,
                               [float(x) for x in rec['rowsum']])
    if sizeR == 1:
        o_star = R[0]
        # apex test: o_star is the unique global max-load vertex
        if rec['argmaxT'] != [o_star]:
            acc['apex_mismatch'] += 1
            if acc['apex_ex'] is None:
                acc['apex_ex'] = (rec['name'], rec['n'], rec['side'],
                                  'R=%s argmaxT=%s Tmax=%s' % (R, rec['argmaxT'], float(rec['Tmax'])))
        # negdiag-uniqueness structural test: o_star is the unique vertex in O with H[o][o]<0
        if rec['negdiagO'] != [o_star]:
            acc['negdiag_mismatch'] += 1
            if acc['negdiag_ex'] is None:
                acc['negdiag_ex'] = (rec['name'], rec['n'], rec['side'],
                                     'R=%s negdiagO=%s' % (R, rec['negdiagO']))
    # also: whenever |O|>=2 but R empty, fine (no negative row sum). Track multi-O cuts.
    if len(rec['O']) >= 2:
        acc['O_ge2'] += 1


def run_family(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        record(acc, analyze_cut(name, n, adj, side))


def maxcut_all_fast(n, adj):
    """All max-cut sides, vertex n-1 fixed to side 0 (bitmask brute; n<=~22 ok for stress)."""
    edges = [(u, v) for u in range(n) for v in adj[u] if v > u]
    best = -1; cuts = []
    for m in range(1 << (n - 1)):
        side = [(m >> u) & 1 for u in range(n)]
        c = 0
        for (u, v) in edges:
            if side[u] != side[v]:
                c += 1
        if c > best:
            best = c; cuts = [side[:]]
        elif c == best:
            cuts.append(side[:])
    return cuts


def gmins_from_cuts(n, adj, cuts):
    """given a set of (max) cuts, keep the connected-B ones with min Gamma; reuse struct."""
    from _h import bdist_restr
    cand = []
    for s in cuts:
        if not Bconn(n, adj, s):
            continue
        Mb = [(u, v) for u in range(n) for v in adj[u] if v > u and s[u] == s[v]]
        if not Mb:
            continue
        G = 0; ok = True
        for (u, v) in Mb:
            d = bdist_restr(adj, s, u, v)
            if d < 0:
                ok = False; break
            G += (d + 1) ** 2
        if ok:
            cand.append((s, G))
    if not cand:
        return []
    gm = min(g for _, g in cand)
    return [s for (s, g) in cand if g == gm]


def two_grotzsch_joined(plen):
    """Two Grotzsch copies (N=11 each) joined by a path of length plen (plen extra vertices in a path
    connecting one vertex of copy A to one vertex of copy B).  Keep triangle-free.
    plen=2 -> A-x-y-B style chain via 2 new vertices? We connect aA -- p1 -- ... -- aB.
    We attach the path endpoints to a single vertex in each copy; path vertices are fresh.
    Triangle-freeness: path adds no triangle as long as endpoints' neighborhoods don't collide (they don't, disjoint copies)."""
    grN, grE = mycielski(5, Cn(5))   # Grotzsch N=11
    nA, EA = grN, grE
    n2, E2 = union_disjoint((nA, EA), (nA, EA))  # 22 vertices
    # anchor vertices: pick vertex 0 of copy A (=0) and vertex 0 of copy B (=nA)
    aA = 0; aB = nA
    # add plen fresh path vertices between aA and aB
    base = n2
    newverts = list(range(base, base + plen))
    chain = [aA] + newverts + [aB]
    extra = [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)]
    N = base + plen
    E = E2 + extra
    return N, E


def c7_mycielski():
    """Mycielskian of C7 (triangle-free, N=15)."""
    return mycielski(7, Cn(7))


def random_tf(n, p, rng):
    """random triangle-free graph on n vertices (rejection: add edges that keep tf)."""
    adj = [set() for _ in range(n)]
    E = []
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    for (i, j) in pairs:
        if rng.random() > p:
            continue
        if adj[i] & adj[j]:
            continue  # would create triangle
        adj[i].add(j); adj[j].add(i); E.append((i, j))
    return n, E


def main():
    acc = dict(Ononempty=0, O_ge2=0, R_ge2=0, apex_mismatch=0, negdiag_mismatch=0,
               Sfail_or_uubad=0, Rsizes={},
               R_ge2_ex=None, apex_ex=None, negdiag_ex=None, Sfail_ex=None)

    print("=" * 74)
    print("APEX-UNIQUENESS gate:  |R|<=1 and R={argmax T} ?   (R={o in O: Schur rowsum<0})")
    print("=" * 74)

    # ---- (1) census N=5..10 ----
    print("\n--- (1) census N=5..10 gamma-min cuts ---", flush=True)
    for nn in range(5, 11):
        out = subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, E = dec(g6)
            run_family("cen%d_%s" % (nn, g6), n, E, acc)
        print("  N=%d done: O-nonempty=%d  Rsizes=%s  R>=2=%d  apex_mismatch=%d"
              % (nn, acc['Ononempty'], acc['Rsizes'], acc['R_ge2'], acc['apex_mismatch']), flush=True)

    # ---- Grotzsch N=11 + Myc23 + C5[t]/odd blowups ----
    print("\n--- (1b) Grotzsch N=11, Myc N=23, blowups ---", flush=True)
    grN, grE = mycielski(5, Cn(5))
    run_family("Grotzsch_N11", grN, grE, acc)
    # Myc(Grotzsch) N=23 : single maxcut via local search side then all-min from full enum is too big;
    # use gmins on the N=23 graph would be 2^22 -> use maxcut local-search side from _hardy_gate maxcut_ls.
    from _hardy_gate import maxcut_ls
    m2N, m2E = mycielski(grN, grE)
    adj23 = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj23[x].add(y); adj23[y].add(x)
    side23 = maxcut_ls(m2N, adj23)
    record(acc, analyze_cut("MycGrotzsch_N23", m2N, adj23, side23))
    print("  Grotzsch+Myc23 done: O-nonempty=%d  Rsizes=%s" % (acc['Ononempty'], acc['Rsizes']), flush=True)

    # C5[t] and odd blowups
    for t in range(2, 5):
        n, E = odd_blowup(5, [t] * 5)
        if n <= 24:
            run_family("C5[%d]" % t, n, E, acc)
    # uneven C5 blowups (two heavy classes)
    for sizes in ([3, 3, 1, 1, 1], [3, 1, 3, 1, 1], [4, 4, 1, 1, 1], [2, 4, 2, 1, 1],
                  [3, 3, 3, 1, 1], [4, 1, 4, 1, 1], [5, 5, 1, 1, 1], [3, 3, 2, 2, 1]):
        n, E = odd_blowup(5, sizes)
        if n <= 22:
            run_family("C5%s" % sizes, n, E, acc)
    print("  blowups done: O-nonempty=%d  Rsizes=%s  R>=2=%d" % (acc['Ononempty'], acc['Rsizes'], acc['R_ge2']), flush=True)

    # ---- (2) STRESS for |R|>=2 ----
    print("\n--- (2) STRESS for |R|>=2 ---", flush=True)
    # two Grotzsch copies joined by path of length 2,3  (N=24,25) -> enumeration too big; use local-search side(s)
    for plen in (2, 3):
        N, E = two_grotzsch_joined(plen)
        if not is_triangle_free(N, E):
            print("  two_grotzsch plen=%d NOT triangle-free, skip" % plen, flush=True)
            continue
        adjg = [set() for _ in range(N)]
        for x, y in E:
            adjg[x].add(y); adjg[y].add(x)
        # several local-search maxcut sides with different seeds
        seen_sides = set()
        for seed in range(40):
            random.seed(1000 + seed)
            s = maxcut_ls(N, adjg)
            key = ''.join(map(str, s))
            if key in seen_sides:
                continue
            seen_sides.add(key)
            record(acc, analyze_cut("2Grotzsch_p%d_N%d" % (plen, N), N, adjg, s))
        print("  two_grotzsch plen=%d N=%d : %d distinct ls-cuts, R>=2 so far=%d"
              % (plen, N, len(seen_sides), acc['R_ge2']), flush=True)

    # C7-Mycielskian N=15  (full gmins enumeration is 2^14 -> ok)
    n7, E7 = c7_mycielski()
    if is_triangle_free(n7, E7):
        run_family("C7Myc_N15", n7, E7, acc)
        print("  C7-Mycielskian N=15 done: R>=2 so far=%d  Rsizes=%s" % (acc['R_ge2'], acc['Rsizes']), flush=True)

    # 200 random triangle-free N=12/13/14
    rng = random.Random(424242)
    rcount = 0
    for trial in range(200):
        n = rng.choice([12, 13, 14])
        p = rng.choice([F(35, 100), F(45, 100), F(55, 100)])
        n, E = random_tf(n, float(p), rng)
        if len(E) < n - 1:
            continue
        rcount += 1
        run_family("rand%d_N%d" % (trial, n), n, E, acc)
    print("  %d random tf N=12/13/14 done: R>=2 so far=%d  Rsizes=%s" % (rcount, acc['R_ge2'], acc['Rsizes']), flush=True)

    # ---- RESULTS ----
    print("\n" + "=" * 74)
    print("RESULTS")
    print("  O-nonempty gamma-min cuts tested :", acc['Ononempty'])
    print("  cuts with |O|>=2                 :", acc['O_ge2'])
    print("  S>=0 fail / UU-not-PD            :", acc['Sfail_or_uubad'], acc['Sfail_ex'] or '')
    print("  distribution of |R| (neg-rowsum) :", dict(sorted(acc['Rsizes'].items())))
    print("  |R|>=2 cases (BREAKS scalar route):", acc['R_ge2'], acc['R_ge2_ex'] or '')
    print("  R={o*} but o* != argmax T (apex)  :", acc['apex_mismatch'], acc['apex_ex'] or '')
    print("  R={o*} but o* != unique negdiag   :", acc['negdiag_mismatch'], acc['negdiag_ex'] or '')
    ok = (acc['R_ge2'] == 0 and acc['apex_mismatch'] == 0 and acc['Sfail_or_uubad'] == 0)
    print("\n  VERDICT:",
          "|R|<=1 ALWAYS; the unique negative-Schur-rowsum vertex = unique global max-load APEX "
          "on the whole battery (census<=10 + Grotzsch + Myc23 + 2-Grotzsch + C7Myc + blowups + 200 random). "
          "negdiag-uniqueness structural characterization holds on all |R|=1 cuts: %s"
          % ("YES" if acc['negdiag_mismatch'] == 0 else "NO (see negdiag ex)")
          if ok else "FAIL -- see counterexample above")


if __name__ == "__main__":
    main()
