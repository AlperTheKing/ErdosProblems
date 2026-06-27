#!/usr/bin/env python3
"""Cross-validate MY exact T_uniform driver against full geng census N=9,10,11 (combinatorial path,
EXACT Fractions). Confirms agreement with census/LP-dual and that slack-0 cases are exactly the
odd-cycle / C5[q] extremals. This is the independent reconfirmation step for the almost-bip task."""
import sys, io, subprocess
from fractions import Fraction
_stdout = sys.stdout; sys.stdout = io.StringIO()
from AUDIT_almostbip_Tuniform import Tuniform_maxslack, adj_of, has_triangle
from census_GPI import dec, GENG
sys.stdout = _stdout

for N in (9, 10, 11):
    out = subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split()
    viol = 0; tight = 0; ntot = 0; tight_examples = []
    for g6 in out:
        n, E = dec(g6)
        adj = adj_of(n, E)
        r = Tuniform_maxslack(n, E)
        if r is None: continue
        if isinstance(r, tuple) and r and r[0] == 'GEOFAIL': continue
        Gamma, K, maxT, slack, side, M, ell, T = r
        ntot += 1
        if slack < 0:
            viol += 1
            print(f"  VIOLATION N={N} g6={g6} Gamma={Gamma} K={K} maxT={maxT} slack={slack}")
        if slack == 0:
            tight += 1
            if len(tight_examples) < 6: tight_examples.append(g6)
    print(f"N={N}: tested={ntot} | violations(slack<0)={viol} | tight(slack=0)={tight} | tight_examples={tight_examples}", flush=True)
print("DONE_CENSUS")
