#!/usr/bin/env python3
"""Random + structured tri-free HIGH-Gamma audit of claim U (max_v T_uniform <= K = N + (N^2-Gamma)).
EXACT Fractions only. Reject-sample to keep Gamma/N^2 >= 0.7 (dense, many bad edges) and also
edge-density ~0.4 (C5 extremal density). Brute maxcut -> cap N<=18. Re-confirm any violation independently."""
import sys, random
from fractions import Fraction
from collections import deque
sys.path.insert(0, "E:/Projects/ErdosProblems/problems/23/writeup")
from census_GPI import maxcut_all, geos, blow

def adj_from_E(n, E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def has_triangle(n, adj):
    for u in range(n):
        nu=adj[u]
        for v in nu:
            if v>u:
                if nu & adj[v]: return True
    return False

def Bconn(n,adj,side):
    start=0
    seen={start};q=deque([start])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen:seen.add(v);q.append(v)
    return len(seen)==n

def bdist_restr(adj,side,s,t):
    d={s:0};q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d:d[v]=d[u]+1;q.append(v)
    return d.get(t,-1)

def gmin(n,adj,cuts):
    """Gamma-minimizing connected-B max cut. Returns (side,Gamma,M,ell) or None."""
    best=None
    for side in cuts:
        if not Bconn(n,adj,side):continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M:continue
        G=0;ok=True;ell={}
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v)
            if d<0:ok=False;break
            ell[(u,v)]=d+1;G+=(d+1)**2
        if ok and (best is None or G<best[1]):best=(side,G,M,ell)
    return best

def max_T_uniform(n, adj, side, M, ell):
    """EXACT Fraction max_v T_uniform(v)."""
    T=[Fraction(0)]*n
    for f in M:
        Ps=geos(adj, side, f[0], f[1])
        nf=len(Ps)
        if nf==0:  # should not happen for a valid bad edge under connected-B
            return None
        share=Fraction(ell[f], nf)
        for P in Ps:
            for v in P:
                T[v]+=share
    return max(T)

def check(n, E):
    """Returns dict with N,Gamma,K,maxT,ratio or None if no valid gamma-min cut."""
    adj=adj_from_E(n,E)
    if has_triangle(n,adj): return None
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    mT=max_T_uniform(n,adj,side,M,ell)
    if mT is None: return None
    K=n+(n*n-G)
    return dict(N=n,Gamma=G,K=K,maxT=mT,ratio=Fraction(G,n*n),side=side,M=M)

def random_trifree(n, p, rng):
    """Random graph then greedily delete an edge from each triangle until tri-free."""
    E=[]
    for i in range(n):
        for j in range(i+1,n):
            if rng.random()<p: E.append((i,j))
    adj=adj_from_E(n,E)
    # remove triangles greedily
    changed=True
    while changed:
        changed=False
        for u in range(n):
            done=False
            for v in list(adj[u]):
                if v>u:
                    common=adj[u]&adj[v]
                    if common:
                        adj[u].discard(v);adj[v].discard(u)
                        changed=True;done=True;break
            if done:break
    E=[(a,b) for a in range(n) for b in adj[a] if b>a]
    return E

def main():
    rng=random.Random(20260626)
    # anchors: C5 blowups (Gamma=N^2 exactly)
    print("=== ANCHORS C5[t] (Gamma=N^2, ratio=1, expect maxT<=K tightly) ===")
    for t in (1,2,3):
        d=check(*blow(t))
        slack=d['K']-d['maxT']
        print(f"  C5[{t}] N={d['N']} Gamma={d['Gamma']} ratio={float(d['ratio']):.3f} K={d['K']} maxT={d['maxT']}={float(d['maxT']):.4f} slack={slack}={float(slack):.4f} OK={d['maxT']<=d['K']}")

    high=[]          # records with ratio>=0.7
    violations=[]
    min_slack_high=None
    total_checked=0
    high_count=0

    # Strategy A: reject-sample high-Gamma. Try varied densities; keep ratio>=0.7.
    print("\n=== Reject-sampling high-Gamma (ratio>=0.7) and density~0.4, N=10..18 ===")
    # fewer trials at large N (brute maxcut 2^(N-1) per graph)
    trials_by_N={10:8000,11:8000,12:6000,13:5000,14:4000,15:3000,16:2000,17:1200,18:700}
    for N in range(10,19):
        Ntrials_per_N=trials_by_N[N]
        kept=0; viol_N=0; worst_slack_N=None
        for it in range(Ntrials_per_N):
            # mix densities: emphasize ~0.4 (C5 extremal) plus a spread that yields high Gamma
            p=rng.choice([0.30,0.35,0.40,0.40,0.45,0.50,0.55])
            E=random_trifree(N,p,rng)
            if len(E)<N-1: continue
            d=check(N,E)
            if d is None: continue
            total_checked+=1
            ratio=d['ratio']
            slack=d['K']-d['maxT']
            if d['maxT']>d['K']:
                violations.append((N,E,d))
                viol_N+=1
            if ratio>=Fraction(7,10):
                high_count+=1; kept+=1
                high.append((N,float(ratio),slack,d['Gamma'],d['K'],d['maxT']))
                if min_slack_high is None or slack<min_slack_high[0]:
                    min_slack_high=(slack,N,d['Gamma'],d['K'],d['maxT'])
                if worst_slack_N is None or slack<worst_slack_N: worst_slack_N=slack
        ws = f"{float(worst_slack_N):.4f}" if worst_slack_N is not None else "n/a"
        print(f"  N={N}: kept(ratio>=0.7)={kept} viol={viol_N} worst_high_slack={ws}", flush=True)

    print(f"\n=== SUMMARY ===")
    print(f"total graphs checked (valid gamma-min cut): {total_checked}")
    print(f"high-Gamma (ratio>=0.7) found: {high_count}")
    if min_slack_high:
        s,N,G,K,mT=min_slack_high
        print(f"min slack among high-Gamma: {s}={float(s):.5f}  at N={N} Gamma={G} K={K} maxT={mT}={float(mT):.4f}")
    print(f"violations (maxT>K): {len(violations)}")
    for (N,E,d) in violations[:20]:
        print(f"  !!! VIOLATION N={N} Gamma={d['Gamma']} K={d['K']} maxT={d['maxT']} E={E}")

    # show top high-Gamma ratio examples
    high.sort(key=lambda r:-r[1])
    print("\n top-10 highest-ratio high-Gamma samples (N, ratio, slack, Gamma, K, maxT):")
    for r in high[:10]:
        print(f"   N={r[0]} ratio={r[1]:.3f} slack={float(r[2]):.4f} Gamma={r[3]} K={r[4]} maxT={float(r[5]):.4f}")

if __name__=="__main__":
    main()
