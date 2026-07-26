"""R9: the families the brief asked to search - Andrasfai, Mycielskian, Kneser, circulants.
Exact bip (all cuts) and exact Lambda (row generation + two-sided certificate) for n <= 20."""
from fractions import Fraction as F
from itertools import combinations
from R9_oddk5_lib import *
import R9_oddk5_minor as MIN

def circ(m):        # Gamma_m : u~v iff 3*circdist(u,v) > m ;  And(k) = Gamma_{3k-1}
    return G(m, [(u, v) for u in range(m) for v in range(u+1, m)
                 if 3*min(v-u, m-(v-u)) > m])
def mycielski(g):
    n = g.n
    E = list(g.E) + [(u, n+v) for (u, v) in g.E] + [(v, n+u) for (u, v) in g.E] \
        + [(n+i, 2*n) for i in range(n)]
    return G(2*n+1, E)
def kneser(n, k):
    S = list(combinations(range(n), k))
    return G(len(S), [(i, j) for i in range(len(S)) for j in range(i+1, len(S))
                      if not (set(S[i]) & set(S[j]))])

rows = []
for k in (2, 3, 4, 5, 6, 7):
    m = 3*k-1
    rows.append((f"And({k})=Gamma_{m}", circ(m)))
rows.append(("Grotzsch = M(C5)", mycielski(Cn(5))))
rows.append(("M(C7)", mycielski(Cn(7))))
rows.append(("Kneser(6,2)", kneser(6, 2)))
rows.append(("Petersen=Kneser(5,2)", kneser(5, 2)))
print(f"{'graph':>22} {'n':>3} {'m':>4} {'og':>3} {'tf':>5} {'bip':>5} {'Lambda':>8} "
      f"{'ratio':>7} {'psi=bip/N^2':>12} {'oddK5':>6}")
for nm, g in rows:
    if g.n > 20:
        print(f"{nm:>22} {g.n:>3} {g.m:>4}   (skipped: n > 20)")
        continue
    b = bip(g)
    r = Lambda(g); verify_Lambda(g, r)
    ratio = F(b)/r['value'] if r['value'] else None
    mk = MIN.has_odd_k5_minor(g)
    print(f"{nm:>22} {g.n:>3} {g.m:>4} {str(odd_girth(g)):>3} {str(g.triangle_free()):>5} "
          f"{b:>5} {str(r['value']):>8} {str(ratio):>7} {str(F(b,g.n*g.n)):>12} {str(mk):>6}")
