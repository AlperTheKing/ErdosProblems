"""Integer-only R29 all-anchor four-pattern transfer audit."""
from collections import Counter, defaultdict, deque
import hashlib, importlib.util, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in (HERE,*HERE.parents) if (p/'GOAL_LOOP.md').is_file())
LEAD=ROOT/'tmp/fanout/r29_gate/lead/r29_lead_gate.py'
OUT=HERE/'RESULT.json'
OWNERS=(0,1,2)

def norm(x,y):
    assert x!=y
    return (x,y) if x<y else (y,x)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def jsha(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def loss(I,S):
    return sum((x in S)!=(y in S) for x,y in I['blue'])-sum((x in S)!=(y in S) for x,y in I['bad'])

def cage():
    spec=importlib.util.spec_from_file_location('r29_lane02_lead',LEAD)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); r=mod.build()
    I={'n':int(r['n']),'blue':frozenset(map(tuple,r['blue'])),'bad':frozenset(map(tuple,r['bad'])),
       'side':tuple(r['side']),'rows':tuple(map(tuple,r['rows'])),'atoms':tuple(map(tuple,r['atoms'])),
       'meta':tuple(dict(x) for x in r['selectorMeta']),'start':r['selectorStart'],'stop':r['selectorStop']}
    rows=list(I['rows'])
    for j,m in enumerate(I['meta']): rows[I['start']+j]=tuple(m['anchorRow'])
    return I,tuple(rows)

def incidence_sha(I):
    return jsha({'n':I['n'],'blue':sorted(I['blue']),'bad':sorted(I['bad']),'side':I['side'],
      'rows':I['rows'],'selector_anchor_rows':[m['anchorRow'] for m in I['meta']],
      'selector_start':I['start']})

def scope(I,rows):
    n=I['n']; pair=Counter(); load=Counter(); support=set(); U=set()
    for atom,row in zip(I['atoms'],rows):
        assert len(row)==5 and norm(row[0],row[-1])==atom
        assert all(norm(x,y) in I['blue'] for x,y in zip(row,row[1:]))
        for x in row:
            assert 0<=x<n; load[x]+=1; U.add(x)
            for y in row: pair[x,y]+=1
        support.update(norm(x,y) for x,y in zip(row,row[1:]))
    active={e for e in I['blue'] if e not in support and e[0] in U and e[1] in U}
    adj=defaultdict(set)
    for x,y in active: adj[x].add(y); adj[y].add(x)
    cid={}; comps=[]
    for root in sorted(U):
        if root in cid: continue
        seen={root}; q=deque([root])
        while q:
            x=q.popleft()
            for y in adj[x]:
                if y not in seen: seen.add(y); q.append(y)
        k=len(comps); comps.append(seen)
        for x in seen: cid[x]=k
    roots={cid[x] for x,y in I['bad'] if x in cid and y in cid and cid[x]==cid[y]}
    av={x for x in U if cid[x] in roots}; demanded={e for e in active if e[0] in av}; deg=Counter()
    for x,y in demanded: deg[x]+=1; deg[y]+=1
    coll={o:2*sum(max(0,pair[o,y]-1) for y in range(n)) for o in av}
    hit={o:max(0,deg[o]-max(0,n-5*load[o])) for o in av}
    return {'pair':pair,'load':load,'U':U,'active':active,'av':av,'demanded':demanded,'coll':coll,'hit':hit}

def add_slots(dst,cells,active):
    arcs={}; rejected=0; prior=set(dst); class_keys=set()
    for o in OWNERS:
        k=0
        for x,y in cells[o]:
            for h in (0,1):
                if h==0 and norm(x,y) in active: rejected+=1; continue
                class_keys.add((x,y,h)); dst[x,y,h]=dst.get((x,y,h),0)|(1<<o); k+=1
        arcs[str(o)]=k
    return {'owner_arc_slots':arcs,'reserved_half_rejections_with_owner_multiplicity':rejected,
      'class_raw_unique_slots':len(class_keys),'class_overlap_with_prior_slots':len(class_keys&prior)}
def hist(slots): return Counter(slots.values())
def cuts(demand,H):
    out=[]
    for A in range(1,8):
        shore=[o for o in OWNERS if A&(1<<o)]; d=sum(demand[o] for o in shore)
        r=sum(v for m,v in H.items() if m&A)
        out.append({'shore_mask':A,'shore':shore,'demand':d,'reachable_unique_slots':r,'defect':d-r})
    return out
def stage(name,before,after,demand,details):
    H=hist(after); C=cuts(demand,H)
    return {'class':name,'class_unique_slots':len(set(after)-set(before)),
      'class_raw_unique_slots':details.pop('class_raw_unique_slots'),
      'overlap_with_prior_slots':details.pop('class_overlap_with_prior_slots'),
      'cumulative_unique_slots':len(after),
      'owner_mask_histogram':{str(k):v for k,v in sorted(H.items())},'hall_cuts':C,
      'maximum_defect':max(x['defect'] for x in C),**details}

def outside_data(I,U):
    n=I['n']; adj=[set() for _ in range(n)]
    for x,y in I['blue']: adj[x].add(y); adj[y].add(x)
    cid=[-1]*n; comps=[]; atts=[]; outside=set(range(n))-U
    for root in sorted(outside):
        if cid[root]>=0: continue
        k=len(comps); cid[root]=k; C=set(); A=set(); q=deque([root])
        while q:
            x=q.popleft(); C.add(x)
            for y in adj[x]:
                if y in U: A.add(y)
                elif cid[y]<0: cid[y]=k; q.append(y)
        comps.append(C); atts.append(A)
    assert (set().union(*comps)==outside) if comps else not outside
    assert sum(map(len,comps))==len(outside) and all(atts)
    L=[0]*len(comps); between=Counter()
    for sign,E in ((1,I['blue']),(-1,I['bad'])):
        for x,y in E:
            a,b=cid[x],cid[y]
            if a>=0 and b>=0:
                if a!=b: between[norm(a,b)]+=sign
            elif a>=0: L[a]+=sign
            elif b>=0: L[b]+=sign
    assert all(not(cid[x]>=0 and cid[y]>=0 and cid[x]!=cid[y]) for x,y in I['blue'])
    assert all(L[k]==loss(I,frozenset(C)) for k,C in enumerate(comps))
    return outside,cid,comps,atts,L,between

def production_audit():
    g=ROOT/'problems/23/lean/Erdos23Delta0/Gamma'; t=ROOT/'problems/23/lean/Erdos23Delta0'
    files=sorted(g.glob('*.lean'))+sorted(t.glob('*FullBank*.lean'))
    texts={str(p.relative_to(ROOT)).replace('\\','/'):p.read_text(encoding='utf-8') for p in files}
    oh={p:s.count('OutsideAttachment')+s.count('outsideAttachment') for p,s in texts.items() if 'OutsideAttachment' in s or 'outsideAttachment' in s}
    ch={p:s.count('commonBad')+s.count('CommonBad') for p,s in texts.items() if 'commonBad' in s or 'CommonBad' in s}
    mn=texts['problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean']
    rc=texts['problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean']
    c5=texts['problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean']
    return {'lean_files_scanned':len(texts),'outside_attachment_identifier_hits':oh,'common_bad_identifier_hits':ch,
      'same_owner_compiled':'def SameOwner' in mn,'row_companion_compiled':'def RowCompanion' in mn and 'def RawValid' in rc,
      'checked_c5_uses_common_blue':'blueb G c T.sourceX T.owner = true' in c5 and 'blueb G c T.sourceY T.owner = true' in c5 and 'dM G c T.switch + 2 <= dB G c T.switch' in c5,
      'outside_attachment_compiled':bool(oh),'common_bad_as_named_compiled':bool(ch)}

def main():
    I,rows=cage(); n=I['n']
    assert (n,len(I['blue']),len(I['bad']),len(rows),len(I['meta']))==(2943,7039,1383,1383,676)
    assert I['blue'].isdisjoint(I['bad']) and I['stop']-I['start']==676
    assert all(I['side'][x]!=I['side'][y] for x,y in I['blue'])
    assert all(I['side'][x]==I['side'][y] for x,y in I['bad'])
    S=scope(I,rows); pair=S['pair']; active=S['active']; assert set(OWNERS)<=S['av']
    demand={o:S['coll'].get(o,0)+S['hit'].get(o,0) for o in OWNERS}; assert sum(demand.values())==19953
    badj=[set() for _ in range(n)]; bluej=[set() for _ in range(n)]
    for x,y in I['bad']: badj[x].add(y); badj[y].add(x)
    for x,y in I['blue']: bluej[x].add(y); bluej[y].add(x)
    lc={}
    def pl(x,y):
        e=norm(x,y)
        if e not in lc: lc[e]=loss(I,frozenset((x,y)))
        return lc[e]
    stages=[]; cur={}
    before=dict(cur); same={o:{(o,y) for y in range(n) if y!=o and pair[o,y]==0} for o in OWNERS}
    stages.append(stage('sameFirst_sameOwner',before,cur,demand,add_slots(cur,same,active)))
    before=dict(cur); common={o:set() for o in OWNERS}; losses=[]
    for o in OWNERS:
        for x in badj[o]:
            for y in badj[o]:
                if x!=y and pair[x,y]==0 and pl(x,y)>=0:
                    assert norm(o,x) in I['bad'] and norm(o,y) in I['bad']
                    common[o].add((x,y)); losses.append(pl(x,y))
    d=add_slots(cur,common,active); d.update({'verified_switch_cells':sum(map(len,common.values())),'minimum_switch_loss':min(losses) if losses else None})
    stages.append(stage('commonBad',before,cur,demand,d))
    before=dict(cur); companions={o:{x for x in range(n) if x!=o and pair[o,x]>0} for o in OWNERS}; row={o:set() for o in OWNERS}; losses=[]
    for o in OWNERS:
        for x in companions[o]:
            for y in companions[o]:
                if x!=y and pair[x,y]==0 and pl(x,y)>=0:
                    assert pair[o,x]>0 and pair[o,y]>0; row[o].add((x,y)); losses.append(pl(x,y))
    d=add_slots(cur,row,active); d.update({'companions_by_owner':{str(o):len(companions[o]) for o in OWNERS},
      'verified_switch_cells':sum(map(len,row.values())),'minimum_switch_loss':min(losses) if losses else None,
      'commonBad_cells_are_rowCompanion_cells':all(common[o]<=row[o] for o in OWNERS)})
    stages.append(stage('rowCompanion',before,cur,demand,d)); assert len(cur)==19925
    common_blue={}; common_blue_new=set()
    for o in OWNERS:
        for x in bluej[o]:
            for y in bluej[o]:
                if x==y or pair[x,y]!=0 or pl(x,y)<2: continue
                for h in (0,1):
                    if h==0 and norm(x,y) in active: continue
                    common_blue[x,y,h]=common_blue.get((x,y,h),0)|(1<<o)
                    if (x,y) not in row[o]: common_blue_new.add((o,x,y,h))
    outside,cid,comps,atts,L,between=outside_data(I,S['U'])
    masks=[]; witnesses={}
    for k,A in enumerate(atts):
        m=0
        for o in OWNERS:
            w=sorted(a for a in A if pair[o,a]>0)
            if w: m|=1<<o; witnesses[o,k]=w[0]
        masks.append(m)
    OH=Counter(); owner_arcs=Counter(); accepted=rejected=0; minloss=None
    for i,C in enumerate(comps):
        for j,D in enumerate(comps):
            m=masks[i]&masks[j]
            if not m: continue
            if i==j: lv=L[i]; cells=len(C)*(len(C)-1)
            else: lv=L[i]+L[j]-2*between[norm(i,j)]; cells=len(C)*len(D)
            if lv<0: rejected+=1; continue
            accepted+=1; minloss=lv if minloss is None else min(minloss,lv); slots=2*cells; OH[m]+=slots
            for o in OWNERS:
                if m&(1<<o):
                    owner_arcs[o]+=slots; assert (o,i) in witnesses and (o,j) in witnesses
                    assert pair[o,witnesses[o,i]]>0 and pair[o,witnesses[o,j]]>0
            assert C.isdisjoint(S['U']) and D.isdisjoint(S['U']) and lv>=0
    FH=hist(cur)+OH; FC=cuts(demand,FH); oslots=sum(OH.values())
    outstage={'class':'outsideComponentAttachment','class_raw_unique_slots':oslots,
      'class_unique_slots':oslots,'overlap_with_prior_slots':0,
      'cumulative_unique_slots':len(cur)+oslots,'owner_mask_histogram':{str(k):v for k,v in sorted(FH.items())},
      'outside_only_owner_mask_histogram':{str(k):v for k,v in sorted(OH.items())},'hall_cuts':FC,
      'maximum_defect':max(x['defect'] for x in FC),'owner_arc_slots':{str(o):owner_arcs[o] for o in OWNERS},
      'outside_vertices':len(outside),'outside_components':len(comps),
      'component_size_histogram':{str(k):v for k,v in sorted(Counter(map(len,comps)).items())},
      'eligible_components_by_owner':{str(o):sum(bool(m&(1<<o)) for m in masks) for o in OWNERS},
      'eligible_vertices_by_owner':{str(o):sum(len(comps[k]) for k,m in enumerate(masks) if m&(1<<o)) for o in OWNERS},
      'accepted_ordered_component_pairs':accepted,'rejected_negative_loss_ordered_component_pairs':rejected,
      'minimum_switch_loss':minloss,'reservation_rejections':0,
      'reserved_half_rejections_with_owner_multiplicity':0,
      'all_structural_and_loss_predicates_verified_by_component_expansion':True}
    stages.append(outstage); assert max(x['defect'] for x in FC)<=0
    hub=next(x for x in FC if x['shore_mask']==7); prod=production_audit()
    assert prod['same_owner_compiled'] and prod['row_companion_compiled'] and prod['checked_c5_uses_common_blue']
    assert not prod['outside_attachment_compiled']
    paths=('tmp/fanout/r29_fullbank_gate/COMMON.md','GOAL_LOOP.md','problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md',
      'tmp/fanout/r29_gate/lead/r29_lead_gate.py','tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py',
      'tmp/fanout/r29_gate/d05/retry2/cut_certificate.json','problems/23/writeup/_claude_r20_staged_matching_gate.py',
      'problems/23/writeup/_claude_r23_outside_attachment_gate.py','problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py',
      'problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md','problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md',
      'problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md','problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean',
      'problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean','problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean',
      'problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean','problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean')
    R={'schema':'R29 all-anchor exact four-pattern transfer audit v1','arithmetic':'integers only',
      'verdict':{'four_pattern_gate_spec':'PASS','complete_implemented_production_relation':'UNDEFINED',
      'reason':'R23 outsideAttachment makes every gate Hall shore nondeficient, but it has no production Lean definition; FullBank is an abstract certificate interface, not a graph-derived provider.'},
      'reconstruction':{'n':n,'blue_edges':len(I['blue']),'bad_edges':len(I['bad']),'rows':len(rows),
      'selector_rows_replaced_by_anchor':len(I['meta']),'selected_vertices':len(S['U']),'active_vertices':len(S['av']),
      'active_edges':len(active),'demanded_active_edges':len(S['demanded']),'canonical_incidence_sha256':incidence_sha(I),
      'all_anchor_rows_sha256':jsha(rows)},
      'hub_shore':{'owners':list(OWNERS),'by_owner':{str(o):{'collision':S['coll'].get(o,0),'hit_need':S['hit'].get(o,0),'demand':demand[o]} for o in OWNERS},
      'demand':sum(demand.values()),'final_reachable_unique_slots':hub['reachable_unique_slots'],'final_defect':hub['defect']},
      'stages':stages,'supplemental_compiled_common_blue':{'reachable_slots_for_hub_owners':len(common_blue),
      'slots_not_already_rowCompanion_for_same_owner':len(common_blue_new),
      'incremental_unique_slots_beyond_same_commonBad_rowCompanion':len(set(common_blue)-set(cur)),
      'cumulative_hall_cuts_if_added':cuts(demand,hist({**cur,**{k:cur.get(k,0)|m for k,m in common_blue.items()}})),
      'predicate':'blue(x,owner), blue(y,owner), free(x,y), loss({x,y}) >= 2','included_in_four_pattern_totals':False},
      'production_surface':prod,'input_sha256':{p:sha(ROOT/p) for p in paths},
      'assertions':{'reconstructed_not_copied':True,'hub_demand_is_19953':sum(demand.values())==19953,
      'same_plus_common_plus_row_reach_is_19925':stages[2]['cumulative_unique_slots']==19925,
      'pre_outside_hub_defect_is_28':next(x['defect'] for x in stages[2]['hall_cuts'] if x['shore_mask']==7)==28,
      'outside_has_zero_overlap_with_selected_source_classes':outstage['overlap_with_prior_slots']==0,
      'four_pattern_all_shores_hall':max(x['defect'] for x in FC)<=0,
      'outside_pattern_missing_from_production_lean':not prod['outside_attachment_compiled']}}
    assert all(R['assertions'].values()); OUT.write_text(json.dumps(R,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'verdict':R['verdict'],'hub_shore':R['hub_shore'],
      'stage_totals':[{'class':s['class'],'increment':s['class_unique_slots'],'cumulative':s['cumulative_unique_slots'],'maximum_defect':s['maximum_defect']} for s in stages],
      'result_sha256':sha(OUT)},indent=2,sort_keys=True))

if __name__=='__main__': main()
