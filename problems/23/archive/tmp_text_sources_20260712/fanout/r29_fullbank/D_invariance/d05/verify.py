#!/usr/bin/env python3
"""Exact selector-invariance verifier for the R29 N=2943 instance.

GRAPH REUSE (and only graph reuse): load r29_lead_gate.build() to obtain the
labelled incidence structure.  Shortest rows, scoped state, demand, source
reach, signatures, and all counts below are independently implemented.
"""
from collections import Counter, defaultdict, deque
import hashlib, importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAD = HERE.parents[2] / "r29_gate" / "lead" / "r29_lead_gate.py"
OWNERS = (0, 1, 2)

def edge(a, b): return (a, b) if a < b else (b, a)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def graph_input():
    s = importlib.util.spec_from_file_location("graph_only", LEAD)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    d = m.build()
    return {"n": int(d["n"]), "blue": frozenset(map(tuple, d["blue"])),
            "bad": frozenset(map(tuple, d["bad"])),
            "rows": tuple(map(tuple, d["rows"])), "atoms": tuple(map(tuple, d["atoms"])),
            "start": int(d["selectorStart"]), "stop": int(d["selectorStop"]),
            "dx": frozenset(int(x) for x in d["dXToLeaf"])}

def adjacency(n, es):
    a = [[] for _ in range(n)]
    for u, v in es: a[u].append(v); a[v].append(u)
    for z in a: z.sort()
    return a

def shortest_rows(adj, s, t):
    ds = [-1] * len(adj); dt = [-1] * len(adj)
    for root, dist in ((s, ds), (t, dt)):
        dist[root] = 0; q = deque([root])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] < 0: dist[v] = dist[u] + 1; q.append(v)
    assert ds[t] == 4
    out = []
    def walk(p):
        u = p[-1]
        if u == t: out.append(tuple(p)); return
        for v in adj[u]:
            if ds[v] == ds[u] + 1 and ds[v] + dt[v] == 4: walk(p + [v])
    walk([s]); return tuple(out)

def state(I, rows):
    """Independent integer implementation of pair/load/support/active state."""
    pair, load, support, selected = Counter(), Counter(), set(), set()
    for r in rows:
        selected.update(r)
        for x in r: load[x] += 1
        for x in r:
            for y in r: pair[x, y] += 1
        support.update(edge(x, y) for x, y in zip(r, r[1:]))
    ae = {e for e in I["blue"] if e not in support and e[0] in selected and e[1] in selected}
    ad = defaultdict(list)
    for u, v in ae: ad[u].append(v); ad[v].append(u)
    comp, groups = {}, []
    for root in sorted(selected):
        if root in comp: continue
        seen = {root}; q = deque([root])
        while q:
            u = q.popleft()
            for v in ad[u]:
                if v not in seen: seen.add(v); q.append(v)
        k = len(groups); groups.append(seen)
        for v in seen: comp[v] = k
    badc = {comp[u] for u, v in I["bad"] if u in comp and v in comp and comp[u] == comp[v]}
    active = {v for v in selected if comp[v] in badc}
    deg = Counter()
    for u, v in ae:
        if u in active and v in active: deg[u] += 1; deg[v] += 1
    collision = {o: 2 * sum(max(0, pair[o, y] - 1) for y in range(I["n"])) for o in OWNERS}
    hit = {o: max(0, deg[o] - max(0, I["n"] - 5 * load[o])) for o in OWNERS}
    return pair, load, support, ae, active, collision, hit

def sources(I, pair, ae, active):
    sd, sign = Counter(), {}
    for e in I["blue"]: sign[e] = 1; sd[e[0]] += 1; sd[e[1]] += 1
    for e in I["bad"]: sign[e] = -1; sd[e[0]] -= 1; sd[e[1]] -= 1
    masks = {}
    for o in OWNERS:
        C = {x for x in range(I["n"]) if pair[o, x] > 0}
        for y in range(I["n"]):
            if y != o and pair[o, y] == 0:
                for h in (0, 1):
                    if not (h == 0 and edge(o, y) in ae and o in active):
                        masks[o, y, h] = masks.get((o, y, h), 0) | (1 << o)
        for x in C:
            for y in C:
                e = edge(x, y) if x != y else None
                if x == y or pair[x, y] or sd[x] + sd[y] - 2 * sign.get(e, 0) < 0: continue
                for h in (0, 1):
                    if not (h == 0 and e in ae and x in active):
                        masks[x, y, h] = masks.get((x, y, h), 0) | (1 << o)
    return masks

def main():
    I = graph_input(); adj = adjacency(I["n"], I["blue"])
    fixed = I["rows"][:I["start"]] + I["rows"][I["stop"]:]
    fixed_support = {edge(x, y) for r in fixed for x, y in zip(r, r[1:])}
    owner_incident = {e for e in I["blue"] if e[0] in OWNERS or e[1] in OWNERS}
    fixed_pair, _, _, _, _, _, _ = state(I, fixed)
    companions = {x for o in OWNERS for x in range(I["n"]) if fixed_pair[o, x] > 0}
    signatures, family_profiles, all_selector_support = Counter(), Counter(), set()
    option_total = 0
    for atom in I["atoms"][I["start"]:I["stop"]]:
        fam = shortest_rows(adj, *atom); assert len(fam) == 680
        local = Counter()
        for r in fam:
            sup = frozenset(edge(x, y) for x, y in zip(r, r[1:]))
            all_selector_support.update(sup)
            sig = (55 in r, sum(x in I["dx"] for x in r),
                   len(sup & fixed_support), len(sup & owner_incident),
                   sum(x in OWNERS for x in r), sum(x in companions for x in r))
            signatures[sig] += 1; local[sig] += 1; option_total += 1
            assert len(r) == len(set(r)) == 5 and edge(r[0], r[-1]) == atom
            assert all(e in I["blue"] for e in sup)
            assert sig[3:] == (0, 0, 0)
        family_profiles[tuple(sorted(local.items()))] += 1

    # One representative tuple suffices after the exhaustive dependency firewall:
    # selectors change neither owner pair/load nor owner-incident support/selection.
    rows = I["rows"]
    pair, load, support, ae, active, collision, hit = state(I, rows)
    # Worst deletion check: remove every edge that any selector option could
    # support.  Fixed selected vertices still leave every owner in a component
    # containing a bad edge.  Any tuple deletes a subset of these edges.
    worst_blue = frozenset(I["blue"] - all_selector_support)
    W = dict(I); W["blue"] = worst_blue
    _, _, _, _, worst_active, _, _ = state(W, fixed)
    assert all(o in worst_active for o in OWNERS)
    masks = sources(I, pair, ae, active); hist = Counter(masks.values())
    demand = {o: collision[o] + hit[o] for o in OWNERS}
    cuts = []
    for sm in range(8):
        d = sum(demand[o] for o in OWNERS if sm >> o & 1)
        reach = sum(v for m, v in hist.items() if m & sm)
        cuts.append({"shore_mask": sm, "demand": d, "reach": reach, "gap": d-reach})
    sig_json = [{"contains_anchor55": k[0], "dX_count": k[1],
                 "fixed_support_edges": k[2], "owner_support_edges": k[3],
                 "owner_vertices": k[4], "owner_companion_vertices": k[5],
                 "options": v} for k,v in sorted(signatures.items())]
    result = {
      "schema": "r29-selector-invariance-v1", "pass": True,
      "graph_reuse": {"only": "r29_lead_gate.build labelled incidence", "sha256": digest(LEAD)},
      "counts": {"n": I["n"], "families": 676, "options_per_family": 680,
                 "options_checked": option_total, "tuples_enumerated": 0},
      "support_signatures": sig_json,
      "distinct_family_profiles": len(family_profiles),
      "worst_case_firewall": {"union_selector_support_edges": len(all_selector_support),
                               "owners_active_after_deleting_union": sorted(worst_active & set(OWNERS))},
      "owner_state": {str(o): {"active": o in active, "load": load[o],
                       "collision_half": collision[o], "hit_need": hit[o],
                       "demand": demand[o]} for o in OWNERS},
      "source_mask_histogram": {str(k): v for k,v in sorted(hist.items())},
      "all_shores": cuts,
      "strongest_verified_statement": "For every one of 680^676 selector tuples, the per-owner demand vector, source owner-mask set, and all eight shore demand/reach/gap triples equal those reported here.",
      "full_shore": cuts[7]
    }
    assert option_total == 676*680 and len(family_profiles) == 1
    assert all(x["owner_support_edges"] == x["owner_vertices"] == x["owner_companion_vertices"] == 0 for x in sig_json)
    assert sum(demand.values()) == 19953 and len(masks) == 19925 and cuts[7]["gap"] == 28
    out = HERE / "result.json"; out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__": main()
