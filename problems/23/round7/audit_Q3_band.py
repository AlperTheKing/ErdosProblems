"""audit_Q3_band.py -- ADVERSARIAL test of the report's strategic conclusion
   "the open BCL band contains nothing near-extremal (max bip/N^2 = 7/225)".

The BCL thresholds are densities |E|/C(n,2).  For a BLOW-UP family G[t] both
psi = bip/N^2 and the density are computable exactly:
     bip(G[t]) = t^2 * bip(G)            (accepted base (1), blow-up identity)
     N = t*n,   |E| = t^2*|E(G)|,        density_t = 2*t*m / (n*(t*n - 1)) -> 2m/n^2 .
So every corpus graph G generates an infinite family whose psi is constant
= bip(G)/n^2 and whose density tends to 2m/n^2.  If 2m/n^2 lies strictly inside
the open band, ALL large members of the family lie inside the open band.
"""
from fractions import Fraction as F
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

FILES = ['audit_tf9_scan.tsv', 'audit_tf10_scan.tsv', 'audit_tf11_scan.tsv'] + \
        ['audit_mtf%d_scan.tsv' % k for k in range(9, 16)]
rows = []
for fn in FILES:
    for line in open(fn):
        g6, n, m, bip, dist = line.split('\t')
        rows.append((g6.strip(), int(n), int(m), int(bip), int(dist)))

LO, HI = F(2486, 10000), F(3197, 10000)
best = F(0); bw = None
for (g6, n, m, b, d) in rows:
    dens_limit = F(2 * m, n * n)                 # density of G[t] as t -> infinity
    if LO < dens_limit < HI:
        psi = F(b, n * n)
        if psi > best:
            best = psi; bw = (g6, n, m, b, d, dens_limit)
print("max psi over blow-up families whose LIMIT density is inside the open BCL band:")
print("   psi =", best, "=", float(best), " ratio to 1/25 =", float(best * 25))
print("   witness", bw)

# smallest t for which the C(n,2)-normalised density of G[t] is already inside the band
if bw:
    g6, n, m, b, d, dl = bw
    for t in range(1, 12):
        dens = F(2 * t * m, n * (t * n - 1))
        inside = LO < dens < HI
        print("   t=%2d  N=%3d |E|=%5d  density=%s=%.6f  inside band: %s  psi=%s=%.6f"
              % (t, t * n, t * t * m, dens, float(dens), inside, F(b, n * n), float(F(b, n * n))))

print()
print("report's claimed band maximum 7/225 =", float(F(7, 225)), " ratio to 1/25 =", float(F(7, 225) * 25))
print("BCL flag bound 1/23.5 =", float(F(2, 47)))
