#!/usr/bin/env python3
"""Test the GPI-workflow's recommended next target: the PER-EDGE OVERLAP-DECAY sub-claim
   for every bad edge e:   sum_{f in M} h_f * I(e,f)  <=  N ,
where a_{e,v} = fraction of e's shortest B-geodesics through v (sum_v a_{e,v}=h_e), and
I(e,f) = sum_v a_{e,v} a_{f,v} (uniform geodesic-membership inner product). Tight at C_odd[q].
If it holds census-wide it isolates the open lemma to a CD-coarea bound on I(e,f); a violation kills
the uniform-routing route (without killing GPI). Census N<=Nmax + witnesses."""
import sys
from collections import deque
from mycielskian_check import mycielskian, edges_of, gamma_min_cut, all_shortest_geos
import flag_engine as fe

def a_vectors(N,adj,side,M):
    """a[e] = dict v->fraction of e's shortest geodesics through v; h[e]=ell(e)."""
    a={}; h={}
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        h[(u,v)]=len(geos[0]); cnt={}
        for P in geos:
            for w in P: cnt[w]=cnt.get(w,0)+1
        a[(u,v)]={w:cnt[w]/len(geos) for w in cnt}
    return a,h

def max_overlap(N,adj,side,M):
    r=a_vectors(N,adj,side,M)
    if r is None: return None
    a,h=r; worst=-1e9; arge=None
    for e in M:
        s=0.0
        for f in M:
            I=sum(a[e].get(w,0)*a[f].get(w,0) for w in a[e])
            s+=h[f]*I
        if s-N>worst: worst=s-N; arge=(e,s)
    return worst,arge

def run_witnesses():
    def C5q(q):
        n=5*q; vid=lambda i,j:i*q+j; side=[0]*n; adj=[set() for _ in range(n)]
        for i in range(5):
            for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
        for i in range(5):
            for a2 in range(q):
                for b in range(q):
                    u=vid(i,a2); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
        M=[(vid(4,a2),vid(0,b)) for a2 in range(q) for b in range(q)]; G=25*len(M)
        return n,adj,side,M
    def decode_g6(s):
        data=[ord(c)-63 for c in s]; n=data[0]; bits=[]
        for d in data[1:]:
            for k in range(5,-1,-1): bits.append((d>>k)&1)
        adj=[set() for _ in range(n)]; idx=0
        for j in range(1,n):
            for i in range(j):
                if idx<len(bits) and bits[idx]: adj[i].add(j); adj[j].add(i)
                idx+=1
        return n,adj
    print("WITNESSES (max_e [sum_f h_f I(e,f)] - N ; <=0 means sub-claim holds):")
    for q in (2,3,4):
        n,adj,side,M=C5q(q); w,arg=max_overlap(n,adj,side,M)
        print(f"  C5[{q}]: N={n} max_e overlap-N = {w:.4f}  (sub-claim {'OK' if w<=1e-9 else 'VIOLATED'}; tight {abs(w)<1e-9})")
    n,adj=decode_g6("G?`F`w"); res,mc=gamma_min_cut(n,[set(x) for x in adj],edges_of([set(x) for x in adj])); side,G,M=res
    w,arg=max_overlap(n,[set(x) for x in adj],side,M); print(f"  n8: N={n} max_e overlap-N = {w:.4f} ({'OK' if w<=1e-9 else 'VIOLATED'})")
    C5e=[(i,(i+1)%5) for i in range(5)]; gN,gadj=mycielskian(5,C5e)
    Ng,adjg=mycielskian(11,edges_of(gadj)); res,mc=gamma_min_cut(Ng,adjg,edges_of(adjg)); side,G,M=res
    w,arg=max_overlap(Ng,adjg,side,M); print(f"  M(Grotzsch): N={Ng} max_e overlap-N = {w:.4f} ({'OK' if w<=1e-9 else 'VIOLATED'})")
    pet=[set() for _ in range(10)]
    for i in range(5):
        for (a2,b) in [(i,(i+1)%5),(5+i,5+(i+2)%5),(i,5+i)]: pet[a2].add(b); pet[b].add(a2)
    Np,adjp=mycielskian(10,edges_of(pet)); res,mc=gamma_min_cut(Np,adjp,edges_of(adjp)); side,G,M=res
    w,arg=max_overlap(Np,adjp,side,M); print(f"  M(Petersen): N={Np} max_e overlap-N = {w:.4f} ({'OK' if w<=1e-9 else 'VIOLATED'})")

def run_census(Nmax,Nmin=8):
    from collections import deque as dq
    def Bconnected(n,adj,side):
        seen={0}; q=dq([0])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
        return len(seen)==n
    for N in range(Nmin,Nmax+1):
        gs=fe.enumerate_graphs(N,triangle_free=True); nconf=0; viol=0; worst=-1e9
        for (n,A0) in gs:
            adj=[set(v for v in range(n) if (A0[u]>>v)&1) for u in range(n)]
            E=[(u,v) for u in range(n) for v in adj[u] if v>u]
            res=gamma_min_cut(n,adj,E)
            if res is None: continue
            side,G,M=res
            if len(M)<2: continue
            r=max_overlap(n,adj,side,M)
            if r is None: continue
            w,arg=r; nconf+=1
            if w>worst: worst=w
            if w>1e-9: viol+=1
        print(f"N={N}: connected-B m>=2 configs={nconf} | overlap-decay VIOLATIONS (sum_f h_f I(e,f) > N)={viol} (worst overlap-N={worst:.4f})",flush=True)
    print("DONE")

if __name__=="__main__":
    run_witnesses()
    if len(sys.argv)>1: run_census(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv)>2 else 8)
