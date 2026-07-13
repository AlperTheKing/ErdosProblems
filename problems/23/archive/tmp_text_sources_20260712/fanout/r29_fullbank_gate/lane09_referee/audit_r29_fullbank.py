"""Independent exact R29 referee gate. Integers only; writes only audit_result.json."""
from collections import Counter, defaultdict, deque
import hashlib, importlib.util, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
LEAD=ROOT/'tmp/fanout/r29_gate/lead/r29_lead_gate.py'
REF=ROOT/'tmp/fanout/r29_gate/d05/retry2/cut_certificate.json'
OWNERS=(0,1,2)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(u,v): return (u,v) if u<v else (v,u)
def jsha(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def load():
    s=importlib.util.spec_from_file_location('r29lead',LEAD); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
    r=m.build()
    d={'n':int(r['n']),'blue':frozenset(map(tuple,r['blue'])),'bad':frozenset(map(tuple,r['bad'])),
       'side':tuple(r['side']),'rows':tuple(map(tuple,r['rows'])),'meta':tuple(r['selectorMeta']),
       'start':int(r['selectorStart'])}
    return d,m

def anchor_rows(d):
    rs=list(d['rows'])
    for j,q in enumerate(d['meta']): rs[d['start']+j]=tuple(q['anchorRow'])
    return tuple(rs)

def state(d,rows):
    pair=Counter(); load=Counter(); support=set(); selected=set()
    for r in rows:
        assert len(r)==5 and len(set(r))==5
        selected.update(r)
        for x in r:
            load[x]+=1
            for y in r: pair[x,y]+=1
        support.update(norm(x,y) for x,y in zip(r,r[1:]))
    ae={e for e in d['blue'] if e not in support and e[0] in selected and e[1] in selected}
    adj=defaultdict(set)
    for u,v in ae: adj[u].add(v); adj[v].add(u)
    comp={}; comps=[]
    for root in sorted(selected):
        if root in comp: continue
        seen={root}; q=deque([root])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if v not in seen: seen.add(v); q.append(v)
        cid=len(comps); comps.append(seen)
        for v in seen: comp[v]=cid
    badc={comp[u] for u,v in d['bad'] if u in comp and v in comp and comp[u]==comp[v]}
    av={v for v in selected if comp[v] in badc}; de={e for e in ae if e[0] in av}
    deg=Counter()
    for u,v in de: deg[u]+=1; deg[v]+=1
    coll={v:2*sum(max(0,pair[v,y]-1) for y in range(d['n'])) for v in av}
    hit={v:max(0,deg[v]-max(0,d['n']-5*load[v])) for v in av}
    return dict(pair=pair,load=load,support=support,selected=selected,active_edges=ae,
                active_vertices=av,demanded_edges=de,component=comp,components=comps,collision=coll,hit=hit)

def signed(d):
    z=Counter(); s={}
    for u,v in d['blue']: s[u,v]=1; z[u]+=1; z[v]+=1
    for u,v in d['bad']: s[u,v]=-1; z[u]-=1; z[v]-=1
    return z,s
def sigma(x,y,z,s): return z[x]+z[y]-2*s.get(norm(x,y),0)
def reserved(st,x,y,h): return h==0 and norm(x,y) in st['active_edges'] and x in st['active_vertices']

def add(dst,cand):
    old=len(dst); overlap=strong=0
    for k,m in cand.items():
        if k in dst:
            overlap+=1; strong+=int((dst[k]|m)!=dst[k]); dst[k]|=m
        else: dst[k]=m
    return {'candidate':len(cand),'overlap':overlap,'new':len(cand)-overlap,
            'mask_strengthened':strong,'union':len(dst),'prior_union':old}

def source_stages(d,st):
    pair=st['pair']; z,sgn=signed(d); src={}; audit={}
    same={}
    for o in OWNERS:
        for y in range(d['n']):
            if y==o or pair[o,y]: continue
            for h in (0,1):
                if not reserved(st,o,y,h): same[o,y,h]=same.get((o,y,h),0)|(1<<o)
    audit['sameFirst']=add(src,same)
    rc={}; companions={o:{x for x in range(d['n']) if pair[o,x]>0} for o in OWNERS}
    for o in OWNERS:
        for x in companions[o]:
            for y in companions[o]:
                if x==y or pair[x,y] or sigma(x,y,z,sgn)<0: continue
                for h in (0,1):
                    if not reserved(st,x,y,h): rc[x,y,h]=rc.get((x,y,h),0)|(1<<o)
    audit['rowCompanion']=add(src,rc); old=dict(src)
    ba=defaultdict(set)
    for u,v in d['blue']: ba[u].add(v); ba[v].add(u)
    cb={}
    for o in OWNERS:
        for x in ba[o]:
            for y in ba[o]:
                if x==y or pair[x,y] or sigma(x,y,z,sgn)<2: continue
                for h in (0,1):
                    if not reserved(st,x,y,h): cb[x,y,h]=cb.get((x,y,h),0)|(1<<o)
    audit['commonBlueTerminal']=add(src,cb)
    audit['companions']={str(o):len(companions[o]) for o in OWNERS}
    return old,src,audit

def hist(src): return Counter(src.values())
def hall(name,h,demand):
    cuts=[]
    for a in range(8):
        ds=sum(demand[o] for o in OWNERS if a&(1<<o)); nr=sum(n for m,n in h.items() if m&a)
        cuts.append({'mask':a,'shore':[o for o in OWNERS if a&(1<<o)],'demand':ds,'reach':nr,'gap':ds-nr,'pass':ds<=nr})
    w=max(cuts,key=lambda x:(x['gap'],-x['mask'])); wn=max(cuts[1:],key=lambda x:(x['gap'],-x['mask']))
    return {'name':name,'histogram':{str(k):v for k,v in sorted(h.items())},'reach':sum(h.values()),
            'cuts':cuts,'worst':w,'worst_nonempty':wn,'all_pass':all(x['pass'] for x in cuts)}

def outside_r23(d,st):
    """Exact aggregate of the R23 prose relation; this is not production semantics."""
    outside=set(range(d['n']))-st['selected']; adj=defaultdict(set)
    for u,v in d['blue']:
        if u in outside and v in outside: adj[u].add(v); adj[v].add(u)
    oc={}; comps=[]
    for root in sorted(outside):
        if root in oc: continue
        seen={root}; q=deque([root])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if v not in seen: seen.add(v); q.append(v)
        cid=len(comps); comps.append(seen)
        for v in seen: oc[v]=cid
    att=[set() for _ in comps]
    for u,v in d['blue']:
        if u in outside and v in st['selected']: att[oc[u]].add(v)
        elif v in outside and u in st['selected']: att[oc[v]].add(u)
    masks=[]
    for A in att:
        m=0
        for o in OWNERS:
            if any(st['pair'][o,a]>0 and st['component'][a]==st['component'][o] for a in A): m|=1<<o
        masks.append(m)
    h=Counter()
    for i,X in enumerate(comps):
        for j,Y in enumerate(comps):
            m=masks[i]&masks[j]
            if not m: continue
            p=len(X)*len(Y)-(len(X) if i==j else 0); h[m]+=2*p
    size_hist=Counter(map(len,comps))
    return {'outside_vertices':len(outside),'component_count':len(comps),'component_size_hist':{str(k):v for k,v in sorted(size_hist.items())},
            'components_with_attachment':sum(bool(A) for A in att),
            'component_mask_hist':{str(m):sum(x==m for x in masks) for m in sorted(set(masks))},
            'vertex_mask_hist':{str(m):sum(len(comps[i]) for i,x in enumerate(masks) if x==m) for m in sorted(set(masks))},
            'source_hist':{str(k):v for k,v in sorted(h.items())},'candidate':sum(h.values()),
            '_hist':h,'_component':oc,'_masks':masks}

def merge_outside(src,out):
    h=hist(src)
    for m,n in out['_hist'].items(): h[m]+=n
    overlap=strong=0; oc=out['_component']; masks=out['_masks']
    for (x,y,_),pm in src.items():
        if x not in oc or y not in oc: continue
        om=masks[oc[x]]&masks[oc[y]]
        if not om: continue
        overlap+=1; um=pm|om; strong+=int(um!=pm)
        h[pm]-=1; h[om]-=1; h[um]+=1
    h+=Counter()
    return h,{'candidate':out['candidate'],'overlap':overlap,'new':out['candidate']-overlap,
              'mask_strengthened':strong,'union':sum(h.values()),'prior_union':len(src)}

def scan_symbols():
    names=['CheckedOutsideAttachmentBaseTerminal','outsideAttachment','CheckedTransferMatching',
           'checkedTransferMatching_to_activeFullBank','ActiveComponentFullBankCert']
    ans={x:[] for x in names}; base=ROOT/'problems/23/lean/Erdos23Delta0'
    paths=list((base/'Gamma').rglob('*.lean'))
    paths += [base/x for x in ['Ell5FullBankInterface.lean','Ell5FullBankHall.lean',
      'Ell5FullBankAssignedSink.lean','Ell5FullBankWallAdapter.lean','Ell5ActiveComponentHall.lean',
      'Ell5ActiveComponentBankHall.lean','Ell5ActiveComponentFlow.lean','EndpointReserveHall.lean']]
    for p in paths:
        lines=p.read_text(encoding='utf-8').splitlines()
        for name in names:
            for i,line in enumerate(lines,1):
                if name in line: ans[name].append({'path':p.relative_to(ROOT).as_posix(),'line':i,'text':line.strip()})
    return ans

def source_hashes():
    rel=['GOAL_LOOP.md','tmp/fanout/r29_fullbank_gate/COMMON.md',
         'problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md',
         'tmp/fanout/r29_gate/lead/r29_lead_gate.py','tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py',
         'tmp/fanout/r29_gate/d05/retry2/cut_certificate.json',
         'problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean',
         'problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedOwnerHallReduction.lean',
         'problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean',
         'problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean',
         'problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean',
         'problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean',
         'problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean',
         'problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean',
         'problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean',
         'problems/23/lean/Erdos23Delta0/Ell5ActiveComponentBankHall.lean',
         'problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean',
         'problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md']
    return {x:sha(ROOT/x) for x in rel}

def main():
    d,lead=load(); rows=anchor_rows(d); st=state(d,rows)
    demand={o:st['collision'].get(o,0)+st['hit'].get(o,0) for o in OWNERS}
    old,terminal,audit=source_stages(d,st)
    implemented=hall('implemented ActiveScoped sameFirst union rowCompanion',hist(old),demand)
    common=hall('implemented terminal predicate composed hypothetically with FreeHalf',hist(terminal),demand)
    out=outside_r23(d,st); fullhist,outinc=merge_outside(terminal,out)
    prose=hall('ActiveScoped + commonBlue terminal + prose-only R23 outsideAttachment',fullhist,demand)
    ref=json.loads(REF.read_text(encoding='utf-8'))['maximum_deficiency_cut']; symbols=scan_symbols()
    leadsha=hashlib.sha256(lead.canonical_bytes({'n':d['n'],'blue':set(d['blue']),'bad':set(d['bad']),'rows':d['rows']})).hexdigest()
    inc={'n':d['n'],'blue':sorted(d['blue']),'bad':sorted(d['bad']),'side':d['side'],'rows':d['rows'],
         'selector_anchor_rows':[x['anchorRow'] for x in d['meta']],'selector_start':d['start']}
    public_out={k:v for k,v in out.items() if not k.startswith('_')}
    result={
      'schema':'R29 FullBank referee exact audit v1','arithmetic':'integers only','verdict':'UNDEFINED',
      'verdict_reason':'No instantiated production relation maps R29 ActiveScoped Demand/FreeHalf to FullBank ports, typed sinks, legal incidence, and exact rational capacities.',
      'reconstruction':{'n':d['n'],'blue':len(d['blue']),'bad':len(d['bad']),'rows':len(rows),
        'selected_vertices':len(st['selected']),'active_vertices':len(st['active_vertices']),
        'active_edges':len(st['active_edges']),'demanded_active_edges':len(st['demanded_edges']),
        'lead_canonical_payload_sha256':leadsha,'incidence_payload_sha256':jsha(inc),
        'all_anchor_rows_canonical_json_sha256':jsha([list(r) for r in rows])},
      'active_scoped':{'owners':{str(o):{'collision':st['collision'].get(o,0),'hit_need':st['hit'].get(o,0),'demand':demand[o]} for o in OWNERS},
        'total_demand':sum(demand.values()),'source_classes_incremental':{'sameFirst':audit['sameFirst'],'rowCompanion':audit['rowCompanion']},
        'implemented_stage':implemented,
        'reference_comparison':{'certificate_sha256':sha(REF),'same_demand':ref['demand']==sum(demand.values()),
          'same_reach':ref['neighborhood']==implemented['reach'],'same_gap':ref['gap']==implemented['worst']['gap'],'same_shore':ref['shore']==list(OWNERS)}},
      'candidate_classes_incremental':{
        'commonBlueTerminal':{'status':'terminal predicate implemented; FreeHalf/global matching composition absent',**audit['commonBlueTerminal']},
        'after_commonBlueTerminal':common,
        'outsideAttachment':{'status':'prose-only/unimplemented in production Lean',**public_out,'incremental':outinc},
        'after_R23_prose_candidate':prose},
      'object_and_unit_audit':{
        'ActiveScoped_demand':'cardinality of ActiveCollisionHalf sum ActiveHitNeed',
        'ActiveScoped_source':'injective cardinality of ordered FreeHalf triples after ScopedReserved',
        'FullBank_relaxed_demand':'rational blockLoad on off-support edge ports O',
        'FullBank_ledger_demand':'rational demandQ supplied inside a FullBankGlobalPackage',
        'FullBank_hall_scale':'token capQ / 25','typed_Door_scale':'raw capQ >= 25 implies hallCapQ >= 1',
        'missing_bridge':'no compiled identification of ActiveScoped units with FullBank port loads or typed token capacities',
        'overlap_rule':'exact union on (sourceX,sourceY,half); no class capacities are arithmetically summed'},
      'production_symbol_scan':symbols,
      'minimal_missing_semantics':[
        'Concrete R29 FullBank port set O and exact rational load per port.',
        'Concrete typed door/vertexSlack/c5Base/prune tokens with capQ, component, and unique source identity.',
        'Computed legal port-to-token incidence, including implemented outsideAttachment/prune if intended.',
        'Bridge from ActiveScoped obligations to FullBank loads, including factor 25 and any half/K scaling.',
        'One overlap-safe flow/spend certificate enforcing reservations, no double spend, and component locality.',
        'Instantiated checked FullBankGlobalPackage or FullBankRelaxedCoverCert for this R29 tuple.'],
      'source_line_contract':{
        'ActiveScoped objects':'Gamma/ActiveScopedMinimumExchange.lean:80-158',
        'owner Hall':'Gamma/ActiveScopedOwnerHallReduction.lean:27-38',
        'common-blue terminal only':'Gamma/CheckedC5BaseTransfer.lean:13-15,35-43',
        'row-companion global separation':'Gamma/CheckedRowCompanionBaseTransfer.lean:8-13,34-41',
        'abstract FullBank cert':'Ell5FullBankInterface.lean:7-10,23-40',
        'abstract rational ledger':'Gamma/FullBankToLengthSurplusCharge.lean:6-14,34-54,67-83,177-227',
        'incidence expressly absent':'Gamma/FullBankPortSinks.lean:80-81',
        'typed adapter expressly separate':'Gamma/TypedFullBankSources.lean:6-14',
        'parameterized production Hall':'Ell5ActiveComponentBankHall.lean:27-64',
        'logical countermodel':'AggregateLedgerNoIncidenceCounterexample.lean:6-16,152-157',
        'R23 prose shape':'writeup/WALL_ATTACK_R23_GPTPRO56.md:7-15,29-34'},
      'input_hashes':source_hashes(),
      'assertions':{
        'r29_counts':d['n']==2943 and len(d['blue'])==7039 and len(d['bad'])==1383,
        'canonical_sha':leadsha=='fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f',
        'scope':len(st['selected'])==2127 and len(st['active_vertices'])==19 and len(st['active_edges'])==1370,
        'demand':sum(demand.values())==19953,'implemented_reach':implemented['reach']==19925,
        'implemented_gap':implemented['worst']['gap']==28 and implemented['worst']['shore']==list(OWNERS),
        'reference_replayed':ref['demand']==19953 and ref['neighborhood']==19925 and ref['gap']==28,
        'outside_unimplemented':not symbols['outsideAttachment'],'transfer_matching_unimplemented':not symbols['CheckedTransferMatching']}}
    assert all(result['assertions'].values())
    p=HERE/'audit_result.json'; p.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'verdict':result['verdict'],'implemented':implemented['worst'],
      'after_commonBlue':common['worst_nonempty'],'after_R23_prose':prose['worst_nonempty'],'R23_all_shores_pass':prose['all_pass'],
      'outside_sources':out['candidate'],'output':str(p),'sha256':sha(p)},sort_keys=True,indent=2))

if __name__=='__main__': main()
