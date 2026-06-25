import random, json
from harness import *
from ls2 import local_search
best=(-1,None)
for te in [35,34,33]:  # top of N=15 band (density 0.31,0.302,0.293)
    for s in range(25):
        r=local_search(15,te,seed=s,rounds=70,cands_per_round=20)
        if r and r[0]>best[0]: best=(r[0],r[1])
b,E=best
E=sorted((min(u,v),max(u,v)) for u,v in E)
bb,ee,mc,d,tf=evalone(15,E)
print(f"N=15 best beta={bb} e={ee} dens={d:.4f} tf={tf} band={in_band(15,ee)} ratio={25*bb/225:.3f}")
print("E15",E)
json.dump({"N":15,"beta":bb,"e":ee,"dens":round(d,4),"edges":[[u,v] for u,v in E]},open("push15.json","w"))
