#!/usr/bin/env python3
"""SKEPTIC audit of D1: gr_exact deficit regenerator + its SOUNDNESS as a bound on d_mono.

Independent reimplementation that does NOT call fx.gr_exact's body. Uses fs._induces_sigma_ordered
only for the inducing predicate (allowed). Recomputes cm from scratch via an EXPLICIT 0/1 cut
(pmap values are in {0,1}) so cm = literal mono-count of one cut on the m non-root vertices.

Three checks:
 (A) equality: my_gr == fx.gr_exact over all triangle-free states n=4..7, all 8 cert atoms. maxdisc must be 0.
 (B) unit case: k=0, q=1/2 -> g = d_edge/2 - 2/25 exactly.
 (C) SOUNDNESS (the load-bearing one): per rule r, is  g_r(H) >= d_mono(H) - 2/25  ?
     d_mono(H) = 2*(e - maxcut(H))/n^2.  This is the inequality the certificate RELIES ON
     (certify_dual.py lines 5-7: min_r g_r = best-profile-cut mono - 2/25 >= d_mono - 2/25).
     We test it on EVERY triangle-free state n=5..9 for each of the 8 atoms. ALSO probe the
     subtle gap: cm ignores root vertices and uses density over m=n-k non-root vertices, while
     d_mono uses the whole n-vertex graph. Report any state where g_r(H) < d_mono(H)-2/25.
"""
import sys, pickle, itertools
from fractions import Fraction as F
import flag_engine as fe
import flag_sdp as fs
import flag_exact as fx

T = F(2, 25)

def my_gr(states, k, Asig, pmap):
    sigma = (k, Asig)
    out = []
    for (n, A) in states:
        if n < 2:
            out.append(F(0)); continue
        adj = [[bool((A[u] >> v) & 1) for v in range(n)] for u in range(n)]
        nk = 1
        for i in range(k):
            nk *= (n - i)
        m = n - k
        Cm2 = m * (m - 1) // 2
        if Cm2 <= 0 or nk == 0:
            out.append(F(0)); continue
        g = F(0)
        for R in itertools.permutations(range(n), k):
            if not fs._induces_sigma_ordered(A, R, sigma):
                continue
            Rset = set(R)
            rest = [w for w in range(n) if w not in Rset]
            # side label per non-root vertex from pmap (q in {0,1} -> explicit side)
            q = {}
            for w in rest:
                alpha = frozenset(i for i in range(k) if adj[w][R[i]])
                q[w] = pmap.get(alpha, F(1, 2))
            # cm via DIFFERENT accumulation order than gr_exact: iterate pairs as combinations
            cm = F(0)
            for u, v in itertools.combinations(rest, 2):
                if adj[u][v]:
                    qu, qv = q[u], q[v]
                    cm += qu * qv + (1 - qu) * (1 - qv)
            g += (cm / Cm2 - T)
        out.append(g / nk)
    return out

def maxcut(n, A):
    adj = [[(A[u] >> v) & 1 for v in range(n)] for u in range(n)]
    best = 0
    for mask in range(1 << (n - 1)):
        side = [(mask >> u) & 1 for u in range(n)]
        cut = 0
        for u in range(n):
            su = side[u]
            for v in range(u + 1, n):
                if adj[u][v] and su != side[v]:
                    cut += 1
        if cut > best:
            best = cut
    return best

def load_atoms():
    d = pickle.load(open('dual_cert_n9.pkl', 'rb'))
    ndix, lam, prov = d['ndix'], d['lam'], d['prov']
    atoms = []
    for c in range(len(lam)):
        if F(lam[c]) == 0:
            continue
        i = ndix[c]
        pr = prov[i]
        assert pr[0] in ("deficit", "deficit_pmap")
        if pr[0] == "deficit":
            _, k, A, cls, p = pr
            pmap = {cls[j]: F(int(p[j])) for j in range(len(cls))}
        else:
            _, k, A, pmap = pr
        atoms.append((c, i, k, A, pmap, F(lam[c])))
    return atoms

def main():
    atoms = load_atoms()
    print(f"loaded {len(atoms)} nonzero deficit atoms")
    # check all pmap values in {0,1}
    for c, i, k, A, pmap, l in atoms:
        vals = set(pmap.values())
        assert vals <= {F(0), F(1)}, f"atom c={c} has non-0/1 pmap {vals}"
    print("all pmap values in {0,1}: OK (genuine integer cuts)")

    # ---- (A) equality vs fx.gr_exact, n=4..7 ----
    print("\n=== (A) equality my_gr vs fx.gr_exact ===")
    maxdisc = F(0); worst = None
    for n in range(4, 8):
        states = fe.enumerate_graphs(n, triangle_free=True)
        for c, i, k, A, pmap, l in atoms:
            mine = my_gr(states, k, A, pmap)
            theirs = fx.gr_exact(states, k, A, pmap, T)
            for j in range(len(states)):
                d = abs(mine[j] - theirs[j])
                if d > maxdisc:
                    maxdisc = d; worst = (n, c, j)
    print(f"max abs discrepancy (Fraction) = {maxdisc}  worst={worst}")

    # ---- (B) unit case k=0, q=1/2 -> g = d_edge/2 - 2/25 ----
    print("\n=== (B) unit case k=0 q=1/2 ===")
    states7 = fe.enumerate_graphs(7, triangle_free=True)
    g0 = my_gr(states7, 0, [], {})  # k=0, no roots, q defaults to 1/2
    edens = fx.edge_density_exact(states7)
    ub_bad = F(0)
    for j in range(len(states7)):
        expect = edens[j] / 2 - T
        if abs(g0[j] - expect) > ub_bad:
            ub_bad = abs(g0[j] - expect)
    print(f"k=0 q=1/2: max |g - (d_edge/2 - 2/25)| = {ub_bad}  (must be 0)")

    # ---- (C) SOUNDNESS: g_r(H) >= d_mono(H) - 2/25 for every state, every atom ----
    print("\n=== (C) SOUNDNESS  g_r(H) >= d_mono(H) - 2/25 ===")
    violations = []
    min_gap = F(10**9)
    for n in range(5, 10):
        states = fe.enumerate_graphs(n, triangle_free=True)
        # precompute d_mono per state
        dmono = []
        for (nn, A) in states:
            e = sum(1 for u in range(nn) for v in range(u + 1, nn) if (A[u] >> v) & 1)
            mc = maxcut(nn, A)
            dmono.append(F(2 * (e - mc), nn * nn))
        for c, i, k, A, pmap, l in atoms:
            gr = my_gr(states, k, A, pmap)
            for j in range(len(states)):
                # g_r is the AVERAGE of (cm/Cm2 - t); if no R induces sigma, g_r=0 (rule silent)
                rhs = dmono[j] - T
                gap = gr[j] - rhs
                if gr[j] != 0 or True:
                    if gap < min_gap:
                        min_gap = gap
                    if gap < 0:
                        violations.append((n, c, i, j, float(gr[j]), float(rhs), float(gap)))
        print(f"  n={n}: states={len(states)}, running min(g_r - (d_mono-2/25)) = {float(min_gap):.4e}, violations so far={len(violations)}")
    print(f"\nGLOBAL min gap (g_r - (d_mono - 2/25)) = {float(min_gap):.6e}")
    print(f"violations (g_r < d_mono - 2/25): {len(violations)}")
    for v in violations[:20]:
        print("   VIOLATION", v)

    # ---- (C2) the actual cert bound: does min over the 8 atoms (each silent->skip) bound d_mono?
    # The cert uses convex combo; min_r g_r >= d_mono - 2/25 must hold where ALL atoms active.
    print("\n=== (C2) does min over ACTIVE atoms (g_r!=0) bound d_mono-2/25 per state? ===")
    bad2 = []
    for n in range(5, 10):
        states = fe.enumerate_graphs(n, triangle_free=True)
        dmono = []
        for (nn, A) in states:
            e = sum(1 for u in range(nn) for v in range(u + 1, nn) if (A[u] >> v) & 1)
            mc = maxcut(nn, A)
            dmono.append(F(2 * (e - mc), nn * nn))
        grs = [my_gr(states, k, A, pmap) for c, i, k, A, pmap, l in atoms]
        for j in range(len(states)):
            active = [grs[a][j] for a in range(len(atoms)) if grs[a][j] != 0]
            if not active:
                continue
            mn = min(active)
            if mn < dmono[j] - T:
                bad2.append((n, j, float(mn), float(dmono[j] - T)))
    print(f"states where min-active-atom < d_mono-2/25: {len(bad2)}")
    for b in bad2[:20]:
        print("   ", b)

if __name__ == "__main__":
    main()
