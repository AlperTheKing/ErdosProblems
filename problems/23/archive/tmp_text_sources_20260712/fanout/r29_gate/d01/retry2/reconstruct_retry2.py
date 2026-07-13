"""Independent integer-only reconstruction/checker for the R29 lead specification."""
from collections import Counter, deque
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEAD = ROOT / "lead" / "r29_lead_gate.py"

def E(a,b):
    if a == b: raise ValueError("loop")
    return (a,b) if a < b else (b,a)

def build_independent():
    B=set(); X=set(); rows=[]; atoms=[]
    def blue_path(p): B.update(E(a,b) for a,b in zip(p,p[1:]))
    r,cl,cr,A=0,1,2,55
    L=range(3,29); R=range(29,55)
    blue_path((cl,r,cr)); B.update(E(cl,x) for x in L); B.update(E(cr,x) for x in R)
    traffic=[(l,cl,r,cr,rr) for l in L for rr in R]
    X.update(E(l,rr) for l in L for rr in R)
    arms=[]; nxt=56
    for leaves in (L,R):
        block=[]
        for leaf in leaves:
            for k in range(26):
                x,y=nxt,nxt+1; nxt+=2; blue_path((leaf,x,y,A)); block.append((leaf,x,y))
        arms.append(block)
    selector=[]; selector_atoms=[]
    for q,block in zip((2760,2761),arms):
        f,d=block[:338],block[338:]
        for j in range(338):
            p=(q,f[j][1],f[(j+1)%338][2],d[j][1],d[(j+1)%338][2])
            blue_path(p); a=E(q,p[-1]); X.add(a)
            selector.append(p[::-1]); selector_atoms.append(a)
    # Circuit, independently expanded from its modular definition.
    off=2762; w=26
    support={E(i,(i+1)%26) for i in range(26)}|{E(w,0)}
    av=[9*k%26 for k in range(13)]
    support|={E(av[i],av[i+1]) for i in range(12)}
    B.update(E(off+a,off+b) for a,b in support)
    ca=sorted({E(i,(i+4)%26) for i in range(26)}|{E(w,3),E(w,23)})
    circuit_atoms=[]; nxt=off+27
    for a,b in ca:
        p=(off+a,*range(nxt,nxt+5),off+b); nxt+=5; blue_path(p)
        z=E(off+a,off+b); X.add(z); circuit_atoms.append(z)
    zL,zR=nxt,nxt+1; nxt+=2
    B.update({E(r,A),E(A,off+2),E(cl,zL),E(zL,A),E(cr,zR),E(zR,A)})
    seed=[]; seed_atoms=[]
    for s in (A,zL,zR):
        p=(s,*range(nxt,nxt+4)); nxt+=4; blue_path(p); a=E(s,p[-1]); X.add(a)
        seed.append(p); seed_atoms.append(a)
    # Unique blue shortest rows for the 28 circuit atoms.
    adj=[[] for _ in range(nxt)]
    for a,b in B: adj[a].append(b); adj[b].append(a)
    for q in adj: q.sort()
    def unique_row(a,b):
        dist=[-1]*nxt; dist[a]=0; todo=deque([a])
        while todo:
            u=todo.popleft()
            for v in adj[u]:
                if dist[v]<0: dist[v]=dist[u]+1; todo.append(v)
        found=[]
        def rec(p):
            if len(p)==5:
                if p[-1]==b: found.append(tuple(p))
                return
            for v in adj[p[-1]]:
                if dist[v]==dist[p[-1]]+1: rec(p+[v])
        rec([a]); assert len(found)==1
        return found[0]
    circuit=[unique_row(*a) for a in circuit_atoms]
    rows=tuple(traffic+selector+circuit+seed)
    atoms=tuple(sorted(E(l,rr) for l in L for rr in R)+selector_atoms+circuit_atoms+seed_atoms)
    assert all(E(p[0],p[-1])==a for p,a in zip(rows,atoms))
    return nxt,B,X,rows,atoms

def enc_edges(es): return json.dumps([list(x) for x in sorted(es)],separators=(",",":" )).encode()
def enc_rows(rs): return json.dumps([list(x) for x in rs],separators=(",",":" )).encode()
def enc_full(n,b,x,rs):
    return json.dumps({"n":n,"blue":[list(e) for e in sorted(b)],"bad":[list(e) for e in sorted(x)],"rows":[list(r) for r in rs]},sort_keys=True,separators=(",",":" )).encode()

def main():
    n,B,X,R,A=build_independent(); G=B|X
    assert (n,len(B),len(X),len(G),len(R),len(A))==(2943,7039,1383,8422,1383,1383)
    assert B.isdisjoint(X)
    adj=[set() for _ in range(n)]
    for u,v in G: adj[u].add(v); adj[v].add(u)
    assert not any(adj[u]&adj[v] for u,v in G)
    # Distances and exact shortest-path multiplicities for every bad edge.
    hist=Counter()
    for a,b in A:
        d=[-1]*n; ways=[0]*n; d[a]=0; ways[a]=1; q=deque([a])
        while q:
            u=q.popleft()
            for v in sorted(Bv[u]):
                if d[v]<0: d[v]=d[u]+1; ways[v]=ways[u]; q.append(v)
                elif d[v]==d[u]+1: ways[v]+=ways[u]
        assert d[b]==4; hist[ways[b]]+=1
    spec=importlib.util.spec_from_file_location("untrusted_lead",LEAD); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    ld=m.build()
    own={"edges":enc_edges(G),"blue":enc_edges(B),"bad":enc_edges(X),"rows":enc_rows(R),"full":enc_full(n,B,X,R)}
    other={"edges":enc_edges(ld["graph"]),"blue":enc_edges(ld["blue"]),"bad":enc_edges(ld["bad"]),"rows":enc_rows(ld["rows"]),"full":m.canonical_bytes(ld)}
    compare={k:own[k]==other[k] for k in own}
    hashes={k:{"retry2":sha256(own[k]).hexdigest(),"lead":sha256(other[k]).hexdigest()} for k in own}
    out={"counts":{"vertices":n,"blue":len(B),"bad":len(X),"edges":len(G),"rows":len(R),"atoms":len(A)},"shortest_path_histogram":dict(sorted(hist.items())),"gamma":25*len(A),"hamming_one_replacements":676*679,"byte_equal":compare,"sha256":hashes}
    Path(__file__).with_name("certificate.json").write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    # adjacency of the blue graph is deliberately global only during checking
    n0,B0,_,_,_=build_independent(); Bv=[set() for _ in range(n0)]
    for u,v in B0: Bv[u].add(v); Bv[v].add(u)
    main()
