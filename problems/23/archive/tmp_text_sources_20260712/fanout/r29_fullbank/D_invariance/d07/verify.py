"""Hostile exact audit of the R29 selector-invariance claim.  No floats."""
from collections import Counter, defaultdict, deque
from hashlib import sha256
import importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
spec = importlib.util.spec_from_file_location("untrusted_r29", LEAD)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
d = m.build(); N=d["n"]; OWN=(0,1,2)
adj=m.adjacency(N,d["blue"])

def state(rows):
    pair=Counter(); load=Counter(); support=set(); selected=set()
    for r in rows:
        for x in r: load[x]+=1; selected.add(x)
        for x in r:
            for y in r: pair[x,y]+=1
        support.update(m.edge(x,y) for x,y in zip(r,r[1:]))
    active={e for e in d["blue"] if e[0] in selected and e[1] in selected and e not in support}
    A=defaultdict(set)
    for u,v in active: A[u].add(v); A[v].add(u)
    comp={}; comps=[]
    for s in sorted(selected):
        if s in comp: continue
        seen={s}; q=deque([s])
        while q:
            u=q.popleft()
            for v in A[u]:
                if v not in seen: seen.add(v); q.append(v)
        k=len(comps); comps.append(seen)
        for v in seen: comp[v]=k
    badc={comp[u] for u,v in d["bad"] if u in comp and v in comp and comp[u]==comp[v]}
    av={v for v in selected if comp[v] in badc}
    ae={e for e in active if e[0] in av}
    deg=Counter()
    for u,v in ae: deg[u]+=1; deg[v]+=1
    collision={o:2*sum(max(0,pair[o,y]-1) for y in range(N)) for o in OWN}
    hit={o:max(0,deg[o]-max(0,N-5*load[o])) for o in OWN}
    return pair,av,active,collision,hit,deg,load

def sources(pair,av,active):
    sd=Counter(); sign={}
    for e in d["blue"]: sign[e]=1; sd[e[0]]+=1; sd[e[1]]+=1
    for e in d["bad"]: sign[e]=-1; sd[e[0]]-=1; sd[e[1]]-=1
    ids={}; reasons=Counter(); reservations=[]
    for o in OWN:
        C={x for x in range(N) if pair[o,x]>0}
        for y in range(N):
            if y==o or pair[o,y]: continue
            for h in (0,1):
                reserved=(h==0 and m.edge(o,y) in active and o in av)
                if reserved: reservations.append((o,y,h,"sameFirst")); continue
                ids[(o,y,h)]=ids.get((o,y,h),0)|(1<<o); reasons[(o,y,h)]|=1
        for x in C:
            for y in C:
                if x==y or pair[x,y]: continue
                e=m.edge(x,y)
                if sd[x]+sd[y]-2*sign.get(e,0)<0: continue
                for h in (0,1):
                    reserved=(h==0 and e in active and x in av)
                    if reserved: reservations.append((x,y,h,"rowCompanion")); continue
                    ids[(x,y,h)]=ids.get((x,y,h),0)|(1<<o); reasons[(x,y,h)]|=2
    rh=Counter(reasons.values())
    return ids,rh,reservations

families=[]; enum_hash=sha256(); touching=0
for atom in d["atoms"][d["selectorStart"]:d["selectorStop"]]:
    fam=tuple(sorted(m.shortest_rows(adj,*atom))); assert len(fam)==680
    families.append(fam)
    for r in fam:
        enum_hash.update(json.dumps(r,separators=(",",":")).encode())
        touching += bool(set(r)&set(OWN))

base=list(d["rows"])
for k,meta in enumerate(d["selectorMeta"]): base[d["selectorStart"]+k]=tuple(meta["anchorRow"])

def audit(label, choices):
    rows=list(base)
    for k,r in enumerate(choices): rows[d["selectorStart"]+k]=r
    pair,av,active,col,hit,deg,load=state(rows); ids,rh,res=sources(pair,av,active)
    out={"label":label,"demand":sum(col.values())+sum(hit.values()),"reach":len(ids),
         "collision":col,"hit":hit,"hub_degree":{o:deg[o] for o in OWN},
         "hub_load":{o:load[o] for o in OWN},"sameFirstOnly":rh[1],
         "rowCompanionOnly":rh[2],"both":rh[3],"reservations":len(res),
         "source_ids_unique":len(ids)==len(set(ids)),"hubs_active":all(o in av for o in OWN)}
    assert out["demand"]==19953 and out["reach"]==19925
    assert out["sameFirstOnly"]==17325 and out["rowCompanionOnly"]==2600 and out["both"]==0
    assert out["source_ids_unique"] and out["hubs_active"]
    return out

# Every option in every family is inspected exactly for the only selector-to-owner
# dependency: direct owner occurrence.  Zero occurrences proves pair/load/support
# at owners are tuple-invariant.  The fixed selected neighbors 55,2929,2930 and
# fixed owner-incident support then make degree/activity/reservations invariant.
single_options_checked=sum(map(len,families))
assert single_options_checked==676*680 and touching==0

anchors=[tuple(x["anchorRow"]) for x in d["selectorMeta"]]
locals_=[[r for r in f if 55 not in r] for f in families]
assert all(len(x)==4 for x in locals_)
patterns=[("all_anchor",anchors)]
for j in range(4): patterns.append((f"all_local_{j}",[x[j] for x in locals_]))
patterns += [
 ("alternating_local",[locals_[k][k%4] for k in range(676)]),
 ("region_split",[anchors[k] if d["selectorMeta"][k]["region"]==0 else locals_[k][3] for k in range(676)]),
 ("sparse_extremes",[locals_[k][0] if k in (0,337,338,675) else anchors[k] for k in range(676)])]
audits=[audit(name,rows) for name,rows in patterns]

# Counting-convention audit: source identity is the ordered triple (x,y,half),
# unioned across owners/reasons.  Reversals and halves remain distinct.
base_ids,_,_=sources(*state(base)[:3])
assert all(h in (0,1) for _,_,h in base_ids)
result={"verdict":"PASS","n":N,"families":676,"options_per_family":680,
 "single_options_checked":single_options_checked,"selector_rows_touching_owner":touching,
 "selector_enumeration_sha256":enum_hash.hexdigest(),"multi_family_audits":audits,
 "source_identity":"ordered (x,y,half), set-unioned over owner/reason",
 "lead_sha256":sha256(LEAD.read_bytes()).hexdigest()}
(HERE/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,sort_keys=True,indent=2))
