#!/usr/bin/env python3
"""Exact fixture replay, independent of dynamic MICRO_FLOW."""
import hashlib,itertools,json,sys
from collections import Counter,defaultdict,deque
from pathlib import Path
H=Path(__file__).resolve().parent; R=H.parents[4]
sys.path[:0]=[str(R/"tmp/fanout/pht_n12_direct"),str(R/"problems/23/writeup")]
import n12_pht as n12
G6="K??E@cyjFgWk"; CH=(0,4,5,7)
def e(a,b): return (a,b) if a<b else (b,a)
def matching(ds,av):
 sm={}; dm={}
 def aug(d,seen):
  for s in av[d]:
   if s in seen: continue
   seen.add(s); old=sm.get(s)
   if old is None or aug(old,seen): sm[s]=d;dm[d]=s;return True
  return False
 un=[]
 for d in sorted(ds,key=lambda z:(len(av[z]),z)):
  if not aug(d,set()): un.append(d)
 L=set(un);Q=deque(un);S=set()
 while Q:
  d=Q.popleft()
  for s in av[d]:
   if dm.get(d)==s or s in S: continue
   S.add(s);d2=sm.get(s)
   if d2 is not None and d2 not in L:L.add(d2);Q.append(d2)
 return dm,un,L,S
def main():
 n,edges=n12.dec(G6); info=n12.loads(n,edges); fam=n12.shortest_row_families(info)
 assert tuple(map(len,fam))==(6,5,8,10)
 rows=tuple(n12.rows_for_choice(fam,CH)); ti=next(i for i,c in enumerate(itertools.product(*(range(len(f)) for f in fam))) if c==CH)
 blue=set(info["Bset"]);bad=set(info["Mset"]);pair=Counter();rc=[0]*n;support=set()
 for r in rows:
  for x in r:
   rc[x]+=1
   for y in r:pair[x,y]+=1
  support|={e(x,y) for x,y in zip(r,r[1:])}
 sel={x for r in rows for x in r};active={q for q in blue if set(q)<=sel and q not in support};par={v:v for v in sel}
 def find(v):
  while par[v]!=v:par[v]=par[par[v]];v=par[v]
  return v
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b:par[max(a,b)]=min(a,b)
 for a,b in active:union(a,b)
 roots={find(a) for a,b in bad if a in sel and b in sel and find(a)==find(b)}
 verts={v for v in sel if find(v) in roots};dactive={q for q in active if find(q[0]) in roots};ad=[0]*n
 for a,b in dactive:ad[a]+=1;ad[b]+=1
 coll={v:2*sum(m-1 for (x,_),m in pair.items() if x==v and m>=2) for v in verts}
 hit={v:max(0,ad[v]-max(0,n-5*rc[v])) for v in verts};micro={v:coll[v]+25*hit[v] for v in verts};owners=tuple(v for v in sorted(verts) if micro[v])
 ba=[set() for _ in range(n)];deg=[0]*n;sg={}
 for a,b in blue:ba[a].add(b);ba[b].add(a);deg[a]+=1;deg[b]+=1;sg[a,b]=1
 for a,b in bad:deg[a]-=1;deg[b]-=1;sg[a,b]=-1
 def sigma(a,b):return deg[a]+deg[b]-2*sg.get(e(a,b),0)
 reserved={(x,y,0) for x in verts for y in range(n) if x!=y and e(x,y) in dactive}
 arcs={o:set() for o in owners};why=defaultdict(lambda:defaultdict(list));free=[]
 for x in range(n):
  for y in range(n):
   if x==y or pair[x,y]:continue
   for h in (0,1):
    s=(x,y,h);free.append(s)
    if s in reserved:continue
    for o in owners:
     w=[]
     if x==o:w+=["eligible:sameFirst"]
     if pair[o,x]>0 and pair[o,y]>0 and sigma(x,y)>=0:w+=["eligible:rowCompanion"]
     if x in ba[o] and y in ba[o] and sigma(x,y)>=2:w+=["commonBlue:Valid"]
     if w:arcs[o].add(s);why[s][o]=w
 ds=[]
 for o in owners:ds += [(o,"collision",i) for i in range(coll[o])]+[(o,"hitMicro",i) for i in range(25*hit[o])]
 av={d:tuple(sorted(arcs[d[0]])) for d in ds};M,un,L,S=matching(ds,av);cuts=[]
 for mask in range(1<<len(owners)):
  shore=[owners[i] for i in range(len(owners)) if mask>>i&1];reach=set().union(*(arcs[o] for o in shore)) if shore else set();d=sum(micro[o] for o in shore);cuts.append({"shore":shore,"demand":d,"reach":len(reach),"defect":d-len(reach)})
 triangles=sum(e(a,b) in edges and e(a,c) in edges and e(b,c) in edges for a in range(n) for b in range(a+1,n) for c in range(b+1,n))
 out={"schema":"N12_COMMON_BLUE_MICRO_REPLAY_V1","arithmetic":"integers only","graph6":G6,"n":n,"edges":[list(x) for x in edges],"triangleCount":triangles,
 "cut":{"side":info["side"],"maxCutSize":len(blue),"rawGamma":info["G"],"blue":[list(x) for x in sorted(blue)],"bad":[list(x) for x in sorted(bad)]},
 "rows":{"familySizes":list(map(len,fam)),"families":[[list(r) for r in f] for f in fam],"choice":list(CH),"tupleIndex":ti,"selected":[list(r) for r in rows],"support":[list(x) for x in sorted(support)]},
 "active":{"edges":[list(x) for x in sorted(active)],"demanded":[list(x) for x in sorted(dactive)],"vertices":sorted(verts)},
 "demand":{"owners":list(owners),"byOwner":{str(o):{"collision":coll[o],"hitNeedSlots":hit[o],"microDemand":micro[o],"rowCount":rc[o],"activeDegree":ad[o],"rawVertexSlack":max(0,n-5*rc[o])} for o in owners},"collision":sum(coll.values()),"hitNeedSlots":sum(hit.values()),"microDemand":len(ds)},
 "sources":{"rawFreeHalfCount":len(free),"scopedReserved":[list(x) for x in sorted(reserved)],"reachableCount":len(set().union(*(arcs[o] for o in owners))),"records":[{"key":list(s),"owners":sorted(why[s]),"reasons":why[s],"sigma":sigma(s[0],s[1])} for s in sorted(why)]},
 "flow":{"value":len(M),"defect":len(ds)-len(M),"assignment":[{"demand":list(d),"source":list(s)} for d,s in sorted(M.items())],"unmatched":[list(x) for x in un],"minCutLeft":[list(x) for x in sorted(L)],"minCutRight":[list(x) for x in sorted(S)]},"ownerShoreCuts":cuts,
 "guardrails":{"rawGraphQuantity":"collision+25*HitNeed","hallScaleCapacity":"capQ/25 only; absent here","typedSourceKey":"ordered FreeHalf key, not CapSource","legalPortIncidence":"absent","noDoubleSpend":"raw injection only","fullBankRepairClaim":False},
 "sourceHashes":{str(p.relative_to(R)).replace("\\","/"):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/"tmp/fanout/pht_n12_direct/n12_pht.py",R/"problems/23/writeup/_h.py",R/"problems/23/writeup/_codex_r20_two_row_exchange_gate.py",R/"problems/23/lean/Erdos23Delta0/Gamma/CommonBlueExtendedMatching.lean",R/"problems/23/lean/Erdos23Delta0/ResidualSourceTokenization.lean",R/"problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean",R/"problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean",R/"problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean"]}}
 deficient=max(cuts,key=lambda x:x["defect"])["shore"];out["flow"]["deficientOwners"]=deficient
 assert triangles==0 and ti==377 and deficient==[10,11] and out["demand"]["collision"]==28 and out["demand"]["hitNeedSlots"]==2 and len(ds)==78 and len(M)==65 and max(x["defect"] for x in cuts)==13
 (H/"result.json").write_text(json.dumps(out,sort_keys=True,indent=2)+"\n");print(json.dumps({"collision":28,"hitNeed":2,"microDemand":78,"maxFlow":65,"defect":13,"owners":owners}))
if __name__=="__main__":main()
