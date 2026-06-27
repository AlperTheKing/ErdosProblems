#!/usr/bin/env python3
"""Fast random near-tight scan N=13..16 (maxcut_all is 2^(n-1), tractable to n=16).
Bias generation toward C5-blowup-like structure (5 random color classes in a 5-cycle pattern)
to actually reach high Gamma/N^2. Log any tight/near-tight no-peel."""
import random, time
from peel_check import check_instance, is_triangle_free

random.seed(7)

def c5_like(n):
    """Assign each vertex a class in 0..4; edges only between consecutive classes (mod 5),
    added with prob p. This is triangle-free (C5 is triangle-free, blow-up preserves it) and
    can reach Gamma near N^2 when classes are balanced and links dense."""
    cls=[random.randint(0,4) for _ in range(n)]
    p=random.choice([0.6,0.8,1.0])
    adj=[set() for _ in range(n)]
    for u in range(n):
        for v in range(u+1,n):
            if (cls[u]-cls[v])%5 in (1,4):
                if random.random()<=p:
                    adj[u].add(v); adj[v].add(u)
    return adj

def c7_like(n):
    cls=[random.randint(0,6) for _ in range(n)]
    p=random.choice([0.7,1.0])
    adj=[set() for _ in range(n)]
    for u in range(n):
        for v in range(u+1,n):
            if (cls[u]-cls[v])%7 in (1,6):
                if random.random()<=p:
                    adj[u].add(v); adj[v].add(u)
    return adj

def main():
    for n in range(13,17):
        t0=time.time(); cnt=0; maxr=0.0; tight=0; near=0; nopeel=0; tight_nopeel=0
        hi_nopeel=[]; tight_examples=[]
        trials=2500
        for it in range(trials):
            r=random.random()
            adj = c5_like(n) if r<0.7 else c7_like(n)
            if not is_triangle_free(n,adj): continue
            res=check_instance(n,adj)
            if not (res.get("ok") and res.get("B_connected") and res.get("m",0)>=2 and res.get("gamma") is not None):
                continue
            cnt+=1; ratio=res["gamma"]/res["n2"]
            if ratio>maxr: maxr=ratio
            if ratio>=0.9: near+=1
            if res["tight"]:
                tight+=1
                if len(tight_examples)<8:
                    edges=[(u,v) for u in range(n) for v in sorted(adj[u]) if v>u]
                    tight_examples.append((res["m"],res["gamma"],res["has_safe_peel"],edges))
            if res["has_safe_peel"] is False:
                nopeel+=1
                if res["tight"]: tight_nopeel+=1
                if ratio>=0.9 and len(hi_nopeel)<6:
                    edges=[(u,v) for u in range(n) for v in sorted(adj[u]) if v>u]
                    hi_nopeel.append((res["m"],res["gamma"],res["n2"],ratio,res["tight"],edges))
        print(f"[N={n}] trials={trials} valid={cnt} max_ratio={maxr:.5f} tight:{tight} "
              f"ratio>=0.9:{near} nopeel:{nopeel} TIGHT_nopeel:{tight_nopeel} t={time.time()-t0:.1f}s", flush=True)
        for (m,g,sp,edges) in tight_examples:
            mark='' if sp else '  <-- TIGHT NO-PEEL OBSTRUCTION'
            print(f"   TIGHT N={n} m={m} gamma={g} safe_peel={sp}{mark}", flush=True)
            if not sp: print(f"      edges={edges}", flush=True)
        for (m,g,n2,ratio,t_,edges) in hi_nopeel:
            print(f"   HI-NOPEEL N={n} m={m} gamma={g} n2={n2} ratio={ratio:.4f} tight={t_}", flush=True)

if __name__=="__main__":
    main()
