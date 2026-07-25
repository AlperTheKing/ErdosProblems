"""Soundness audit of the claimed reduced-pattern lists f8_rmtf_<n>.g6."""
import glob, os, sys
from audit_f8_lib import (g6dec, g6enc, edges, trifree, maximal_tf, twinfree,
                          connected, mindeg, bip_exact, canon_str, hom_exists, cayleyZ)

D = os.path.dirname(os.path.abspath(__file__))
C5 = cayleyZ(5, [1])

tot = 0
allcanon = {}
print(f"{'n':>3} {'#claimed':>8} {'TF':>4} {'maxTF':>6} {'twinfree':>9} {'conn':>5} "
      f"{'d>=3':>5} {'distinct':>9} {'bip range':>12} {'C5-colourable':>14}")
for fn in sorted(glob.glob(os.path.join(D, 'f8_rmtf_*.g6')),
                 key=lambda p: int(p.rsplit('_', 1)[1].split('.')[0])):
    n_ = int(fn.rsplit('_', 1)[1].split('.')[0])
    lines = [l.strip() for l in open(fn) if l.strip()]
    if not lines:
        print(f"{n_:>3} {0:>8}   (empty)")
        continue
    ok = dict(tf=0, mx=0, tw=0, cn=0, d3=0)
    cans, bips, c5c = set(), [], 0
    for l in lines:
        n, adj = g6dec(l)
        assert n == n_, (l, n, n_)
        ok['tf'] += trifree(n, adj)
        ok['mx'] += maximal_tf(n, adj)
        ok['tw'] += twinfree(n, adj)
        ok['cn'] += connected(n, adj)
        ok['d3'] += (mindeg(n, adj) >= 3)
        cans.add(canon_str(n, adj))
        b, m = bip_exact(n, adj)
        bips.append(b)
        c5c += hom_exists(n, adj, *C5)
    for c in cans:
        allcanon.setdefault(c, n_)
    tot += len(lines)
    print(f"{n_:>3} {len(lines):>8} {ok['tf']:>4} {ok['mx']:>6} {ok['tw']:>9} {ok['cn']:>5} "
          f"{ok['d3']:>5} {len(cans):>9} {min(bips):>5}..{max(bips):<5} {c5c:>14}")
print("total patterns:", tot, " distinct canonical forms:", len(allcanon))
