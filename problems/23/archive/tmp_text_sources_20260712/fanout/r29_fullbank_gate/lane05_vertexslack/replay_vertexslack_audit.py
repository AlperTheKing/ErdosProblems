"""Exact R29 vertexSlack audit; integer/Fraction arithmetic only."""
from collections import Counter, defaultdict, deque
from fractions import Fraction
import hashlib, importlib.util, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in (HERE,*HERE.parents) if (p/'GOAL_LOOP.md').is_file())
LEAD=ROOT/'tmp/fanout/r29_gate/lead/r29_lead_gate.py'
CERT=ROOT/'tmp/fanout/r29_gate/d05/retry2/cut_certificate.json'
OUT=HERE/'result.json'; OWNERS=(0,1,2)
PROD=(
'problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean',
'problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean',
'problems/23/lean/Erdos23Delta0/Ell5SingletonEndpointFlow.lean',
'problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean',
'problems/23/lean/Erdos23Delta0/Ell5FullBankHall.lean',
'problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean',
'problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean',
'problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean',
'problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean',
'problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean',
'problems/23/lean/Erdos23Delta0/CollisionReserveCounting.lean')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(u,v):
    assert u!=v
    return (u,v) if u<v else (v,u)
def qstr(q): return str(q.numerator) if q.denominator==1 else f'{q.numerator}/{q.denominator}'

def cage():
    s=importlib.util.spec_from_file_location('r29_vertexslack_input',LEAD)
    m=importlib.util.module_from_spec(s); s.loader.exec_module(m); r=m.build()
    return {'n':int(r['n']),'blue':frozenset(map(tuple,r['blue'])),'bad':frozenset(map(tuple,r['bad'])),
      'side':tuple(r['side']),'rows':tuple(map(tuple,r['rows'])),'atoms':tuple(map(tuple,r['atoms'])),
      'meta':tuple(dict(x) for x in r['selectorMeta']),'start':r['selectorStart'],'stop':r['selectorStop']}

def canonical_sha(C):
    p={'n':C['n'],'blue':sorted(C['blue']),'bad':sorted(C['bad']),'rows':C['rows']}
    return hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def anchor_rows(C):
    rows=list(C['rows'])
    for j,m in enumerate(C['meta']): rows[C['start']+j]=tuple(m['anchorRow'])
    return tuple(rows)

def scope(C,rows):
    n=C['n']; occ=Counter(x for r in rows for x in r); pair=Counter(); support=set()
    for r in rows:
        assert len(r)==len(set(r))==5
        for x in r:
            for y in r: pair[x,y]+=1
        support.update(norm(x,y) for x,y in zip(r,r[1:]))
    selected=set(occ)
    active={e for e in C['blue'] if e not in support and e[0] in selected and e[1] in selected}
    adj=defaultdict(set)
    for u,v in active: adj[u].add(v); adj[v].add(u)
    comp={}; comps=[]
    for root in sorted(selected):
        if root in comp: continue
        seen={root}; todo=deque([root])
        while todo:
            u=todo.popleft()
            for v in adj[u]:
                if v not in seen: seen.add(v); todo.append(v)
        k=len(comps); comps.append(seen)
        for v in seen: comp[v]=k
    badc={comp[u] for u,v in C['bad'] if u in comp and v in comp and comp[u]==comp[v]}
    av={v for v in selected if comp[v] in badc}; dae={e for e in active if e[0] in av and e[1] in av}
    deg=Counter()
    for u,v in dae: deg[u]+=1; deg[v]+=1
    coll={v:2*sum(max(0,pair[v,y]-1) for y in range(n)) for v in av}
    hit={v:max(0,deg[v]-max(0,n-5*occ[v])) for v in av}
    return dict(occ=occ,pair=pair,selected=selected,support=support,active=active,av=av,dae=dae,deg=deg,coll=coll,hit=hit)

def sources(C,S):
    pair=S['pair']; active=S['active']; av=S['av']; sd=Counter(); sign={}
    for e in C['blue']: sign[e]=1; sd[e[0]]+=1; sd[e[1]]+=1
    for e in C['bad']: sign[e]=-1; sd[e[0]]-=1; sd[e[1]]-=1
    companions={o:{x for x in range(C['n']) if pair[o,x]>0} for o in OWNERS}
    masks={}; reasons={}
    for o in OWNERS:
        for y in range(C['n']):
            if y==o or pair[o,y]!=0: continue
            for h in (0,1):
                s=(o,y,h); reserved=h==0 and norm(o,y) in active and o in av
                if not reserved: masks[s]=masks.get(s,0)|(1<<o); reasons[s]=reasons.get(s,0)|1
    for o in OWNERS:
        for x in companions[o]:
            for y in companions[o]:
                if x==y or pair[x,y]!=0: continue
                e=norm(x,y); sigma2=sd[x]+sd[y]-2*sign.get(e,0)
                if sigma2<0: continue
                for h in (0,1):
                    s=(x,y,h); reserved=h==0 and e in active and x in av
                    if not reserved: masks[s]=masks.get(s,0)|(1<<o); reasons[s]=reasons.get(s,0)|2
    return masks,reasons,companions

def call_search(symbol):
    run=subprocess.run(['git','grep','-n','-F',symbol,'--','problems/23/lean/Erdos23Delta0'],cwd=ROOT,text=True,capture_output=True,check=False)
    assert run.returncode in (0,1)
    hits=[]
    for raw in run.stdout.splitlines():
        path,line_no,line=raw.split(':',2)
        if not line.lstrip().startswith(('noncomputable def '+symbol,'def '+symbol)):
            hits.append(f'{path}:{line_no}')
    return {'nondefinition_occurrences':len(hits),'locations':hits}

def main():
    C=cage(); n=C['n']; graph=C['blue']|C['bad']
    assert (n,len(C['blue']),len(C['bad']),len(graph))==(2943,7039,1383,8422)
    assert C['blue'].isdisjoint(C['bad'])
    assert all(C['side'][u]!=C['side'][v] for u,v in C['blue'])
    assert all(C['side'][u]==C['side'][v] for u,v in C['bad'])
    rows=anchor_rows(C)
    for a,r in zip(C['atoms'],rows):
        assert norm(r[0],r[-1])==a and all(norm(u,v) in C['blue'] for u,v in zip(r,r[1:]))
    S=scope(C,rows); masks,reasons,companions=sources(C,S)
    db={o:S['coll'][o]+S['hit'][o] for o in OWNERS}; demand=sum(db.values()); reach=len(masks); defect=demand-reach
    assert (demand,reach,defect)==(19953,19925,28)
    slack={v:Fraction(max(0,n-5*S['occ'][v]),1) for v in range(n)}
    owner_slack=sum((slack[v] for v in OWNERS),Fraction(0)); absorb=min(Fraction(defect),owner_slack)
    active_slack=sum((slack[v] for v in S['av']),Fraction(0)); all_slack=sum(slack.values(),Fraction(0))
    owners={str(v):{'row_occurrence':S['occ'][v],'selected_load_T':5*S['occ'][v],
      'ordinary_slack_hall_units':qstr(slack[v]),'collision_demand':S['coll'][v],'hit_need_demand':S['hit'][v]} for v in OWNERS}
    aprof={str(v):{'row_occurrence':S['occ'][v],'selected_load_T':5*S['occ'][v],
      'ordinary_slack_hall_units':qstr(slack[v])} for v in sorted(S['av'])}
    ref=json.loads(CERT.read_text(encoding='utf-8'))['maximum_deficiency_cut']
    assert ref=={'demand':demand,'gap':defect,'neighborhood':reach,'shore':[0,1,2],'shore_mask':7}
    result={
      'schema':'R29 vertexSlack exact audit v1','verdict':'UNDEFINED',
      'verdict_reason':'No compiled graph-to-vertexSlack/token constructor fixes kap, capQ, component ownership, or legal incidence for R29; implemented incremental FullBank capacity is not a defined number.',
      'reconstruction':{'n':n,'blue_edges':len(C['blue']),'bad_edges':len(C['bad']),'graph_edges':len(graph),'rows':len(rows),
        'selector_rows_replaced_by_anchor':len(C['meta']),'selected_vertices':len(S['selected']),'active_vertices':len(S['av']),
        'active_edges':len(S['active']),'demanded_active_edges':len(S['dae']),'canonical_input_sha256':canonical_sha(C)},
      'auxiliary_hub_shore_recomputed':{'owners':list(OWNERS),'demand_by_owner':{str(k):v for k,v in db.items()},
        'demand':demand,'distinct_freehalf_reach':reach,'defect':defect,
        'source_histogram_by_owner_mask':{str(k):v for k,v in sorted(Counter(masks.values()).items())},
        'source_histogram_by_reason_mask':{str(k):v for k,v in sorted(Counter(reasons.values()).items())},
        'companion_counts':{str(o):len(companions[o]) for o in OWNERS}},
      'implemented_local_vertexSlack_contract':{
        'sink_key':'core vertex x','fixed_endpoint_route_per_incident_nonDoor_edge':'1/2',
        'capacity_obligation':'(# incident non-Door off-support edges)/2 <= kap(x)',
        'eligibility_obligation':'x in core C and x incident to edge e implies inc(e, vertexSlack(x))',
        'door_overlap_removal':'D and O\\D partition edge load; D uses own Door, O\\D uses endpoint vertexSlack',
        'global_ledger_hall_scaling':'hallCapQ(token) = capQ(token)/25',
        'missing_scaling_bridge':'No compiled theorem equates local kap(x) with typed/global ledger capQ/25.'},
      'conditional_ordinary_slack_not_a_fullbank_instance':{
        'formula':'max(0, N - T(v)), T(v)=5*row_occurrence(v)','owners':owners,
        'owner_slack_sum_hall_units':qstr(owner_slack),'incremental_absorbable_defect_if_only_owner_incidence_is_allowed':qstr(absorb),
        'residual_defect_under_that_conditional_model':qstr(Fraction(defect)-absorb),'active_vertex_profile':aprof,
        'active_component_slack_sum_hall_units':qstr(active_slack),'all_vertex_slack_sum_hall_units':qstr(all_slack),
        'active_component_sum_is_not_reachable_capacity':'Using non-owner component slack for hub obligations requires the missing legal incidence/flow adapter.'},
      'overlap_audit':{
        'door_vs_vertexSlack':'Locally disjoint only after explicit D subset O is supplied; no R29 D extractor is compiled.',
        'transfer_FreeHalf_vs_vertexSlack':'No compiled common token/incidence adapter exists, so disjoint incremental capacity is undefined.',
        'safe_increment_from_vertexSlack_for_hub_shore':'0 under conditional owner-only incidence, because all three owner slacks are zero.'},
      'constructor_search':{
        'certificate_of_singletonCore_vertexSlack':call_search('certificate_of_singletonCore_vertexSlack'),
        'certificate_of_internalEndpointSlack_boundaryDoors':call_search('certificate_of_internalEndpointSlack_boundaryDoors')},
      'missing_api':['R29/core extractor producing S,F,O,D,C from GraphData/CutData/RowDB',
        'graph theorem/definition fixing slack(v) and kap(vertexSlack(v))','typed vertexSlack token constructor integrated into FullBankGlobalPackage',
        'legal port/obligation-to-vertexSlack incidence adapter','shared no-double-spend relation joining FreeHalf transfer, Door, and vertexSlack sources'],
      'sha256':{'lead_constructor':sha(LEAD),'reference_cut_certificate':sha(CERT),**{p:sha(ROOT/p) for p in PROD}}}
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'verdict':'UNDEFINED','demand':demand,'reach':reach,'defect':defect,
      'owner_slack':qstr(owner_slack),'conditional_increment':qstr(absorb),
      'active_component_slack_nonbinding':qstr(active_slack),'output':str(OUT)},sort_keys=True))
if __name__=='__main__': main()