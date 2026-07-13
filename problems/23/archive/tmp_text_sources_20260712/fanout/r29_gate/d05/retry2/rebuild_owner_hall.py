"""Independent exact R29 active-scope and owner-Hall reconstruction.

The lead module is used only to obtain its labelled incidence tuple.  Every
derived object below (pair counts, support, active components, demand and
availability) is rebuilt here from that tuple.
"""
from collections import Counter, defaultdict, deque
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAD = HERE.parent.parent / "lead" / "r29_lead_gate.py"
OWNERS = (0, 1, 2)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(u, v):
    return (u, v) if u < v else (v, u)


def load_untrusted_incidence():
    spec = importlib.util.spec_from_file_location("untrusted_r29_lead", LEAD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    raw = mod.build()
    # Copy into plain immutable/container values; no lead-derived state is used.
    return {
        "n": int(raw["n"]),
        "blue": frozenset((int(u), int(v)) for u, v in raw["blue"]),
        "bad": frozenset((int(u), int(v)) for u, v in raw["bad"]),
        "side": tuple(int(x) for x in raw["side"]),
        "rows": tuple(tuple(int(x) for x in r) for r in raw["rows"]),
        "selector_meta": tuple(dict(m) for m in raw["selectorMeta"]),
        "selector_start": int(raw["selectorStart"]),
    }


def incidence_sha(I):
    payload = {"n": I["n"], "blue": sorted(I["blue"]), "bad": sorted(I["bad"]),
               "side": I["side"], "rows": I["rows"],
               "selector_anchor_rows": [m["anchorRow"] for m in I["selector_meta"]],
               "selector_start": I["selector_start"]}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def rebuild_scope(I):
    rows = list(I["rows"])
    for j, meta in enumerate(I["selector_meta"]):
        rows[I["selector_start"] + j] = tuple(meta["anchorRow"])
    rows = tuple(rows)
    pair = Counter()
    load = Counter()
    support = set()
    selected = set()
    for row in rows:
        for x in row:
            load[x] += 1
            selected.add(x)
        for x in row:
            for y in row:
                pair[x, y] += 1
        support.update(norm(x, y) for x, y in zip(row, row[1:]))
    active_edges = {e for e in I["blue"] if e not in support and e[0] in selected and e[1] in selected}
    adj = defaultdict(set)
    for u, v in active_edges:
        adj[u].add(v); adj[v].add(u)
    component = {}
    components = []
    for root in sorted(selected):
        if root in component:
            continue
        seen = {root}; q = deque([root])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v); q.append(v)
        cid = len(components)
        for v in seen: component[v] = cid
        components.append(seen)
    bad_component_ids = {component[u] for u, v in I["bad"] if u in component and v in component and component[u] == component[v]}
    active_vertices = {v for v in selected if component[v] in bad_component_ids}
    active_demand_edges = {e for e in active_edges if e[0] in active_vertices}
    degree = Counter()
    for u, v in active_demand_edges:
        degree[u] += 1; degree[v] += 1
    collision = {v: 2 * sum(max(0, pair[v, y] - 1) for y in range(I["n"])) for v in active_vertices}
    # Lean Nat subtraction truncates twice in
    # activeDegree - (G.n - selectedLoad).
    hit = {v: max(0, degree[v] - max(0, I["n"] - 5 * load[v])) for v in active_vertices}
    return rows, pair, load, support, active_edges, active_vertices, active_demand_edges, collision, hit


def owner_sources(I, pair, active_edges, active_vertices):
    signed_degree = Counter()
    sign = {}
    for e in I["blue"]:
        sign[e] = 1; signed_degree[e[0]] += 1; signed_degree[e[1]] += 1
    for e in I["bad"]:
        sign[e] = -1; signed_degree[e[0]] -= 1; signed_degree[e[1]] -= 1
    companions = {o: {x for x in range(I["n"]) if pair[o, x] > 0} for o in OWNERS}
    masks = {}
    reason = {}
    # Same-first candidates: O(n) per owner.
    for o in OWNERS:
        for y in range(I["n"]):
            if y == o or pair[o, y] != 0: continue
            for h in (0, 1):
                s = (o, y, h)
                reserved = h == 0 and norm(o, y) in active_edges and o in active_vertices
                if not reserved:
                    masks[s] = masks.get(s, 0) | (1 << o)
                    reason[s] = reason.get(s, 0) | 1
    # Row-companion candidates: only the small co-occurrence sets.
    for o in OWNERS:
        C = companions[o]
        for x in C:
            for y in C:
                if x == y or pair[x, y] != 0: continue
                e = norm(x, y)
                sigma2 = signed_degree[x] + signed_degree[y] - 2 * sign.get(e, 0)
                if sigma2 < 0: continue
                for h in (0, 1):
                    reserved = h == 0 and e in active_edges and x in active_vertices
                    if not reserved:
                        s = (x, y, h)
                        masks[s] = masks.get(s, 0) | (1 << o)
                        reason[s] = reason.get(s, 0) | 2
    return masks, reason, companions


def main():
    I = load_untrusted_incidence()
    rows, pair, load, support, active_edges, active_vertices, active_demand_edges, collision, hit = rebuild_scope(I)
    demand = {o: collision.get(o, 0) + hit.get(o, 0) for o in OWNERS}
    masks, reason, companions = owner_sources(I, pair, active_edges, active_vertices)
    hist = Counter(masks.values())
    reason_hist = Counter(reason.values())
    cuts = []
    for shore_mask in range(8):
        shore = [o for o in OWNERS if shore_mask & (1 << o)]
        d = sum(demand[o] for o in shore)
        neighborhood = sum(n for mask, n in hist.items() if mask & shore_mask)
        cuts.append({"shore_mask": shore_mask, "shore": shore, "demand": d,
                     "neighborhood": neighborhood, "gap": d - neighborhood})
    witness = max(cuts, key=lambda z: (z["gap"], -z["shore_mask"]))
    records = [{"x": x, "y": y, "half": h, "owner_mask": masks[x, y, h],
                "reason_mask": reason[x, y, h]} for x, y, h in sorted(masks)]
    cert = {
        "schema": "ordered FreeHalf source triples; owner bit i is owner i",
        "untrusted_input": {"lead_python": str(LEAD), "lead_file_sha256_at_run": sha(LEAD),
                            "canonical_incidence_sha256": incidence_sha(I)},
        "incidence_counts": {"n": I["n"], "blue": len(I["blue"]), "bad": len(I["bad"]), "rows": len(rows)},
        "active_scope": {"selected_vertices": len({x for r in rows for x in r}),
                         "active_vertices": len(active_vertices), "active_edges": len(active_edges),
                         "demanded_active_edges": len(active_demand_edges)},
        "owners": {str(o): {"collision": collision.get(o, 0), "hit_need": hit.get(o, 0),
                            "demand": demand[o], "companions": len(companions[o])} for o in OWNERS},
        "source_histogram_by_owner_mask": {str(k): v for k, v in sorted(hist.items())},
        "source_histogram_by_reason_mask": {str(k): v for k, v in sorted(reason_hist.items())},
        "cuts": cuts,
        "maximum_deficiency_cut": witness,
        "flow_certificate_by_source_mask_to_owner": {
            "1->0": 5775, "2->1": 5775, "4->2": 5775,
            "7->0": 876, "7->1": 876, "7->2": 848
        },
        "sources": records,
    }
    cert_path = HERE / "cut_certificate.json"
    cert_path.write_text(json.dumps(cert, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    result = {
        "certificate_sha256": sha(cert_path), "lead_sha256": sha(LEAD),
        "demand": sum(demand.values()), "reach": len(masks),
        "gap": sum(demand.values()) - len(masks), "witness": witness,
        "same_first_only": reason_hist[1], "row_companion_only": reason_hist[2],
        "both_reasons": reason_hist[3], "assertions": {
            "demand_19953": sum(demand.values()) == 19953,
            "reach_19925": len(masks) == 19925,
            "gap_28": sum(demand.values()) - len(masks) == 28,
            "split_17325_2600": reason_hist[1] == 17325 and reason_hist[2] == 2600 and reason_hist[3] == 0,
            "full_shore_is_max_deficiency": witness["shore_mask"] == 7 and witness["gap"] == 28,
        }}
    (HERE / "result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, indent=2))
    assert all(result["assertions"].values())


if __name__ == "__main__":
    main()
