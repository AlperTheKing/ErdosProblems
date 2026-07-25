import sys
from fractions import Fraction
names = {}
for l in open(sys.argv[2]):
    p = l.rstrip('\n').split('\t')
    names[p[0]] = p[1]
rows = []
for l in open(sys.argv[1]):
    p = l.split()
    if len(p) < 4 or not p[1].startswith('n='):
        continue
    g6, n, m, b = p[0], int(p[1][2:]), int(p[2][2:]), int(p[3][4:])
    rows.append((b / n ** 2, names.get(g6, '?'), n, m, b))
for r, nm, n, m, b in rows:
    print(f'{nm:28s} n={n:3d} m={m:5d} bip={b:4d}  ratio={str(Fraction(b,n*n)):>12} = {r:.7f}')
print()
print('sorted by ratio, top 12:')
for r, nm, n, m, b in sorted(rows, reverse=True)[:12]:
    print(f'  {r:.7f} {str(Fraction(b,n*n)):>10}  {nm:28s} n={n} m={m} bip={b}')
