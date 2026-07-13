"""Hostile exact replay of the canonical R29 all-anchor owner-Hall cut.

Only the labelled graph/row constructor is imported.  Scope, demand, source
eligibility, deduplication, shores, and hashes are recomputed here.
"""
from collections import Counter, defaultdict, deque
from fractions import Fraction
import hashlib, importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BUILDER = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
LEAN = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean"
TYPED = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean"
WIRING = ROOT / "problems/23/writeup/WIRING_SPECS_GPTPRO.md"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def edge(a,b): return (a,b) if a < b else (b,a)

def raw_fixture():
    s=importlib.util.spec_from_file_location("r29_constructor_only", BUILDER)
    m=importlib.util.module_from_spec(s); s.loader.exec_module(m); z=m.build()
    return int(z["n"]), {tuple(e) for e in z["blue"]}, {tuple(e) for e in z["bad"]}, \
        [tuple(r) for r in z["rows"]], [dict(x) for x in z["selectorMeta"]], int(z["selectorStart"])

def main():
    n,blue,bad,rows,meta,start=raw_fixture()
    for j,x in enumerate(meta): rows[start+j]=tuple(x["anchorRow"])
    pair=Counter(); load=Counter(); support=set(); selected=set()
    for r in rows:
        selected.update(r)
        for x in r: load[x]+=1
        for x in r:
            for y in r: pair[x,y]+=1
        support.update(edge(x,y) for x,y in zip(r,r[1:]))
    active={e for e in blue if e not in support and e[0] in selected and e[1] in selected}
    adj=defaultdict(set)
    for x,y in active: adj[x].add(y); adj[y].add(x)
    comp={}; comps=[]
    for root in sorted(selected):
        if root in comp: continue
        seen={root}; q=deque([root])
        while q:
            x=q.popleft()
            for y in adj[x]:
                if y not in seen: seen.add(y); q.append(y)
        cid=len(comps); comps.append(seen)
        for x in seen: comp[x]=cid
    badc={comp[x] for x,y in bad if x in comp and y in comp and comp[x]==comp[y]}
    av={x for x in selected if comp[x] in badc}
    ae={e for e in active if e[0] in av}
    deg=Counter()
    for x,y in ae: deg[x]+=1; deg[y]+=1
    collision={x:2*sum(max(0,pair[x,y]-1) for y in range(n)) for x in av}
    hit={x:max(0,deg[x]-max(0,n-5*load[x])) for x in av}
    owners=(0,1,2); demand={o:collision.get(o,0)+hit.get(o,0) for o in owners}
    signed=Counter(); sign={}
    for e in blue: sign[e]=1; signed[e[0]]+=1; signed[e[1]]+=1
    for e in bad: sign[e]=-1; signed[e[0]]-=1; signed[e[1]]-=1
    masks={}; reasons={}; companions={o:{x for x in range(n) if pair[o,x]>0} for o in owners}
    def add(k,o,r): masks[k]=masks.get(k,0)|(1<<o); reasons[k]=reasons.get(k,0)|r
    for o in owners:
        for y in range(n):
            if y==o or pair[o,y]: continue
            for h in (0,1):
                if not (h==0 and edge(o,y) in active and o in av): add((o,y,h),o,1)
        C=companions[o]
        for x in C:
            for y in C:
                if x==y or pair[x,y]: continue
                e=edge(x,y)
                if signed[x]+signed[y]-2*sign.get(e,0) < 0: continue
                for h in (0,1):
                    if not (h==0 and e in active and x in av): add((x,y,h),o,2)
    hist=Counter(masks.values()); rh=Counter(reasons.values())
    cuts=[]
    for sm in range(8):
        d=sum(demand[o] for o in owners if sm&(1<<o))
        reach=sum(v for k,v in hist.items() if k&sm)
        cuts.append({"shoreMask":sm,"demand":d,"reach":reach,"defect":d-reach})
    witness=max(cuts,key=lambda x:(x["defect"],-x["shoreMask"]))
    # Unit audit: TypedFullBankSources defines hallCapQ := capQ/25.
    hall_defect=Fraction(witness["defect"],1); required_capQ=25*hall_defect
    out={
      "fixture":{"n":n,"blue":len(blue),"bad":len(bad),"rows":len(rows),"selectors":len(meta)},
      "scope":{"selected":len(selected),"activeComponents":len(badc),"activeVertices":len(av),"activeEdges":len(active)},
      "ownerDemand":{str(o):{"collision":collision.get(o,0),"hit":hit.get(o,0),"total":demand[o]} for o in owners},
      "reasonCounts":{"sameFirstOnly":rh[1],"rowCompanionOnly":rh[2],"both":rh[3]},
      "distinctOrderedFreeHalfKeys":len(masks),"cuts":cuts,"maxDefectCut":witness,
      "units":{"hallDefect":str(hall_defect),"capQNeededAt25PerHallUnit":str(required_capQ)},
      "audits":{"reasonDoubleCountAbsent":rh[3]==0,"fullShore19953_19925_28":witness=={"shoreMask":7,"demand":19953,"reach":19925,"defect":28}},
      "hashes":{"builder":sha(BUILDER),"leanFullBank":sha(LEAN),"leanTypedSources":sha(TYPED),"wiringSpecs":sha(WIRING)}
    }
    p=HERE/"replay_result.json"; p.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    out["hashes"]["replayResult"]=sha(p)
    print(json.dumps(out,sort_keys=True,indent=2))
    assert all(out["audits"].values())

if __name__=="__main__": main()
