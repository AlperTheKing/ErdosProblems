r"""CLAUDE bounded descent probe below the invalidated 23115 'global minimum' on the reconstructed 2943 cage.

The d09 cell bound is FALSIFIED (witnesses in _claude_r29_cellbound_witnesses.json; best sample 23109). This probe
characterizes the true landscape below 23115:
  PHASE 1: single-local scan — for the first SCAN_K selectors of each region, evaluate all 4 local rows as a
           single-local move from the all-anchor tuple; record delta histogram (which locals are 'free' = negative,
           which activate a leaf = ~+198).
  PHASE 2: greedy stack — starting from all-anchor, add best-negative locals one at a time (re-evaluating exactly;
           keep if score strictly drops), cap GREEDY_CAP adds; report the best exact tuple found + its score.
  PHASE 3: Hall check at the best tuple found — rebuild the d05 owner-Hall gate (same semantics: same-first +
           row-companion sigma>=0 sources, half-0 reservation) at that tuple; report hub-shore demand/reach/defect.
All exact/integer. Deterministic. Output JSON: _claude_r29_descent_probe_result.json.
Run from repo root: python problems/23/writeup/_claude_r29_descent_probe.py
"""
import importlib.util
import json
import time
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
D09V = ROOT / "tmp/fanout/r29_gate/d09/retry2/verify.py"
SCAN_K = 80          # selectors scanned per region in phase 1
GREEDY_CAP = 80      # max greedy adds in phase 2
OWNERS = (0, 1, 2)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(u, v):
    return (u, v) if u < v else (v, u)


def hall_at(data, rows):
    """d05-equivalent owner-Hall at an arbitrary tuple (independent reimpl, same semantics)."""
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
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        for v in seen:
            comp[v] = root
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
                reserved = h == 0 and norm(o, y) in active_edges and o in av
                if not reserved:
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
                    reserved = h == 0 and e in active_edges and x in av
                    if not reserved:
                        masks[x, y, h] = masks.get((x, y, h), 0) | (1 << o)
    hist = Counter(masks.values())
    d_full = sum(demand.values())
    reach_full = sum(v for m, v in hist.items() if m & 7)
    return {"hubs_active": sorted(set(OWNERS) & av), "demand": demand, "demand_full": d_full,
            "reach_full": reach_full, "defect_full": d_full - reach_full,
            "active_vertices": len(av)}


def main():
    t0 = time.time()
    lead = load("r29_lead", LEAD)
    d09 = load("r29_d09_verify", D09V)
    data = lead.build()
    n = data["n"]
    start, stop = data["selectorStart"], data["selectorStop"]
    meta = data["selectorMeta"]
    base_rows = [tuple(r) for r in data["rows"]]
    adjb = d09.adj(n, data["blue"])
    fams = []
    for i, atom in enumerate(data["atoms"][start:stop]):
        fam = d09.shortest(adjb, *atom)
        locs = [tuple(x) for x in fam if 55 not in x]
        fams.append({"region": meta[i]["region"], "anchor": tuple(meta[i]["anchorRow"]), "locals": locs})
    anchor_rows = list(base_rows)
    for i, f in enumerate(fams):
        anchor_rows[start + i] = f["anchor"]
    s_anchor = d09.state(data, tuple(anchor_rows))["score"]
    print("all-anchor score = %d (expect 23115)" % s_anchor, flush=True)

    # PHASE 1: single-local scan
    reg_idx = {0: [i for i, f in enumerate(fams) if f["region"] == 0],
               1: [i for i, f in enumerate(fams) if f["region"] == 1]}
    deltas = []
    neg_moves = []
    for region in (0, 1):
        for i in reg_idx[region][:SCAN_K]:
            for li, lrow in enumerate(fams[i]["locals"]):
                rows = list(anchor_rows)
                rows[start + i] = lrow
                sc = d09.state(data, tuple(rows))["score"]
                d = sc - s_anchor
                deltas.append(d)
                if d < 0:
                    neg_moves.append((d, i, li))
    hist = Counter(deltas)
    print("PHASE1 single-local delta histogram (%d moves): %s" % (len(deltas), dict(sorted(hist.items()))), flush=True)

    # PHASE 2: greedy stack of negative moves (best deltas first, re-evaluated exactly)
    neg_moves.sort()
    cur = list(anchor_rows)
    cur_score = s_anchor
    added = []
    used = set()
    for d, i, li in neg_moves[:GREEDY_CAP]:
        if i in used:
            continue
        trial = list(cur)
        trial[start + i] = fams[i]["locals"][li]
        sc = d09.state(data, tuple(trial))["score"]
        if sc < cur_score:
            cur = trial
            cur_score = sc
            used.add(i)
            added.append({"selector": i, "local_index": li, "score_after": sc})
    print("PHASE2 greedy: %d adds, best score %d (delta %+d vs all-anchor)" % (len(added), cur_score, cur_score - s_anchor), flush=True)
    s2 = lead.scoped_state(data, tuple(cur))["score"]
    assert s2 == cur_score, (s2, cur_score)

    # PHASE 3: Hall at best tuple
    hall = hall_at(data, tuple(cur))
    print("PHASE3 Hall at best tuple: hubs_active=%s demand_full=%d reach_full=%d DEFECT=%d (active_vertices=%d)"
          % (hall["hubs_active"], hall["demand_full"], hall["reach_full"], hall["defect_full"], hall["active_vertices"]), flush=True)

    out = {"all_anchor_score": s_anchor, "scan_k_per_region": SCAN_K,
           "single_local_delta_histogram": {str(k): v for k, v in sorted(hist.items())},
           "greedy_adds": added, "best_score_found": cur_score,
           "best_tuple_local_choices": [{"selector": a["selector"], "local_index": a["local_index"]} for a in added],
           "hall_at_best": hall, "elapsed_sec": round(time.time() - t0, 1)}
    Path(__file__).with_name("_claude_r29_descent_probe_result.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("result JSON written; elapsed %.1fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
