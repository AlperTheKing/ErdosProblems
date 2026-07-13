"""Exact R29 FullBank LP audit; integers/Fraction only."""
from collections import Counter, defaultdict, deque
from fractions import Fraction
import hashlib, importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
CUT_CERT = ROOT / "tmp/fanout/r29_gate/d05/retry2/cut_certificate.json"
RESULT = HERE / "RESULT.json"
REPORT = HERE / "REPORT.md"
HASHES = HERE / "HASHES.json"
OWNERS = (0, 1, 2)
SOURCE_FILES = [
 "GOAL_LOOP.md", "problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md",
 "tmp/fanout/r29_fullbank_gate/COMMON.md", "tmp/fanout/r29_gate/lead/r29_lead_gate.py",
 "tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py",
 "tmp/fanout/r29_gate/d05/retry2/cut_certificate.json",
 "tmp/fanout/r29_gate/d09/retry2/best_tuple.json",
 "problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean",
 "problems/23/lean/Erdos23Delta0/Ell5FullBankAssignedSink.lean",
 "problems/23/lean/Erdos23Delta0/Ell5FullBankHall.lean",
 "problems/23/lean/Erdos23Delta0/Ell5FullBankWallAdapter.lean",
 "problems/23/lean/Erdos23Delta0/BankedWallLP.lean",
 "problems/23/lean/Erdos23Delta0/RelaxedCoverGraphBridge.lean",
 "problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean",
 "problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean",
 "problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean",
 "problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean",
 "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean",
 "problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean",
 "problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean",
 "problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean",
 "problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean",
] + [f"problems/23/writeup/WALL_ATTACK_R{i}_GPTPRO56.md" for i in range(18, 24)]

def E(u, v):
 assert u != v
 return (u, v) if u < v else (v, u)
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(p.read_bytes())
def enc(x): return json.dumps(x, sort_keys=True, separators=(",", ":")).encode("ascii")
def sha_obj(x): return sha_bytes(enc(x))
def rat(x):
 x = Fraction(x); return {"numerator": x.numerator, "denominator": x.denominator}
def edges(xs): return [list(x) for x in sorted(xs)]

def load_cage():
 spec = importlib.util.spec_from_file_location("r29_lead_constructor", LEAD)
 assert spec and spec.loader
 mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
 return mod, mod.build()

def anchored(data):
 rows = [tuple(r) for r in data["rows"]]
 for j, meta in enumerate(data["selectorMeta"]):
  rows[data["selectorStart"] + j] = tuple(meta["anchorRow"])
 return tuple(rows)

def rebuild(data, rows):
 n = data["n"]; pair = Counter(); load = Counter(); support = set(); selected = set()
 for row in rows:
  selected.update(row); load.update(row)
  support.update(E(x, y) for x, y in zip(row, row[1:]))
  for x in row:
   for y in row: pair[x, y] += 1
 active = {e for e in set(data["blue"]) - support if e[0] in selected and e[1] in selected}
 adj = defaultdict(set)
 for u, v in active: adj[u].add(v); adj[v].add(u)
 component_of = {}; components = []
 for root in sorted(selected):
  if root in component_of: continue
  seen = {root}; q = deque([root])
  while q:
   u = q.popleft()
   for v in adj[u]:
    if v not in seen: seen.add(v); q.append(v)
  cid = len(components); components.append(seen)
  for v in seen: component_of[v] = cid
 bad_cids = {component_of[u] for u, v in data["bad"]
             if u in component_of and v in component_of and component_of[u] == component_of[v]}
 active_v = {v for v in selected if component_of[v] in bad_cids}
 demanded = {e for e in active if e[0] in active_v}
 deg = Counter(x for e in demanded for x in e)
 collision = {v: 2 * sum(max(0, pair[v, y] - 1) for y in range(n)) for v in active_v}
 hit = {v: max(0, deg[v] - max(0, n - 5 * load[v])) for v in active_v}
 return dict(rows=rows, pair=pair, load=load, support=support, selected=selected,
             active=active, active_v=active_v, demanded=demanded,
             components=components, component_of=component_of,
             collision=collision, hit=hit)

def auxiliary(data, st):
 n = data["n"]; pair = st["pair"]; sdeg = Counter(); sign = {}
 for e in data["blue"]:
  sign[e] = 1; sdeg[e[0]] += 1; sdeg[e[1]] += 1
 for e in data["bad"]:
  sign[e] = -1; sdeg[e[0]] -= 1; sdeg[e[1]] -= 1
 companions = {o: {x for x in range(n) if pair[o, x] > 0} for o in OWNERS}
 masks = {}; reasons = {}
 for o in OWNERS:
  for y in range(n):
   if y == o or pair[o, y]: continue
   for h in (0, 1):
    s = (o, y, h); reserved = h == 0 and E(o, y) in st["active"] and o in st["active_v"]
    if not reserved:
     masks[s] = masks.get(s, 0) | (1 << o); reasons[s] = reasons.get(s, 0) | 1
 for o in OWNERS:
  C = companions[o]
  for x in C:
   for y in C:
    if x == y or pair[x, y]: continue
    e = E(x, y); sigma2 = sdeg[x] + sdeg[y] - 2 * sign.get(e, 0)
    if sigma2 < 0: continue
    for h in (0, 1):
     s = (x, y, h); reserved = h == 0 and e in st["active"] and x in st["active_v"]
     if not reserved:
      masks[s] = masks.get(s, 0) | (1 << o); reasons[s] = reasons.get(s, 0) | 2
 demand = {o: st["collision"].get(o, 0) + st["hit"].get(o, 0) for o in OWNERS}
 mh, rh = Counter(masks.values()), Counter(reasons.values()); cuts = []
 for sm in range(8):
  shore = [o for o in OWNERS if sm & (1 << o)]
  d = sum(demand[o] for o in shore); r = sum(v for k, v in mh.items() if k & sm)
  cuts.append(dict(shore_mask=sm, shore=shore, demand=d, reachable_sources=r, defect=d-r))
 records = [[x, y, h, masks[x,y,h], reasons[x,y,h]] for x,y,h in sorted(masks)]
 return {"demand_by_owner": demand, "companions_by_owner": {str(k):len(v) for k,v in companions.items()},
  "source_histogram_by_owner_mask": {str(k):v for k,v in sorted(mh.items())},
  "source_histogram_by_reason_mask": {str(k):v for k,v in sorted(rh.items())},
 "source_count": len(masks), "source_records_sha256": sha_obj(records), "cuts": cuts}

def singleton_shell(name, core, data, st):
 """Exact compiled half-singleton Door/vertex requirement, not available capacity."""
 blue, bad, support = set(data["blue"]), set(data["bad"]), st["support"]
 S = {e for e in bad if e[0] in core and e[1] in core}
 F = {e for e in support if e[0] in core and e[1] in core}; O = blue - F
 internal = {e for e in O if e[0] in core and e[1] in core}
 boundary = {e for e in O if (e[0] in core) ^ (e[1] in core)}
 exterior = O - internal - boundary
 assert internal.isdisjoint(boundary) and internal.isdisjoint(exterior) and boundary.isdisjoint(exterior)
 half = Fraction(1, 2)
 load = {e: half * int(e[0] in core) + half * int(e[1] in core) for e in O}
 deg = Counter(v for e in internal for v in e)
 vcap = {v: half * deg[v] for v in sorted(core) if deg[v]}
 dcap = {e: half for e in sorted(boundary)}
 sep = {str(v): edges(e for e in bad if v in e) for v in sorted(core)}
 dB = {str(v): edges(e for e in blue if v in e) for v in sorted(core)}
 coverage = {e: sum((half for v in core if v in e), Fraction(0)) for e in S}
 congestion = {e: sum((half for v in core if v in e), Fraction(0)) for e in F}
 routed = {e: (half if e in boundary else (1 if e in internal else 0)) for e in O}
 assert all(x == 1 for x in coverage.values()) and all(x == 1 for x in congestion.values())
 assert all(load[e] == routed[e] for e in O)
 assert sum(vcap.values(), Fraction(0)) == len(internal)
 assert sum(dcap.values(), Fraction(0)) == half * len(boundary)
 total = sum(load.values(), Fraction(0))
 assert total == sum(vcap.values(), Fraction(0)) + sum(dcap.values(), Fraction(0))
 arcs = {
  "door": [{"port":list(e), "sink":["door",e[0],e[1]], "q":rat(half)} for e in sorted(boundary)],
  "vertexSlack": [{"port":list(e), "sink":["vertexSlack",v], "q":rat(half)}
                  for e in sorted(internal) for v in e],
  "c5Base": [], "prune": []}
 return {
  "name": name, "status": "GRAPH_DERIVED_REQUIREMENT_ONLY",
  "warning": "Required capacities/incidence are constructor hypotheses, not R29 production tokens.",
  "core_vertices": sorted(core),
  "sets": {"S_bad_internal":edges(S), "F_selected_support_internal":edges(F),
           "O_blue_minus_F":edges(O), "O_internal":edges(internal),
           "O_boundary":edges(boundary), "O_exterior_zero_load":edges(exterior)},
  "counts": {"K_singleton_cuts":len(core), "S":len(S), "F":len(F), "O":len(O),
             "O_internal_load_one":len(internal), "O_boundary_load_half":len(boundary),
             "O_exterior_load_zero":len(exterior)},
  "variables": {"lambda":{str(v):rat(half) for v in sorted(core)}, "q_nonzero_arcs":arcs},
  "separator": {"formula":"sep(x)=deltaM({x}); dB(x)=deltaB({x})",
                "sep_by_singleton_cut":sep, "dB_by_singleton_cut":dB},
  "exact_checks": {"coverage_all_equal_one":True, "support_congestion_all_equal_one":True,
    "route_equal_load_on_every_O_port":True, "required_capacity_equal_flow_by_sink":True,
    "F_disjoint_O":F.isdisjoint(O),
    "dB_subset_F_union_O":all(set(map(tuple,dB[str(v)])) <= F|O for v in core)},
  "load_histogram": {f"{q.numerator}/{q.denominator}":n for q,n in sorted(Counter(load.values()).items())},
  "total_external_load":rat(total),
  "incremental_disjoint_source_classes": [
   {"class":"door", "ports_after_prior_classes_removed":len(boundary),
    "required_capacity_total":rat(sum(dcap.values(),Fraction(0))), "production_available_capacity":None},
   {"class":"vertexSlack", "ports_after_door_removed":len(internal),
    "required_capacity_total":rat(sum(vcap.values(),Fraction(0))), "production_available_capacity":None},
   {"class":"c5Base", "ports_after_door_and_vertexSlack_removed":None,
    "required_capacity_total":None, "production_available_capacity":None},
   {"class":"prune", "ports_after_prior_classes_removed":None,
    "required_capacity_total":None, "production_available_capacity":None}],
  "required_capacity_by_sink": {
   "door":[{"sink":["door",e[0],e[1]],"capacity":rat(q)} for e,q in sorted(dcap.items())],
   "vertexSlack":[{"sink":["vertexSlack",v],"capacity":rat(q)} for v,q in sorted(vcap.items())],
   "c5Base":None, "prune":None}}

def hashes():
 out = {}
 for rel in SOURCE_FILES:
  p = ROOT / rel; assert p.is_file(), rel; out[rel] = sha_file(p)
 rel = Path(__file__).resolve().relative_to(ROOT).as_posix(); out[rel] = sha_file(Path(__file__).resolve())
 return out

MISSING = [
 ("hub_shore_to_fullbank_atom_or_localCover", "Demand owners/obligations -> FullBank Atom/S or FullBankLocalCover",
  "No compiled consumer connects ActiveCollisionHalf/ActiveHitNeed to either FullBank structure.",
  "problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:27-40"),
 ("r29_F_O_K_Ufam_lambda", "production S,F,O,K,Ufam,lambda",
  "The interface is parametric; the singleton shells are not a provider for 19,953 obligations.",
  "problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:27-40"),
 ("r29_checked_FullBankGlobalPackage", "P : FullBankGlobalPackage G c rows and hP : P.Checked",
  "No R29 component/local ownership, tokens, spends, reserves, or checked identities exist.",
  "problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:134-143,177-227"),
 ("ledger_token_table_all_four_kinds", "token(comp,kind,sourceId,capQ) for door/vertexSlack/c5Base/prune",
  "The four classes are enumerated but no R29 token table is provided.",
  "problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:25-30,69-82"),
 ("port_to_token_legal_incidence", "inc : Port -> Sink -> Prop including non-door arcs",
  "FullBankPortSinks explicitly says legal edge-to-token incidence is absent.",
  "problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:80-81"),
 ("typed_token_to_wall_sink_adapter", "sinkOf injection, legality preservation, cap equality",
  "DoorWallAdapter is a supplied obligation and has no R29 instance.",
  "problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean:34-42"),
 ("door_source_data", "portEdge, typed tokens, doorOf injection, capQ >= 25",
  "OwnEdgeDoorSourceData checks supplied data; it does not construct it from the graph.",
  "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:91-112"),
 ("vertexSlack_available_capacity_and_incidence", "per-vertex kap and legal internal-port arcs",
  "The singleton bridge takes these as hypotheses and does not derive ledger capacity.",
  "problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:75-100"),
 ("c5Base_enumerator_token_capacity_incidence", "finite terminals, source tokens/capQ, legal arcs",
  "The compiled module checks one switch terminal; matching/Free ownership are separate.",
  "problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean:13-15,24-43"),
 ("prune_transition_token_capacity_incidence", "checked prune transitions, slot transport, tokens, arcs",
  "Prune is an enum/source constructor only; no graph-derived provider is compiled.",
  "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:24-41"),
 ("production_q_or_assignedSink", "exact q(c,j) satisfying routing/incidence/capacity",
  "AssignedSink constructs q only after sink, legality, and hcap are supplied.",
  "problems/23/lean/Erdos23Delta0/Ell5FullBankAssignedSink.lean:55-93"),
 ("r29_lean_GraphData_RowDB_adapter", "literal R29 GraphData/CutData/RowDB provider",
  "The deterministic constructor is Python; no compiled R29 package imports the instance.",
  "tmp/fanout/r29_gate/lead/r29_lead_gate.py:129-276")]

def main():
 lead, data = load_cage(); rows = anchored(data); st = rebuild(data, rows); aux = auxiliary(data, st)
 cage_sha = sha_bytes(lead.canonical_bytes(data))
 assert cage_sha == "fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f"
 tuple_sha = sha_obj([list(r) for r in rows])
 assert tuple_sha == "ab37d295364a110795388fbb8bb695f5ae849514348ff84bc29edf8ca57493f9"
 assert sha_file(ROOT / "tmp/fanout/r29_gate/d09/retry2/best_tuple.json") == "93d5d64c55338186603b718b5d6bb162d907c4fc868ce276808e01822c395901"
 cert = json.loads(CUT_CERT.read_text(encoding="utf-8")); full = aux["cuts"][7]
 assert full == {"shore_mask":7,"shore":[0,1,2],"demand":19953,"reachable_sources":19925,"defect":28}
 assert cert["maximum_deficiency_cut"]["demand"] == 19953
 assert cert["maximum_deficiency_cut"]["neighborhood"] == 19925
 assert cert["maximum_deficiency_cut"]["gap"] == 28
 assert aux["source_histogram_by_owner_mask"] == {"1":5775,"2":5775,"4":5775,"7":2600}
 assert aux["source_histogram_by_reason_mask"] == {"1":17325,"2":2600}
 hub_comp = set(st["components"][st["component_of"][0]])
 assert len(hub_comp) == 19 and all(st["component_of"][o] == st["component_of"][0] for o in OWNERS)
 literal = singleton_shell("literal_owner_shore_{0,1,2}", set(OWNERS), data, st)
 closure = singleton_shell("active_component_closure_of_hub_shore", hub_comp, data, st)
 assert literal["counts"]["S"] == 0 and closure["counts"]["S"] == 1
 O = set(data["blue"]) - st["support"]
 internal = {e for e in O if e[0] in st["selected"] and e[1] in st["selected"]}
 boundary = {e for e in O if (e[0] in st["selected"]) ^ (e[1] in st["selected"])}
 exterior = O - internal - boundary
 assert (len(internal),len(boundary),len(exterior)) == (1370,2760,112)
 missing = [{"field":a,"required_type":b,"reason":c,"source":d} for a,b,c,d in MISSING]
 output = {
  "schema":"r29-fullbank-lp-audit-v1", "decision":"UNDEFINED",
  "decisive_question_answer":"The complete implemented production relation cannot be instantiated: atoms/local ownership, ledger tokens, capacities, legal incidence, and routing providers are absent. Neither absorption of 28 nor a production FullBank Hall defect is proved.",
  "arithmetic":"integer and fractions.Fraction only",
  "reconstruction": {"n":data["n"],"blue_edges":len(data["blue"]),"bad_edges":len(data["bad"]),
   "rows":len(rows),"selected_vertices":len(st["selected"]),"selected_support_edges":len(st["support"]),
   "selected_support_edges_list":edges(st["support"]),"off_support_blue_edges":len(O),
   "off_support_load_classes_for_full_selected_core":{"internal_load_one":len(internal),
    "boundary_load_half":len(boundary),"exterior_load_zero":len(exterior),
    "total_load":rat(len(internal)+Fraction(len(boundary),2))},
   "active_edges":len(st["active"]),"active_vertices":len(st["active_v"]),
   "demanded_active_edges":len(st["demanded"]),"cage_sha256":cage_sha,
   "raw_all_anchor_rows_sha256":tuple_sha,
   "d09_encoded_all_anchor_tuple_sha256":"93d5d64c55338186603b718b5d6bb162d907c4fc868ce276808e01822c395901"},
  "auxiliary_relation_rebuilt": {"status":"FAIL_FOR_AUXILIARY_RELATION_ONLY",
   "owners":{str(o):{"collision":st["collision"].get(o,0),"hit_need":st["hit"].get(o,0),
                     "demand":aux["demand_by_owner"][o]} for o in OWNERS},
   **aux, "cut_certificate_file_sha256":sha_file(CUT_CERT)},
  "implemented_lp_contract": {
   "variables":"lambda_k >= 0; q_cj >= 0",
   "coverage":"r in S: 1 <= sum_{k in K, r in sep(k)} lambda_k",
   "support_congestion":"c in F: sum_{k in K, c in dB(k)} lambda_k <= 1",
   "port_routing":"c in O: sum_{k in K, c in dB(k)} lambda_k <= sum_{j in J} q_cj",
   "sink_capacity":"j in J: sum_{c in O} q_cj <= kap(j)",
   "incidence_support":"q_cj > 0 implies inc(c,j)",
   "graph_separator":"sep(k)=deltaM(G,cut,Ufam(k)); dB(k)=deltaB(G,cut,Ufam(k))",
   "hall_consumer_extra_conditions":["Disjoint F O","dB(k) subset F union O",
                                      "card(sep(k)) <= card(dB(k))"],
   "sink_classes_declared":["door","vertexSlack","c5Base","prune"],
   "ledger_hall_capacity_formula":"kap(token)=token.capQ/25"},
  "graph_derived_singleton_shells":[literal,closure],
  "interpretation_guardrails":[
   "The literal owner shore has S.card=0 in the graph-edge singleton LP; it is not the 19,953-element Demand shore.",
   "The active-component closure has S.card=1; it also is not the 19,953-element Demand shore.",
   "Required singleton capacities are not available production capacities.",
   "C5-base prose capacities are not counted without a compiled token/cap/incidence provider.",
   "Prune contributes no counted capacity without a compiled graph transition/provider.",
   "Comparing auxiliary defect 28 with singleton external load is ill-typed without the missing adapter."],
  "missing_provider_fields":missing,
  "exact_assertions":{"cage_hash_matches_authoritative":True,"all_anchor_tuple_hash_matches_authoritative":True,
   "auxiliary_demand_19953":True,"auxiliary_reach_19925":True,"auxiliary_defect_28":True,
   "hub_vertices_share_one_19_vertex_active_component":True,"literal_hub_singleton_atom_count_zero":True,
   "hub_component_singleton_atom_count_one":True,"complete_production_lp_instantiated":False},
  "source_sha256":hashes()}
 RESULT.write_text(json.dumps(output,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 if REPORT.is_file():
  manifest = {p.name:sha_file(p) for p in (Path(__file__).resolve(),RESULT,REPORT)}
  manifest["note"] = "HASHES.json intentionally omits its own recursive hash; input hashes are in RESULT.json/source_sha256."
  HASHES.write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"decision":"UNDEFINED","demand":19953,"reach":19925,"defect":28,
  "hub_component_vertices":19,"hub_component_singleton_external_load":closure["total_external_load"],
  "missing_provider_fields":len(missing),"result":str(RESULT)},sort_keys=True))

if __name__ == "__main__": main()
