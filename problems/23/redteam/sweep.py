import random, itertools, json
from harness import *
from ls2 import local_search

# For each N, sweep target_e across the WHOLE band, find max beta and record edge list.
def band_edges(N):
    lo=int(0.2486*N*N/2)+1
    hi=int(0.3197*N*N/2)
    return lo,hi

best_per_N={}
for N in [15,20,25]:
    lo,hi=band_edges(N)
    print(f"N={N} band e in [{lo},{hi}] N^2/25={N*N/25:.2f}")
    bestrec=None
    # focus on top of band (more edges => more beta typically); sample a few e values
    for te in range(hi, lo-1, -2):
        seeds = 12 if N<=20 else 6
        best=(-1,None)
        for s in range(seeds):
            r=local_search(N,te,seed=s,rounds=80,cands_per_round=25)
            if r and r[0]>best[0]: best=r
        if best[1] is None: continue
        b,E=best
        bb,ee,mc,d,tf=evalone(N,list(E))
        ratio=bb/(N*N/25)
        print(f"  te={te}: beta={bb} dens={d:.4f} ratio={ratio:.3f}")
        if bestrec is None or bb>bestrec[0]:
            bestrec=(bb,ee,d,ratio,sorted(E))
    best_per_N[N]=bestrec
    print(f"  -> N={N} BEST beta={bestrec[0]} e={bestrec[1]} dens={bestrec[2]:.4f} ratio={bestrec[3]:.3f}")

with open("best_per_N.json","w") as f:
    json.dump({str(k):{"beta":v[0],"e":v[1],"dens":v[2],"ratio":v[3],"edges":v[4]} for k,v in best_per_N.items()}, f)
print("SAVED best_per_N.json")
