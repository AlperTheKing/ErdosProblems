"""Part 3: rigorously certify the K=151/16 counterexample family (C5 + pendants) is LEGITIMATE:
   triangle-free, the gamma-min cut is a GLOBAL max cut (CP-SAT exact), B-connected, beta=1, single geodesic.
   This shows the central inequality V2 <= (151/16)*Gamma*(N^2/25-beta) is FALSE at N>=12 on a valid config,
   i.e. 151/16 is NOT a universal constant (route 'spectral' constant is unbounded ~K(N)).
"""
from fractions import Fraction as F
from _h import Bconn, maxcut_all, bdist_restr
from _satzmu_conn import struct_for_side
from _bdef_construct import is_triangle_free
try:
    from ortools.sat.python import cp_model
    HAVE_OR = True
except Exception:
    HAVE_OR = False

def c5_with_pendants(pads):
    E = [(i, (i + 1) % 5) for i in range(5)]
    nxt = 5
    for _ in range(pads):
        E.append((0, nxt)); nxt += 1
    return nxt, E

def gmins(n, E):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    cuts = [s for s in maxcut_all(n, adj) if Bconn(n, adj, s)]
    cand = []
    for s in cuts:
        Mb = [(u, v) for u in range(n) for v in adj[u] if v > u and s[u] == s[v]]
        if not Mb: continue
        G = 0; ok = True
        for (u, v) in Mb:
            d = bdist_restr(adj, s, u, v)
            if d < 0: ok = False; break
            G += (d + 1) ** 2
        if ok: cand.append((s, G))
    if not cand: return adj, [], None
    gm = min(g for _, g in cand)
    return adj, [s for s, g in cand if g == gm], gm

def brute_maxcut_size(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E: adj[a].add(b); adj[b].add(a)
    edges = [(u, v) for u in range(n) for v in adj[u] if v > u]
    best = -1
    for m in range(1 << (n - 1)):
        side = [(m >> u) & 1 for u in range(n)]
        c = sum(1 for u, v in edges if side[u] != side[v])
        best = max(best, c)
    return best

def cpsat_max(n, E, tlim=30):
    if not HAVE_OR: return None
    m = cp_model.CpModel(); x = [m.NewBoolVar("x%d" % i) for i in range(n)]; t = []
    for a, b in E:
        z = m.NewBoolVar("e%d_%d" % (a, b)); m.AddBoolXOr([x[a], x[b], z.Not()]); t.append(z)
    m.Maximize(sum(t)); s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tlim
    st = s.Solve(m)
    return int(round(s.ObjectiveValue())), int(round(s.BestObjectiveBound())), st == cp_model.OPTIMAL

print("=== Part 3: certify C5+pendant counterexamples to K=151/16 ===", flush=True)
for pads in [1, 6, 7, 11]:   # N=6,11(extremal),12(first breach),16
    n, E = c5_with_pendants(pads)
    tf = is_triangle_free(n, E)
    adj, cuts, gm = gmins(n, E)
    # cut size of a gamma-min cut
    s0 = cuts[0]
    cutsize = sum(1 for u in range(n) for v in adj[u] if v > u and s0[u] != s0[v])
    bmax = brute_maxcut_size(n, E)
    cp = cpsat_max(n, E) if HAVE_OR else None
    st = struct_for_side(n, adj, s0)
    M, ell, T, mu, cyc = st
    beta = len(M); Gamma = sum(F(ell[f]) ** 2 for f in M)
    V2 = sum((t - F(n)) ** 2 for t in T); Gbud = F(n * n, 25) - beta
    r = V2 / (Gamma * Gbud) if Gbud > 0 else None
    ngeo = [len(cyc[f]) for f in M]
    print("\n  pads=%d N=%d triangle-free=%s Bconn(cut)=%s" % (pads, n, tf, Bconn(n, adj, s0)), flush=True)
    print("    gamma-min cut size=%d  brute-force max-cut=%d  global-max=%s" % (cutsize, bmax, cutsize == bmax), flush=True)
    if cp is not None:
        print("    CP-SAT opt=%d bound=%d OPTIMAL=%s  matches=%s" % (cp[0], cp[1], cp[2], cp[0] == cp[1] == cutsize), flush=True)
    print("    beta=%d Gamma=%s ell=%s n_geodesics=%s" % (beta, str(Gamma), [ell[f] for f in M], ngeo), flush=True)
    if r is not None:
        print("    V2=%s Gbud=%s  ratio r=%s=%.5f   151/16=%.5f   r>151/16 ? %s" % (
            str(V2), str(Gbud), str(r), float(r), float(F(151,16)), r > F(151,16)), flush=True)
