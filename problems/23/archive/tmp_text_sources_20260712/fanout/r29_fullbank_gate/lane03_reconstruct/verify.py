"""Exact R29 all-anchor audit. Imports only the lane-local constructor transcription."""
from collections import Counter, defaultdict, deque
from hashlib import sha256
import json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]; sys.path.insert(0,str(HERE))
import constructor as C

def E(a,b): return (a,b) if a<b else (b,a)
def cb(x,nl=False): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()+ (b"\n" if nl else b"")
def H(x): return sha256(x).hexdigest()
def HF(p): return H(p.read_bytes())
def adj(n,es):
 a=[set() for _ in range(n)]
 for u,v in es:a[u].add(v);a[v].add(u)
 return [tuple(sorted(x)) for x in a]
def bfs(a,s):
 d=[-1]*len(a);w=[0]*len(a);d[s]=0;w[s]=1;q=deque([s])
 while q:
  u=q.popleft()
  for v in a[u]:
   if d[v]<0:d[v]=d[u]+1;w[v]=w[u];q.append(v)
   elif d[v]==d[u]+1:w[v]+=w[u]
 return d,w
def comps(V,es):
 a={v:set() for v in V}
 for u,v in es:a[u].add(v);a[v].add(u)
 unseen=set(V);gs=[];ci={}
 while unseen:
  z=min(unseen);unseen.remove(z);g={z};q=deque([z])
  while q:
   u=q.popleft()
   for v in sorted(a[u]):
    if v in unseen:unseen.remove(v);g.add(v);q.append(v)
  i=len(gs);gs.append(g)
  for v in g:ci[v]=i
 return gs,ci

def state(d,rows):
 n=d['n'];sel=set();sup=set();pair=Counter();load=Counter()
 for r in rows:
  sel.update(r)
  for x in r:
   load[x]+=1
   for y in r:pair[x,y]+=1
  sup.update(E(x,y) for x,y in zip(r,r[1:]))
 ae={e for e in d['blue'] if e[0] in sel and e[1] in sel and e not in sup}
 gs,ci=comps(sel,ae); ac={ci[u] for u,v in d['bad'] if u in ci and v in ci and ci[u]==ci[v]}
 av={v for v in sel if ci[v] in ac}; de={e for e in ae if ci[e[0]] in ac}; deg=Counter()
 for u,v in de:deg[u]+=1;deg[v]+=1
 coll={v:2*sum(m-1 for (x,y),m in pair.items() if x==v and m>1) for v in av}
 hit={v:max(0,deg[v]-max(0,n-5*load[v])) for v in av}
 return locals()

def sources(d,s):
 owners=(0,1,2);pair=s['pair'];sd=Counter();sg={}
 for u,v in d['blue']:sg[u,v]=1;sd[u]+=1;sd[v]+=1
 for u,v in d['bad']:sg[u,v]=-1;sd[u]-=1;sd[v]-=1
 co={o:{x for x in range(d['n']) if pair[o,x]>0} for o in owners};mask={};reason={}
 def add(z,o,r):mask[z]=mask.get(z,0)|(1<<o);reason[z]=reason.get(z,0)|r
 for o in owners:
  for y in range(d['n']):
   if y==o or pair[o,y]:continue
   for h in (0,1):
    if not(h==0 and E(o,y) in s['ae'] and o in s['av']):add((o,y,h),o,1)
 for o in owners:
  for x in sorted(co[o]):
   for y in sorted(co[o]):
    if x==y or pair[x,y]:continue
    e=E(x,y)
    if sd[x]+sd[y]-2*sg.get(e,0)<0:continue
    for h in (0,1):
     if not(h==0 and e in s['ae'] and x in s['av']):add((x,y,h),o,2)
 mh,rh=Counter(mask.values()),Counter(reason.values());dem={o:s['coll'][o]+s['hit'][o] for o in owners};cuts=[]
 for sm in range(8):
  sh=[o for o in owners if sm&(1<<o)];D=sum(dem[o] for o in sh);N=sum(v for m,v in mh.items() if m&sm)
  cuts.append({'shore_mask':sm,'shore':sh,'demand':D,'neighborhood':N,'defect':D-N})
 rec=[{'x':x,'y':y,'half':h,'owner_mask':mask[x,y,h],'reason_mask':reason[x,y,h]} for x,y,h in sorted(mask)]
 return locals()

def main():
 d=C.build();n=d['n'];B=d['blue'];M=d['bad'];G=d['graph'];a=adj(n,B);ga=adj(n,G)
 # Reconstruct all-anchor choices from indexed metadata, never from a certificate.
 rows=list(d['rows'])
 for j,m in enumerate(d['selectorMeta']):rows[d['selectorStart']+j]=tuple(m['anchorRow'])
 rows=tuple(rows)
 assert (n,len(B),len(M),len(G),len(rows))==(2943,7039,1383,8422,1383) and B.isdisjoint(M)
 assert all(d['side'][u]!=d['side'][v] for u,v in B) and all(d['side'][u]==d['side'][v] for u,v in M)
 tri=next(([u,v,min(set(ga[u])&set(ga[v]))] for u,v in sorted(G) if set(ga[u])&set(ga[v])),None);assert tri is None
 reach=sum(x>=0 for x in bfs(a,0)[0]);assert reach==n
 dh=Counter();wh=Counter();kh=defaultdict(Counter);members=0
 kinds=['traffic']*676+['selector']*676+['circuit']*28+['seed']*3
 for atom,row,k in zip(d['atoms'],rows,kinds):
  ds,w=bfs(a,atom[0]);dh[ds[atom[1]]]+=1;wh[w[atom[1]]]+=1;kh[k][w[atom[1]]]+=1
  members+=E(row[0],row[-1])==atom and len(row)==len(set(row))==5 and all(E(x,y) in B for x,y in zip(row,row[1:])) and ds[atom[1]]==4
 assert dh==Counter({4:1383}) and wh==Counter({1:707,680:676}) and members==1383
 assert len(set(rows))==1383 and all(len(set(r))==5 for r in rows)
 # Anchor membership: every chosen selector row is one of its 680 geodesics.
 part=Counter();anchor_members=0
 for atom,m in zip(d['atoms'][d['selectorStart']:d['selectorStop']],d['selectorMeta']):
  fam=C.shortest_rows(a,*atom);aa=[r for r in fam if 55 in r];ll=[r for r in fam if 55 not in r]
  part[len(aa),len(ll)]+=1;anchor_members+=tuple(m['anchorRow']) in aa
 assert part==Counter({(676,4):676}) and anchor_members==676
 s=state(d,rows);ct=sum(s['coll'].values());ht=sum(s['hit'].values());score=ct+ht
 assert (len(s['sel']),len(s['ae']),len(s['av']),len(s['de']),ct,ht,score)==(2127,1370,19,18,23108,7,23115)
 h=sources(d,s);co=set(range(55));assert all(h['co'][o]==co for o in (0,1,2))
 assert all((s['coll'][o],s['hit'][o])==(6650,1) for o in (0,1,2))
 assert len(h['mask'])==19925 and h['rh']==Counter({1:17325,2:2600}) and h['mh']==Counter({1:5775,2:5775,4:5775,7:2600})
 witness=max(h['cuts'],key=lambda z:(z['defect'],-z['shore_mask']))
 assert witness=={'shore_mask':7,'shore':[0,1,2],'demand':19953,'neighborhood':19925,'defect':28}
 inc={'n':n,'blue':[list(e) for e in sorted(B)],'bad':[list(e) for e in sorted(M)],'rows':[list(r) for r in d['rows']]}
 incsha=H(cb(inc));assert incsha=='fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f'
 rowsha=H(cb([list(r) for r in rows])); sourcesha=H(cb(h['rec']))
 groups=[]
 for i in sorted(s['ac']):
  g=s['gs'][i];ee=sorted(e for e in s['ae'] if e[0] in g and e[1] in g);mm=sorted(e for e in M if e[0] in g and e[1] in g)
  groups.append({'component_id':i,'vertices':sorted(g),'vertex_count':len(g),'active_edges':[list(e) for e in ee],
                 'active_edge_count':len(ee),'internal_bad_edges':[list(e) for e in mm],'internal_bad_edge_count':len(mm)})
 vd={str(v):{'selected_row_count':s['load'][v],'selected_load':5*s['load'][v],'active_degree':s['deg'][v],
     'ordinary_vertex_slack':max(0,n-5*s['load'][v]),'collision_halves':s['coll'][v],
     'hit_need':s['hit'][v],'demand':s['coll'][v]+s['hit'][v]} for v in sorted(s['av'])}
 cp={}
 for o in (0,1,2):
  ph=Counter(s['pair'][o,x] for x in sorted(h['co'][o]));cp[str(o)]={'vertices':sorted(h['co'][o]),'count':55,
     'pair_multiplicity_histogram':{str(k):v for k,v in sorted(ph.items())},'collision_halves':s['coll'][o],
     'hit_need':s['hit'][o],'demand':s['coll'][o]+s['hit'][o]}
 oracle={'schema':'r29-lane03-structural-oracle-v1','arithmetic':'integer-only',
  'identities':{'canonical_baseline_incidence_sha256':incsha,'canonical_all_anchor_rows_sha256':rowsha,
                'auxiliary_source_stream_sha256':sourcesha},
  'constructor':{'vertices':n,'graph_edges':len(G),'blue_edges':len(B),'bad_edges':len(M),'cut_side_sizes':{'0':d['side'].count(0),'1':d['side'].count(1)}},
  'graph_checks':{'blue_bad_disjoint':True,'all_blue_cross_cut':True,'all_bad_monochromatic':True,'triangle_free':True,
                  'blue_connected':True,'blue_vertices_reached_from_0':reach},
  'row_database':{'bad_atom_count':1383,'bad_atom_keys_nodup':len(set(d['atoms']))==1383,
    'blue_distance_histogram':{str(k):v for k,v in sorted(dh.items())},'shortest_row_count_histogram':{str(k):v for k,v in sorted(wh.items())},
    'class_histograms':{k:{str(x):y for x,y in sorted(v.items())} for k,v in sorted(kh.items())},
    'selected_row_membership_count':members,'within_row_nodup_count':1383,'selected_row_tuple_nodup':True},
  'all_anchor_selection':{'selector_count':676,'changed_from_baseline':sum(x!=y for x,y in zip(d['rows'],rows)),
    'family_size':680,'family_partition':{'anchor_rows':676,'local_rows':4,'families':676},
    'chosen_selector_rows_in_anchor_subfamily':anchor_members,'chosen_selector_rows_containing_anchor':sum(55 in r for r in rows[676:1352]),
    'all_selected_rows_containing_anchor':sum(55 in r for r in rows)},
  'active_scope':{'selected_vertices':len(s['sel']),'selected_support_edges':len(s['sup']),'active_edges':len(s['ae']),
    'inactive_component_active_edges':len(s['ae']-s['de']),'component_count_on_selected_vertices':len(s['gs']),
    'component_size_histogram':{str(k):v for k,v in sorted(Counter(len(g) for g in s['gs']).items())},
    'active_component_count':len(s['ac']),'active_vertices':sorted(s['av']),'active_vertex_count':len(s['av']),
    'demanded_active_edges':len(s['de']),'active_components':groups,'vertex_demand':vd,
    'collision_halves':ct,'hit_need':ht,'obligation_demand':score},
  'hub_shore':{'owners':[0,1,2],'companions':cp,'demand':sum(h['dem'].values()),'implemented_auxiliary_relation':{
    'same_first_only':h['rh'][1],'row_companion_only':h['rh'][2],'overlap_same_first_row_companion':h['rh'][3],
    'distinct_reachable_free_half_sources':len(h['mask']),'source_histogram_by_owner_mask':{str(k):v for k,v in sorted(h['mh'].items())},
    'all_owner_shores':h['cuts'],'maximum_deficiency_shore':witness}}}
 op=HERE/'STRUCTURAL_ORACLE.json';op.write_bytes(cb(oracle,True))
 checks={'n_2943':n==2943,'B_7039':len(B)==7039,'M_1383':len(M)==1383,'triangle_free':tri is None,'blue_connected':reach==n,
  'distance4_all_bad':dh==Counter({4:1383}),'row_histogram':wh==Counter({1:707,680:676}),'row_nodup':len(set(rows))==1383,
  'anchor_membership_676':anchor_members==676,'hub_companions_55':all(h['co'][o]==co for o in (0,1,2)),
  'active_vertices_19':len(s['av'])==19,'hub_demand_19953':sum(h['dem'].values())==19953,
  'reach_19925':len(h['mask'])==19925,'defect_28':witness['defect']==28}
 assert all(checks.values())
 result={'schema':'r29-lane03-result-v1','assigned_lane_status':'PASS','decisive_fullbank_status':'UNDEFINED',
  'arithmetic':'integer-only','assertions':checks,'exact':{'vertices':n,'blue_edges':len(B),'bad_edges':len(M),'graph_edges':len(G),
  'row_histogram':{str(k):v for k,v in sorted(wh.items())},'active_vertices':len(s['av']),'active_components':len(s['ac']),
  'global_active_scoped_demand':score,'hub_shore_demand':19953,'hub_shore_auxiliary_reach':19925,'hub_shore_auxiliary_defect':28},
  'identities':oracle['identities'],'oracle':'STRUCTURAL_ORACLE.json','scope_note':'PASS is structural/ActiveScoped only; FullBank remains UNDEFINED in this lane.'}
 rp=HERE/'RESULT.json';rp.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 inputs=[ROOT/'GOAL_LOOP.md',ROOT/'tmp/fanout/r29_fullbank_gate/COMMON.md',ROOT/'problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md',
 ROOT/'tmp/fanout/r29_gate/lead/r29_lead_gate.py',ROOT/'tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py',ROOT/'tmp/fanout/r29_gate/d05/retry2/cut_certificate.json',
 ROOT/'problems/23/lean/Erdos23Delta0/CertGraph.lean',ROOT/'problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean',
 ROOT/'problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean',ROOT/'problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean',
 ROOT/'problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedOwnerHallReduction.lean']
 outs=[HERE/'constructor.py',HERE/'verify.py',op,rp]+([HERE/'REPORT.md'] if (HERE/'REPORT.md').exists() else [])
 rel=lambda p:str(p.relative_to(ROOT)).replace('\\','/')
 hashes={'schema':'r29-lane03-sha256-v1','inputs':{rel(p):HF(p) for p in inputs},'outputs':{rel(p):HF(p) for p in outs}}
 (HERE/'HASHES.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n');print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
