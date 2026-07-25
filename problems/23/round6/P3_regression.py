"""P3_regression.py -- MANDATORY regression of every new rule claimed in P3.md against
round5/claude_witness_regression.py, plus the Vega lifts of those witnesses.

Three things are checked.

 (R1) The circle-side specialisation of the new family.  My family is
         ARCPLUS = { A u T : A a cyclic arc of the Gamma-circle, T a subset of the <=8 special
                             vertices x,y,a,b,c,u,v,w }.
      On a pure circle graph (no special vertices) ARCPLUS degenerates to the full arc family, so
      it must pass check_rule.  Run explicitly, not assumed.

 (R2) The EXACTNESS claim "arc cuts contain a minimum cut" on every recorded witness:
      arcbound(x) == min over ALL 2^(m-1) cuts.  A single witness with a strict gap would kill it.

 (R3) The Vega lift: for every witness whose circle length m is of the form 3i-1 (so that Gamma_m
      is the Andrasfai graph Gamma_i sitting inside a Vega graph), put the witness weights on the
      circle part of each of the four Vega graphs on Gamma_i and 0 on the specials, then check
      (a) ARCPLUS min <= 1/25, (b) ARCPLUS min == true bip.
"""
import sys, os, itertools
from fractions import Fraction as F

sys.path.insert(0, os.path.abspath(r'E:\Projects\ErdosProblems\problems\23\round5'))
from claude_witness_regression import WITNESSES, check_rule, gamma, mono, arcbound  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import P3_vega as V  # noqa: E402


def true_min_all_cuts(m, adj, x):
    best = None
    for mask in range(1 << (m - 1)):
        inA = [bool((mask >> t) & 1) for t in range(m)]
        v = mono(m, adj, x, inA)
        if best is None or v < best:
            best = v
    return best


def vega_arcplus_min(G, order, i, w):
    """min over ARCPLUS of the monochromatic mass, exactly (Fractions)."""
    L = 3 * i - 1
    circ = [t for t in order if isinstance(t, int)]
    spec = [t for t in order if isinstance(t, str)]
    E = [(a, b) for a, b in G.edges()]
    best = None
    for s in range(1, L + 1):
        for ln in range(L + 1):
            A = set()
            for t in range(ln):
                p = (s - 1 + t) % L + 1
                if p in G:
                    A.add(p)
            for mask in range(1 << len(spec)):
                S = set(A)
                for t, sv in enumerate(spec):
                    if (mask >> t) & 1:
                        S.add(sv)
                val = sum(w[a] * w[b] for a, b in E if (a in S) == (b in S))
                if best is None or val < best:
                    best = val
    return best


def vega_true_bip(G, order, w):
    V_ = [t for t in order if w[t] > 0]
    E = [(a, b) for a, b in G.edges() if w[a] > 0 and w[b] > 0]
    n = len(V_)
    best = None
    for mask in range(1 << max(0, n - 1)):
        S = {V_[t] for t in range(n) if (mask >> t) & 1}
        val = sum(w[a] * w[b] for a, b in E if (a in S) == (b in S))
        if best is None or val < best:
            best = val
    return best if best is not None else F(0)


def main():
    print('=' * 100)
    print('(R1) circle-side specialisation of ARCPLUS = the full arc family')
    print('=' * 100)
    bad = check_rule(lambda m, adj, x: arcbound(m, adj, x), 'ARCPLUS|circle = full arc family')
    print()
    print('=' * 100)
    print('(R2) EXACTNESS: is arcbound == min over ALL cuts on every recorded witness?')
    print('=' * 100)
    gaps = []
    for wname, m, w, why in WITNESSES:
        adj = gamma(m)
        q = sum(w)
        x = [F(wi, q) for wi in w]
        ab = arcbound(m, adj, x)
        tm = true_min_all_cuts(m, adj, x)
        tag = 'EXACT' if ab == tm else '*** GAP ***'
        print('  %-26s m=%3d  arcbound=%-10s  true min over all cuts=%-10s  %s'
              % (wname, m, str(ab), str(tm), tag))
        if ab != tm:
            gaps.append(wname)
    print('  exactness of the arc family on the regression set:',
          'HOLDS on all %d witnesses' % len(WITNESSES) if not gaps else 'FAILS on ' + ','.join(gaps))
    print()
    print('=' * 100)
    print('(R3) Vega lift of every witness whose m = 3i-1')
    print('=' * 100)
    anyfail = False
    for wname, m, w, why in WITNESSES:
        if (m + 1) % 3:
            print('  %-26s m=%3d  skipped (m is not 3i-1, no Vega graph on this circle)' % (wname, m))
            continue
        i = (m + 1) // 3
        if i < 2:
            continue
        q = sum(w)
        fam, _ = V.vega_family(i)
        for name, G, _wt in fam:
            order = V.canon_order(G)
            wt = {}
            ok = True
            for t in order:
                if isinstance(t, int):
                    wt[t] = F(w[t - 1], q)
                else:
                    wt[t] = F(0)
            tot = sum(wt.values())
            if tot == 0:
                continue
            ap = vega_arcplus_min(G, order, i, wt)
            tb = vega_true_bip(G, order, wt)
            le = ap <= F(1, 25)
            ex = (ap == tb)
            if not le or not ex:
                anyfail = True
            print('  %-22s on %-12s  ARCPLUSmin=%-12s (%.6f)  trueBip=%-12s  <=1/25:%-5s exact:%s'
                  % (wname, name, str(ap), float(ap), str(tb), le, ex))
    print('  Vega lift:', 'ALL PASS' if not anyfail else '*** FAILURE ***')


if __name__ == '__main__':
    main()
