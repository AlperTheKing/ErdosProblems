"""Independent exact global selector verifier for the untrusted R29 constructor.

The lead module is used only as an incidence oracle.  All path enumeration,
scoped-state evaluation, lower-bound checking, and serialization below are
implemented here with integer arithmetic.
"""
from collections import Counter, deque
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from json import dumps
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"

def load_incidence():
    spec = spec_from_file_location("untrusted_r29_lead", LEAD)
    mod = module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.build()

def adj(n, edges):
    a=[[] for _ in range(n)]
    for u,v in edges: a[u].append(v); a[v].append(u)
    for z in a: z.sort()
    return a

def shortest(a,s,t):
    ds=[-1]*len(a); dt=[-1]*len(a); ds[s]=dt[t]=0
    for root,d in ((s,ds),(t,dt)):
        q=deque([root])
        while q:
            u=q.popleft()
            for v in a[u]:
                if d[v]<0: d[v]=d[u]+1; q.append(v)
    assert ds[t]==4
    out=[]
    def go(p):
        u=p[-1]
        if u==t: out.append(tuple(p)); return
        for v in a[u]:
            if ds[v]==ds[u]+1 and ds[v]+dt[v]==4: go(p+[v])
    go([s]); return tuple(out)

def state(data, rows):
    n=data["n"]; selected=set(); support=set(); row_count=[0]*n
    pair=Counter()
    for row in rows:
        selected.update(row)
        for x in row:
            row_count[x]+=1
            for y in row: pair[x,y]+=1
        for u,v in zip(row,row[1:]): support.add((u,v) if u<v else (v,u))
    active={e for e in data["blue"] if e not in support and e[0] in selected and e[1] in selected}
    parent={v:v for v in selected}
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(x,y):
        x=find(x); y=find(y)
        if x!=y: parent[max(x,y)]=min(x,y)
    for u,v in active: union(u,v)
    roots={find(u) for u,v in data["bad"] if u in selected and v in selected and find(u)==find(v)}
    av={v for v in selected if find(v) in roots}
    deg=[0]*n
    for u,v in active:
        if find(u) in roots: deg[u]+=1; deg[v]+=1
    collision={v:2*sum(m-1 for (x,y),m in pair.items() if x==v and m>1) for v in av}
    hit={v:max(0,deg[v]-max(0,n-5*row_count[v])) for v in av}
    return {"active":sorted(av),"collision":collision,"hit":hit,
            "collisionTotal":sum(collision.values()),"hitTotal":sum(hit.values()),
            "score":sum(collision.values())+sum(hit.values())}

def h(path): return sha256(path.read_bytes()).hexdigest()

def main():
    d=load_incidence(); a=adj(d["n"],d["blue"])
    start,stop=d["selectorStart"],d["selectorStop"]
    families=[]; tuple_rows=[]; touch=[Counter(),Counter()]
    for i,(atom,meta) in enumerate(zip(d["atoms"][start:stop],d["selectorMeta"])):
        fam=shortest(a,*atom); assert len(fam)==680 and len(set(fam))==680
        anchors=[r for r in fam if 55 in r]; locals_=[r for r in fam if 55 not in r]
        assert len(anchors)==676 and len(locals_)==4
        chosen=tuple(meta["anchorRow"]); assert chosen in anchors
        local_leaves=[]
        for row in locals_:
            xs=[v for v in row if v in d["dXToLeaf"]]; assert len(xs)==1
            leaf=d["dXToLeaf"][xs[0]]; local_leaves.append(leaf)
        for leaf in set(local_leaves): touch[meta["region"]][leaf]+=1
        families.append({"selector":i,"atom":list(atom),"region":meta["region"],
                         "family_index":fam.index(chosen),"row":list(chosen),
                         "local_leaf_multiset":sorted(local_leaves)})
        tuple_rows.append(chosen)
    assert all(len(x)==13 and set(x.values())=={27} for x in touch)
    rows=list(d["rows"])
    for i,row in enumerate(tuple_rows): rows[start+i]=row
    st=state(d,tuple(rows)); assert st["score"]==23115

    # Check every integer lower-bound cell, not a floating relaxation.
    # l,r are numbers of local choices in the two 338-selector regions.
    cells=[]; best=None; arg=[]
    for l in range(339):
      for r in range(339):
        al,ar=338-l,338-r
        c55=2*((al+ar)+max(0,al-1)+max(0,ar-1))
        covered=(l+26)//27+(r+26)//27
        lb=20411+c55+200*covered+(4 if l==r==0 else 0)
        if best is None or lb<best: best=lb; arg=[(l,r)]
        elif lb==best: arg.append((l,r))
        cells.append(lb)
    assert best==23115 and arg==[(0,0)] and min(cells[1:])>best

    arm=set(range(56,2760)); hubs={0,1,2}; q={2760,2761}; leaves=set(range(3,55))
    active=set(st["active"])
    tuple_doc={"format":"r29-d09-best-tuple-v1","score":st["score"],
               "selector_choices":families}
    tp=HERE/"best_tuple.json"; tp.write_text(dumps(tuple_doc,sort_keys=True,separators=(",",":"))+"\n")
    cert={"method":"independent integer lower-bound verifier over all 339^2 local-count cells",
      "incidence_source_untrusted":str(LEAD.relative_to(ROOT)).replace("\\","/"),
      "incidence_source_sha256":h(LEAD),"selectors":676,"family_size":680,
      "family_partition":{"anchor":676,"local":4},
      "local_touch_counts":[dict(sorted(x.items())) for x in touch],
      "lower_bound":{"formula":"20411+C55(l,r)+200*(ceil(l/27)+ceil(r/27))+4*[l=r=0]",
        "cells_checked":len(cells),"minimum":best,"unique_argmin_local_counts":[0,0],
        "next_cell_lower_bound":min(cells[1:])},
      "best_tuple_file":"best_tuple.json","best_tuple_sha256":h(tp),
      "exact_state":{"score":st["score"],"collision":st["collisionTotal"],"hit_need":st["hitTotal"],
        "active_vertices":st["active"],"positive_owners":{str(v):st["collision"][v]+st["hit"][v] for v in st["active"] if st["collision"][v]+st["hit"][v]>0}},
      "deactivation":{"hubs_active":sorted(hubs&active),"hubs_inactive":sorted(hubs-active),
        "traffic_leaves_active":sorted(leaves&active),"traffic_leaves_inactive":sorted(leaves-active),
        "arm_descendants_active":sorted(arm&active),"arm_descendants_inactive_count":len(arm-active),
        "selector_q_active":sorted(q&active),"selector_q_inactive":sorted(q-active)},
      "arithmetic":"integers only; no float acceptance"}
    cp=HERE/"certificate.json"; cp.write_text(dumps(cert,sort_keys=True,indent=2)+"\n")
    files=[LEAD,HERE/"verify.py",tp,cp,HERE/"report.md"]
    (HERE/"hashes.json").write_text(dumps({str(p.relative_to(ROOT)).replace("\\","/"):h(p) for p in files},sort_keys=True,indent=2)+"\n")
    print(dumps({"minimum":best,"tuple_sha256":h(tp),"certificate_sha256":h(cp),"active":st["active"]},separators=(",",":")))

if __name__=="__main__": main()
