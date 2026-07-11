r"""CLAUDE independent micro-scale re-gate of the Codex N12 fixture K??E@cyjFgWk (all 2400 tuples).

CODEX CLAIMS (15:44Z + 15:53Z): on g6 K??E@cyjFgWk (n=12), census Gamma-min connected max cut, complete row
families sized [6,5,8,10], SOME tuple (their choice [0,4,5,7]) has collision demand 28, HitNeed slots 2, micro
demand 28+25*2=78, common-blue-extended max flow 65, DEFECT 13, deficient owners {10,11}; AND at score-MINIMAL
tuples MicroMatching passes (their minimum gate: 0 failures over all N12 medium/heavy).

MY GATE (ordering-ambiguity-free): enumerate ALL prod(family sizes)=2400 tuples with MY OWN implementation
(P1 same-first + P3 row-companion sigma>=0 + common-blue TerminalData.Valid sources; obligations = collision
halves + 25x HitNeed per owner; Hall over ALL owner shores). Verify: (i) some tuple realizes the claimed
(78, 65, 13, {10,11}) profile; (ii) the tuple-level failure histogram; (iii) every minimum-scoped-score tuple
passes micro Hall. Exact/integer only. Run from repo root.
"""
import importlib.util
import sys
from collections import Counter, defaultdict, deque
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "problems/23/writeup"))
from _h import dec, maxcut_all, gmin  # census helpers (graph6 decode, exact maxcut, Gamma-min B-conn selection)

G6 = "K??E@cyjFgWk"


def norm(u, v):
    return (u, v) if u < v else (v, u)


def main():
    n, E = dec(G6)
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v)
        adj[v].add(u)
    cuts = maxcut_all(n, [sorted(a) for a in adj])
    best = gmin(n, [sorted(a) for a in adj], cuts)
    assert best is not None, "no Gamma-min B-connected max cut"
    side = best[0]
    blue = {norm(u, v) for u, v in E if side[u] != side[v]}
    bad = sorted(norm(u, v) for u, v in E if side[u] == side[v])
    print("n=%d |E|=%d |B|=%d |M|=%d bad=%s" % (n, len(E), len(blue), len(bad), bad))
    badj = [sorted(w for w in adj[u] if side[w] != side[u]) for u in range(n)]

    def bfs(s):
        d = [-1] * n
        d[s] = 0
        q = deque([s])
        while q:
            x = q.popleft()
            for y in badj[x]:
                if d[y] < 0:
                    d[y] = d[x] + 1
                    q.append(y)
        return d

    def geos(s, t):
        ds, dt = bfs(s), bfs(t)
        D = ds[t]
        out = []

        def go(p):
            u = p[-1]
            if u == t:
                out.append(tuple(p))
                return
            for v in badj[u]:
                if ds[v] == ds[u] + 1 and dt[v] == D - ds[v]:
                    go(p + [v])

        go([s])
        return D, out

    fams = []
    for (u, v) in bad:
        D, F = geos(u, v)
        assert D == 4, (u, v, D)
        fams.append(F)
    sizes = sorted(len(F) for F in fams)
    print("family sizes: %s (claim sorted [5,6,8,10])" % [len(F) for F in fams])
    assert sizes == [5, 6, 8, 10], sizes

    bl_adj = defaultdict(set)
    m_adj = defaultdict(set)
    for u, v in blue:
        bl_adj[u].add(v)
        bl_adj[v].add(u)
    for u, v in bad:
        m_adj[u].add(v)
        m_adj[v].add(u)

    def dB2(x, y):
        return len(bl_adj[x]) + len(bl_adj[y]) - 2 * (y in bl_adj[x])

    def dM2(x, y):
        return len(m_adj[x]) + len(m_adj[y]) - 2 * (y in m_adj[x])

    signed = Counter()
    sgn = {}
    for e in blue:
        sgn[e] = 1
        signed[e[0]] += 1
        signed[e[1]] += 1
    for e in bad:
        sgn[e] = -1
        signed[e[0]] -= 1
        signed[e[1]] -= 1

    def micro_state(rows):
        pair = Counter()
        loadc = Counter()
        support = set()
        selected = set()
        for row in rows:
            for x in row:
                loadc[x] += 1
                selected.add(x)
            for x in row:
                for y in row:
                    pair[x, y] += 1
            support.update(norm(a, b) for a, b in zip(row, row[1:]))
        act = {e for e in blue if e not in support and e[0] in selected and e[1] in selected}
        cadj = defaultdict(set)
        for u, v in act:
            cadj[u].add(v)
            cadj[v].add(u)
        comp = {}
        for r0 in sorted(selected):
            if r0 in comp:
                continue
            c = {r0}
            q = deque([r0])
            while q:
                x = q.popleft()
                for y in cadj[x]:
                    if y not in c:
                        c.add(y)
                        q.append(y)
            for y in c:
                comp[y] = r0
        roots = {comp[u] for u, v in bad if u in comp and v in comp and comp[u] == comp[v]}
        av = {v for v in selected if comp[v] in roots}
        deg = Counter()
        for u, v in act:
            if comp[u] in roots:
                deg[u] += 1
                deg[v] += 1
        coll = {v: 2 * sum(max(0, pair[v, y] - 1) for y in range(n)) for v in av}
        hit = {v: max(0, deg[v] - max(0, n - 5 * loadc[v])) for v in av}
        owners = sorted(v for v in av if coll[v] + hit[v] > 0)
        srcs = {}
        for o in owners:
            # P1 same-first
            for y in range(n):
                if y == o or pair[o, y] != 0:
                    continue
                for h in (0, 1):
                    if not (h == 0 and norm(o, y) in act and o in av):
                        srcs.setdefault((o, y, h), set()).add(o)
            # P3 row-companion
            C = {x for x in range(n) if pair[o, x] > 0 and x != o}
            for x in C:
                for y in C:
                    if x == y or pair[x, y] != 0:
                        continue
                    e = norm(x, y)
                    if signed[x] + signed[y] - 2 * sgn.get(e, 0) < 0:
                        continue
                    for h in (0, 1):
                        if not (h == 0 and e in act and x in av):
                            srcs.setdefault((x, y, h), set()).add(o)
            # common-blue
            nb = sorted(bl_adj[o])
            for i, x in enumerate(nb):
                for y in nb[i + 1:]:
                    if pair[x, y] != 0 or dM2(x, y) + 2 > dB2(x, y):
                        continue
                    for (a, b) in ((x, y), (y, x)):
                        for h in (0, 1):
                            if not (h == 0 and norm(a, b) in act and a in av):
                                srcs.setdefault((a, b, h), set()).add(o)
        micro = {o: coll[o] + 25 * hit[o] for o in owners}
        # Hall over all owner shores
        worst = (0, ())
        for mask in range(1, 1 << len(owners)):
            shore = [owners[i] for i in range(len(owners)) if mask & (1 << i)]
            d = sum(micro[o] for o in shore)
            reach = sum(1 for k, os in srcs.items() if os & set(shore))
            gap = d - reach
            if gap > worst[0]:
                worst = (gap, tuple(shore), d, reach)
        return dict(score=sum(coll.values()) + sum(hit.values()), coll=sum(coll.values()),
                    hits=sum(hit.values()), micro_total=sum(micro.values()), owners=owners, worst=worst)

    results = []
    for choice in product(*[range(len(F)) for F in fams]):
        rows = tuple(fams[i][choice[i]] for i in range(len(bad)))
        st = micro_state(rows)
        results.append((choice, st))
    fails = [(c, s) for c, s in results if s["worst"][0] > 0]
    match13 = [(c, s) for c, s in fails if s["micro_total"] == 78 and s["worst"][0] == 13
               and set(s["worst"][1]) == {10, 11}]
    minscore = min(s["score"] for _, s in results)
    min_fail = [(c, s) for c, s in results if s["score"] == minscore and s["worst"][0] > 0]
    print("tuples: %d | micro-Hall failures: %d | claimed profile (micro 78, defect 13, owners {10,11}): %d found"
          % (len(results), len(fails), len(match13)))
    if match13:
        c, s = match13[0]
        print("  example choice %s: coll=%d hit=%d micro=%d worst=%s" % (c, s["coll"], s["hits"], s["micro_total"], s["worst"]))
    print("min scoped score over tuples: %d | min-score tuples failing micro Hall: %d (claim 0)"
          % (minscore, len(min_fail)))
    ok = bool(match13) and len(min_fail) == 0
    print("=" * 72)
    print("VERDICT: %s -- Codex claims %s on this fixture (my own P1+P3+common-blue micro implementation, all %d tuples)"
          % ("PASS" if ok else "FAIL", "CONFIRMED" if ok else "NOT reproduced", len(results)))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
