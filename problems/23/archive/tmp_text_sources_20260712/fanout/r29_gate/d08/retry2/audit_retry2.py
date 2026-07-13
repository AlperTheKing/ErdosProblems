"""Exact clean-room audit of the R29 selector landscape (integer only)."""
from collections import Counter, deque
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def E(a,b):
    assert a != b
    return (a,b) if a < b else (b,a)

def construct():
    B=set(); X=set(); rows=[]; atoms=[]
    def path(p): B.update(E(a,b) for a,b in zip(p,p[1:]))
    r,cl,cr,A=0,1,2,55; L=list(range(3,29)); R=list(range(29,55))
    path((cl,r,cr)); B.update(E(cl,x) for x in L); B.update(E(cr,x) for x in R)
    traffic=[(l,cl,r,cr,rr) for l in L for rr in R]
    X.update(E(l,rr) for l in L for rr in R)
    blocks=[]; nxt=56
    for leaves in (L,R):
        block=[]
        for leaf in leaves:
            for _ in range(26):
                x,y=nxt,nxt+1; nxt+=2; path((leaf,x,y,A)); block.append((leaf,x,y))
        blocks.append(block)
    selectors=[]; selector_atoms=[]; meta=[]
    for side,(q,block) in enumerate(zip((2760,2761),blocks)):
        F,D=block[:338],block[338:]
        for j in range(338):
            displayed=(q,F[j][1],F[(j+1)%338][2],D[j][1],D[(j+1)%338][2])
            path(displayed); atom=E(q,displayed[-1]); X.add(atom)
            selectors.append(displayed[::-1]); selector_atoms.append(atom)
            meta.append((side,j,q,F,D))
    off=2762; w=26
    support={E(i,(i+1)%26) for i in range(26)}|{E(w,0)}
    av=[9*k%26 for k in range(13)]
    support|={E(av[i],av[i+1]) for i in range(12)}
    B.update(E(off+a,off+b) for a,b in support)
    circuit_atoms=sorted({E(off+i,off+(i+4)%26) for i in range(26)}|{E(off+w,off+3),E(off+w,off+23)})
    nxt=off+27; circuit=[]
    for atom in circuit_atoms:
        p=(atom[0],*range(nxt,nxt+5),atom[1]); nxt+=5; path(p); X.add(atom); circuit.append(p)
    zL,zR=nxt,nxt+1; nxt+=2
    B.update({E(r,A),E(A,off+2),E(cl,zL),E(zL,A),E(cr,zR),E(zR,A)})
    seed=[]; seed_atoms=[]
    for s in (A,zL,zR):
        p=(s,*range(nxt,nxt+4)); nxt+=4; path(p); a=E(s,p[-1]); X.add(a); seed.append(p); seed_atoms.append(a)
    # The six-edge subdivisions make the circuit atoms bad edges, but their
    # selected rows are the unique four-edge routes in the 27-vertex support.
    aa=adjacency(nxt,B); circuit=[shortest_rows(aa,*a)[0] for a in circuit_atoms]
    assert all(len(shortest_rows(aa,*a))==1 for a in circuit_atoms)
    rows=tuple(traffic+selectors+circuit+seed)
    atoms=tuple(sorted(E(l,rr) for l in L for rr in R)+selector_atoms+circuit_atoms+seed_atoms)
    return nxt,B,X,rows,atoms,meta,blocks

def adjacency(n,edges):
    a=[set() for _ in range(n)]
    for u,v in edges: a[u].add(v); a[v].add(u)
    return [tuple(sorted(x)) for x in a]

def shortest_rows(adj,s,t):
    d=[-1]*len(adj); d[s]=0; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if d[v]<0: d[v]=d[u]+1; q.append(v)
    out=[]
    def rec(p):
        if len(p)==5:
            if p[-1]==t: out.append(tuple(p))
            return
        for v in adj[p[-1]]:
            if d[v]==d[p[-1]]+1: rec(p+[v])
    rec([s]); return tuple(sorted(out))

def state(n,B,X,rows):
    pair=Counter(); rc=[0]*n; support=set(); selected=set()
    for row in rows:
        selected.update(row)
        for x in row:
            rc[x]+=1
            for y in row: pair[x,y]+=1
        support.update(E(a,b) for a,b in zip(row,row[1:]))
    active={e for e in B if e[0] in selected and e[1] in selected and e not in support}
    par={v:v for v in selected}
    def find(v):
        while par[v]!=v: par[v]=par[par[v]]; v=par[v]
        return v
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b: par[max(a,b)]=min(a,b)
    for a,b in active: union(a,b)
    roots={find(a) for a,b in X if a in selected and b in selected and find(a)==find(b)}
    active_v={v for v in selected if find(v) in roots}
    demanded={e for e in active if find(e[0]) in roots}; deg=Counter()
    for a,b in demanded: deg[a]+=1; deg[b]+=1
    col={v:2*sum(m-1 for (x,_),m in pair.items() if x==v and m>=2) for v in active_v}
    hit={v:max(0,deg[v]-max(0,n-5*rc[v])) for v in active_v}
    return {"score":sum(col.values())+sum(hit.values()),"collision":sum(col.values()),"hit":sum(hit.values()),
            "active_vertices":sorted(active_v),"positive":{str(v):col[v]+hit[v] for v in sorted(active_v) if col[v]+hit[v]}}

def main():
    n,B,X,base,atoms,meta,blocks=construct(); adj=adjacency(n,B); start=676
    assert (n,len(B),len(X),len(B|X),len(base),len(atoms))==(2943,7039,1383,8422,1383,1383)
    families=[]; shapes=Counter(); touches=[Counter(),Counter()]
    for i,(side,j,q,F,D) in enumerate(meta):
        fam=shortest_rows(adj,*atoms[start+i]); families.append(fam)
        anchors=[r for r in fam if 55 in r]; local=[r for r in fam if 55 not in r]
        assert (len(anchors),len(local))==(676,4); shapes[676,4]+=1
        # A local row's D-x is at position 1.  D indices j and j+1 occur;
        # a leaf owns 26 consecutive D indices, hence it is available to
        # exactly those 26 families plus the preceding cyclic family: 27.
        D_x_leaf={x:leaf for leaf,x,y in D}
        touched={D_x_leaf[r[1]] for r in local}
        for leaf in touched: touches[side][leaf]+=1
    assert shapes==Counter({(676,4):676})
    assert all(len(t)==13 and set(t.values())=={27} for t in touches)

    # Anchor choices on each side are edges of C_676: x_j--y_j and
    # x_j--y_(j+1).  A collision-free choice of 338 edges is a perfect
    # matching.  Propagation around the cycle leaves exactly two matchings.
    matchings=[]
    for phase in (0,1):
        choice=[]
        for i,(side,j,q,F,D) in enumerate(meta):
            target=(D[(j+1)%338][2],55,F[(j+phase)%338][2],F[j][1],q)
            assert target in families[i]; choice.append(target)
        matchings.append(choice)
    minima=[]
    for pl in (0,1):
        for pr in (0,1):
            rs=list(base)
            for i,(side,*_) in enumerate(meta): rs[start+i]=matchings[pl if side==0 else pr][i]
            st=state(n,B,X,tuple(rs)); assert st["score"]==23115; minima.append({"phases":[pl,pr],"state":st})

    # Count-only global lower bound; scan all 339^2 orbit-count states.
    best=10**9; arg=[]
    for ll in range(339):
      for lr in range(339):
        al,ar=338-ll,338-lr
        c55=2*((al+ar)+max(0,al-1)+max(0,ar-1))
        bd=20411+c55+200*((ll+26)//27+(lr+26)//27)+(4 if ll==lr==0 else 0)
        if bd<best: best,arg=bd,[(ll,lr)]
        elif bd==best: arg.append((ll,lr))
    assert (best,arg)==(23115,[(0,0)])
    active=set(minima[0]["state"]["active_vertices"])
    hubs={0,1,2}; leaves=set(range(3,55)); descendants=set(range(56,2760)); anchor={55}; circuit=set(range(2762,2929)); cable={2929,2930}
    deactivation={"hubs_active":sorted(active&hubs),"leaves_active":sorted(active&leaves),"descendants_active":sorted(active&descendants),
                  "anchor_active":sorted(active&anchor),"circuit_active":sorted(active&circuit),"cable_seed_vertices_active":sorted(active&cable)}
    assert deactivation["hubs_active"]==[0,1,2] and not deactivation["leaves_active"] and not deactivation["descendants_active"]
    canonical=json.dumps({"n":n,"blue":sorted(B),"bad":sorted(X),"rows":base},sort_keys=True,separators=(",",":")).encode()
    cert={"status":"CERTIFIED","minimum":best,"minimizer_count":4,"minimizer_phases":[x["phases"] for x in minima],
          "family_shape":{"families":676,"anchor_each":676,"local_each":4},"D_leaf_local_family_degrees":[dict(sorted(t.items())) for t in touches],
          "lower_bound_unique_count_state":list(arg[0]),"minimum_state":minima[0]["state"],"deactivation_at_every_minimizer":deactivation,
          "sha256":{"canonical_instance":sha256(canonical).hexdigest(),"audit_script":sha256(Path(__file__).read_bytes()).hexdigest()}}
    (HERE/"certificate.json").write_text(json.dumps(cert,sort_keys=True,indent=2)+"\n")
    print(json.dumps(cert,sort_keys=True))

if __name__=="__main__": main()
