#!/usr/bin/env python3
"""Fast max-cut for M(Grotzsch) N=23 (and other N up to ~24), then run the UNIFORM-SPLIT (U) test.
Uses incremental Gray-code cut-value update over all 2^(N-1) sign vectors with bitset adjacency,
collecting ALL maximum cuts, then runs the EXACT-Fraction T_uniform check from AUDIT_mycielski_uniform."""
from fractions import Fraction
import AUDIT_mycielski_uniform as A

def maxcut_all_fast(n, adj):
    # adjacency bitmask
    nb=[0]*n
    for u in range(n):
        m=0
        for v in adj[u]: m|=(1<<v)
        nb[u]=m
    # cut value of side-bitmask S = number of edges with one endpoint in S
    # iterate Gray code over n-1 free bits (vertex 0 fixed to 0)
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    # incremental: track cut by flipping one vertex at a time
    side=[0]*n
    def cutval():
        return sum(1 for u,v in edges if side[u]!=side[v])
    # Gray code over vertices 1..n-1
    best=-1; cuts=[]
    cur=cutval()  # all zero -> 0
    # delta when flipping vertex x: new same-side neighbors become cross and vice versa
    # change = (#neighbors on opposite side) - (#neighbors on same side) BEFORE flip... but easier recompute via neighbor scan
    deg=[len(adj[u]) for u in range(n)]
    # maintain for each vertex count of neighbors with side==1
    cnt1=[0]*n  # neighbors currently on side 1
    total=2**(n-1)
    g_prev=0
    for i in range(total):
        g=i^(i>>1)
        if i>0:
            diff=g ^ g_prev
            x=diff.bit_length()  # which free bit changed; free bits map to vertex x (1..n-1)
            # bit position p (0-indexed) corresponds to vertex p+1
            p=(diff).bit_length()-1
            v=p+1
            newside=1-side[v]
            # cut delta = (#neighbors on same side as old) - (#neighbors on opposite)
            same = (cnt1[v] if side[v]==1 else deg[v]-cnt1[v])
            opp  = deg[v]-same
            cur += (same - opp)
            side[v]=newside
            for u in adj[v]:
                if newside==1: cnt1[u]+=1
                else: cnt1[u]-=1
            g_prev=g
        if cur>best:
            best=cur; cuts=[side[:]]
        elif cur==best:
            cuts.append(side[:])
    return cuts

def run(name, n, E):
    adj=A.build_adj(n,E)
    assert A.is_triangle_free(n,adj), 'not triangle-free'
    cuts=maxcut_all_fast(n,adj)
    r=A.gmin(n,adj,cuts)
    if r is None:
        print(f'[{name}] N={n}: no connected-B monochromatic max cut'); return None
    side,G,M,ell=r
    K=n+(n*n-G)
    T=A.T_uniform(n,adj,side,M,ell)
    maxT=max(T)
    sl=Fraction(K)-maxT
    viol=maxT>K
    mc=sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
    print(f'[{name}] N={n} Gamma={G} K={K} maxcut={mc} numMaxCuts={len(cuts)} maxT={maxT} (~{float(maxT):.4f}) slack={sl} (~{float(sl):.4f}) {"*** VIOLATION ***" if viol else "OK"}')
    return G,K,maxT,viol,sl

if __name__=='__main__':
    # sanity: M(C5)=Grotzsch via fast path must match brute (Gamma=100,maxT=815/63)
    n,E=A.cycle(5); N,EE=A.mycielskian(n,E)
    print('--- sanity M(C5) via fast maxcut (expect Gamma=100 maxT=815/63) ---')
    run('M(C5)=Grotzsch[fast]', N, EE)
    print('--- M(Grotzsch) N=23 ---')
    gn,gE=A.mycielskian(*A.cycle(5))
    N,EE=A.mycielskian(gn,gE)
    run('M(Grotzsch)', N, EE)
    # also M_2(Petersen) N=21 and M(C9) N=19, generalized M_4(C5) N=21(too big for n? 21 ok)
    print('--- extra high-chromatic / large-N targets ---')
    n,E=A.petersen(); run('M_2(Petersen)', *A.gen_mycielskian(n,E,2))
    n,E=A.cycle(9); run('M(C9)', *A.mycielskian(n,E))
    n,E=A.cycle(5); run('M_4(C5)', *A.gen_mycielskian(n,E,4))   # N=21
    n,E=A.cycle(11); run('M(C11) skip-if-big', *A.mycielskian(n,E))  # N=23
