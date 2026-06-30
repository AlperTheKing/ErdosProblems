"""Part 2 of independent verify route 'spectral'.
(A) Confirm the binding N=11 config is a single-C5-geodesic graph and that the closed form
    K(N) = (N^2 + 5N - 25)/(N+5) is exactly the ratio for the single-geodesic family => UNBOUNDED ~N.
(B) Extra adversarial hunt: bigger single-geodesic configs (C5 + isolated-ish pendant pentagon),
    extra ad-hoc triangle-free graphs, and larger Mycielskian/odd-cycle blow-ups, to see if any config
    EXCEEDS its own K(N) (i.e. whether 151/16 is really only the N=11 value, not a hidden universal bound).
(C) Direct construction of a single-geodesic config at N=16 to show ratio > 151/16 (DISPROVES universality
    of the constant 151/16, exactly as the notes warn).
All EXACT Fraction.
"""
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all, bdist_restr
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, union_disjoint, is_triangle_free

def gmins(n, E):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    cuts = [s for s in maxcut_all(n, adj) if Bconn(n, adj, s)]
    cand = []
    for s in cuts:
        Mb = [(u, v) for u in range(n) for v in adj[u] if v > u and s[u] == s[v]]
        if not Mb:
            continue
        G = 0; ok = True
        for (u, v) in Mb:
            d = bdist_restr(adj, s, u, v)
            if d < 0:
                ok = False; break
            G += (d + 1) ** 2
        if ok:
            cand.append((s, G))
    if not cand:
        return adj, []
    gm = min(g for _, g in cand)
    return adj, [s for s, g in cand if g == gm]

def ratio_for(n, adj, side, want_detail=False):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    if not M:
        return None
    N = n; beta = len(M)
    Gamma = sum(F(ell[f]) ** 2 for f in M)
    V2 = sum((t - F(N)) ** 2 for t in T)
    Gbud = F(N * N, 25) - F(beta)
    if Gbud <= 0:
        return ('GBUD<=0', N, beta, V2, Gamma, Gbud)
    r = V2 / (Gamma * Gbud)
    if want_detail:
        ngeo = {f: len(cyc[f]) for f in M}
        return (r, N, beta, V2, Gamma, Gbud, ell, ngeo, [str(t) for t in T])
    return (r, N, beta, V2, Gamma, Gbud)

# --- (A) inspect binding census config J????A?oB~? at its gamma-min cut(s) ---
print("=== (A) binding config J????A?oB~? detail ===", flush=True)
n, E = dec("J????A?oB~?")
adj, cuts = gmins(n, E)
for s in cuts:
    d = ratio_for(n, adj, s, want_detail=True)
    if d and d[0] != 'GBUD<=0':
        r, N, beta, V2, Gamma, Gbud, ell, ngeo, Ts = d
        print("  N=%d beta=%d r=%s=%.6f ell=%s n_geodesics=%s" % (
            N, beta, str(r), float(r), list(ell.values()), list(ngeo.values())), flush=True)
        print("    V2=%s Gamma=%s Gbud=%s  T(distinct)=%s" % (str(V2), str(Gamma), str(Gbud), sorted(set(Ts))), flush=True)

# --- closed-form check K(N)=(N^2+5N-25)/(N+5) for single-C5-geodesic family ---
# A single bad edge with a UNIQUE shortest alternating geodesic of 5 vertices (a clean C5) embedded so that
# exactly those 5 vertices carry load ell=5 each (single geodesic => p_f indicator on 5 verts, T=5 on them, 0 else).
# Then beta=1, Gamma=25. T(v)=5 on 5 verts, 0 on N-5 verts.
# V2 = 5*(5-N)^2 + (N-5)*N^2 = (N-5)*(... )  let's just compute symbolically via Fraction at several N.
print("\n=== closed form K(N)=(N^2+5N-25)/(N+5) for single-C5-geodesic family ===", flush=True)
for N in [11, 12, 16, 23, 50, 100]:
    # 5 verts load 5, N-5 verts load 0, beta=1, Gamma=25
    V2 = 5 * (F(5) - N) ** 2 + (N - 5) * (F(0) - N) ** 2
    Gamma = F(25); Gbud = F(N * N, 25) - 1
    r = V2 / (Gamma * Gbud)
    KN = F(N * N + 5 * N - 25, N + 5)
    print("  N=%3d  r=%s=%.5f   K(N)formula=%s=%.5f   match=%s" % (
        N, str(r), float(r), str(KN), float(KN), r == KN), flush=True)

# --- (B)/(C) build an actual triangle-free graph with a single 5-vertex geodesic at N=16 to EXCEED 151/16 ---
# Take a C5 (verts 0..4, edges cycle) -- but C5 alone with max cut has 1 bad edge and a UNIQUE geodesic
# only if the alternating structure forces it. Then pad with N-5 disconnected... but B must be connected.
# Simplest realizable: the extremal single-geodesic appears in census; to push N up we need a triangle-free,
# B-connected graph whose gamma-min cut has beta=1 and Gamma small while N is large. We test a family:
# pentagon C5 with a tree of cut-edges hung off it (extra leaves) to grow N while keeping a single bad edge.
print("\n=== (C) grow N with beta=1: C5 + pendant cut-edges (B-connected), exact ratio vs 151/16 ===", flush=True)
def c5_with_pendants(pads):
    """C5 on 0..4; attach 'pads' pendant leaves to vertex 0 (each leaf is a new vertex adjacent only to 0).
       Leaves go on the opposite side -> they are cut edges, add to N, keep triangle-free + B-connected,
       and (hopefully) keep beta=1 with the same single geodesic."""
    E = [(i, (i + 1) % 5) for i in range(5)]
    nxt = 5
    for _ in range(pads):
        E.append((0, nxt)); nxt += 1
    return nxt, E
for pads in range(0, 14):
    n, E = c5_with_pendants(pads)
    if not is_triangle_free(n, E):
        print("  pads=%d N=%d NOT triangle-free" % (pads, n)); continue
    adj, cuts = gmins(n, E)
    best = None
    for s in cuts:
        d = ratio_for(n, adj, s)
        if d and d[0] != 'GBUD<=0':
            if best is None or d[0] > best[0]:
                best = d
    if best is None:
        print("  pads=%d N=%d: no valid gamma-min single-load cut (beta/geo issue)" % (pads, n)); continue
    r, N, beta, V2, Gamma, Gbud = best
    KN = F(N * N + 5 * N - 25, N + 5)
    print("  pads=%d N=%d beta=%d r=%s=%.5f  vs 151/16=%.5f  (exceeds151/16=%s)  K(N)=%.5f match=%s" % (
        pads, N, beta, str(r), float(r), float(F(151,16)), r > F(151,16), float(KN), r == KN), flush=True)

# --- (B) extra ad-hoc triangle-free graphs: Petersen, C5xK2 (Mobius), random-ish trees-of-pentagons ---
print("\n=== (B) extra ad-hoc triangle-free graphs ===", flush=True)
def petersen():
    E = [(i, (i + 1) % 5) for i in range(5)]                  # outer C5
    E += [(5 + i, 5 + (i + 2) % 5) for i in range(5)]          # inner pentagram
    E += [(i, 5 + i) for i in range(5)]                        # spokes
    return 10, E
extra_graphs = {
    "Petersen": petersen(),
    "Grotzsch": mycielski(5, Cn(5)),
    "Myc(C7)": mycielski(7, Cn(7)),
    "Myc(C9)": mycielski(9, Cn(9)),
    "Myc(Grotzsch)N23": mycielski(*mycielski(5, Cn(5))),
}
gmax = (F(-1), '')
for nm, (nn, E) in extra_graphs.items():
    if not is_triangle_free(nn, E):
        print("  %s: NOT triangle-free, skip" % nm); continue
    adj, cuts = gmins(nn, E)
    best = None
    for s in cuts:
        d = ratio_for(nn, adj, s)
        if d and d[0] != 'GBUD<=0':
            if best is None or d[0] > best[0]:
                best = d
    if best is None:
        print("  %s N=%d: no Gbud>0 cut" % (nm, nn)); continue
    r, N, beta, V2, Gamma, Gbud = best
    if r > gmax[0]: gmax = (r, nm)
    print("  %s N=%d beta=%d max-r=%s=%.5f  exceeds151/16=%s" % (nm, N, beta, str(r), float(r), r > F(151,16)), flush=True)
print("\n  extra-graph max ratio = %.5f at %s" % (float(gmax[0]), gmax[1]), flush=True)
