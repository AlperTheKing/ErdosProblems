"""Test the boundary-preserving re-cut for the induction gap.
For a K-component C with boundary all in B (cut, zero-mu), consider re-cuts of C that KEEP every boundary
vertex on its original side (so all boundary edges stay cut, global cut stays max, B stays connected if C's
internal re-cut keeps C connected to boundary). Among such re-cuts that are internally MAX cuts of G[C]:
 - is the restricted cut sigma|_C already gamma-min among them?
 - what is the min achievable internal Gamma? Is it <= |C|^2?

The induction needs: for a CRITICAL C (Gamma_C=N|C|), gamma-minimality forbids it because a boundary-preserving
re-cut to the island's gamma-min (<= |C|^2 < N|C|) would reduce global Gamma. We TEST whether boundary vertices
constrain this. Key question: can the island reach a max cut with Gamma <= |C|^2 while keeping boundary fixed?

We test on the bridge island {0..4} (non-critical, Gamma_C=25=|C|^2 already), and on any census island."""
from fractions import Fraction as F
from itertools import product
from collections import deque
from _bdef_construct import loads, mycielski, union_disjoint, add_edges, Cn

def analyze_island(name, n, E, Cset):
    info=loads(n,E)
    adj=info['adj']; side=info['side']
    C=sorted(Cset); m=len(C); idx={v:i for i,v in enumerate(C)}
    # boundary vertices of C (have a neighbor outside C) and their fixed side
    bnd={}  # local idx -> required side (original)
    iedges=[]
    for u in C:
        for v in adj[u]:
            if v in Cset and v>u: iedges.append((idx[u],idx[v]))
            elif v not in Cset:
                bnd[idx[u]]=side[u]  # u is a boundary vertex; keep its side fixed
    def bdist(s,a,b):
        ad=[[] for _ in range(m)]
        for x,y in iedges:
            if s[x]!=s[y]: ad[x].append(y); ad[y].append(x)
        d={a:0};q=deque([a])
        while q:
            u=q.popleft()
            for v in ad[u]:
                if v not in d: d[v]=d[u]+1;q.append(v)
        return d.get(b,-1)
    def conn(s):
        ad=[[] for _ in range(m)]
        for x,y in iedges:
            if s[x]!=s[y]: ad[x].append(y); ad[y].append(x)
        seen={0};q=deque([0])
        while q:
            u=q.popleft()
            for v in ad[u]:
                if v not in seen: seen.add(v);q.append(v)
        return len(seen)==m
    # internal max cut size
    best=-1
    for bits in range(1<<m):
        s=[(bits>>i)&1 for i in range(m)]
        c=sum(1 for a,b in iedges if s[a]!=s[b])
        best=max(best,c)
    # enumerate boundary-preserving cuts, internally max, connected; min Gamma
    minG=None; restrictedG=None
    orig=[side[v] for v in C]
    for bits in range(1<<m):
        s=[(bits>>i)&1 for i in range(m)]
        if any(s[i]!=req for i,req in bnd.items()): continue  # boundary fixed
        c=sum(1 for a,b in iedges if s[a]!=s[b])
        if c!=best: continue
        if not conn(s): continue
        Mloc=[(a,b) for a,b in iedges if s[a]==s[b]]
        G=0;ok=True
        for a,b in Mloc:
            dd=bdist(s,a,b)
            if dd<0: ok=False;break
            G+=(dd+1)**2
        if not ok: continue
        if minG is None or G<minG: minG=G
        if s==orig: restrictedG=G
    print(f"[{name}] |C|={m} #bnd-verts={len(bnd)} restrictedGamma={restrictedG} "
          f"min boundary-preserving max-cut Gamma={minG} |C|^2={m*m} "
          f"reaches<=|C|^2:{minG is not None and minG<=m*m}")

if __name__=="__main__":
    isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
    n,E=union_disjoint(isl,g15); n,E=add_edges((n,E),[(0,5)])
    analyze_island("bridge island {0..4}", n, E, {0,1,2,3,4})
