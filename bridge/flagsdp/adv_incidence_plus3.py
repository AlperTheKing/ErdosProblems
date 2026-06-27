#!/usr/bin/env python3
"""Incidence-bipartite-plus (v3): GENERAL chords on the small Levi graphs.

For Heawood (N=14) and Mobius-Kantor (N=16) we add ANY triangle-safe chords
(not restricted to within-part), then let the harness compute the TRUE max cut
(side=None) which may differ from the even/odd bipartition. This catches the case
where a clever chord set makes some original edges become monochromatic under the
new max cut, raising m and Gamma.

Also: deliberately try to hit the Gamma=N^2 ridge by combining the Levi graph with
a C5-blowup-like local structure (mixed family) -- e.g. add a 5-vertex odd-girth
gadget chorded onto the Levi graph. Reported separately.
"""
import itertools, random
from peel_check import check_instance, is_triangle_free

def lcf_graph(n, lcf):
    adj = [set() for _ in range(n)]
    for i in range(n):
        j = (i + 1) % n
        adj[i].add(j); adj[j].add(i)
    for i in range(n):
        j = (i + lcf[i]) % n
        adj[i].add(j); adj[j].add(i)
    return adj

SMALL = {
    "Heawood":      (14, [5, -5] * 7),
    "MobiusKantor": (16, [5, -5] * 8),
}

def tri_safe_chords(n, adj):
    cands = []
    for u in range(n):
        for v in range(u + 1, n):
            if v in adj[u]:
                continue
            if adj[u] & adj[v]:
                continue
            cands.append((u, v))
    return cands

def add_set(adj0, chords):
    adj = [set(s) for s in adj0]
    for (x, y) in chords:
        if y in adj[x] or (adj[x] & adj[y]):
            return None
        adj[x].add(y); adj[y].add(x)
    return adj

def run():
    random.seed(7)
    obstructions = []
    near_tight = []
    tested = 0
    for name, (n, lcf) in SMALL.items():
        adj0 = lcf_graph(n, lcf)
        cands = tri_safe_chords(n, adj0)
        print(f"=== {name} N={n} #tri-safe-chords={len(cands)} ===")
        # singles
        for ch in cands:
            adj = add_set(adj0, [ch])
            if adj is None:
                continue
            r = check_instance(n, adj, side=None)
            tested += 1
            _rec(name, ("single", ch), r, obstructions, near_tight)
        # doubles (sample many)
        pairs = list(itertools.combinations(cands, 2))
        random.shuffle(pairs)
        for (a, b) in pairs[:5000]:
            adj = add_set(adj0, [a, b])
            if adj is None:
                continue
            r = check_instance(n, adj, side=None)
            tested += 1
            _rec(name, ("double", (a, b)), r, obstructions, near_tight)
        # triples (sample)
        trips = list(itertools.combinations(cands, 3))
        random.shuffle(trips)
        for (a, b, c) in trips[:5000]:
            adj = add_set(adj0, [a, b, c])
            if adj is None:
                continue
            r = check_instance(n, adj, side=None)
            tested += 1
            _rec(name, ("triple", (a, b, c)), r, obstructions, near_tight)

    print(f"\n===== TESTED {tested} =====")
    near_tight.sort(key=lambda t: -t[0])
    print("TOP near-tight (m>=2):")
    for ratio, name, how, r in near_tight[:25]:
        flag = " <<<OBSTRUCTION" if (r.get('has_safe_peel') is False and r.get('ge_n2')) else ""
        print(f"  ratio={ratio:.4f} [{name} {how}] N={r['N']} m={r['m']} gamma={r['gamma']} "
              f"n2={r['n2']} tight={r['tight']} safe_peel={r.get('has_safe_peel')}{flag}")
    print(f"\nOBSTRUCTIONS: {len(obstructions)}")
    for name, how, r in obstructions[:50]:
        print(f"  [{name} {how}] N={r['N']} m={r['m']} gamma={r['gamma']} n2={r['n2']} "
              f"detail={r['detail']}")

def _rec(name, how, r, obstructions, near_tight):
    if not r.get("ok") or r.get("m", 0) < 2 or not r.get("B_connected"):
        return
    g = r.get("gamma"); n2 = r.get("n2")
    if g is None:
        return
    ratio = g / n2
    if ratio >= 0.80:
        near_tight.append((ratio, name, how, r))
    if r.get("ge_n2") and r.get("has_safe_peel") is False:
        obstructions.append((name, how, r))

if __name__ == "__main__":
    run()
