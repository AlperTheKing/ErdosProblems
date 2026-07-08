r"""Full structural dump of C5[t] ell=5 atoms/supports (the extremal, where Hall is TIGHT + sunflower-heavy).
Goal: read off the correct non-uniform weighting/measure for a counting proof of support-expansion.
EXACT. Run from problems/23/writeup."""
from fractions import Fraction as F
from _h import maxcut_all, gmin, blow
from _codex_k2t_switch_probe import adj_from_edges
from _claude_residual_hall_gate import residuals, geos_paths


def dump(t):
    n, E = blow(t); adj = adj_from_edges(n, E)
    best = gmin(n, adj, maxcut_all(n, adj))
    side, G, M, ell = best
    print("=" * 90)
    print("C5[%d]  N=%d  |M|=%d  Gamma=%d  N^2=%d" % (t, n, len(M), G, n * n))
    # part labels: vertex i in part i//t
    part = {v: v // t for v in range(n)}
    print("side by part:")
    for p in range(5):
        vs = [v for v in range(n) if part[v] == p]
        print("   part %d = %s  sides=%s" % (p, vs, [side[v] for v in vs]))
    cd = residuals(n, adj, side); T = cd['T']
    atoms5 = [e for e in M if ell[e] == 5]
    print("ell=5 atoms: %d" % len(atoms5))
    Vcol = {}; Ecol = {}
    for e in atoms5:
        Ps = geos_paths(adj, side, e[0], e[1])
        Vs = set(); Es = set()
        for P in Ps:
            Vs.update(P)
            for i in range(len(P) - 1):
                a, b = P[i], P[i + 1]; Es.add((min(a, b), max(a, b)))
        for v in Vs: Vcol[v] = Vcol.get(v, 0) + 1
        for c in Es: Ecol[c] = Ecol.get(c, 0) + 1
        print("  atom %s parts(%d,%d) #geo=%d |V_e|=%d |P_e|=%d  V_e-parts=%s"
              % (e, part[e[0]], part[e[1]], len(Ps), len(Vs), len(Es),
                 sorted(set(part[v] for v in Vs))))
    print("VERTEX column deg d_vert(v) (#atoms whose vertex-support contains v):")
    for p in range(5):
        vs = [(v, Vcol.get(v, 0)) for v in range(n) if part[v] == p]
        print("   part %d: %s" % (p, vs))
    print("   T-load by part:")
    for p in range(5):
        vs = [(v, str(T[v])) for v in range(n) if part[v] == p]
        print("     part %d: %s" % (p, vs))
    maxdv = max(Vcol.values()) if Vcol else 0
    maxde = max(Ecol.values()) if Ecol else 0
    print("  max d_vert=%d  max d_edge=%d  |V_all|=%d  sum d_vert=%d (=sum|V_e|)  sum d_edge=%d"
          % (maxdv, maxde, len(Vcol), sum(Vcol.values()), sum(Ecol.values())))
    # VH check S=all: 25*m5 <= N*|V_all|
    print("  VH S=all: 25*%d = %d  vs  N*|V_all| = %d*%d = %d  => slack %d"
          % (len(atoms5), 25 * len(atoms5), n, len(Vcol), n * len(Vcol), n * len(Vcol) - 25 * len(atoms5)))
    # per-vertex: sum over atoms of (25/|V_e|) routed uniformly -> load; check <= N
    unif_load = {v: F(0) for v in range(n)}
    for e in atoms5:
        Ps = geos_paths(adj, side, e[0], e[1])
        Vs = set()
        for P in Ps: Vs.update(P)
        for v in Vs:
            unif_load[v] += F(25, len(Vs))
    mx = max(unif_load.values())
    print("  uniform-support routing (25/|V_e| to each support vertex): max vertex load = %s (cap N=%d) %s"
          % (mx, n, "OK" if mx <= n else "OVER"))


if __name__ == '__main__':
    for t in range(1, 5):
        dump(t)
