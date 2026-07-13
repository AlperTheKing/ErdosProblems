"""Exact structural audit of every R29 selector row (integer/set arithmetic only)."""
from collections import Counter, defaultdict, deque
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"

spec = importlib.util.spec_from_file_location("r29_lead", LEAD)
r29 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r29)
d = r29.build()
adj = r29.adjacency(d["n"], d["blue"])
blue_inc = defaultdict(set)
for e in d["blue"]:
    blue_inc[e[0]].add(e); blue_inc[e[1]].add(e)

# The reference tuple is the all-anchor tuple certified by d05/d09 and the
# global-minimum falsifier.  Multiplicities make the delta formula exact even
# when another row also uses the same vertex or edge.
base = list(d["rows"])
for i, meta in enumerate(d["selectorMeta"]):
    base[d["selectorStart"] + i] = meta["anchorRow"]

v_mult = Counter(v for row in base for v in row)
e_mult = Counter(r29.edge(a, b) for row in base for a, b in zip(row, row[1:]))
U0 = set(v_mult)
S0 = set(e_mult)
I0 = {e for e in d["blue"] if e[0] in U0 and e[1] in U0 and e not in S0}

def deltas(old, new):
    ov, nv = Counter(old), Counter(new)
    oe = Counter(r29.edge(a,b) for a,b in zip(old,old[1:]))
    ne = Counter(r29.edge(a,b) for a,b in zip(new,new[1:]))
    Uadd = {v for v in nv if v_mult[v] - ov[v] == 0}
    Udel = {v for v in ov if v_mult[v] - ov[v] > 0 and v_mult[v] - ov[v] + nv[v] == 0}
    U1 = (U0 | Uadd) - Udel
    Sadd = {e for e in ne if e_mult[e] - oe[e] == 0}
    Sdel = {e for e in oe if e_mult[e] - oe[e] > 0 and e_mult[e] - oe[e] + ne[e] == 0}
    S1 = (S0 | Sadd) - Sdel
    candidates=set(Sadd)|set(Sdel)
    for v in Uadd|Udel: candidates.update(blue_inc[v])
    Iadd=set(); Idel=set()
    for e in candidates:
        now=e[0] in U1 and e[1] in U1 and e not in S1
        before=e in I0
        if now and not before: Iadd.add(e)
        if before and not now: Idel.add(e)
    return Uadd, Udel, Iadd, Idel

def components(edges, vertices):
    a = defaultdict(list)
    for u,v in edges: a[u].append(v); a[v].append(u)
    out=[]; unseen=set(vertices)
    while unseen:
        s=min(unseen); seen={s}; q=deque([s]); unseen.remove(s)
        while q:
            u=q.popleft()
            for v in a[u]:
                if v in unseen: unseen.remove(v); seen.add(v); q.append(v)
        out.append(frozenset(seen))
    return out

def active_components(I, U):
    return [c for c in components(I,U)
            if any(u in c and v in c for u,v in d["bad"])]

def active_sizes_and_hubs(I, U):
    parent={v:v for v in U}; size={v:1 for v in U}
    def f(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for u,v in I:
        a,b=f(u),f(v)
        if a!=b:
            if size[a]<size[b]: a,b=b,a
            parent[b]=a; size[a]+=size[b]
    roots={f(u) for u,v in d["bad"] if u in U and v in U and f(u)==f(v)}
    hr=f(0)
    return tuple(sorted((size[r] for r in roots),reverse=True)), {h for h in (0,1,2) if f(h)==hr}

base_ac = active_components(I0,U0)
base_hub = next(c for c in base_ac if 0 in c)
assert {0,1,2} <= base_hub

classes=Counter(); active_signatures=Counter(); atom_summaries=[]; checked=0
all_ud=set(); all_ide=set(); all_changed_vertices=set()
for k,(atom,meta) in enumerate(zip(
        d["atoms"][d["selectorStart"]:d["selectorStop"]], d["selectorMeta"])):
    family=r29.shortest_rows(adj,*atom)
    assert len(family)==680
    assert sum(55 in row for row in family)==676
    old=meta["anchorRow"]
    per=Counter()
    for row in family:
        ua,ud,ia,ide=deltas(old,row)
        typ="anchor" if 55 in row else "local"
        key=(typ,len(ua),len(ud),len(ia),len(ide))
        classes[key]+=1; per[key]+=1; checked+=1
        if typ == "anchor":
            # No anchor alternative adds an I-edge.  The universal fixed hub
            # certificate below survives all deletions, and no new active
            # component can be born by deletion.
            assert not ia
            active_signatures[(typ, tuple(sorted(map(len,base_ac),reverse=True)))]+=1
        else:
            U1=(U0|ua)-ud; I1=(I0|ia)-ide
            sizes,hubs=active_sizes_and_hubs(I1,U1)
            assert hubs=={0,1,2}
            active_signatures[(typ,sizes)]+=1
        all_ud.update(ud); all_ide.update(ide)
        all_changed_vertices.update(ua|ud)
        all_changed_vertices.update(v for e in ia|ide for v in e)
    atom_summaries.append({"selector":k,"atom":atom,"region":meta["region"],
                           "classes":{"|".join(map(str,x)):n for x,n in sorted(per.items())}})

# One universal certificate replaces 459,680 redundant BFS runs.  Delete at
# once every vertex and I-edge that any single selector replacement can delete.
# The surviving graph is a subgraph of every replacement state.  Its hub
# component contains the whole old active hub component, so no replacement can
# split it; changed material is already in that component, so other active
# components are literally unchanged.  Added edges can only enlarge/merge it.
mandatory_U=U0-all_ud
fixed_I={e for e in I0-all_ide if e[0] in mandatory_U and e[1] in mandatory_U}
fixed_components=components(fixed_I,mandatory_U)
fixed_hub=next(c for c in fixed_components if 0 in c)
assert base_hub <= fixed_hub
other_active_vertices=set().union(*(c for c in base_ac if c != base_hub)) if len(base_ac)>1 else set()
assert not (all_changed_vertices & other_active_vertices)
assert {0,1,2} <= fixed_hub

result={
 "n":d["n"], "selectors":676, "rows_per_selector":680,
 "rows_checked":checked, "reference":"all-anchor",
 "base_U":len(U0), "base_I":len(I0),
 "base_active_component_sizes":sorted(map(len,base_ac),reverse=True),
 "base_hub_component_size":len(base_hub),
 "universal_fixed_hub_component_size":len(fixed_hub),
 "universally_deletable_vertices":len(all_ud),
 "universally_deletable_I_edges":len(all_ide),
 "changed_vertices_outside_reference_U":len(all_changed_vertices-U0),
 "global_classes":{"|".join(map(str,x)):n for x,n in sorted(classes.items())},
 "active_component_classes":{"|".join((x[0],",".join(map(str,x[1])))):n
                             for x,n in sorted(active_signatures.items())},
 "per_selector":atom_summaries,
 "lead_sha256":sha256(LEAD.read_bytes()).hexdigest(),
}
(HERE/"result.json").write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps({k:v for k,v in result.items() if k!="per_selector"},indent=2))
