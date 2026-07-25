"""audit_Q3_table.py -- rebuild the P2.3 band table and the P2.5/b.7 BCL band table
from MY OWN scans (audit_*_scan.tsv), in exact Fractions.  Cross-check against
the pass-2 tables in Q3.md.
"""
from fractions import Fraction as F
import glob, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
FILES = ['audit_tf9_scan.tsv', 'audit_tf10_scan.tsv', 'audit_tf11_scan.tsv'] + \
        ['audit_mtf%d_scan.tsv' % k for k in range(9, 16)]

rows = []
for fn in FILES:
    with open(fn) as f:
        for line in f:
            g6, n, m, bip, dist = line.split('\t')
            n, m, bip, dist = int(n), int(m), int(bip), int(dist)
            rows.append((g6.strip(), n, m, bip, dist, fn))
print("total exact data points:", len(rows))

BANDS = [(F(0), F(0)), (F(0), F(1, 100)), (F(1, 100), F(1, 50)), (F(1, 50), F(3, 100)),
         (F(3, 100), F(1, 25)), (F(1, 25), F(1, 20)), (F(1, 20), F(3, 50)),
         (F(3, 50), F(2, 25)), (F(2, 25), F(1, 10)), (F(1, 10), F(3, 20)), (F(3, 20), F(10))]

print("\n%-22s %8s %12s %12s %14s  %s" % ("band of d=dist/N^2", "#pts", "max psi", "deficit", "max R", "witness"))
psi_ge = []
allmaxR = F(0); allmaxRw = None
for (lo, hi) in BANDS:
    sel = []
    for (g6, n, m, bip, dist, fn) in rows:
        d = F(dist, n * n)
        if (lo == hi == 0 and d == 0) or (lo != hi and lo < d <= hi):
            sel.append((g6, n, m, bip, dist))
    if not sel:
        continue
    mpsi = max(F(b, n * n) for (g, n, m, b, dd) in sel)
    wpsi = [g for (g, n, m, b, dd) in sel if F(b, n * n) == mpsi][0]
    mR = F(0); wR = None
    for (g, n, m, b, dd) in sel:
        den = n * n - 25 * b
        if den <= 0:
            print("   !!! psi >= 1/25 with d>0:", g, n, m, b, dd)
            continue
        r = F(25 * dd, den)
        if r > mR:
            mR = r; wR = (g, n, m, b, dd)
    if mR > allmaxR:
        allmaxR = mR; allmaxRw = wR
    print("%-22s %8d %12s %12s %14s  %s" % ("(%s,%s]" % (lo, hi), len(sel), mpsi, F(1, 25) - mpsi, mR, wR))

print("\nGLOBAL max R over the corpus:", allmaxR, "=", float(allmaxR), "witness", allmaxRw)

# psi >= 1/25 points
eq = [(g, n, m, b, dd) for (g, n, m, b, dd, fn) in rows if F(b, n * n) >= F(1, 25)]
print("\npoints with psi >= 1/25:", len(eq))
for e in eq:
    print("   ", e, " psi =", F(e[3], e[1] ** 2), " dist =", e[4])

# a(N)
print("\na(N) from the corpora (max bip):")
for n in range(9, 16):
    vals = [b for (g, nn, m, b, dd, fn) in rows if nn == n]
    print("   N=%d  max bip = %d   (N^2/25 = %s)" % (n, max(vals), F(n * n, 25)))

# BCL density bands, |E| / C(n,2)
print("\nBCL band measurement (density = |E|/C(N,2)):")
lo_t, hi_t = F(2486, 10000), F(3197, 10000)
groups = {'open band': [], 'above 0.3197': [], 'below 0.2486': []}
for (g6, n, m, bip, dist, fn) in rows:
    dens = F(2 * m, n * (n - 1))
    if dens > hi_t:
        groups['above 0.3197'].append((g6, n, m, bip, dist))
    elif dens < lo_t:
        groups['below 0.2486'].append((g6, n, m, bip, dist))
    else:
        groups['open band'].append((g6, n, m, bip, dist))
for k, v in groups.items():
    if not v:
        continue
    mm = max(F(b, n * n) for (g, n, m, b, dd) in v)
    w = [(g, n, m, b, dd) for (g, n, m, b, dd) in v if F(b, n * n) == mm][0]
    print("   %-14s #pts %6d   max bip/N^2 = %-10s = %.6f   witness %s" % (k, len(v), mm, float(mm), w))

# density of C13(1,5) and of its blow-ups (asymptotic normalisation)
print("\nC13(1,5): |E|/C(13,2) =", F(26, 78), "=", float(F(26, 78)))
print("C13(1,5)[t] as t->infinity: |E|/C(13t,2) ->", F(2 * 26, 169), "=", float(F(52, 169)),
      "  (BCL upper threshold 0.3197)")
print("  => the blow-up family of C13(1,5) lies", "INSIDE the open BCL band" if F(52, 169) < hi_t else "in the settled range")
