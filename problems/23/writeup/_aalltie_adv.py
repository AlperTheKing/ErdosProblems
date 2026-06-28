"""DIRECT adversarial search for A-alltie violations (the ACTUAL claim, not the N/2 artifact):
   zero-mu B-edge uv, T(u)=N, and T(v)>0.
Search random triangle-free graphs N up to 26, plus Mycielskians, blowups, dense structured.
Report ANY violation immediately (exact). Also record, for each sat-zero-mu case, T(v) (should be 0).
Exact Fraction."""
import random, subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def rand_trifree(N, p, seed):
    rnd=random.Random(seed)
    adj=[set() for _ in range(N)]; E=[]
    pairs=[(i,j) for i in range(N) for j in range(i+1,N)]; rnd.shuffle(pairs)
    for i,j in pairs:
        if rnd.random()>p: continue
        if adj[i]&adj[j]: continue
        adj[i].add(j); adj[j].add(i); E.append((i,j))
    return E

def check(N,E):
    info=loads(N,E)
    if info is None: return 0,0,None
    T=info['T']; mu=mu_edges(info); n=info['n']
    cases=0; viol=0; wit=None
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        for (a,b) in [(u,v),(v,u)]:
            if T[a]==n:
                cases+=1
                if T[b]!=0:
                    viol+=1
                    if wit is None: wit=(a,b,str(T[a]),str(T[b]),n)
    return cases,viol,wit

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

if __name__=="__main__":
    print("=== DIRECT A-alltie adversarial search (zero-mu uv, T(u)=N, T(v)>0 = VIOLATION) ===")
    tot_cases=0; tot_viol=0; first=None
    for N in range(10,27):
        for p in [0.25,0.35,0.45,0.55]:
            for seed in range(80):
                E=rand_trifree(N,p,seed*97+N*131+int(p*1000))
                c,v,w=check(N,E)
                tot_cases+=c; tot_viol+=v
                if v>0 and first is None: first=(N,p,seed,w)
        print(f"  up to N={N}: A-alltie cases={tot_cases} VIOLATIONS={tot_viol}"+(f"  FIRST {first}" if first else ""), flush=True)
    # Mycielskian chain
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    cur=C5
    for k in range(4):
        info=loads(*cur)
        c,v,w=(check(*cur))
        print(f"  Myc^{k}(C5) N={cur[0]}: cases={c} viol={v} {w or ''}", flush=True)
        cur=mycielski(*cur)
        if cur[0]>60: break
    print(f"TOTAL random: cases={tot_cases} VIOLATIONS={tot_viol}")
