"""Worker 7 exact adversarial audit of the R29 four-pattern count."""
from collections import Counter, defaultdict, deque
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
TUPLE = ROOT / "tmp/fanout/r29_gate/d09/retry2/best_tuple.json"
CERT = ROOT / "tmp/fanout/r29_fullbank/B_fourpattern/certificate.json"
OUT = Path(__file__).resolve().parent / "audit.json"
OWNERS = (0, 1, 2)

def norm(x, y): return (x, y) if x < y else (y, x)
def digest(p): return sha256(p.read_bytes()).hexdigest()

def components(vertices, edges):
    adj = defaultdict(set)
    for x, y in edges:
        adj[x].add(y); adj[y].add(x)
    label = {}
    blocks = []
    for root in sorted(vertices):
        if root in label: continue
        k = len(blocks); seen = {root}; q = deque([root]); label[root] = k
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y in vertices and y not in seen:
                    seen.add(y); label[y] = k; q.append(y)
        blocks.append(seen)
    return label, blocks

def main():
    spec = spec_from_file_location("r29_input", LEAD)
    mod = module_from_spec(spec); spec.loader.exec_module(mod); d = mod.build()
    witness = json.loads(TUPLE.read_text())
    rows = list(map(tuple, d["rows"]))
    tuple_rows = [tuple(z["row"]) for z in witness["selector_choices"]]
    anchor_rows = [tuple(z["anchorRow"]) for z in d["selectorMeta"]]
    assert tuple_rows == anchor_rows
    for j, row in enumerate(tuple_rows): rows[d["selectorStart"] + j] = row

    selected = {x for row in rows for x in row}
    pair = Counter((x, y) for row in rows for x in row for y in row)
    load = Counter(x for row in rows for x in row)
    support = {norm(x, y) for row in rows for x, y in zip(row, row[1:])}
    active_edges = {e for e in d["blue"] if e not in support and set(e) <= selected}
    selected_cid, selected_comps = components(selected, active_edges)
    bad_cids = {selected_cid[x] for x, y in d["bad"]
                if x in selected_cid and y in selected_cid and selected_cid[x] == selected_cid[y]}
    active_vertices = {x for x in selected if selected_cid[x] in bad_cids}
    demanded_edges = {e for e in active_edges if e[0] in active_vertices}
    degree = Counter(x for e in demanded_edges for x in e)
    collision = {x: 2 * sum(max(0, pair[x, y] - 1) for y in range(d["n"])) for x in active_vertices}
    hit = {x: max(0, degree[x] - max(0, d["n"] - 5 * load[x])) for x in active_vertices}
    demand = {o: collision[o] + hit[o] for o in OWNERS}

    # Outside blue components and their selected attachment boundaries.
    outside = set(range(d["n"])) - selected
    outside_edges = {e for e in d["blue"] if set(e) <= outside}
    outside_cid, outside_comps = components(outside, outside_edges)
    attachments = [set() for _ in outside_comps]
    for x, y in d["blue"]:
        if x in outside and y in selected: attachments[outside_cid[x]].add(y)
        if y in outside and x in selected: attachments[outside_cid[y]].add(x)

    relaxed = {}; scoped = {}; witness_cids = {}
    for o in OWNERS:
        relaxed[o] = set(); scoped[o] = set(); witness_cids[o] = Counter()
        for k, block in enumerate(outside_comps):
            ws = {a for a in attachments[k] if pair[o, a] > 0}
            for a in ws: witness_cids[o][selected_cid[a]] += len(block)
            if ws: relaxed[o] |= block
            if any(selected_cid[a] == selected_cid[o] for a in ws): scoped[o] |= block

    # Rebuild old sources as ordered cells, deduplicating across patterns/owners.
    signed_degree = Counter(); sign = {}
    for e in d["blue"]: sign[e] = 1; signed_degree[e[0]] += 1; signed_degree[e[1]] += 1
    for e in d["bad"]: sign[e] = -1; signed_degree[e[0]] -= 1; signed_degree[e[1]] -= 1
    badn = defaultdict(set)
    for x, y in d["bad"]: badn[x].add(y); badn[y].add(x)
    masks = {}; reasons = {}; reservations = set()
    def add(o, cell, reason):
        masks[cell] = masks.get(cell, 0) | (1 << o); reasons[cell] = reasons.get(cell, 0) | reason
    for o in OWNERS:
        for y in range(d["n"]):
            if y != o and pair[o, y] == 0: add(o, (o, y), 1)
        for pool, bit in ((badn[o], 2), ({x for x in range(d["n"]) if pair[o, x]}, 4)):
            for x in pool - {o}:
                for y in pool - {o}:
                    if x != y and pair[x, y] == 0 and signed_degree[x] + signed_degree[y] - 2 * sign.get(norm(x,y), 0) >= 0:
                        add(o, (x, y), bit)
    def cap(cell):
        if norm(*cell) in demanded_edges and cell[0] in active_vertices:
            reservations.add(cell); return 1
        return 2
    old_capacity = sum(cap(c) for c in masks)
    old_hist = Counter()
    for c, mask in masks.items(): old_hist[mask] += cap(c)

    # Add outside sources twice: relaxed implementation and canonical-spec scoped version.
    def augmented(eligible):
        mm = dict(masks)
        for o in OWNERS:
            for x in eligible[o]:
                for y in eligible[o]:
                    if x != y: mm[x, y] = mm.get((x, y), 0) | (1 << o)
        hist = Counter()
        for c, mask in mm.items(): hist[mask] += cap(c)
        cuts = []
        total = sum(demand.values())
        for shore in range(8):
            dem = sum(demand[o] for o in OWNERS if shore & (1 << o))
            reach = sum(v for mask, v in hist.items() if mask & shore)
            cuts.append([shore, dem, reach, dem-reach, total-dem+reach])
        return mm, hist, cuts
    relaxed_m, relaxed_h, relaxed_cuts = augmented(relaxed)
    scoped_m, scoped_h, scoped_cuts = augmented(scoped)

    result = {
      "sha256": {"lead": digest(LEAD), "tuple": digest(TUPLE), "claimed_certificate": digest(CERT)},
      "tuple": {"rows": len(rows), "selector_rows": len(tuple_rows), "selected": len(selected),
                "tuple_rows_equal_anchor_rows": tuple_rows == anchor_rows},
      "scope": {"active_vertices": len(active_vertices), "active_edges": len(active_edges),
                "demanded_active_edges": len(demanded_edges), "owner_component_ids": [selected_cid[o] for o in OWNERS],
                "owner_component_size": len(selected_comps[selected_cid[0]])},
      "demand": {str(o): {"collision": collision[o], "hit": hit[o], "total": demand[o]} for o in OWNERS},
      "outside": {"vertices": len(outside), "components": len(outside_comps),
                  "size_histogram": dict(sorted(Counter(map(len, outside_comps)).items()))},
      "eligible_outside_vertices": {str(o): {"relaxed": len(relaxed[o]), "component_scoped": len(scoped[o]),
                  "attachment_witness_component_histogram": dict(sorted(witness_cids[o].items()))} for o in OWNERS},
      "old_sources": {"unique_ordered_cells": len(masks), "capacity_after_reservations": old_capacity,
                      "capacity_by_owner_mask": dict(sorted(old_hist.items())),
                      "reserved_ordered_cells": sorted(map(list, reservations))},
      "relaxed_four_pattern": {"unique_ordered_cells": len(relaxed_m), "capacity": sum(relaxed_h.values()),
                                "capacity_by_owner_mask": dict(sorted(relaxed_h.items())), "cuts": relaxed_cuts},
      "component_scoped_four_pattern": {"unique_ordered_cells": len(scoped_m), "capacity": sum(scoped_h.values()),
                                "capacity_by_owner_mask": dict(sorted(scoped_h.items())), "cuts": scoped_cuts},
    }
    OUT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__": main()
