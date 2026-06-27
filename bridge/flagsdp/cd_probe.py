#!/usr/bin/env python3
"""Probe the CD-PRESERVATION crux of the safe-peel lemma (while GPT reasons).
For a FIXED bad edge uv, enumerate ALL simple B-paths u..v (=> all odd cycles through uv),
peel each C=V(path), and check the obstruction form exactly:
    g(S) := [delta_B(S)-delta_M(S)] - [e_B(S,C)-e_M(S,C)]  >= 0  for all S subset V\\C.
min_S g(S) >= 0  <=>  CD preserved after peeling C. Report min g, the argmin S, |C|, L vs bound,
for SHORTEST vs NON-shortest geodesics. A non-shortest C with min g < 0 pins 'shortest is essential'."""
from collections import deque
from itertools import combinations

def C5q(q):
    n=5*q
    def vid(i,j): return i*q+j
    side=[0]*n
    for i in range(5):
        for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
    adj=[set() for _ in range(n)]
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
    M=[(vid(4,a),vid(0,b)) for a in range(q) for b in range(q)]
    return n,adj,side,M

def Badj(n,adj,side):
    B=[set() for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            if side[u]!=side[v]: B[u].add(v); B[v].add(u)
    return B

def all_simple_paths(B,s,t,maxlen=9):
    # all simple paths s..t in graph B, up to maxlen edges
    out=[]
    def dfs(path,seen):
        u=path[-1]
        if u==t:
            out.append(list(path)); return
        if len(path)-1>=maxlen: return
        for w in B[u]:
            if w not in seen:
                seen.add(w); path.append(w); dfs(path,seen); path.pop(); seen.discard(w)
    dfs([s],{s}); return out

def bdist(B,src,banned):
    d={src:0}; q=deque([src])
    while q:
        u=q.popleft()
        for w in B[u]:
            if w not in banned and w not in d: d[w]=d[u]+1; q.append(w)
    return d

def cd_min(keep,n,adj,side,Mfull,C):
    """CORRECT: CD-in-(G-C) holds for S  <=>  delta_{B'}(S) >= delta_{M'}(S), with B',M' = B,M restricted
    to keep (edges to C removed). Return min over S of h(S)=delta_{B'}(S)-delta_{M'}(S) and the argmin,
    plus at that argmin the full-graph margin and the edges-to-C loss (e_B(S,C)-e_M(S,C)) for structure."""
    K=sorted(keep); idx={v:i for i,v in enumerate(K)}; m=len(K); kset=set(K); Cset=set(C)
    Be=[(u,v) for u in K for v in adj[u] if v>u and v in kset and side[u]!=side[v]]   # B within keep
    Me=[(u,v) for (u,v) in Mfull if u in kset and v in kset]                          # M within keep
    eBc={u:0 for u in K}; eMc={u:0 for u in K}
    Mset=set((min(a,b),max(a,b)) for (a,b) in Mfull)
    for u in K:
        for c in adj[u]:
            if c in Cset:
                if side[u]!=side[c]: eBc[u]+=1
                elif (min(u,c),max(u,c)) in Mset: eMc[u]+=1
    if m>22: return None
    best=10**9; arg=None; aux=None
    for mask in range(1<<m):
        inS=[(mask>>idx[u])&1 for u in K]
        dMp=sum(1 for (u,v) in Me if inS[idx[u]]!=inS[idx[v]])   # delta_{M'}(S)
        dBp=sum(1 for (u,v) in Be if inS[idx[u]]!=inS[idx[v]])   # delta_{B'}(S)
        h=dBp-dMp
        if h<best:
            best=h; arg=[u for u in K if inS[idx[u]]]
            eB=sum(eBc[u] for u in K if inS[idx[u]]); eM=sum(eMc[u] for u in K if inS[idx[u]])
            aux=(dBp+eB)-(dMp+eM), eB-eM   # (full margin delta_B(S)-delta_M(S), loss e_B-e_M)
    return best,arg,aux

def probe(name,builder,bad_idx=0,maxlen=9):
    n,adj,side,M=builder()
    B=Badj(n,adj,side)
    NN=n
    # Gamma of full instance
    G=0
    for (a,b) in M:
        d=bdist(B,a,set()).get(b,-1); G+=(d+1)**2 if d>=0 else 0
    u,v=M[bad_idx]
    paths=all_simple_paths(B,u,v,maxlen=maxlen)
    lens=sorted(set(len(p)-1 for p in paths))   # edge-lengths
    print(f"\n=== {name}: N={NN} Gamma={G} N^2={NN*NN} | bad edge ({u},{v}); B-path edge-lengths present={lens} (cycle |C|=len+1) ===",flush=True)
    seen_s=set()
    for p in sorted(paths,key=len):
        C=p; s=len(C)
        if s in seen_s: continue   # one representative per |C| (CD/L are symmetric across the q^2 transversals)
        keep=[x for x in range(n) if x not in set(C)]
        Mp=[(a,b) for (a,b) in M if a in keep and b in keep]
        bn=set(C)
        Gp=0; ok=True
        for (a,b) in Mp:
            d=bdist(B,a,bn).get(b,-1)
            if d<0: ok=False; break
            Gp+=(d+1)**2
        res=cd_min(keep,n,adj,side,Mp,C) if ok else None
        L=G-Gp if ok else None; bound=2*s*NN-s*s
        tag="SHORTEST" if s==lens[0]+1 else "longer  "
        if res is None:
            print(f"  |C|={s} [{tag}] DISCONNECTED bad edge in B' (cond (2) fails) — skip",flush=True)
        else:
            mn,arg,aux=res
            ok2 = (mn>=0) and (L<=bound)
            fullm,loss = aux
            print(f"  |C|={s} [{tag}] min(dB'-dM')={mn} ({'CD OK' if mn>=0 else 'CD BREAKS'}; at tight S: fullMargin={fullm}, loss eB-eM={loss}) | L={L}<=2sN-s^2={bound}? {L<=bound} | Gamma'={Gp} N'^2={(NN-s)**2} => {'SAFE' if ok2 else 'UNSAFE'}",flush=True)
        seen_s.add(s)

if __name__=="__main__":
    probe("C5[2]", lambda: C5q(2), bad_idx=0, maxlen=9)
    probe("C5[3]", lambda: C5q(3), bad_idx=0, maxlen=7)
    print("\nDONE",flush=True)
