import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h2_redteam2 import analyze

# import the CANDS list from rt2_candidates without its reporting block
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rt2_candidates.py')).read()
src = src.split('# Filter & report')[0]
ns = {'__file__': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rt2_candidates.py')}
exec(src, ns)
CANDS = ns['CANDS']

N15 = [(name, N, edges) for (name, N, edges) in CANDS if N == 15]
for name, N, edges in N15:
    r = analyze(name, N, edges)
    if not r['triangle_free']:
        print(f"{name:30s} SKIP (triangle)")
        continue
    print(f"{name:30s} E={r['E']:2d} beta={r['beta']:2d} target={r['target']} "
          f"min_drop={r['min_drop']:2d} margin={r['margin']:+d}  {r['verdict']}")
    if r['margin'] > 0:
        print("    ARGMIN 5-set:", r['argmin'])
