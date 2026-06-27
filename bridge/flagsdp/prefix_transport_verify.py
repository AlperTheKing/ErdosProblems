#!/usr/bin/env python3
"""Verify the PREFIX-DEFECT TRANSPORT LEMMA (the piece GPT says IS rigorous, after retracting the shell route):
for a shortest bad geodesic C=v_0..v_{h-1} and a residual CD-obstruction S subset R=V\C with
defect eta = delta_{M[R]}(S) - delta_{B[R]}(S) > 0:
    e^sigma(C\P_i, S) + e^sigma(P_i, R\S) >= eta     for 0 <= i < h-1,    P_i={v_0..v_i},
where e^sigma(A,D)=e_B(A,D)-e_M(A,D). GPT claims this follows from CD (the original cut-domination). A single
failure would mean either my reading is wrong or the lemma is wrong. Also report the defect-overlap signal:
does another bad edge's shortest cycle non-parallel-overlap C?"""
from collections import deque

def Bedges_Medges(n,adj,side):
    B=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]!=side[v]]
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    return set(B),set(M)

def e_sig(A,D,Bset,Mset):
    """signed attachment e_B(A,D)-e_M(A,D) between disjoint vertex sets A,D."""
    A=set(A); D=set(D); eB=0; eM=0
    for (u,v) in Bset:
        if (u in A and v in D) or (v in A and u in D): eB+=1
    for (u,v) in Mset:
        if (u in A and v in D) or (v in A and u in D): eM+=1
    return eB-eM

def bdistB(n,adj,side,src,banned):
    d={src:0}; q=deque([src])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in banned and v not in d: d[v]=d[u]+1; q.append(v)
    return d

def shortest_geodesics(n,adj,side,s,t):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    paths=[]
    def rec(v,acc):
        if v==s: paths.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[]); return paths

def max_obstruction(n,adj,side,M,C):
    """return (eta, S) maximizing delta_{M[R]}(S)-delta_{B[R]}(S) over S subset R=V\C."""
    Cset=set(C); K=[v for v in range(n) if v not in Cset]; idx={v:i for i,v in enumerate(K)}; m=len(K); kset=set(K)
    Be=[(u,v) for u in K for v in adj[u] if v>u and v in kset and side[u]!=side[v]]
    Mp=[(a,b) for (a,b) in M if a in kset and b in kset]
    best=0; arg=[]
    for mask in range(1<<m):
        dM=sum(1 for (u,v) in Mp if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        dB=sum(1 for (u,v) in Be if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        if dM-dB>best: best=dM-dB; arg=[u for u in K if (mask>>idx[u])&1]
    return best,arg

def check(name,n,adj,side,M):
    Bset,Mset=Bedges_Medges(n,adj,side)
    G=0
    for (a,b) in M:
        d=bdistB(n,adj,side,a,set()).get(b,-1); G+= (d+1)**2 if d>=0 else 0
    print(f"\n=== {name}: N={n} Gamma={G} N^2={n*n} deficit={n*n-G} M={M} ===")
    for (u,v) in M:
        for C in shortest_geodesics(n,adj,side,u,v):
            eta,S=max_obstruction(n,adj,side,M,C)
            if eta<=0: continue
            R=[x for x in range(n) if x not in set(C)]; RminusS=[x for x in R if x not in set(S)]
            h=len(C); ok=True; rows=[]
            for i in range(h-1):
                Pi=C[:i+1]; CminusPi=C[i+1:]
                lhs=e_sig(CminusPi,S,Bset,Mset)+e_sig(Pi,RminusS,Bset,Mset)
                rows.append((i,lhs))
                if lhs<eta: ok=False
            tag="OK" if ok else "FAIL"
            print(f"  bad({u},{v}) C={C} eta={eta} S={S}: transport e^s(C\\P_i,S)+e^s(P_i,R\\S) vs eta -> {[(i,l) for (i,l) in rows]}  [>={eta}? {tag}]")
            # defect-overlap signal: count OTHER bad edges whose shortest cycle shares >=2 vertices with C
            ov=0
            for (x,y) in M:
                if (x,y)==(u,v): continue
                for C2 in shortest_geodesics(n,adj,side,x,y):
                    if len(set(C2)&set(C))>=2: ov+=1; break
            print(f"     defect-overlap signal: {ov} other bad edge(s) have a shortest cycle sharing >=2 vertices with C")

def gpt_b():
    n=8; side=[0,0]+[1]*6
    B=[(1,2),(0,4),(1,5),(0,6),(0,2),(1,7),(0,5),(1,3)]; M=[(6,7),(3,4)]
    adj=[set() for _ in range(n)]
    for (u,v) in B+M: adj[u].add(v); adj[v].add(u)
    return n,adj,side,M

if __name__=="__main__":
    n,adj,side,M=gpt_b(); check("GPT (b) N=8 (shortest peels fail, Gamma=50<64)", n,adj,side,M)
    print("\nDONE")
