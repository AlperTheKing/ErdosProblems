"""Broaden the GCD exact gate: (a) odd-cycle blow-ups C_m[t] (the extremal family; expect tight, 0 fail)
   for m in {5,7,9,11}, t up to 4; (b) random triangle-free graphs N=12,14,16 over their gamma-min cuts."""
import random
from _gcd import run_gmin

def Cblow(m,t):
    n=m*t
    E=[(i*t+a, ((i+1)%m)*t+b) for i in range(m) for a in range(t) for b in range(t)]
    return n,E

def rand_tf(n, p, rng):
    adj=[set() for _ in range(n)]
    E=[]
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    rng.shuffle(pairs)
    for (i,j) in pairs:
        if rng.random()>p: continue
        if adj[i]&adj[j]: continue   # would create triangle
        adj[i].add(j); adj[j].add(i); E.append((i,j))
    return n,E

def test(nm,n,E):
    res=run_gmin(n,E)
    if not res: print(f"  {nm} N={n}: no bad edges / no conn maxcut",flush=True); return 0,0
    bad=sum(1 for r in res if not r[0]); mineig=min(r[1] for r in res)
    print(f"  {nm} N={n}: cuts={len(res)} BOTH-PSD-FAILS={bad} min-mineig(H)={mineig:+.5f}",flush=True)
    return len(res),bad

if __name__=="__main__":
    print("=== GCD stress: odd-cycle blow-ups + random triangle-free ===",flush=True)
    tot=0; fails=0
    for m in (5,7,9,11):
        for t in (1,2,3,4):
            if m*t>32: continue
            n,E=Cblow(m,t); c,b=test(f"C{m}[{t}]",n,E); tot+=c; fails+=b
    print(f"  blow-up subtotal: cuts={tot} FAILS={fails}",flush=True)
    rng=random.Random(12345)
    rtot=0; rfails=0; rg=0
    for n in (12,14,16):
        for p in (0.25,0.35,0.45):
            for rep in range(8):
                _,E=rand_tf(n,p,rng); rg+=1
                res=run_gmin(n,E)
                if not res: continue
                for r in res:
                    rtot+=1
                    if not r[0]: rfails+=1; print(f"  !!! RANDOM FAIL N={n} p={p} rep={rep} E={E}",flush=True)
    print(f"  random triangle-free: graphs={rg} cuts={rtot} BOTH-PSD-FAILS={rfails}",flush=True)
    print(f"=== TOTAL: blowup+random cuts={tot+rtot} FAILS={fails+rfails} ===",flush=True)
