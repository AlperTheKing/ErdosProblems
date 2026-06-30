"""Exact gate for Codex's one-sided endpoint-Gamma lemma (block 361):
      b = 25*M(P)  >=  (26/27) * (DG0 + DG4)
   for every L=5 gamma-min connected-B max-cut row, where
      DG0 = g['A.dGam.v0'] (endpoint singleton {x0} flip Gamma-diff, 0 if not neutral+connected)
      DG4 = g['A.dGam.v4'] similarly for {x4}.
   gamma-min => DG0,DG4 >= 0 => RHS >= 0 => b >= 0 => L=5 unified atom.
   This is a PER-ROW inequality (not a uniform cone), so it escapes the cross-row
   Farkas dual that killed the equality certificate.

   ALL arithmetic exact Fraction. Reports first violating row with full data.
"""
import sys
from fractions import Fraction as F
from _wf_deficit_farkas import (build_rows_for_cut, collect_rows, families,
                                 odd_blowup, GEN_LABELS)
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
import subprocess

C = F(26, 27)
I0 = GEN_LABELS.index('A.dGam.v0')
I4 = GEN_LABELS.index('A.dGam.v4')

def check_rows(rows):
    """Return (nrows, viols, min_slack, min_slack_row)."""
    viols = []
    min_slack = None; msr = None
    for r in rows:
        b = r['b']; dg0 = r['g'][I0]; dg4 = r['g'][I4]
        rhs = C * (dg0 + dg4)
        slack = b - rhs            # lemma: slack >= 0
        if slack < 0:
            viols.append((r['name'], r['N'], r['f'], r['P'],
                          str(b), str(dg0), str(dg4), str(r['Gamma']),
                          [str(x) for x in r['h']]))
        if min_slack is None or slack < min_slack:
            min_slack = slack; msr = r
    return len(rows), viols, min_slack, msr

def run_family(name, n, E):
    rows = collect_rows(name, n, E)
    return check_rows(rows)

def main():
    total = 0; allviol = []; gmin = None; gmin_row = None
    # 1) families() battery (census N<=10 + theta + C5[t] + nonuniform + glued islands)
    fams = families()
    # 2) extend census to N=11 (exhaustive triangle-free connected)
    outg = subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True).stdout.split()
    for g6 in outg:
        nn, EE = dec(g6); fams.append(("cen11-%s" % g6, nn, EE))
    # 3) extra stress blow-ups (larger / lopsided C5 blow-ups, still gmins-feasible n<=12)
    for sizes in [(2,2,2,2,2),(3,1,1,1,1),(2,1,1,1,1),(3,3,2,2,2),(1,2,1,2,1)]:
        if sum(sizes) <= 12:
            nn, EE = odd_blowup(5, list(sizes)); fams.append(("stressC5%s" % (sizes,), nn, EE))

    for (name, n, E) in fams:
        nr, viols, ms, msr = run_family(name, n, E)
        total += nr
        if viols:
            allviol += viols
            print("VIOLATION in %s: %d rows" % (name, len(viols)))
            for v in viols[:3]:
                print("   ", v)
            sys.stdout.flush()
        if ms is not None and (gmin is None or ms < gmin):
            gmin = ms; gmin_row = (name, msr['N'], msr['f'], msr['P'])
    print("=" * 60)
    print("TOTAL ROWS:", total)
    print("VIOLATIONS:", len(allviol))
    print("MIN SLACK (b - 26/27*(DG0+DG4)):", str(gmin), "at", gmin_row)
    if allviol:
        print("FIRST VIOLATION:", allviol[0])
    else:
        print("LEMMA HOLDS on this battery (exact Fraction).")

if __name__ == "__main__":
    main()
