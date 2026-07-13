"""Exact integer R29 c5Base/FreeHalf audit; four patterns are diagnostic only."""
from collections import Counter, deque
import hashlib, importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
OWNERS = (0, 1, 2)
SOURCES = {
 "common_contract": HERE.parent / "COMMON.md", "goal": ROOT / "GOAL_LOOP.md",
 "r29_writeup": ROOT / "problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md",
 "lead": LEAD, "owner_hall": ROOT / "tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py",
 "cut_certificate": ROOT / "tmp/fanout/r29_gate/d05/retry2/cut_certificate.json",
 "r19": ROOT / "problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md",
 "r20": ROOT / "problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md",
 "r23": ROOT / "problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md",
 "r23_gate": ROOT / "problems/23/writeup/_claude_r23_outside_attachment_gate.py",
 "r23_full_gate": ROOT / "problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py",
 "checked_c5": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean",
 "checked_row": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean",
 "typed_sources": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean",
 "fullbank_ledger": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean",
 "fullbank_sinks": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean",
 "ell5_interface": ROOT / "problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean",
 "ell5_hall": ROOT / "problems/23/lean/Erdos23Delta0/Ell5FullBankHall.lean"}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def edge(x,y):
 assert x != y
 return (x,y) if x < y else (y,x)

def load_cage():
 spec=importlib.util.spec_from_file_location("r29lead",LEAD); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
 raw=mod.build()
 return {"n":int(raw["n"]),"blue":frozenset(map(tuple,raw["blue"])),"bad":frozenset(map(tuple,raw["bad"])),
  "side":tuple(raw["side"]),"rows":tuple(map(tuple,raw["rows"])),"meta":tuple(dict(x) for x in raw["selectorMeta"]),
  "selector_start":int(raw["selectorStart"])}

def payload_sha(c):
 p={"n":c["n"],"blue":[list(x) for x in sorted(c["blue"])],"bad":[list(x) for x in sorted(c["bad"])],"rows":[list(x) for x in c["rows"]]}
 return hashlib.sha256(json.dumps(p,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def incidence_sha(c):
 p={"n":c["n"],"blue":sorted(c["blue"]),"bad":sorted(c["bad"]),"side":c["side"],"rows":c["rows"],
  "selector_anchor_rows":[x["anchorRow"] for x in c["meta"]],"selector_start":c["selector_start"]}
 return hashlib.sha256(json.dumps(p,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def validate(c):
 n=c["n"]; adj=[set() for _ in range(n)]
 for x,y in c["blue"]|c["bad"]: adj[x].add(y); adj[y].add(x)
 rows_ok=sum(len(r)==5 and edge(r[0],r[-1]) in c["bad"] and all(edge(x,y) in c["blue"] for x,y in zip(r,r[1:])) for r in c["rows"])
 return {"n":n,"blue":len(c["blue"]),"bad":len(c["bad"]),"edges":len(c["blue"]|c["bad"]),
  "triangles":sum(len(adj[x]&adj[y]) for x,y in c["blue"]|c["bad"])//3,
  "blue_crossing_displayed_cut":sum(c["side"][x]!=c["side"][y] for x,y in c["blue"]),
  "bad_uncut_displayed_cut":sum(c["side"][x]==c["side"][y] for x,y in c["bad"]),
  "row_count":len(c["rows"]),"valid_length5_bad_endpoint_blue_path_rows":rows_ok,
  "lead_canonical_payload_sha256":payload_sha(c),"owner_incidence_sha256":incidence_sha(c)}

def anchor_rows(c):
 rows=list(c["rows"])
 for j,m in enumerate(c["meta"]): rows[c["selector_start"]+j]=tuple(m["anchorRow"])
 return tuple(rows)

def rebuild(c,rows):
 n=c["n"]; pair=Counter(); load=Counter(); support=set(); selected=set()
 for row in rows:
  for x in row:
   load[x]+=1; selected.add(x)
   for y in row: pair[x,y]+=1
  support.update(edge(x,y) for x,y in zip(row,row[1:]))
 active={e for e in c["blue"] if e not in support and e[0] in selected and e[1] in selected}
 parent={x:x for x in selected}
 def find(x):
  while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
  return x
 def union(x,y):
  x,y=find(x),find(y)
  if x!=y: parent[max(x,y)]=min(x,y)
 for x,y in active: union(x,y)
 for x in selected: find(x)
 badroots={find(x) for x,y in c["bad"] if x in selected and y in selected and find(x)==find(y)}
 activev={x for x in selected if find(x) in badroots}; demanded={e for e in active if e[0] in activev}; degree=Counter()
 for x,y in demanded: degree[x]+=1; degree[y]+=1
 coll={v:2*sum(max(0,pair[v,y]-1) for y in range(n)) for v in activev}
 hit={v:max(0,degree[v]-max(0,n-5*load[v])) for v in activev}
 return {"rows":rows,"pair":pair,"load":load,"selected":selected,"active":active,"activev":activev,"demanded":demanded,
  "root":{x:find(x) for x in selected},"collision":coll,"hit":hit}

def outside_components(c,s):
 adj=[set() for _ in range(c["n"])]
 for x,y in c["blue"]: adj[x].add(y); adj[y].add(x)
 cid=[-1]*c["n"]; comps=[]; atts=[]
 for root in range(c["n"]):
  if root in s["selected"] or cid[root]>=0: continue
  k=len(comps); cid[root]=k; vertices=set(); att=set(); todo=deque([root])
  while todo:
   x=todo.popleft(); vertices.add(x)
   for y in adj[x]:
    if y in s["selected"]: att.add(y)
    elif cid[y]<0: cid[y]=k; todo.append(y)
  comps.append(frozenset(vertices)); atts.append(frozenset(att))
 return cid,tuple(comps),tuple(atts)

def loss(c,S):
 return sum((x in S)!=(y in S) for x,y in c["blue"])-sum((x in S)!=(y in S) for x,y in c["bad"])

def build_patterns(c,s):
 n=c["n"]; pair=s["pair"]; sd=Counter(); sign={}; badnb=[set() for _ in range(n)]
 for e in c["blue"]: sign[e]=1; sd[e[0]]+=1; sd[e[1]]+=1
 for e in c["bad"]: sign[e]=-1; sd[e[0]]-=1; sd[e[1]]-=1; badnb[e[0]].add(e[1]); badnb[e[1]].add(e[0])
 def free(x,y,h): return x!=y and pair[x,y]==0 and not(h==0 and edge(x,y) in s["active"] and x in s["activev"])
 def sigma2(x,y): return sd[x]+sd[y]-2*sign.get(edge(x,y),0)
 order=("sameFirst","commonBad","rowCompanion","outsideAttachment")
 pats={name:{o:set() for o in OWNERS} for name in order}; companions={o:{x for x in range(n) if pair[o,x]>0} for o in OWNERS}
 for o in OWNERS:
  for y in range(n):
   for h in (0,1):
    if free(o,y,h): pats["sameFirst"][o].add((o,y,h))
  for x in badnb[o]:
   for y in badnb[o]:
    if x!=y and sigma2(x,y)>=0:
     for h in (0,1):
      if free(x,y,h): pats["commonBad"][o].add((x,y,h))
  for x in companions[o]:
   for y in companions[o]:
    if x!=y and sigma2(x,y)>=0:
     for h in (0,1):
      if free(x,y,h): pats["rowCompanion"][o].add((x,y,h))
 cid,comps,atts=outside_components(c,s); eg={o:set() for o in OWNERS}; es={o:set() for o in OWNERS}; losses={}
 for o in OWNERS:
  oroot=s["root"].get(o)
  for k,att in enumerate(atts):
   witnesses={a for a in att if pair[o,a]>0}
   if witnesses: eg[o].add(k)
   if any(s["root"].get(a)==oroot for a in witnesses): es[o].add(k)
  vertices=sorted(x for k in es[o] for x in comps[k])
  for x in vertices:
   for y in vertices:
    if x==y: continue
    key=tuple(sorted((cid[x],cid[y])))
    if key not in losses: losses[key]=loss(c,comps[cid[x]]|comps[cid[y]])
    if losses[key]>=0:
     for h in (0,1): assert free(x,y,h); pats["outsideAttachment"][o].add((x,y,h))
 # The archived R23 Python gate omits the prose component equality.  Compute
 # that implemented gate relation separately, without treating it as Lean.
 comp_loss={k:loss(c,comp) for k,comp in enumerate(comps)}; cross=Counter()
 for x,y in c["blue"]:
  if cid[x]>=0 and cid[y]>=0 and cid[x]!=cid[y]: cross[tuple(sorted((cid[x],cid[y])))]+=1
 for x,y in c["bad"]:
  if cid[x]>=0 and cid[y]>=0 and cid[x]!=cid[y]: cross[tuple(sorted((cid[x],cid[y])))]-=1
 archived={o:set() for o in OWNERS}; archived_losses=Counter()
 for o in OWNERS:
  vertices=sorted(x for k in eg[o] for x in comps[k])
  for x in vertices:
   for y in vertices:
    if x==y: continue
    cx,cy=cid[x],cid[y]
    union_loss=comp_loss[cx] if cx==cy else comp_loss[cx]+comp_loss[cy]-2*cross[tuple(sorted((cx,cy)))]
    archived_losses[union_loss]+=1
    if union_loss>=0:
     for h in (0,1): assert free(x,y,h); archived[o].add((x,y,h))
 outside={"selected_vertices":len(s["selected"]),"outside_vertices":n-len(s["selected"]),"outside_blue_components":len(comps),
  "component_sizes_histogram":dict(sorted(Counter(map(len,comps)).items())),"attachment_sizes_histogram":dict(sorted(Counter(map(len,atts)).items())),
  "eligible_components_r23_gate_without_component_equality":{str(o):len(eg[o]) for o in OWNERS},
  "eligible_vertices_r23_gate_without_component_equality":{str(o):sum(len(comps[k]) for k in eg[o]) for o in OWNERS},
  "eligible_components_with_prose_component_equality":{str(o):len(es[o]) for o in OWNERS},
  "eligible_vertices_with_prose_component_equality":{str(o):sum(len(comps[k]) for k in es[o]) for o in OWNERS},
  "checked_component_pair_losses_prose_component_scoped":{f"{x},{y}":z for (x,y),z in sorted(losses.items())},
  "archived_gate_ordered_pair_loss_histogram":{str(k):v for k,v in sorted(archived_losses.items())}}
 return pats,outside,archived

def summarize(pats,demand):
 order=("sameFirst","commonBad","rowCompanion","outsideAttachment"); acc=set(); unions={}; inc={}
 for name in order:
  u=set().union(*(pats[name][o] for o in OWNERS)); unions[name]=u
  inc[name]={"per_owner_eligible_slots":{str(o):len(pats[name][o]) for o in OWNERS},
   "sum_per_owner_double_counting_shared_slots":sum(len(pats[name][o]) for o in OWNERS),"unique_slots_before_prior_class_dedup":len(u),
   "overlap_with_prior_classes":len(u&acc),"new_unique_slots":len(u-acc),"cumulative_unique_slots":len(acc|u)}; acc|=u
 masks=Counter()
 for src in acc: masks[sum(1<<o for o in OWNERS if any(src in pats[name][o] for name in order))]+=1
 cuts=[]
 for sm in range(8):
  shore=[o for o in OWNERS if sm&(1<<o)]; d=sum(demand[o] for o in shore); reach=sum(v for m,v in masks.items() if m&sm)
  cuts.append({"shore_mask":sm,"shore":shore,"demand":d,"neighborhood":reach,"defect":d-reach})
 return {"class_order":list(order),"incremental_capacity":inc,
  "pairwise_source_overlap":{f"{a}&{b}":len(unions[a]&unions[b]) for i,a in enumerate(order) for b in order[i+1:]},
  "final_source_histogram_by_owner_mask":{str(k):v for k,v in sorted(masks.items())},"final_unique_slots":len(acc),"shore_cuts":cuts,
  "maximum_deficiency_cut":max(cuts,key=lambda z:(z["defect"],-z["shore_mask"]))}

def compare_existing_certificate(pats):
 cert=json.loads(SOURCES["cut_certificate"].read_text(encoding="utf-8"))
 recorded={(z["x"],z["y"],z["half"]):(z["owner_mask"],z["reason_mask"]) for z in cert["sources"]}
 computed={}
 for src in set().union(*(pats[name][o] for name in ("sameFirst","commonBad","rowCompanion","outsideAttachment") for o in OWNERS)):
  owner_mask=sum(1<<o for o in OWNERS if any(src in pats[name][o] for name in ("sameFirst","commonBad","rowCompanion","outsideAttachment")))
  reason_mask=(1 if any(src in pats["sameFirst"][o] for o in OWNERS) else 0)|(2 if any(src in pats["rowCompanion"][o] for o in OWNERS) else 0)
  computed[src]=(owner_mask,reason_mask)
 common=set(computed)&set(recorded)
 return {"recorded_sources":len(recorded),"computed_sources":len(computed),"missing_from_recorded":len(set(computed)-set(recorded)),
  "extra_in_recorded":len(set(recorded)-set(computed)),"owner_mask_mismatches":sum(computed[x][0]!=recorded[x][0] for x in common),
  "reason_mask_mismatches":sum(computed[x][1]!=recorded[x][1] for x in common),"exact_record_equality":computed==recorded}

def main():
 c=load_cage(); valid=validate(c); rows=anchor_rows(c); s=rebuild(c,rows); demand={o:s["collision"].get(o,0)+s["hit"].get(o,0) for o in OWNERS}
 pats,outside,archived=build_patterns(c,s); cap=summarize(pats,demand); cert_compare=compare_existing_certificate(pats)
 archived_pats={name:{o:set(pats[name][o]) for o in OWNERS} for name in ("sameFirst","commonBad","rowCompanion","outsideAttachment")}
 archived_pats["outsideAttachment"]=archived; archived_cap=summarize(archived_pats,demand)
 A={"n_2943":valid["n"]==2943,"blue_7039":valid["blue"]==7039,"bad_1383":valid["bad"]==1383,"triangle_free":valid["triangles"]==0,
  "all_rows_valid":valid["valid_length5_bad_endpoint_blue_path_rows"]==1383,
  "canonical_sha":valid["lead_canonical_payload_sha256"]=="fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f",
  "selected_2127":len(s["selected"])==2127,"active_vertices_19":len(s["activev"])==19,"active_edges_1370":len(s["active"])==1370,
  "demanded_active_edges_18":len(s["demanded"])==18,"owner_demands_6651":all(demand[o]==6651 for o in OWNERS),
  "same_first_17325":cap["incremental_capacity"]["sameFirst"]["new_unique_slots"]==17325,
  "common_bad_zero":cap["incremental_capacity"]["commonBad"]["new_unique_slots"]==0,
  "row_companion_2600":cap["incremental_capacity"]["rowCompanion"]["new_unique_slots"]==2600,
  "outside_attachment_zero":cap["incremental_capacity"]["outsideAttachment"]["new_unique_slots"]==0,
  "total_unique_19925":cap["final_unique_slots"]==19925,
  "full_shore_defect_28":cap["maximum_deficiency_cut"]["shore_mask"]==7 and cap["maximum_deficiency_cut"]["defect"]==28,
  "archived_gate_outside_912600":archived_cap["incremental_capacity"]["outsideAttachment"]["new_unique_slots"]==912600,
  "archived_gate_total_932525":archived_cap["final_unique_slots"]==932525,
  "archived_gate_full_shore_surplus_912572":archived_cap["shore_cuts"][7]["defect"]==-912572,
  "existing_cut_certificate_exact_record_equality":cert_compare["exact_record_equality"]}
 result={"schema":"R29 all-anchor exact c5Base/FreeHalf diagnostic audit v1","arithmetic":"integer only",
  "status":{"prose_component_scoped_four_pattern_relation":"FAIL","archived_r23_python_gate_relation":"PASS","implemented_production_c5base_absorption":"UNDEFINED",
   "reason":"compiled terminal checkers and abstract ledgers do not construct a graph-derived c5Base token family or transfer-to-bank adapter"},
  "cage_validation":valid,"all_anchor_scope":{"changed_selector_rows":len(c["meta"]),"selected_vertices":len(s["selected"]),
   "active_vertices":len(s["activev"]),"active_edges":len(s["active"]),"demanded_active_edges":len(s["demanded"]),
   "owners":{str(o):{"collision":s["collision"].get(o,0),"hit_need":s["hit"].get(o,0),"demand":demand[o],
    "companions":sum(s["pair"][o,x]>0 for x in range(c["n"])),"bad_neighbors":sum(o in e for e in c["bad"])} for o in OWNERS},
   "hub_shore_demand":sum(demand.values()),"hit_need_total":sum(s["hit"].get(o,0) for o in OWNERS)},
  "outside_attachment_diagnostic":outside,"source_capacity_prose_component_scoped":cap,"source_capacity_archived_r23_gate":archived_cap,
  "existing_cut_certificate_comparison":cert_compare,
  "conversion_semantics":{"writeup_only":"collision match cancels; HitNeed match would create one c5Base token from its matched FreeHalf key",
   "hub_hit_need_units":sum(s["hit"].get(o,0) for o in OWNERS),"full_checked_matching_exists_under_four_patterns":False,
   "production_tokens_constructed_by_this_gate":0,"abstract_capacity_fields_counted_as_supply":False},
  "assertions":A,"source_sha256":{k:sha(v) for k,v in SOURCES.items()},"script_sha256":sha(Path(__file__))}
 assert all(A.values()),A
 (HERE/"audit_result.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,sort_keys=True,indent=2))

if __name__=="__main__": main()
