r"""CLAUDE independent exact gate for R30's PATTERN 5 (quiescent-component attachment) on the 2943 cage.

CLAIMS UNDER TEST (R30, at the all-anchor tuple):
  P5-1 leaf ell=3's quiescent component K (in Q = B[V minus activeScope]) has exactly 1379 vertices;
  P5-2 its active attachment boundary is exactly {c_L=1, anchor=55};
  P5-3 the 14 lock-arm first vertices x_j = 56,58,...,82 all lie in K and pair(3,x_j)=0 (FreeHalf pairs);
  P5-4 every hub v in {0,1,2} is eligible: exists a,b in boundary with pair(v,a)>0, pair(v,b)>0 and
       activeComp(a)=activeComp(v)=activeComp(b);
  P5-5 the 28 halves (3,x_j,eps) are UNRESERVED and GENUINELY NEW (disjoint from the 19925 old sources);
  P5-6 switch loss of K is exactly 26 and >= 0 (max-cut annotation);
  P5-7 augmented Hall: old 19925 + new 28 = 19953 => ALL 8 hub-shore cuts have gap <= 0 (full shore exactly 0)
       => exact matching exists (Gale/Hall for 3 owners) => defect PAID.
BONUS: P5-augmented full-shore gap at the greedy-23055 tuple and one random tuple (informational).
All exact/integer. Run from repo root: python problems/23/writeup/_claude_r29_pattern5_gate.py
"""
import importlib.util
import random
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
D09V = ROOT / "tmp/fanout/r29_gate/d09/retry2/verify.py"
OWNERS = (0, 1, 2)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(u, v):
    return (u, v) if u < v else (v, u)


def full_state(data, rows):
    """Scope + owner-source internals (d05 semantics, my implementation)."""
    n = data["n"]
    blue = {norm(*e) for e in data["blue"]}
    bad = {norm(*e) for e in data["bad"]}
    pair = Counter()
    load_c = Counter()
    support = set()
    selected = set()
    for row in rows:
        for x in row:
            load_c[x] += 1
            selected.add(x)
        for x in row:
            for y in row:
                pair[x, y] += 1
        support.update(norm(a, b) for a, b in zip(row, row[1:]))
    active_edges = {e for e in blue if e not in support and e[0] in selected and e[1] in selected}
    adj = defaultdict(set)
    for u, v in active_edges:
        adj[u].add(v)
        adj[v].add(u)
    comp = {}
    for root in sorted(selected):
        if root in comp:
            continue
        seen = {root}
        q = deque([root])
        while q:
            u = q.popleft()
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    q.append(w)
        for w in seen:
            comp[w] = root
    bad_roots = {comp[u] for u, v in bad if u in comp and v in comp and comp[u] == comp[v]}
    av = {v for v in selected if comp[v] in bad_roots}
    deg = Counter()
    for u, v in active_edges:
        if comp[u] in bad_roots:
            deg[u] += 1
            deg[v] += 1
    collision = {v: 2 * sum(max(0, pair[v, y] - 1) for y in range(n)) for v in av}
    hit = {v: max(0, deg[v] - max(0, n - 5 * load_c[v])) for v in av}
    demand = {o: collision.get(o, 0) + hit.get(o, 0) for o in OWNERS}
    signed_degree = Counter()
    sign = {}
    for e in blue:
        sign[e] = 1
        signed_degree[e[0]] += 1
        signed_degree[e[1]] += 1
    for e in bad:
        sign[e] = -1
        signed_degree[e[0]] -= 1
        signed_degree[e[1]] -= 1
    companions = {o: {x for x in range(n) if pair[o, x] > 0} for o in OWNERS}
    masks = {}
    for o in OWNERS:
        for y in range(n):
            if y == o or pair[o, y] != 0:
                continue
            for h in (0, 1):
                if not (h == 0 and norm(o, y) in active_edges and o in av):
                    masks[o, y, h] = masks.get((o, y, h), 0) | (1 << o)
    for o in OWNERS:
        C = companions[o]
        for x in C:
            for y in C:
                if x == y or pair[x, y] != 0:
                    continue
                e = norm(x, y)
                if signed_degree[x] + signed_degree[y] - 2 * sign.get(e, 0) < 0:
                    continue
                for h in (0, 1):
                    if not (h == 0 and e in active_edges and x in av):
                        masks[x, y, h] = masks.get((x, y, h), 0) | (1 << o)
    return dict(n=n, blue=blue, bad=bad, pair=pair, selected=selected, support=support,
                active_edges=active_edges, comp=comp, av=av, demand=demand, masks=masks)


def hub_cuts(demand, masks, extra_mask7=0):
    hist = Counter(masks.values())
    out = []
    for shore_mask in range(8):
        d = sum(demand[o] for o in OWNERS if shore_mask & (1 << o))
        reach = sum(v for m, v in hist.items() if m & shore_mask)
        if shore_mask:
            reach += extra_mask7
        out.append((shore_mask, d, reach, d - reach))
    return out


def p5_at(data, rows, leaf=3, verbose=True):
    st = full_state(data, rows)
    n = st["n"]
    A = st["av"]
    quiet = [v for v in range(n) if v not in A]
    qadj = defaultdict(set)
    for u, v in st["blue"]:
        if u not in A and v not in A:
            qadj[u].add(v)
            qadj[v].add(u)
    qcomp = {}
    for root in quiet:
        if root in qcomp:
            continue
        seen = {root}
        q = deque([root])
        while q:
            u = q.popleft()
            for w in qadj[u]:
                if w not in seen:
                    seen.add(w)
                    q.append(w)
        for w in seen:
            qcomp[w] = root
    if leaf in A:
        return dict(leaf_active=True, st=st)
    K = {v for v in quiet if qcomp[v] == qcomp[leaf]}
    boundary = {a for a in A for z in K if norm(z, a) in st["blue"]}
    xs = [56 + 2 * j for j in range(14)]
    xs_ok = all(x in K for x in xs)
    free_ok = all(st["pair"][leaf, x] == 0 for x in xs)
    elig = {}
    for v in OWNERS:
        ok = any(st["pair"][v, a] > 0 and st["comp"].get(a) == st["comp"].get(v) for a in boundary)
        elig[v] = ok
    new_keys = [(leaf, x, h) for x in xs for h in (0, 1)]
    disjoint = all(k not in st["masks"] for k in new_keys)
    unreserved = all(not (h == 0 and norm(leaf, x) in st["active_edges"] and leaf in st["av"]) for (_, x, h) in new_keys)
    bcut = sum(1 for u, v in st["blue"] if (u in K) != (v in K))
    mcut = sum(1 for u, v in st["bad"] if (u in K) != (v in K))
    loss = bcut - mcut
    extra = len(new_keys) if all(elig.values()) and xs_ok and free_ok and disjoint and unreserved else 0
    cuts = hub_cuts(st["demand"], st["masks"], extra_mask7=extra)
    full = cuts[7]
    if verbose:
        print("  |K(leaf %d)| = %d (claim 1379) | boundary = %s (claim {1,55})" % (leaf, len(K), sorted(boundary)))
        print("  xs in K: %s | pair(leaf,x)=0 all: %s | hub eligibility: %s" % (xs_ok, free_ok, elig))
        print("  28 new keys disjoint from old sources: %s | unreserved: %s" % (disjoint, unreserved))
        print("  switch loss(K) = %d - %d = %d (claim 26, >=0)" % (bcut, mcut, loss))
        print("  augmented cuts (mask,d,reach,gap): %s" % [c for c in cuts if c[0] == 7])
    return dict(leaf_active=False, K=len(K), boundary=sorted(boundary), xs_ok=xs_ok, free_ok=free_ok,
                elig=elig, disjoint=disjoint, unreserved=unreserved, loss=loss,
                full_gap=full[3], all_cuts=cuts, st=st)


def main():
    lead = load("r29_lead", LEAD)
    d09 = load("r29_d09_verify", D09V)
    data = lead.build()
    start, stop = data["selectorStart"], data["selectorStop"]
    base_rows = [tuple(r) for r in data["rows"]]
    adjb = d09.adj(data["n"], data["blue"])
    fams = []
    for i, atom in enumerate(data["atoms"][start:stop]):
        fams.append([tuple(x) for x in d09.shortest(adjb, *atom)])
    anchor_rows = list(base_rows)
    for j in range(676):
        anchor_rows[start + j] = tuple(data["selectorMeta"][j]["anchorRow"])

    print("=== PATTERN-5 GATE at ALL-ANCHOR ===")
    r = p5_at(data, tuple(anchor_rows))
    ok = (not r["leaf_active"] and r["K"] == 1379 and r["boundary"] == [1, 55] and r["xs_ok"] and r["free_ok"]
          and all(r["elig"].values()) and r["disjoint"] and r["unreserved"] and r["loss"] == 26
          and r["full_gap"] == 0 and all(g <= 0 for (_, _, _, g) in r["all_cuts"]))
    print("ALL-ANCHOR VERDICT: %s" % ("PASS — 28/28 PAID, all 8 shores nonneg-slack => exact matching EXISTS"
                                       if ok else "FAIL %s" % {k: v for k, v in r.items() if k != "st"}))

    # BONUS: random tuple + all-local0 (informational)
    rng = random.Random(5)
    rand_rows = list(base_rows)
    for j in range(676):
        rand_rows[start + j] = fams[j][rng.randrange(len(fams[j]))]
    print("=== PATTERN-5 at RANDOM tuple (informational) ===")
    r2 = p5_at(data, tuple(rand_rows))
    print("  full-shore gap after P5(leaf3-only): %s (leaf3 active: %s)"
          % (r2.get("full_gap"), r2.get("leaf_active")))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
