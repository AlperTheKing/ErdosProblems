#!/usr/bin/env python3
"""STRATEGY E -- the FINAL candidate identity and its tightness analysis.

After calibration, the genuinely-quadratic, non-self-tight candidate is the
WINDING-CAUCHY double count via the cycle-degree inequality applied to a
SINGLE GLOBAL closed walk that visits every bad-edge cycle.

Set-up.  Connected B, max cut. For each bad edge e pick shortest odd cycle C_e
(length ell_e). Consider the MULTISET UNION W = sum_e [C_e] of these cycles as
a degree-weighted closed-walk system. Define on each vertex v:
    lambda_v := #{e : v in C_e}    (the load).
Two exact bookkeeping identities (no inequality yet):
    (A)  sum_v lambda_v       = sum_e ell_e        =: S1
    (B)  sum_v d(v) lambda_v  = sum_e D_e          (D_e=sum_{v in C_e} d(v))

Cycle-degree (6) per cycle:  D_e <= N (ell_e - 1)/2.            (the only inequality)
Summing:    sum_e D_e  <=  (N/2) sum_e (ell_e - 1) = (N/2)(S1 - beta).   (I)

Now the QUADRATIC step.  We want Gamma = sum ell_e^2. The trick that produces a
SQUARE: weight each cycle by ell_e itself (not 1) -- i.e. use the load
    mu_v := sum_{e : v in C_e} ell_e .
Then  sum_v mu_v = sum_e ell_e^2 = Gamma   (each cycle contributes ell_e to each
of its ell_e vertices => ell_e^2 total).  And we bound sum_v mu_v by a Cauchy
against the degrees / the budget N.  We TEST which budget makes it tight at C5[q].

We compute:
  Gamma = sum_v mu_v,
  P := sum_v mu_v^2,   maxmu,
  and the candidate Cauchy bound  Gamma^2 = (sum mu_v)^2 <= N * P    (Cauchy with 1)
  i.e. Gamma <= sqrt(N*P).  Tight when mu_v constant.  On C5[q] mu_v should be
  constant (= 5q by symmetry) => Gamma = N * 5q? check: N*5q=5q*5q=25q^2=N^2. YES.
So the candidate IS:  Gamma <= max_v mu_v * (#v with mu>0)  and the SHARP form
  Gamma  <=  N * max_v mu_v / 5  ??  -- we measure max_v mu_v vs N.
"""
import math
import numpy as np
from collections import deque
from strat_e_probe import adjset, maxcut, petersen, c5n, gpt_k23, theta46
import flag_engine as fe


def cut_structure(N, adj):
    mc, side = maxcut(N, adj)
    adjB=[set() for _ in range(N)]; M=[]
    for u in range(N):
        for v in adj[u]:
            if v>u:
                if side[u]!=side[v]: adjB[u].add(v); adjB[v].add(u)
                else: M.append((u,v))
    return side, adjB, M


def bfs_dist(N, adjB, src):
    d=[-1]*N; d[src]=0; dq=deque([src])
    while dq:
        x=dq.popleft()
        for w in adjB[x]:
            if d[w]<0: d[w]=d[x]+1; dq.append(w)
    return d


def shortest_path(N, adjB, u, v):
    prev={u:None}; dq=deque([u])
    while dq:
        x=dq.popleft()
        if x==v: break
        for w in adjB[x]:
            if w not in prev: prev[w]=x; dq.append(w)
    path=[]; cur=v
    while cur is not None: path.append(cur); cur=prev[cur]
    return path


def mu_analysis(N, adj):
    side, adjB, M = cut_structure(N, adj)
    deg=[len(adj[v]) for v in range(N)]
    mu=[0.0]*N      # sum of ell over cycles through v
    lam=[0.0]*N     # count of cycles through v
    ells=[]
    for (u,v) in M:
        d=bfs_dist(N,adjB,u); ell=d[v]+1; ells.append(ell)
        path=shortest_path(N,adjB,u,v)
        for w in path:
            mu[w]+=ell; lam[w]+=1
    Gamma=sum(l*l for l in ells)
    assert abs(sum(mu)-Gamma)<1e-9, (sum(mu),Gamma)
    P=sum(x*x for x in mu)
    maxmu=max(mu) if mu else 0.0
    nnz=sum(1 for x in mu if x>0)
    cauchy=math.sqrt(N*P)   # Gamma<=sqrt(N*P)
    return Gamma, P, maxmu, nnz, cauchy, mu, ells


def run():
    def cycle(L):
        A=[0]*L
        for i in range(L):
            A[i]|=1<<((i+1)%L); A[(i+1)%L]|=1<<i
        return L,A
    named=[(*c5n(1),"C5[1]"),(*c5n(2),"C5[2]"),(*c5n(3),"C5[3]"),(*c5n(4),"C5[4]"),
           (*petersen(),"Petersen"),(*gpt_k23(),"K23-N13"),(*theta46(),"theta46"),
           (*cycle(5),"C5"),(*cycle(7),"C7"),(*cycle(9),"C9")]
    print("=== Strategy E final: mu-load, Cauchy sqrt(N*P), maxmu vs N ===", flush=True)
    print(f"{'name':10s} {'N':>3s} {'Gamma':>6s} {'P':>8s} {'maxmu':>6s} {'nnz':>4s} "
          f"{'sqrt(NP)':>8s} {'G<=sqrtNP':>9s} {'maxmu/N':>8s}", flush=True)
    for (N,A,label) in named:
        adj=adjset(N,A)
        Gamma,P,maxmu,nnz,cauchy,mu,ells=mu_analysis(N,adj)
        ok="OK" if Gamma<=cauchy+1e-6 else "FAIL"
        print(f"{label:10s} {N:>3d} {Gamma:>6.0f} {P:>8.1f} {maxmu:>6.1f} {nnz:>4d} "
              f"{cauchy:>8.2f} {ok:>9s} {maxmu/N:>8.3f}", flush=True)
    # Now exhaustive: does Gamma <= sqrt(N*P) hold (it's Cauchy, always true) and is it
    # TIGHT only at C5[q]? More importantly does sqrt(N*P) <= N^2 ? i.e. P <= N^3.
    print("\n=== Exhaustive connected-B N<=9: is P <= N^3 (=> Gamma<=sqrt(N*P)<=N^2)? ===", flush=True)
    for N in range(5,10):
        states=fe.enumerate_graphs(N, triangle_free=True)
        worst=0.0; wi=None; cnt=0; viol=0
        for (n,A) in states:
            adj=adjset(n,A)
            side,adjB,M=cut_structure(n,adj)
            if not M: continue
            seen=[False]*n; dq=deque([0]); seen[0]=True; nc=1
            while dq:
                x=dq.popleft()
                for w in adjB[x]:
                    if not seen[w]: seen[w]=True; nc+=1; dq.append(w)
            if nc!=n: continue
            Gamma,P,maxmu,nnz,cauchy,mu,ells=mu_analysis(n,adj)
            cnt+=1
            r=P/(n**3)
            if r>worst: worst=r; wi=(n,Gamma,round(P,1))
            if P>n**3+1e-6: viol+=1
        print(f"  N={N}: connB={cnt}, max P/N^3={worst:.4f} viol(P>N^3)={viol} at {wi}", flush=True)


if __name__ == "__main__":
    run()
