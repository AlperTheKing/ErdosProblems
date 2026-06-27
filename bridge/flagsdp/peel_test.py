#!/usr/bin/env python3
"""GPT Pro's GEODESIC ODD-CYCLE PEELING test for the Connected-B Gamma Lemma (theta regime).
For a bad edge uv in M, take a shortest B-geodesic P (u..v); C = V(P) (the odd cycle P+uv, |C|=ell=d_B+1).
Peel C; recompute B', M', Gamma'. ACCEPT the peel if:
  (1) G-C still cut-dominated: for all S subset V', delta_{M'}(S) <= delta_{B'}(S);
  (2) every remaining bad edge in a single B'-component;
  (3) L(C)=Gamma-Gamma' <= 2|C|N - |C|^2.
Target on C5[4] (=GPT 'c5paths20', N=20, Gamma=400): a 5-peel gives (20,400)->(15,225), L=175.
LEMMA being tested: every connected-B theta instance with Gamma>=N^2 has a SAFE peel."""
from collections import deque
import itertools
from ear_invariant import C5_blowup, c5_paths, theta_witness, odd_cycle, evaluate, bdist_graph

def Bgraph(n, adj, side):
    adjB=[set() for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            if v>u and side[u]!=side[v]: adjB[u].add(v); adjB[v].add(u)
    return adjB

def shortest_path(n, adjB, s, t):
    par={s:None}; q=deque([s])
    while q:
        u=q.popleft()
        if u==t: break
        for w in adjB[u]:
            if w not in par: par[w]=u; q.append(w)
    if t not in par: return None
    path=[]; x=t
    while x is not None: path.append(x); x=par[x]
    return path[::-1]

def components(n, adjB, keep):
    seen=set(); comps=[]
    for s in keep:
        if s in seen: continue
        comp=set(); q=deque([s]); seen.add(s)
        while q:
            u=q.popleft(); comp.add(u)
            for w in adjB[u]:
                if w in keep and w not in seen: seen.add(w); q.append(w)
        comps.append(comp)
    return comps

def cut_dom(keep, adjB, M):
    """check forall S subset keep: delta_M(S) <= delta_B(S). Brute (2^|keep|). keep=sorted list."""
    K=sorted(keep); kset=set(K); idx={v:i for i,v in enumerate(K)}; m=len(K)
    Bedges=[(u,v) for u in K for v in adjB[u] if v>u and v in kset]
    Medges=[(u,v) for (u,v) in M if u in kset and v in kset]
    if m>18: return None  # too big to brute
    for mask in range(1<<m):
        dM=sum(1 for (u,v) in Medges if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        dB=sum(1 for (u,v) in Bedges if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        if dM>dB: return False
    return True

def peel_test(name, builder):
    n, adj, side, M, *_ = builder()
    _, Gamma, ells, adjB = evaluate(n, adj, side, M)
    NN=n
    print(f"\n=== {name}: N={NN} m={len(M)} Gamma={Gamma} N^2={NN*NN} (tight={Gamma==NN*NN}) ells={sorted(e for e in ells if e)} ===",flush=True)
    found=[]
    for (u,v) in M:
        P=shortest_path(n, adjB, u, v)
        if P is None: continue
        C=set(P); s=len(C)
        keep=[x for x in range(n) if x not in C]
        if not keep: continue
        # rebuild restricted
        Mp=[(a,b) for (a,b) in M if a in keep and b in keep]
        # recompute Gamma' via B-distances in B' (component-aware: bdist on adjB restricted)
        adjBp=[set(w for w in adjB[x] if w not in C) for x in range(n)]
        Gp=0; okdist=True
        for (a,b) in Mp:
            d=bdist_graph(n, adjBp, a)[b]
            if d<0: okdist=False; break
            Gp += (d+1)**2
        if not okdist:
            # a bad edge got disconnected in B' -> condition (2) fails for this peel
            continue
        comps=components(n, adjBp, set(keep))
        # cond (2): every remaining bad edge inside one component
        badspan=all(any(a in cc and b in cc for cc in comps) for (a,b) in Mp)
        cd=cut_dom(keep, adjBp, Mp)
        L=Gamma-Gp; bound=2*s*NN - s*s
        accept = (cd is True) and badspan and (L<=bound)
        found.append((u,v,s,Gp,L,bound,cd,badspan,accept))
        if accept or s<=6:
            print(f"  peel bad-edge({u},{v}) s={s}: Gamma'={Gp} (N'={NN-s}, N'^2={(NN-s)**2}) L={L} <= 2sN-s^2={bound}? {L<=bound} | CD={cd} badspan={badspan} => {'ACCEPT' if accept else 'reject'}",flush=True)
    anyacc=any(f[-1] for f in found)
    print(f"  >>> {name}: safe peel EXISTS? {anyacc}",flush=True)
    return anyacc

def C5q(q):
    """CORRECT extremal C5[q]: parts P0..P4 size q, P_i ~ P_{i+1} complete bipartite. Max cut sides
    [0,1,0,1,0] => the ONLY mono seam is P4-P0 (q^2 bad edges); all other 4 seams in B. Each bad edge
    u in P4, v in P0: d_B(u,v)=4 (path P4-P3-P2-P1-P0), ell=5 => Gamma = q^2*25 = 25q^2 = N^2 (TIGHT)."""
    n=5*q
    def vid(i,j): return i*q+j
    side=[0]*n
    for i in range(5):
        for j in range(q): side[vid(i,j)] = (0 if i in (0,2,4) else 1)
    adj=[set() for _ in range(n)]
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
    M=[(vid(4,a),vid(0,b)) for a in range(q) for b in range(q)]
    return n, adj, side, M, {}

if __name__=="__main__":
    peel_test("C5[4] EXTREMAL (GPT c5paths20, Gamma=400=N^2)", lambda: C5q(4))
    peel_test("C5[3] EXTREMAL", lambda: C5q(3))
    peel_test("C5[5] EXTREMAL", lambda: C5q(5))
    peel_test("odd_cycle C7 (other tight family)", lambda: odd_cycle(7))
    peel_test("odd_cycle C9", lambda: odd_cycle(9))
    print("\nDONE",flush=True)
