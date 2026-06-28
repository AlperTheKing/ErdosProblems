"""Mine the cond1 obstruction for GCD.

For H = L_omega + diag(N-T), split Q={T<=N}.  The principal block H_QQ is a
grounded Laplacian on the omega graph induced by Q.  A Q-component is dangerous
only if every vertex has zero ground, where

    ground(v) = (N-T(v)) + omega(v,O).

This script reports saturated Q-components and their grounding sources.
"""
from fractions import Fraction as F
import subprocess

from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from _gcd import build_H
from _bdef_construct import Cn, mycielski, union_disjoint, is_triangle_free


def gamma_min_sides(n, E):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y)
        adj[y].add(x)
    cuts = [s for s in maxcut_all(n, adj) if Bconn(n, adj, s)]
    cand = []
    for s in cuts:
        bad = [(u, v) for u in range(n) for v in adj[u] if v > u and s[u] == s[v]]
        if not bad:
            continue
        gamma = 0
        ok = True
        for u, v in bad:
            d = bdist_restr(adj, s, u, v)
            if d < 0:
                ok = False
                break
            gamma += (d + 1) ** 2
        if ok:
            cand.append((s, gamma))
    if not cand:
        return adj, []
    gm = min(g for _, g in cand)
    return adj, [s for s, g in cand if g == gm]


def q_components(H, T, n):
    O = [v for v in range(n) if T[v] > n]
    Q = [v for v in range(n) if T[v] <= n]
    qset = set(Q)
    seen = set()
    out = []
    for start in Q:
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        comp = []
        while stack:
            v = stack.pop()
            comp.append(v)
            for u in Q:
                if u not in seen and H[v][u] < 0:
                    seen.add(u)
                    stack.append(u)
        grounds = {}
        deficits = {}
        boundary = {}
        for v in comp:
            internal_offdiag = sum(H[v][u] for u in comp if u != v)
            ground = H[v][v] + internal_offdiag
            deficit = F(n) - T[v]
            omega_to_o = ground - deficit
            grounds[v] = ground
            deficits[v] = deficit
            boundary[v] = omega_to_o
        out.append(
            dict(
                comp=sorted(comp),
                sat=sorted(v for v in comp if T[v] == n),
                deficit_vertices=sorted(v for v in comp if deficits[v] > 0),
                boundary_vertices=sorted(v for v in comp if boundary[v] > 0),
                total_ground=sum(grounds.values(), F(0)),
                O=O,
            )
        )
    return out


def analyze_side(adj, side, n):
    built = build_H(adj, side, n)
    if built is None:
        return []
    H, T, _ = built
    return [c for c in q_components(H, T, n) if c["sat"]]


def summarize_graph(name, n, E, max_lines=12):
    adj, sides = gamma_min_sides(n, E)
    total_sat_components = 0
    zero_ground = 0
    examples = []
    for side in sides:
        comps = analyze_side(adj, side, n)
        total_sat_components += len(comps)
        for c in comps:
            if c["total_ground"] == 0:
                zero_ground += 1
            if len(examples) < max_lines:
                examples.append(c)
    print(
        f"{name}: gamma-min-cuts={len(sides)} sat-Q-components={total_sat_components} "
        f"zero-ground={zero_ground}",
        flush=True,
    )
    for c in examples:
        tg = c["total_ground"]
        print(
            f"  comp={c['comp']} sat={c['sat']} deficit={c['deficit_vertices']} "
            f"boundaryO={c['boundary_vertices']} |O|={len(c['O'])} ground={tg}",
            flush=True,
        )


if __name__ == "__main__":
    print("=== GCD cond1 component diagnostic ===", flush=True)
    named = []
    c5 = (5, Cn(5))
    g = mycielski(*c5)
    named.append(("Grotzsch", *g))
    named.append(("Myc(Grotzsch)", *mycielski(*g)))
    named.append(("Myc(C7)", *mycielski(7, Cn(7))))
    for g6 in ["G?bF`w", "I?BD@g]Qo", "I?ABCc]}?", "J??CE?{{?]?"]:
        n, E = dec(g6)
        named.append((g6, n, E))
    for name, n, E in named:
        summarize_graph(name, n, E)

    for nn in range(8, 11):
        total = 0
        zero = 0
        satcuts = 0
        witness = None
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj, sides = gamma_min_sides(n, E)
            for side in sides:
                comps = analyze_side(adj, side, n)
                if comps:
                    satcuts += 1
                total += len(comps)
                for c in comps:
                    if c["total_ground"] == 0:
                        zero += 1
                        witness = witness or (g6, c)
        print(
            f"census N={nn}: cuts-with-sat={satcuts} sat-Q-components={total} zero-ground={zero}",
            flush=True,
        )
        if witness:
            print(f"  WIT {witness}", flush=True)

    print("--- glued island spot-check ---", flush=True)
    g15 = mycielski(7, Cn(7))
    gr = mycielski(5, Cn(5))
    for iN, iE in [(5, Cn(5)), (7, Cn(7))]:
        for gN, gE in [g15, gr]:
            for br in [[(0, 0)], [(0, 1)], [(0, 2)], [(0, 0), (2, 3)]]:
                if any(j >= gN for _, j in br):
                    continue
                n, E = union_disjoint((iN, iE), (gN, gE))
                for i, j in br:
                    E = E + [(i, iN + j)]
                if n > 22 or not is_triangle_free(n, E):
                    continue
                summarize_graph(f"isl{iN}+gad{gN}+{br}", n, E, max_lines=2)
