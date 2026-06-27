#!/usr/bin/env python3
"""Adversarial angle: incidence-bipartite-plus (v2, efficient).

Strategy. Start from a high-girth BIPARTITE graph (parts X,Y) -- Heawood, Pappus,
Desargues, Mobius-Kantor, and the Levi incidence graphs. The natural bipartition
(X|Y) cuts EVERY original edge, so it is automatically a max cut of the bipartite
graph. Now add chords WITHIN one part (X-X or Y-Y). Each such chord:
  - is monochromatic under (X|Y) -> a bad edge (forces m>=2 with >=2 chords),
  - keeps triangle-freeness iff its endpoints share no common neighbor,
  - and (X|Y) REMAINS a max cut as long as adding chords doesn't create a larger
    cut. We VERIFY this by letting the harness compute the true maxcut and only
    keeping instances where (X|Y) achieves it (harness rejects a non-max forced side,
    and when side=None it auto-picks the true Gamma-min max cut, so we just read it).

We bias toward configurations that make Gamma LARGE (chords whose endpoints are
B-FAR apart raise (d_B+1)^2), to chase Gamma=N^2 tightness, and we record every
m>=2, Gamma>=N^2 instance and any has_safe_peel False.

Efficiency: max cut via a fast bitmask over the SMALLER part only is not valid in
general, so we cap auto-maxcut to N<=16 and for N in {18,20} we FORCE side=(X|Y)
and rely on the harness's max-cut check to confirm it's a true max cut (one
2^(n-1) enumeration per accepted instance, but we prune hard first).
"""
import itertools, random
from collections import deque
from peel_check import (check_instance, is_triangle_free, Bconnected, gamma_of,
                        maxcut_all, has_safe_peel)

# ---- bipartite named graphs with explicit 2-coloring (parts by parity of LCF index) ----
# We build each as an LCF graph; bipartite classes = even/odd vertex index works for
# these standard cyclic LCF drawings (Heawood/Pappus/Desargues/MK are bipartite with
# the even/odd 2-coloring of the Hamiltonian cycle, since all chord spans are odd).

def lcf_graph(n, lcf):
    adj = [set() for _ in range(n)]
    for i in range(n):
        j = (i + 1) % n
        adj[i].add(j); adj[j].add(i)
    for i in range(n):
        j = (i + lcf[i]) % n
        adj[i].add(j); adj[j].add(i)
    return adj

def bipartition_evenodd(n, adj):
    """Return side[] = vertex parity, and whether it is a valid 2-coloring (no mono edge)."""
    side = [v % 2 for v in range(n)]
    valid = all(side[u] != side[v] for u in range(n) for v in adj[u])
    return side, valid

NAMED = {
    "Heawood":      (14, [5, -5] * 7),
    "MobiusKantor": (16, [5, -5] * 8),
    "Pappus":       (18, [5, 7, -7, 7, -7, -5] * 3),
    "Desargues":    (20, [5, -5, 9, -9] * 5),
}

def adj_to_edges(n, adj):
    return [(u, v) for u in range(n) for v in adj[u] if v > u]

def part_chord_candidates(n, adj, side):
    """X-X and Y-Y pairs that are triangle-safe (no shared neighbor) and non-adjacent."""
    cands = []
    for u in range(n):
        for v in range(u + 1, n):
            if side[u] != side[v]:
                continue          # only within a part -> guaranteed monochromatic under (X|Y)
            if v in adj[u]:
                continue
            if adj[u] & adj[v]:
                continue          # shared neighbor -> would create triangle
            cands.append((u, v))
    return cands

def Bdist(n, adj, side, s, t):
    d = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if side[u] != side[v] and v not in d:
                d[v] = d[u] + 1; q.append(v)
    return d.get(t, None)

import sys
LOG = open("adv_plus2_results.txt", "w")
def out(*a):
    s = " ".join(str(x) for x in a)
    sys.stdout.write(s + "\n"); sys.stdout.flush(); LOG.write(s + "\n"); LOG.flush()

def run():
    random.seed(2026)
    obstructions = []
    near_tight = []     # (1 - gamma/n2) small
    tested = 0
    best_ratio = 0.0
    best_info = None

    for name, (n, lcf) in NAMED.items():
        adj0 = lcf_graph(n, lcf)
        side, valid = bipartition_evenodd(n, adj0)
        tf0 = is_triangle_free(n, adj0)
        # B-distance table within the original bipartite graph (side=parity)
        out(f"=== {name} N={n} bipartite2col={valid} triangle_free={tf0} ===")
        if not valid:
            out("   even/odd is NOT a 2-coloring; skip")
            continue
        cands = part_chord_candidates(n, adj0, side)
        # rank candidate chords by B-distance (far = large (d+1)^2 contribution)
        scored = []
        for (u, v) in cands:
            dist = Bdist(n, adj0, side, u, v)
            scored.append(((dist if dist is not None else 0), (u, v)))
        scored.sort(reverse=True)
        far = [uv for _, uv in scored]

        use_force = (n > 16)   # for N=18,20 force side=parity (harness verifies it's max)

        # ---- enumerate small sets of chords, biased to far (high-Gamma) ones ----
        # singles
        for (a, b) in far:
            adj = [set(s) for s in adj0]
            adj[a].add(b); adj[b].add(a)
            tested += 1
            r = check_instance(n, adj, side=side if use_force else None)
            _record(name, ("single", (a, b)), r, obstructions, near_tight)
        # doubles: pair far chords; ensure the two chords don't themselves create a triangle
        npick = 60 if n <= 16 else 40
        topfar = far[:npick]
        for (a, b), (c, d) in itertools.combinations(topfar, 2):
            adj = [set(s) for s in adj0]
            # add both; check triangle-free incrementally
            bad = False
            for (x, y) in [(a, b), (c, d)]:
                if y in adj[x] or (adj[x] & adj[y]):
                    bad = True; break
                adj[x].add(y); adj[y].add(x)
            if bad:
                continue
            tested += 1
            r = check_instance(n, adj, side=side if use_force else None)
            _record(name, ("double", ((a, b), (c, d))), r, obstructions, near_tight)
        # triples (only for N<=16 to bound runtime)
        if n <= 16:
            tp = far[:30]
            cnt = 0
            for trip in itertools.combinations(tp, 3):
                adj = [set(s) for s in adj0]
                bad = False
                for (x, y) in trip:
                    if y in adj[x] or (adj[x] & adj[y]):
                        bad = True; break
                    adj[x].add(y); adj[y].add(x)
                if bad:
                    continue
                tested += 1; cnt += 1
                r = check_instance(n, adj, side=None)
                _record(name, ("triple", trip), r, obstructions, near_tight)
                if cnt >= 6000:
                    break

    out(f"\n===== TESTED {tested} instances =====")
    near_tight.sort(key=lambda t: -t[0])
    out(f"NEAR-TIGHT / TIGHT (m>=2, by gamma/n2 ratio), top 25:")
    for ratio, name, how, r in near_tight[:25]:
        flag = " <<<OBSTRUCTION" if (r.get('has_safe_peel') is False and r.get('ge_n2')) else ""
        out(f"  ratio={ratio:.4f} [{name} {how}] N={r['N']} m={r['m']} gamma={r['gamma']} "
              f"n2={r['n2']} tight={r['tight']} Bconn={r['B_connected']} "
              f"safe_peel={r.get('has_safe_peel')}{flag}")
    out(f"\nOBSTRUCTIONS (tight gamma>=N^2, m>=2, no safe peel): {len(obstructions)}")
    for name, how, r in obstructions[:50]:
        out(f"  [{name} {how}] N={r['N']} m={r['m']} gamma={r['gamma']} n2={r['n2']} "
              f"side={r['side']} safe_peel={r['has_safe_peel']} detail={r['detail']}")

def _record(name, how, r, obstructions, near_tight):
    if not r.get("ok"):
        return
    if r.get("m", 0) < 2:
        return
    if not r.get("B_connected"):
        return
    gamma = r.get("gamma"); n2 = r.get("n2")
    if gamma is None:
        return
    ratio = gamma / n2
    if ratio >= 0.80:
        near_tight.append((ratio, name, how, r))
    if r.get("ge_n2") and r.get("has_safe_peel") is False:
        obstructions.append((name, how, r))

if __name__ == "__main__":
    run()
