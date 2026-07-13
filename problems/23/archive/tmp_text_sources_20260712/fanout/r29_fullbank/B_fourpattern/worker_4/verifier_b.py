"""Independent exact R29 four-pattern hub-shore accounting verifier.

Only the canonical R29 graph constructor is imported.  Tuple incidence,
active components, demands, pattern eligibility, capacities, and Hall shores
are rebuilt here with integer arithmetic (Fraction is used for Q reporting).
"""
from collections import Counter, defaultdict, deque
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CANON = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
OUT = HERE / "certificate_b.json"
OWNERS = (0, 1, 2)

def edge(a, b): return (a, b) if a < b else (b, a)
def digest(path): return sha256(path.read_bytes()).hexdigest()
def qtext(n):
    q = Fraction(n, 2)
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"

def canonical():
    s = spec_from_file_location("canonical_r29_worker4", CANON)
    assert s and s.loader
    m = module_from_spec(s); s.loader.exec_module(m)
    return m, m.build()

def tuple_primitives(d):
    rows = [tuple(r) for r in d["rows"]]
    for i, meta in enumerate(d["selectorMeta"]):
        rows[d["selectorStart"] + i] = tuple(meta["anchorRow"])
    pair, load = Counter(), Counter()
    chosen, row_edges = set(), set()
    for r in rows:
        chosen.update(r)
        for x in r:
            load[x] += 1
            for y in r: pair[x, y] += 1
        row_edges.update(edge(x, y) for x, y in zip(r, r[1:]))
    return tuple(rows), pair, load, chosen, row_edges

def active_and_demand(d, pair, load, chosen, row_edges):
    active = {e for e in d["blue"] if e not in row_edges and e[0] in chosen and e[1] in chosen}
    parent = {v: v for v in chosen}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def join(x, y):
        x, y = find(x), find(y)
        if x != y: parent[max(x,y)] = min(x,y)
    for x,y in active: join(x,y)
    live_roots = {find(x) for x,y in d["bad"] if x in chosen and y in chosen and find(x)==find(y)}
    live_v = {v for v in chosen if find(v) in live_roots}
    live_e = {e for e in active if find(e[0]) in live_roots}
    deg = Counter()
    for x,y in live_e: deg[x]+=1; deg[y]+=1
    collision = {v: 2*sum(max(0,pair[v,z]-1) for z in range(d["n"])) for v in live_v}
    hit = {v: max(0,deg[v]-max(0,d["n"]-5*load[v])) for v in live_v}
    demand = {o: collision[o]+hit[o] for o in OWNERS}
    return active, live_e, live_v, collision, hit, demand

def outside(d, chosen, pair):
    adj = [set() for _ in range(d["n"])]
    for x,y in d["blue"]: adj[x].add(y); adj[y].add(x)
    cid = [-1]*d["n"]; comps=[]; attach=[]
    for seed in range(d["n"]):
        if seed in chosen or cid[seed]>=0: continue
        k=len(comps); cid[seed]=k; vs=set(); at=set(); todo=deque([seed])
        while todo:
            x=todo.popleft(); vs.add(x)
            for y in adj[x]:
                if y in chosen: at.add(y)
                elif cid[y]<0: cid[y]=k; todo.append(y)
        comps.append(frozenset(vs)); attach.append(frozenset(at))
    eligible={o:{x for k,c in enumerate(comps) if any(pair[o,a]>0 for a in attach[k]) for x in c} for o in OWNERS}
    return cid, comps, attach, eligible

def loss_functions(d, cid, comps):
    sign={e:1 for e in d["blue"]}; sign.update({e:-1 for e in d["bad"]})
    sd=Counter()
    for (x,y),s in sign.items(): sd[x]+=s; sd[y]+=s
    cl=[]
    for c in comps:
        internal=sum(s for (x,y),s in sign.items() if x in c and y in c)
        cl.append(sum(sd[x] for x in c)-2*internal)
    cross=Counter()
    for (x,y),s in sign.items():
        a,b=cid[x],cid[y]
        if a>=0 and b>=0 and a!=b: cross[edge(a,b)]+=s
    def pair(x,y): return sd[x]+sd[y]-2*sign.get(edge(x,y),0)
    def union(x,y):
        a,b=cid[x],cid[y]
        return cl[a] if a==b else cl[a]+cl[b]-2*cross[edge(a,b)]
    return pair, union

def patterns(d, pair, live_e, live_v, eligible, pair_loss, union_loss):
    badn=defaultdict(set)
    for x,y in d["bad"]: badn[x].add(y); badn[y].add(x)
    owner_mask={}; first_pattern={}; owner_arcs=Counter(); new_cells=Counter(); new_caps=Counter(); losses=Counter()
    def cap(cell): return 1 if edge(*cell) in live_e and cell[0] in live_v else 2
    def add(name,o,cell):
        bit=1<<o
        if not owner_mask.get(cell,0)&bit: owner_arcs[name]+=1
        if cell not in owner_mask:
            first_pattern[cell]=name; new_cells[name]+=1; new_caps[name]+=cap(cell)
        owner_mask[cell]=owner_mask.get(cell,0)|bit
    for o in OWNERS:
        for y in range(d["n"]):
            if y!=o and pair[o,y]==0: add("sameFirst",o,(o,y))
    for o in OWNERS:
        for x in sorted(badn[o]):
            for y in sorted(badn[o]):
                if x!=y and pair[x,y]==0 and pair_loss(x,y)>=0: add("commonBad",o,(x,y))
    for o in OWNERS:
        cs=sorted(x for x in range(d["n"]) if x!=o and pair[o,x]>0)
        for x in cs:
            for y in cs:
                if x!=y and pair[x,y]==0 and pair_loss(x,y)>=0: add("rowCompanion",o,(x,y))
    for o in OWNERS:
        xs=sorted(eligible[o])
        for x in xs:
            for y in xs:
                if x!=y and union_loss(x,y)>=0:
                    add("outsideAttachment",o,(x,y))
                    if o==0: losses[union_loss(x,y)]+=1
    bymask=Counter()
    for c,m in owner_mask.items(): bymask[m]+=cap(c)
    reserved=sorted(c for c in owner_mask if cap(c)==1)
    return owner_mask,bymask,new_cells,new_caps,owner_arcs,losses,reserved

def main():
    mod,d=canonical(); rows,pair,load,chosen,row_edges=tuple_primitives(d)
    active,live_e,live_v,collision,hit,demand=active_and_demand(d,pair,load,chosen,row_edges)
    cid,comps,attach,eligible=outside(d,chosen,pair)
    pair_loss,union_loss=loss_functions(d,cid,comps)
    masks,bymask,cells,caps,arcs,losses,reserved=patterns(d,pair,live_e,live_v,eligible,pair_loss,union_loss)
    shores=[]
    for sm in range(8):
        dem=sum(demand[o] for o in OWNERS if sm&(1<<o)); reach=sum(c for m,c in bymask.items() if m&sm)
        shores.append({"mask":sm,"owners":[o for o in OWNERS if sm&(1<<o)],"demand":dem,"reach":reach,"deficiency":dem-reach})
    old=sum(caps[x] for x in ("sameFirst","commonBad","rowCompanion")); total=sum(bymask.values())
    checks={
      "n":d["n"]==2943, "score":sum(collision.values())+sum(hit.values())==23115,
      "demand":demand=={0:6651,1:6651,2:6651}, "sameFirst":caps["sameFirst"]==17325,
      "commonBad":caps["commonBad"]==0, "rowCompanion":caps["rowCompanion"]==2600,
      "old_defect":sum(demand.values())-old==28, "eligible":all(len(eligible[o])==676 for o in OWNERS),
      "outside_loss":losses==Counter({8:456300}), "outside_capacity":caps["outsideAttachment"]==912600,
      "total_reach":total==932525, "hall":max(x["deficiency"] for x in shores)==0,
      "reservations":reserved==[(0,55),(1,2929),(2,2930)]}
    assert all(checks.values()),checks
    cert={"schema":"r29-fourpattern-worker4-v1","arithmetic":"integer/Fraction; no floats",
      "canonical":{"path":str(CANON.relative_to(ROOT)).replace('\\','/'),"sha256":digest(CANON),"payload_sha256":sha256(mod.canonical_bytes(d)).hexdigest()},
      "tuple":{"vertices":d["n"],"rows":len(rows),"selected_vertices":len(chosen),"active_vertices":len(live_v),"active_edges":len(active),"demanded_active_edges":len(live_e)},
      "owners":{str(o):{"collision":collision[o],"hit_need":hit[o],"demand_halves":demand[o],"demand_q":qtext(demand[o]),"eligible_outside":len(eligible[o])} for o in OWNERS},
      "outside":{"vertices":d["n"]-len(chosen),"components":len(comps),"size_histogram":dict(sorted(Counter(map(len,comps)).items())),"loss_histogram":dict(losses)},
      "patterns":{p:{"new_cells":cells[p],"owner_arcs":arcs[p],"new_halves":caps[p],"q_capacity":qtext(caps[p])} for p in ("sameFirst","commonBad","rowCompanion","outsideAttachment")},
      "capacity_by_owner_mask":dict(sorted(bymask.items())),"reserved_cells":[list(x) for x in reserved],
      "old_three":{"reach":old,"defect":sum(demand.values())-old},"four_pattern":{"reach":total,"max_deficiency":max(x["deficiency"] for x in shores)},
      "shores":shores,"checks":checks}
    OUT.write_text(json.dumps(cert,sort_keys=True,indent=2)+"\n",encoding="ascii")
    print(json.dumps({"certificate":OUT.name,"sha256":digest(OUT),"demand":sum(demand.values()),"old_reach":old,"old_defect":28,"full_reach":total,"max_deficiency":0},sort_keys=True))

if __name__=="__main__": main()
