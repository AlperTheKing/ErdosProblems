"""Independent integer audit of the R29 four-pattern owner-quotient cut.

Rebuilds the exact source relation, expands every ordered cell into its
unreserved half keys, and sums cut capacities directly (not from certificate
histograms).  No floating-point arithmetic is used.
"""
from collections import Counter, defaultdict, deque
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
OWNERS = range(3)


def edge(x, y):
    return (x, y) if x < y else (y, x)


spec = spec_from_file_location("r29", LEAD)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)
d = mod.build()
rows = list(d["rows"])
for i, meta in enumerate(d["selectorMeta"]):
    rows[d["selectorStart"] + i] = tuple(meta["anchorRow"])

pair = Counter((x, y) for row in rows for x in row for y in row)
selected = {x for row in rows for x in row}
support = {edge(x, y) for row in rows for x, y in zip(row, row[1:])}
active = {e for e in d["blue"] if e not in support and e[0] in selected and e[1] in selected}

# Active components and the demanded active component scope.
parent = {x: x for x in selected}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(x, y):
    x, y = find(x), find(y)
    if x != y:
        parent[max(x, y)] = min(x, y)
for x, y in active:
    union(x, y)
roots = {find(x) for x, y in d["bad"] if x in selected and y in selected and find(x) == find(y)}
demanded_active = {e for e in active if find(e[0]) in roots}
selected_component = {x: find(x) for x in selected}

# Outside blue components and owner eligibility.
adj = defaultdict(set)
for x, y in d["blue"]:
    adj[x].add(y); adj[y].add(x)
cid = {}
components = []
attachments = []
for root in range(d["n"]):
    if root in selected or root in cid:
        continue
    k = len(components); cid[root] = k; todo = deque([root]); comp = set(); att = set()
    while todo:
        x = todo.popleft(); comp.add(x)
        for y in adj[x]:
            if y in selected: att.add(y)
            elif y not in cid: cid[y] = k; todo.append(y)
    components.append(comp); attachments.append(att)
eligible_out = {
    o: {x for k, att in enumerate(attachments)
        if any(pair[o, a] and selected_component[a] == selected_component[o] for a in att)
        for x in components[k]}
    for o in OWNERS
}

sign = {e: 1 for e in d["blue"]}
sign.update({e: -1 for e in d["bad"]})
def loss(vertices):
    return sum(s for (x, y), s in sign.items() if (x in vertices) != (y in vertices))
component_loss = [loss(comp) for comp in components]
cross_sign = Counter()
for (x,y), s in sign.items():
    if x in cid and y in cid and cid[x] != cid[y]:
        cross_sign[edge(cid[x],cid[y])] += s
def union_loss(k, ell):
    if k == ell: return component_loss[k]
    return component_loss[k] + component_loss[ell] - 2*cross_sign[edge(k,ell)]

# owner_mask is eligibility of an ordered cell.  Provenance is irrelevant:
# overlapping patterns do not create another copy of either half.
owner_mask = {}
def add(o, cell): owner_mask[cell] = owner_mask.get(cell, 0) | (1 << o)
badnbr = defaultdict(set)
for x, y in d["bad"]: badnbr[x].add(y); badnbr[y].add(x)
companions = {o: {x for x in range(d["n"]) if pair[o, x]} for o in OWNERS}
for o in OWNERS:
    for y in range(d["n"]):
        if y != o and not pair[o, y]: add(o, (o, y))
    for x in badnbr[o]:
        for y in badnbr[o]:
            if x != y and not pair[x, y] and loss({x, y}) >= 0: add(o, (x, y))
    for x in companions[o]:
        for y in companions[o]:
            if x != y and not pair[x, y] and loss({x, y}) >= 0: add(o, (x, y))
    for x in eligible_out[o]:
        for y in eligible_out[o]:
            if x != y and union_loss(cid[x],cid[y]) >= 0: add(o, (x, y))

# Directly expand half keys. Reserved means precisely half 0 of an active edge.
halves = []
for (x, y), mask in owner_mask.items():
    for h in (0, 1):
        if not (h == 0 and edge(x, y) in demanded_active):
            halves.append((x, y,h,mask))

mask_capacity = Counter(mask for x,y,h,mask in halves)
assert mask_capacity == {1: 5775, 2: 5775, 4: 5775, 7: 2600}
reservations = sorted((x,y,0) for (x,y) in owner_mask if edge(x,y) in demanded_active)
assert reservations == [(0,55,0),(1,2929,0),(2,2930,0)]

def cuts(per_owner):
    total = sum(per_owner.values()); out = []
    for shore in range(8):
        ds = sum(per_owner[o] for o in OWNERS if shore & (1 << o))
        # Independent direct summation over expanded half keys.
        crossing_sources = sum(1 for x,y,h,mask in halves if mask & shore)
        cap = total - ds + crossing_sources
        out.append({"shore_mask":shore,"demand":ds,"source_capacity":crossing_sources,
                    "cut_capacity":cap,"deficiency":ds-crossing_sources})
    return out

aux = cuts({0:6651,1:6651,2:6651})
literal = cuts({0:6650,1:6650,2:6650})
assert min(x["cut_capacity"] for x in aux) == 19925
assert min(x["cut_capacity"] for x in literal) == 19925
assert max(x["deficiency"] for x in aux) == 28
assert max(x["deficiency"] for x in literal) == 25

result = {
  "arithmetic":"integers only",
  "expanded_unreserved_half_keys":len(halves),
  "capacity_by_owner_mask":dict(sorted(mask_capacity.items())),
  "reservations":reservations,
  "auxiliary_demand_including_hit_need":aux,
  "literal_collision_demand_after_reservation":literal,
  "auxiliary_min_cut":min(x["cut_capacity"] for x in aux),
  "literal_collision_min_cut":min(x["cut_capacity"] for x in literal),
}
(HERE / "certificate.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="ascii")
print(json.dumps(result,sort_keys=True))
