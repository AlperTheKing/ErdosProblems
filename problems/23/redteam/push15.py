import random, json
from harness import *
from ls2 import local_search
# Push N=15 across band with many seeds; capture best edge list
best=(-1,None,None)
for te in range(38,30,-1):   # band N=15: e in [29,35] -> density (0.2756,0.3111)... extend
    if not in_band(15,te): continue
    for s in range(40):
        r=local_search(15,te,seed=s,rounds=120,cands_per_round=25)
        if r and r[0]>best[0]:
            best=(r[0],te,r[1])
b,te,E=best
bb,ee,mc,d,tf=evalone(15,list(E))
print(f"N=15 PUSH best beta={bb} e={ee} dens={d:.4f} tf={tf} band={in_band(15,ee)} ratio={bb/(225/25):.3f}")
print("EDGES",sorted([(min(u,v),max(u,v)) for u,v in E]))
json.dump({"N":15,"beta":bb,"e":ee,"dens":d,"edges":sorted([[min(u,v),max(u,v)] for u,v in E])}, open("push15.json","w"))
