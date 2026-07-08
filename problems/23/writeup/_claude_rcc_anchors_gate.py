r"""RCC ANCHORS gate (2026-07-08, Fable-5). Fraction-exact verification of GPT-Pro reply 2 Task-1 anchor
certificates (GAP1_SSE_RELAXEDCUTCOVER_GPTPRO.md):
  1A C5[t]: zero-external-load relaxed cover = singletons {x}, x in A4 (lambda=1). Check coverage>=1 on all bad
     edges, congestion<=1 on all F-edges, delta_B({x}) subseteq E_short(S) (=> external load 0). t=1..3.
  1B odd cycle C_N: bank identity Door+Base vs Demand: DoorCap=25(N-2), BaseCap=max(0,N^2-25N+25),
     Demand=N^2-25. Claim: N<=23 => Demand<=Door; N>=25 => Door+Base == Demand EXACTLY (tight!). N=5..41 odd.
  1C CP11 escaping counterpattern: cover {p},{q} lambda=1: coverage e=1,f=1,h=2; delta_B({p})={p-a,p-r1},
     delta_B({q})={q-c,q-r3}, ALL in multi-geodesic E_short(S) => external 0.
Any failure = GPT-Pro's anchor cert is WRONG (falsifier-first). Exact integer/Fraction only. Run from writeup.
"""
from fractions import Fraction
from _codex_k2t_switch_probe import adj_from_edges
from _claude_residual_hall_gate import geos_paths, residuals


def support_edges(adj, side, e):
    edges = set()
    for P in geos_paths(adj, side, e[0], e[1]):
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]
            edges.add((min(a, b), max(a, b)))
    return frozenset(edges)


def check_cover(n, adj, side, cover, name):
    """cover: dict frozenset(U) -> Fraction weight. Verify coverage/congestion/external exactly."""
    cd = residuals(n, adj, side)
    ell = cd['ell']
    S = [e for e in cd['M'] if ell[e] == 5]
    Pe = {e: support_edges(adj, side, e) for e in S}
    F = set().union(*Pe.values()) if S else set()
    dB_all = [(a, b) for a in range(n) for b in adj[a] if a < b and side[a] != side[b]]
    ok = True
    for e in S:
        cov = sum(w for U, w in cover.items() if (e[0] in U) != (e[1] in U))
        if cov < 1:
            print("   FAIL coverage %s: row %s cov=%s" % (name, e, cov)); ok = False
    for c in F:
        cong = sum(w for U, w in cover.items() if (c[0] in U) != (c[1] in U))
        if cong > 1:
            print("   FAIL congestion %s: edge %s cong=%s" % (name, c, cong)); ok = False
    ext = Fraction(0)
    for c in dB_all:
        if tuple(sorted(c)) not in F and (min(c), max(c)) not in F:
            ext += sum(w for U, w in cover.items() if (c[0] in U) != (c[1] in U))
    if ext != 0:
        print("   FAIL external %s: load=%s (want 0)" % (name, ext)); ok = False
    return ok, len(S), len(F), ext


def c5t_build(t):
    n = 5 * t
    E = []
    for a in range(5):
        b = (a + 1) % 5
        for i in range(t):
            for j in range(t):
                u, w = a * t + i, b * t + j
                E.append((min(u, w), max(u, w)))
    adj = adj_from_edges(n, E)
    side = [0 if (v // t) in (0, 2, 4) else 1 for v in range(n)]
    return n, adj, side


def main():
    allok = True
    print("=== 1A C5[t] singleton-A4 cover ===")
    for t in (1, 2, 3):
        n, adj, side = c5t_build(t)
        A4 = [v for v in range(n) if v // t == 4]
        cover = {frozenset([x]): Fraction(1) for x in A4}
        ok, ns, nf, ext = check_cover(n, adj, side, cover, "C5[%d]" % t)
        print("   C5[%d]: |S|=%d |F|=%d cover-ok=%s external=%s" % (t, ns, nf, ok, ext))
        allok &= ok
    print("=== 1B odd-cycle bank identity ===")
    for N in range(5, 43, 2):
        demand = N * N - 25
        door = 25 * (N - 2)
        base = max(0, N * N - 25 * N + 25)
        if N <= 23:
            ok = demand <= door
            tag = "Demand<=Door: %d<=%d %s" % (demand, door, ok)
        else:
            ok = (door + base == demand)
            tag = "Door+Base==Demand: %d+%d==%d %s (TIGHT)" % (door, base, demand, ok)
        print("   C_%d: %s" % (N, tag))
        allok &= ok
    print("=== 1C CP11 {p},{q} cover ===")
    V = ['p', 'q', 'a', 'b', 'bb', 'c', 'y', 'w', 'r1', 'r2', 'r3']
    idx = {v: i for i, v in enumerate(V)}
    given = {v: 0 for v in ['p', 'q', 'b', 'bb', 'y', 'w', 'r2']}
    for v in ['a', 'c', 'r1', 'r3']:
        given[v] = 1
    B = [('p', 'a'), ('a', 'b'), ('b', 'c'), ('c', 'y'), ('q', 'c'), ('c', 'bb'), ('bb', 'a'),
         ('a', 'w'), ('p', 'r1'), ('r1', 'r2'), ('r2', 'r3'), ('r3', 'q')]
    M = [('p', 'y'), ('q', 'w'), ('p', 'q')]
    E = [(min(idx[u], idx[w]), max(idx[u], idx[w])) for u, w in B + M]
    n = 11
    adj = adj_from_edges(n, E)
    side = [given[v] for v in V]
    cover = {frozenset([idx['p']]): Fraction(1), frozenset([idx['q']]): Fraction(1)}
    ok, ns, nf, ext = check_cover(n, adj, side, cover, "CP11")
    print("   CP11: |S|=%d |F|=%d cover-ok=%s external=%s" % (ns, nf, ok, ext))
    allok &= ok
    # explicit boundary check p-r1 in E_short(h) (the alternate outside geodesic)
    cd = residuals(n, adj, side)
    Ph = support_edges(adj, side, (idx['p'], idx['q']))
    pr1 = (min(idx['p'], idx['r1']), max(idx['p'], idx['r1']))
    print("   p-r1 in P_h (multi-geodesic):", pr1 in Ph)
    allok &= (pr1 in Ph)
    print("=" * 72)
    print("VERDICT:", "ALL THREE ANCHOR CERTS EXACT-VERIFIED (GPT-Pro Task 1 sound)" if allok
          else "ANCHOR FAILURE -- GPT-Pro Task-1 cert wrong; see FAIL lines")


if __name__ == '__main__':
    main()
