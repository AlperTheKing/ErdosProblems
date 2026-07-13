#!/usr/bin/env python3
"""Exact R29 Door audit; geometric edge counts are not bank capacity."""
from __future__ import annotations
import hashlib, importlib.util, json, re, subprocess
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
CUT_CERT = ROOT / "tmp/fanout/r29_gate/d05/retry2/cut_certificate.json"
LEAN = ROOT / "problems/23/lean/Erdos23Delta0"
SOURCES = {
 "aggregate_package": LEAN / "Gamma/FullBankToLengthSurplusCharge.lean",
 "finite_sinks": LEAN / "Gamma/FullBankPortSinks.lean",
 "typed_sources": LEAN / "Gamma/TypedFullBankSources.lean",
 "typed_half_layer": LEAN / "Gamma/TypedOwnDoorHalfLayer.lean",
 "no_incidence_countermodel": LEAN / "AggregateLedgerNoIncidenceCounterexample.lean",
 "boundary_bridge": LEAN / "Ell5InternalEndpointSlackFullBank.lean",
 "all_door_fast_path": LEAN / "EndpointHalfDoorComplete.lean",
 "root_layer": LEAN / "RootLayerHalfSqueeze.lean",
 "petal_half_layer": LEAN / "DisjointPetalHalfSqueeze.lean",
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def norm(u,v): return (u,v) if u < v else (v,u)

def load_lead():
 spec = importlib.util.spec_from_file_location("r29_lead_authoritative", LEAD)
 if spec is None or spec.loader is None: raise RuntimeError(f"cannot import {LEAD}")
 mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
 return mod

def anchor_rows(data):
 rows = list(data["rows"])
 for j,m in enumerate(data["selectorMeta"]):
  rows[data["selectorStart"]+j] = tuple(m["anchorRow"])
 return tuple(rows)

def incidence_sha(data,rows):
 payload={"n":data["n"],"blue":sorted(data["blue"]),"bad":sorted(data["bad"]),
  "side":data["side"],"rows":rows,
  "selector_anchor_rows":[m["anchorRow"] for m in data["selectorMeta"]],
  "selector_start":data["selectorStart"]}
 return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def rebuild(data,rows):
 selected={x for row in rows for x in row}
 support={norm(x,y) for row in rows for x,y in zip(row,row[1:])}
 active={e for e in data["blue"] if e not in support and e[0] in selected and e[1] in selected}
 adj=defaultdict(set)
 for u,v in active: adj[u].add(v); adj[v].add(u)
 comp_of={}; comps=[]
 for root in sorted(selected):
  if root in comp_of: continue
  seen={root}; q=deque([root])
  while q:
   u=q.popleft()
   for v in adj[u]:
    if v not in seen: seen.add(v); q.append(v)
  cid=len(comps)
  for v in seen: comp_of[v]=cid
  comps.append(seen)
 active_ids={comp_of[u] for u,v in data["bad"] if u in comp_of and v in comp_of and comp_of[u]==comp_of[v]}
 active_vertices={v for v in selected if comp_of[v] in active_ids}
 demanded={e for e in active if e[0] in active_vertices}
 hub_ids={comp_of[v] for v in (0,1,2)}
 if len(hub_ids)!=1: raise AssertionError(f"hub owners split: {hub_ids}")
 hub_id=next(iter(hub_ids)); hub=comps[hub_id]
 off=set(data["blue"])-support
 boundary=lambda shore:{e for e in off if (e[0] in shore)!=(e[1] in shore)}
 return {"selected":selected,"support":support,"active":active,"comps":comps,
  "active_ids":active_ids,"active_vertices":active_vertices,"demanded":demanded,
  "hub_id":hub_id,"hub":hub,"off":off,"hub_boundary":boundary(hub),
  "selected_boundary":boundary(selected),
  "hub_internal":{e for e in off if e[0] in hub and e[1] in hub}}

def matching_lines(path,needles):
 lines=path.read_text(encoding="utf-8").splitlines()
 return {s:[i for i,line in enumerate(lines,1) if s in line] for s in needles}

def source_audit():
 lean_files=sorted(LEAN.glob("*.lean"))
 for sub in ("BranchB","Cert","Ell5","Gamma","Rows","Toy"):
  lean_files.extend(sorted((LEAN/sub).rglob("*.lean")))
 pkg=[]; typed=[]; adapters=[]; outside=[]
 for path in lean_files:
  rel=path.relative_to(ROOT).as_posix()
  for n,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
   item={"path":rel,"line":n,"text":line.strip()}
   if re.search(r"\bdef\s+\w+\s*:\s*FullBankGlobalPackage\b",line): pkg.append(item)
   if re.search(r"\bdef\s+\w+\s*:\s*OwnEdgeDoorSourceData\b",line): typed.append(item)
   if re.search(r"\bdef\s+\w+\s*:\s*DoorWallAdapter\b",line): adapters.append(item)
   if "CheckedOutsideAttachment" in line or "outsideAttachment" in line: outside.append(item)
 anchors={
  "aggregate_package":matching_lines(SOURCES["aggregate_package"],["structure LedgerToken","structure FullBankGlobalPackage","structure Checked","no_double_spend","token_source_unique"]),
  "finite_sinks":matching_lines(SOURCES["finite_sinks"],["def DoorToken","def doorHallCapQ","Guardrail: legal edge-to-token incidence is still absent"]),
  "typed_sources":matching_lines(SOURCES["typed_sources"],["structure OwnEdgeDoorSourceData","portEdge :","doorOf :","def Checked","def doorLegal","def hallCapQ"]),
  "typed_half_layer":matching_lines(SOURCES["typed_half_layer"],["structure DoorWallAdapter","sinkOf :","legal_of_door_source","structure TypedPetalGeometry","port_is_boundary"]),
  "no_incidence_countermodel":matching_lines(SOURCES["no_incidence_countermodel"],["no relation between wall ports and ledger tokens","typed, checked port-to-token incidence adapter is logically needed","theorem checkedAggregatePackage_and_noHalfLayerRouting"]),
  "boundary_bridge":matching_lines(SOURCES["boundary_bridge"],["let D := O.filter fun e => edgeBoundary C e = true","No endpoint or Door","hboundaryDoorLegal","hboundaryDoorCapacity"]),
  "root_layer":matching_lines(SOURCES["root_layer"],["No existence theorem for a root layer, petal shores, or mandatory Doors"]),
  "all_door_fast_path":matching_lines(SOURCES["all_door_fast_path"],["ownDoor_inc","ownDoor_capacity","There is no current R7 `FullBankLPBundle` type carrying extractor labels"]),
 }
 o14=subprocess.run(["rg","-l","--glob","*.lean","FullBankGlobalPackage|OwnEdgeDoorSourceData|DoorWallAdapter|CapSource\\.door|doorHallCapQ",str(LEAN/"O14")],capture_output=True,text=True,check=False)
 if o14.returncode not in (0,1): raise RuntimeError(o14.stderr)
 return {"lean_file_count_scanned":len(lean_files),"o14_lean_file_count":sum(1 for _ in (LEAN/"O14").rglob("*.lean")),"o14_rg_returncode":o14.returncode,"o14_matching_files":[x for x in o14.stdout.splitlines() if x],"full_bank_package_value_hits":pkg,
  "typed_r29_door_data_value_hits":typed,"door_wall_adapter_value_hits":adapters,"compiled_outside_attachment_hits":outside,
  "anchors":anchors,"conclusion":{"operational_r29_door_provider_present":False,
  "reason":"Aggregate package has no port incidence; typed checker/adapter are uninstantiated inputs."}}

def main():
 data=load_lead().build(); rows=anchor_rows(data); scope=rebuild(data,rows)
 cert=json.loads(CUT_CERT.read_text(encoding="utf-8")); shore=cert["maximum_deficiency_cut"]
 inc_sha=incidence_sha(data,tuple(data["rows"])); audit=source_audit()
 active_summary=[]
 for cid in sorted(scope["active_ids"]):
  vs=sorted(scope["comps"][cid]); active_summary.append({"component_id":cid,"cardinality":len(vs),"vertices":vs,"contains_hub_owner":sorted(set(vs)&{0,1,2})})
 checks={
  "n_2943":data["n"]==2943,"blue_7039":len(data["blue"])==7039,
  "bad_1383":len(data["bad"])==1383,"rows_1383":len(rows)==1383,
  "selected_vertices_2127":len(scope["selected"])==2127,
  "active_edges_1370":len(scope["active"])==1370,
  "active_vertices_19":len(scope["active_vertices"])==19,
  "demanded_active_edges_18":len(scope["demanded"])==18,
  "hub_owner_shore_012":shore["shore"]==[0,1,2],
  "aux_demand_19953":shore["demand"]==19953,
  "aux_neighborhood_19925":shore["neighborhood"]==19925,
  "aux_defect_28":shore["gap"]==28,
  "canonical_incidence_sha_matches_certificate":inc_sha==cert["untrusted_input"]["canonical_incidence_sha256"],
  "no_r29_typed_door_provider":not audit["typed_r29_door_data_value_hits"] and not audit["door_wall_adapter_value_hits"] and not audit["o14_matching_files"],
  "outside_attachment_pattern_not_compiled":not audit["compiled_outside_attachment_hits"],
 }
 result={
  "schema":"r29-door-audit-v1","status":"UNDEFINED","arithmetic":"integers only",
  "status_scope":"Whether production Door capacity absorbs the 28-unit HUB-shore defect is undefined because no implemented R29 port-to-Door-token provider exists.",
  "reconstruction":{"lead_import":LEAD.relative_to(ROOT).as_posix(),"lead_sha256":sha(LEAD),
   "canonical_all_anchor_incidence_sha256":inc_sha,
   "counts":{"n":data["n"],"blue":len(data["blue"]),"bad":len(data["bad"]),"rows":len(rows),
    "selected_vertices":len(scope["selected"]),"selected_support_edges":len(scope["support"]),
    "active_edges":len(scope["active"]),"active_vertices":len(scope["active_vertices"]),
    "demanded_active_edges":len(scope["demanded"]),"selected_active_graph_components":len(scope["comps"]),
    "active_component_count":len(scope["active_ids"])},"active_components":active_summary,
   "hub_component":{"component_id":scope["hub_id"],"cardinality":len(scope["hub"]),
    "vertices":sorted(scope["hub"]),"contains_owner_shore":[0,1,2]},
   "auxiliary_owner_hall":{"source":CUT_CERT.relative_to(ROOT).as_posix(),"source_sha256":sha(CUT_CERT),
    "shore":shore["shore"],"demand":shore["demand"],"neighborhood":shore["neighborhood"],"defect":shore["gap"],
    "warning":"ActiveScoped FreeHalf incidence, not production FullBank incidence."}},
  "geometric_diagnostics_not_capacity":{"definition_used":"blue off-support edge with exactly one endpoint in named shore",
   "warning":"Edges are not asserted to possess Door tokens; production legality/token identity are absent.",
   "blue_off_support_edges":len(scope["off"]),"hub_component_internal_blue_off_support_edges":len(scope["hub_internal"]),
   "hub_component_boundary_blue_off_support_edges":len(scope["hub_boundary"]),
   "hub_component_boundary_edges":[list(e) for e in sorted(scope["hub_boundary"])],
   "selected_vertex_union_boundary_blue_off_support_edges":len(scope["selected_boundary"]),
   "selected_vertex_union_boundary_edges_sha256":hashlib.sha256(json.dumps(sorted(scope["selected_boundary"]),separators=(",",":")).encode()).hexdigest()},
  "production_door_semantics":{"geometric_candidate_in_one_bridge":"D = O.filter (edgeBoundary C e = true), O = cutEdges G s \\ F",
   "typed_token_key":"CapSource.door (portEdge p)","typed_check_requires":["injective portEdge","doorOf source equality","raw capQ >= 25"],
   "hall_scale":"capQ / 25","routing_requires":["DoorWallAdapter.sinkOf","sinkOf injective","source equality implies wall legality","wall capacity equals hallCapQ"]},
  "door_capacity_accounting":{"four_pattern_reachable_capacity_before_doors":None,"raw_reachable_door_token_count":None,
   "raw_reachable_door_capacity":None,"overlap_with_four_pattern_sources":None,"incremental_reachable_door_capacity":None,
   "post_door_defect":None,"no_double_spend_check":"NOT INSTANTIABLE FOR R29",
   "reason":"No R29 Port value, portEdge, typed ledger, doorOf, DoorWallAdapter, or legal relation connects the cage to Door sinks."},
  "minimal_missing_data":["Concrete finite R29 wall Port enumeration and portEdge map.","Typed R29 token table with component and CapSource payloads.",
   "doorOf accepted by checkOwnEdgeDoors.","DoorWallAdapter into the production wall Sink type.","Actual R29 petal shores/walls and checked boundary equations.",
   "Common source identity relating Door and four-pattern tokens for overlap/no-double-spend."],
  "source_audit":audit,"source_hashes_sha256":{name:sha(path) for name,path in sorted(SOURCES.items())},"checks":checks}
 if not all(checks.values()): raise AssertionError([k for k,v in checks.items() if not v])
 out=HERE/"door_audit.json"; out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"status":result["status"],"counts":result["reconstruction"]["counts"],
  "hub_component":result["reconstruction"]["hub_component"],"geometry":result["geometric_diagnostics_not_capacity"],
  "capacity":result["door_capacity_accounting"],"checks":checks,"output":str(out),"output_sha256":sha(out)},sort_keys=True,indent=2))
if __name__=="__main__": main()





