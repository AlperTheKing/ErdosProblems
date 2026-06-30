"""FOURTH probe: is R = MAJ (iff), or only R subset MAJ?  And final |R|>=2 hunt with FULL maxcut
enumeration over engineered two-hub triangle-free graphs (n<=18 so 2^(n-1) brute is feasible).

From probe3 (672 O-nonempty gamma-min cuts incl 343 with |O|>=2):
  R subset MAJ = {o: a_o > sum_{p!=o in O} a_p}, |MAJ|<=1, so |R|<=1.  0 failures.
  Saw MycC5[2,1,1,1,1]: O=[2,12], a={2:0.884, 12:2.814}, MAJ=[12] but R=[]  -> MAJ nonempty, R empty.
  => inclusion is STRICT sometimes: strict-majority is NECESSARY (for r_o<0) but maybe not SUFFICIENT.

This probe records, for every O-nonempty gamma-min cut:
  - whether MAJ nonempty while R empty (count 'MAJ_only'),
  - the GAP g_o = a_o - sum_{p!=o} a_p for the (unique) MAJ vertex, vs rowsum_o, to see what extra
    condition (beyond strict majority) flips the row sum negative -- candidate: r_o<0 needs the apex
    overload to beat majority *plus the cycle conductance it sheds into U*.
And a HARD |R|>=2 hunt: full-enumerate maxcut on engineered graphs with two symmetric heavy hubs
that are NOT tied (break the tie so both could be majority -- impossible, but verify):
   - C5 blowup [a,1,b,1,1] with a!=b both large (asymmetric two heavy non-adjacent classes), n<=18,
   - Mycielskian(odd_blowup) full-enum where mn<=18,
   - 'theta-like' two-hub: two stars' centers joined through a long even path kept triangle-free.
EXACT Fraction. Run: python _apex_uniqueness_probe4.py
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski, is_triangle_free
from _hardy_gate import BETA, build_H
from _schur_overload_gate import schur_on_O


def rec_for(name, n, adj, side):
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
    if r['S'] is None or r['rowsum'] is None:
        return None
    rowsum = r['rowsum']
    R = [O[i] for i in range(len(O)) if rowsum[i] < 0]
    a = {o: T[o] - N for o in O}
    tot = sum(a.values())
    MAJ = [o for o in O if a[o] > tot - a[o]]
    # gap per MAJ vertex and its rowsum
    info = []
    for i, o in enumerate(O):
        info.append((o, a[o], a[o] - (tot - a[o]), rowsum[i]))
    return dict(name=name, n=n, side=''.join(map(str, side)), O=O, R=R, a=a, MAJ=MAJ,
                rowsum=rowsum, info=info, psdS=r['psdS'])


def maxcut_all_brute(n, adj):
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


def gmin_sides(n, adj):
    from _h import bdist_restr
    cuts = [s for s in maxcut_all_brute(n, adj) if Bconn(n, adj, s)]
    cand = []
    for s in cuts:
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
    return [s for s, g in cand if g == gm]


def main():
    print("=" * 74)
    print("PROBE4: R vs MAJ (iff?) + hard |R|>=2 hunt via FULL maxcut enumeration (n<=18)")
    print("=" * 74)

    acc = dict(O=0, R0=0, R1=0, Rge2=0, MAJ_only=0, R_minus_MAJ=0,
               Rge2_ex=None, majonly_ex=[], notsub_ex=None)

    def feed(rec):
        if rec is None:
            return
        acc['O'] += 1
        R = rec['R']; MAJ = rec['MAJ']
        if len(R) == 0:
            acc['R0'] += 1
        elif len(R) == 1:
            acc['R1'] += 1
        else:
            acc['Rge2'] += 1
            if acc['Rge2_ex'] is None:
                acc['Rge2_ex'] = (rec['name'], rec['side'], R,
                                  {o: float(rec['a'][o]) for o in R}, [float(x) for x in rec['rowsum']])
        if not set(R) <= set(MAJ):
            acc['R_minus_MAJ'] += 1
            if acc['notsub_ex'] is None:
                acc['notsub_ex'] = (rec['name'], rec['side'], 'R=%s MAJ=%s' % (R, MAJ))
        if MAJ and not R:
            acc['MAJ_only'] += 1
            if len(acc['majonly_ex']) < 6:
                # show the majority vertex's gap and rowsum
                o = MAJ[0]
                gi = next(x for x in rec['info'] if x[0] == o)
                acc['majonly_ex'].append((rec['name'], o, float(gi[1]), float(gi[2]), float(gi[3])))

    def fam(name, n, E, full=False):
        if not is_triangle_free(n, E):
            return
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        sides = gmin_sides(n, adj) if full else (gmins(n, E)[1])
        for s in sides:
            feed(rec_for(name, n, adj, s))

    # census 8..10 again for the R-vs-MAJ relationship
    print("\n--- census 8..10 (R vs MAJ) ---", flush=True)
    for nn in range(8, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            fam("cen%d" % nn, n, E)
    grN, grE = mycielski(5, Cn(5))
    fam("Grotzsch", grN, grE)
    print("  done: O=%d R0=%d R1=%d Rge2=%d MAJ_only=%d notsub=%d"
          % (acc['O'], acc['R0'], acc['R1'], acc['Rge2'], acc['MAJ_only'], acc['R_minus_MAJ']), flush=True)

    # hard |R|>=2 hunt: full enumeration, two-hub engineered, n<=18
    print("\n--- hard |R|>=2 hunt (full maxcut enumeration, n<=18) ---", flush=True)
    fams = []
    # asymmetric two heavy non-adjacent classes in C5
    for a, b in [(3,2),(4,2),(4,3),(5,2),(3,3),(5,3)]:
        n, E = odd_blowup(5, [a, 1, b, 1, 1])
        if n <= 18:
            fams.append(("C5[%d,1,%d,1,1]" % (a, b), n, E))
    # Mycielskian of small blowups, full enum if mn<=18
    for sizes in [[2,1,1,1,1],[2,2,1,1,1],[3,1,1,1,1]]:
        bn, bE = odd_blowup(5, sizes)
        mn, mE = mycielski(bn, bE)
        if mn <= 17:
            fams.append(("Myc%s_N%d" % (sizes, mn), mn, mE))
    # two-hub through long path (kept tf): two stars K_{1,3} centers joined by even path
    def two_star_path(leg, plen):
        # star A center cA=0 leaves 1..leg ; star B center cB joined by path of plen fresh verts
        E = []
        cA = 0
        leavesA = list(range(1, 1 + leg))
        for x in leavesA: E.append((cA, x))
        nxt = 1 + leg
        path = list(range(nxt, nxt + plen)); nxt += plen
        cB = nxt; nxt += 1
        leavesB = list(range(nxt, nxt + leg)); nxt += leg
        for x in leavesB: E.append((cB, x))
        chain = [cA] + path + [cB]
        for i in range(len(chain) - 1): E.append((chain[i], chain[i+1]))
        return nxt, E
    for leg, plen in [(3,3),(4,3),(3,5)]:
        n, E = two_star_path(leg, plen)
        if n <= 18:
            fams.append(("2star_leg%d_p%d_N%d" % (leg, plen, n), n, E))

    for name, n, E in fams:
        if not is_triangle_free(n, E):
            print("  %s NOT tf, skip" % name, flush=True)
            continue
        before = (acc['O'], acc['R1'], acc['Rge2'])
        fam(name, n, E, full=True)
        print("  %-26s N=%2d : O+=%d R1+=%d Rge2+=%d"
              % (name, n, acc['O'] - before[0], acc['R1'] - before[1], acc['Rge2'] - before[2]), flush=True)

    print("\n" + "=" * 74)
    print("RESULTS")
    print("  O-nonempty cuts        :", acc['O'])
    print("  |R|=0 / 1 / >=2        :", acc['R0'], acc['R1'], acc['Rge2'])
    print("  |R|>=2 (BREAKS scalar) :", acc['Rge2'], acc['Rge2_ex'] or '(none -- |R|<=1 holds)')
    print("  R NOT subset MAJ       :", acc['R_minus_MAJ'], acc['notsub_ex'] or '(R subset MAJ always)')
    print("  MAJ nonempty but R empty (strict-maj necessary, NOT sufficient):", acc['MAJ_only'])
    print("    examples (name, apex o, a_o, gap=a_o-sum_other, rowsum_o):")
    for ex in acc['majonly_ex']:
        print("      ", ex)
    print("\n  INTERPRETATION: |R|<=1 because R subset MAJ and |MAJ|<=1 (only one vertex can hold")
    print("  strict majority of the O-overload).  Strict majority is NECESSARY for a negative Schur")
    print("  row sum; the extra slack (gap vs rowsum) is the cycle conductance the apex sheds into U.")
    ok = (acc['Rge2'] == 0 and acc['R_minus_MAJ'] == 0)
    print("  VERDICT:", "|R|<=1 STRUCTURAL (R subset MAJ, |MAJ|<=1) -- scalar one-terminal route SUFFICES."
          if ok else "FAIL")


if __name__ == "__main__":
    main()
