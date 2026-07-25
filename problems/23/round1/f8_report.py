import re, sys
from fractions import Fraction

fn = sys.argv[1] if len(sys.argv) > 1 else 'f8_fam_heur.txt'
key = sys.argv[2] if len(sys.argv) > 2 else 'bipUB'
top = int(sys.argv[3]) if len(sys.argv) > 3 else 30

names = {}
try:
    for l in open('f8_fam_names.txt'):
        a = l.rstrip('\n').split('\t')
        names.setdefault(a[0], a[1])
except FileNotFoundError:
    pass

rows = []
pat = re.compile(r'(\S+) n=(\d+) m=(\d+) (?:bipUB|bip)=(\d+) ratio=\S+ (\S+)')
for l in open(fn):
    mm = pat.match(l)
    if mm:
        g6, n, m, b, r = mm.group(1), int(mm.group(2)), int(mm.group(3)), int(mm.group(4)), float(mm.group(5))
        rows.append((r, g6, n, m, b))
rows.sort(reverse=True)
print(f'TOP {top} by {key}/N^2   (file {fn}, {len(rows)} graphs)')
for r, g6, n, m, b in rows[:top]:
    fr = Fraction(b, n * n)
    print(f'  {r:.7f} = {fr}   n={n:3d} m={m:4d} {key}={b:4d}   {names.get(g6,"?")[:44]:44s} {g6[:46]}')
print()
print('count ratio > 1/25   :', sum(1 for r in rows if r[0] > 0.04))
print('count ratio > 0.0380 :', sum(1 for r in rows if r[0] > 0.038))
print('count ratio > 0.0350 :', sum(1 for r in rows if r[0] > 0.035))
