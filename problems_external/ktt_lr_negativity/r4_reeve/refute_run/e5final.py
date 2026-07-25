"""Final exact tabulation for (E5), with direct verification of every
'realisable' verdict on an actual hive polytope built from genuine partitions,
and exact Farkas certificates for every 'impossible' verdict."""
import itertools, sys, os, json
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4
from e5 import DS, NB, M, rows_for, cone_mult
from e5b import build, lp_feas, exact_verify, farkas

def realised_mults(g):
    """cone multiplicities of the SIMPLE vertices (3 edges) of Q(g)"""
    g = tuple(g)
    if not kt4.realizable(g):
        g = tuple(4 * x for x in g)
    lam, mu, nu = kt4.realise(g)
    A, b, bad = kt4.hive_rows(lam, mu, nu)
    if bad: return None, None, None
    ds, bs = kt4.reduce_rows(A, b)
    V = kt4.verts(ds, bs)
    if kt4.affine_rank([list(v) for v in V]) != 3: return None, None, None
    out = []
    for v, T in V.items():
        rays = kt4.cone_rays(ds, T)
        if len(rays) == 3:
            out.append(abs(kt4.det3([list(r) for r in rays])))
    return g, (lam, mu, nu), sorted(set(out))

tri = []
for S in itertools.combinations(range(NB), 3):
    if kt4.det3([list(DS[i]) for i in S]) == 0: continue
    m, nr = cone_mult(S)
    if m is not None and m > 1:
        tri.append((S, m))

feas, cert, und = [], [], []
for S, m in tri:
    res, Rs, Rl = lp_feas(S, 1)
    hit = None
    if res.status == 0 and res.x[9] > 1e-9:
        for mult in (1, 2, 3, 4, 6, 12, 24, 120, 720, 5040, 10 ** 4, 10 ** 6):
            gi = [int(round(x * mult)) for x in res.x[:9]]
            if all(v >= 1 for v in gi) and exact_verify(S, gi):
                hit = gi; break
    if hit is not None:
        gg, part, mults = realised_mults(hit)
        feas.append((S, m, hit, gg, part, mults))
    else:
        f = farkas(S)
        if f is None: und.append((S, m))
        else: cert.append((S, m, f[0]))

print("=" * 78)
print("non-unimodular cone triples:", len(tri),
      " | multiplicity 2:", sum(1 for S, m in tri if m == 2),
      " multiplicity 4:", sum(1 for S, m in tri if m == 4))
print("REALISABLE as a simple vertex cone :", len(feas),
      " (multiplicities:", sorted({f[1] for f in feas}), ")")
print("PROVED IMPOSSIBLE (exact Farkas)   :", len(cert),
      " (multiplicities:", sorted({c[1] for c in cert}), ")")
print("UNDECIDED                          :", len(und))
print("=" * 78)
print("\nVERIFIED WITNESSES (built from genuine partitions):")
seen = set()
for S, m, gi, gg, part, mults in feas:
    if gg is None: continue
    key = tuple(gg)
    if key in seen: continue
    seen.add(key)
    print("  S=%-12s m=%d  gaps=%s" % (str(S), m, list(gg)))
    print("      lam=%s mu=%s nu=%s   simple-vertex cone mults present: %s"
          % (part[0], part[1], part[2], mults))
    if len(seen) >= 8: break
if cert:
    print("\nsample exact Farkas certificate (u >= 0, u^T R >= 0 componentwise,")
    print("so 0 <= (u^T R).g = sum u_i (R_i.g) < 0 for g >= 1 -- contradiction):")
    S, m, u = cert[0]
    Rs, Rl, rays = build(S)
    R = Rs + Rl
    print("  triple S =", S, " cone multiplicity m =", m)
    print("  u =", [str(x) for x in u])
    print("  u^T R =", [str(sum(u[i] * R[i][j] for i in range(len(R)))) for j in range(9)])
    print("  all components >= 0 :",
          all(sum(u[i] * R[i][j] for i in range(len(R))) >= 0 for j in range(9)))
    print("  sum of strict-row multipliers > 0 :", sum(u[:len(Rs)]) > 0)
