#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 6: exhaustive sterile-shape enumeration for the
LIVE COMPONENT LOWER BOUND (t-uniform candidate lemma).

Setting: at a live state, the profile owner v has latent degree exactly 1
(unique latent edge = active edge).  Its active component C (in the latent
graph, all vertices selected) must CAPTURE a bad edge: some bad edge {a,b}
with a,b both in V(C).  Bad edges are monochromatic (same shore); latent
edges are blue (cross-shore).  Triangle-freeness of G forbids a bad pair
{a,b} having ANY common blue neighbour; in particular a common neighbour
inside C (latent subset of blue) is forbidden.  So a NECESSARY condition for
capture within shape H is: a same-shore pair {a,b} in V(H) with no common
H-neighbour.  (Sound for impossibility results: within-H exclusions are a
subset of the true exclusions.)

Enumeration: all connected bipartite graphs H with 1..6 edges (up to iso via
canonical form on <= 7 vertices), with a marked vertex v of H-degree exactly 1.
Report, per edge count e:
  - number of (shape, marked v) classes;
  - number admitting ANY capture pair;
  - capture pairs classified INCIDENT (v in pair) / REMOTE (v not in pair).
CLAIMS VERIFIED:
  C6a  e <= 3: NO shape admits a capture pair (=> every live state has >= 4
       latent edges in the owner's component; t-uniform, triangle-freeness only).
  C6b  e = 4: exactly one admitting class: the path P5 with v at an end; its
       unique capture pair = the two ends {v, b} (INCIDENT: vb must be bad).
  C6c  e = 5: full classification printed (remote capture becomes possible).
Also run WITHOUT the deg(v)=1 restriction (any marked vertex) for robustness.
"""
from itertools import combinations
from collections import defaultdict

def connected(n, edges):
    if n == 0:
        return False
    adj = defaultdict(set)
    for u, w in edges:
        adj[u].add(w); adj[w].add(u)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); stack.append(w)
    return len(seen) == n

def bipartite_classes(n, edges):
    """return shore colouring dict or None"""
    adj = defaultdict(set)
    for u, w in edges:
        adj[u].add(w); adj[w].add(u)
    col = {0: 0}
    stack = [0]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in col:
                col[w] = 1 - col[u]
                stack.append(w)
            elif col[w] == col[u]:
                return None
    return col

def canon(n, edges, marked):
    """canonical form of (graph, marked vertex) under vertex permutations"""
    from itertools import permutations
    best = None
    for p in permutations(range(n)):
        pe = tuple(sorted(tuple(sorted((p[u], p[w]))) for u, w in edges))
        key = (pe, p[marked])
        if best is None or key < best:
            best = key
    return best

def capture_pairs(n, edges, col):
    adj = defaultdict(set)
    for u, w in edges:
        adj[u].add(w); adj[w].add(u)
    out = []
    for a, b in combinations(range(n), 2):
        if col[a] != col[b]:
            continue                      # bad edges are same-shore
        if adj[a] & adj[b]:
            continue                      # common blue neighbour => triangle
        out.append((a, b))
    return out

def enumerate_shapes(max_e=6, require_deg1=True):
    """Counts RAW labelled (shape, marked v) pairs; canonicalizes ONLY the
    admitting ones (few) so the class claims stay exact while the sterile
    bulk is never permuted."""
    results = defaultdict(lambda: dict(raw=0, raw_admitting=0, classes_admitting=0,
                                       examples=[]))
    seen_admit = set()
    for e in range(1, max_e + 1):
        # graphs with e edges have at most e+1 vertices (connected)
        for n in range(2, e + 2):
            all_pairs = list(combinations(range(n), 2))
            for es in combinations(all_pairs, e):
                verts = set()
                for u, w in es:
                    verts |= {u, w}
                if verts != set(range(n)):
                    continue
                if not connected(n, es):
                    continue
                col = bipartite_classes(n, es)
                if col is None:
                    continue
                deg = defaultdict(int)
                for u, w in es:
                    deg[u] += 1; deg[w] += 1
                pairs = capture_pairs(n, es, col)
                for v in range(n):
                    if require_deg1 and deg[v] != 1:
                        continue
                    results[e]['raw'] += 1
                    if pairs:
                        results[e]['raw_admitting'] += 1
                        key = canon(n, es, v)
                        if key in seen_admit:
                            continue
                        seen_admit.add(key)
                        results[e]['classes_admitting'] += 1
                        inc = [p for p in pairs if v in p]
                        rem = [p for p in pairs if v not in p]
                        results[e]['examples'].append(
                            (n, tuple(es), v, tuple(inc), tuple(rem)))
    return results

def describe(es, n):
    deg = defaultdict(int)
    for u, w in es:
        deg[u] += 1; deg[w] += 1
    ds = sorted(deg[i] for i in range(n))
    # path test
    ispath = ds.count(1) == 2 and all(d <= 2 for d in ds)
    return f"degseq={ds}{' PATH' if ispath else ''}"

if __name__ == '__main__':
    print("=== marked vertex REQUIRED deg 1 (profile owner) ===")
    res = enumerate_shapes(6, require_deg1=True)
    ok = True
    for e in sorted(res):
        r = res[e]
        print(f"e={e}: raw={r['raw']} raw_admitting={r['raw_admitting']} "
              f"classes_admitting={r['classes_admitting']}")
        for (n, es, v, inc, rem) in r['examples'][:12]:
            print(f"   n={n} v={v} edges={es} {describe(es, n)} "
                  f"INCIDENT={inc} REMOTE={rem}")
    c6a = all(res[e]['raw_admitting'] == 0 for e in (1, 2, 3))
    print(f"C6a (e<=3 all sterile): {'PASS' if c6a else 'FAIL'}")
    ok &= c6a
    r4 = res[4]
    c6b = (r4['classes_admitting'] == 1)
    if c6b:
        (n, es, v, inc, rem) = r4['examples'][0]
        deg = defaultdict(int)
        for u, w in es:
            deg[u] += 1; deg[w] += 1
        ds = sorted(deg[i] for i in range(n))
        c6b = (n == 5 and ds == [1, 1, 2, 2, 2] and len(inc) == 1 and len(rem) == 0)
    print(f"C6b (e=4: unique admitting class = P5 end-marked, "
          f"single INCIDENT end-pair): {'PASS' if c6b else 'FAIL'}")
    ok &= c6b
    # e=5 classification summary
    r5 = res[5]
    n_inc_only = sum(1 for (_, _, _, inc, rem) in r5['examples'] if inc and not rem)
    n_rem_any = sum(1 for (_, _, _, inc, rem) in r5['examples'] if rem)
    print(f"C6c e=5: classes_admitting={r5['classes_admitting']} "
          f"(incident-only={n_inc_only}, with-remote={n_rem_any})")

    print()
    print("=== marked vertex UNRESTRICTED (any owner latent degree) ===")
    res2 = enumerate_shapes(5, require_deg1=False)
    for e in sorted(res2):
        r = res2[e]
        print(f"e={e}: raw={r['raw']} raw_admitting={r['raw_admitting']} "
              f"classes_admitting={r['classes_admitting']}")
    c6d = all(res2[e]['raw_admitting'] == 0 for e in (1, 2, 3))
    print(f"C6d (e<=3 sterile even without deg-1 marking): "
          f"{'PASS' if c6d else 'FAIL'}")
    ok &= c6d
    print()
    print("VERDICT:", "ALL PASS" if ok else "SOME FAIL")
