import json
from harness import *

cands=[]
def add(desc,N,edges):
    edges=[(min(u,v),max(u,v)) for u,v in edges]
    edges=sorted(set(edges))
    b,e,mc,d,tf=evalone(N,edges)
    cands.append({"description":desc,"N":N,"edges":[[u,v] for u,v in edges],
                  "claimed_beta":b,"claimed_density":round(d,4),
                  "maxcut":mc,"tri_free":tf,"ratio_to_Nsq25":round(b/(N*N/25),3),
                  "in_band":in_band(N,e)})

# 1. Petersen (N=10, e=15, density 0.30) beta=3
pet=[(0,1),(1,2),(2,3),(3,4),(4,0),(5,7),(7,9),(9,6),(6,8),(8,5),(0,5),(1,6),(2,7),(3,8),(4,9)]
add("Petersen graph (Kneser K(5,2)), girth 5, density 0.30 band; beta=3 vs N^2/25=4",10,pet)

# 2. Petersen[2] blow-up (N=20, e=60, density 0.30) beta=12
def blowup(N,edges,t):
    NN=N*t; ee=[]
    for u,v in edges:
        for a in range(t):
            for c in range(t):
                ee.append((u*t+a,v*t+c))
    return NN,ee
N,e=blowup(10,pet,2); add("Petersen[2] balanced blow-up, density 0.30; beta=12 vs N^2/25=16",N,e)

# 3. circulant n=20 S={1,3,8} (e=60, density 0.30) beta=12
def circulant(n,S):
    edges=set()
    for i in range(n):
        for s in S:
            j=(i+s)%n; edges.add((min(i,j),max(i,j)))
    return n,list(edges)
N,e=circulant(20,[1,3,8]); add("Circulant C_20(1,3,8), triangle-free, density 0.30; beta=12 vs N^2/25=16",N,e)

# 4. circulant n=22 S={1,3,8} beta=14 density 0.2727
N,e=circulant(22,[1,3,8]); add("Circulant C_22(1,3,8), density 0.273; beta=14 vs N^2/25=19.36",N,e)

# 5. circulant n=24 S={1,4,11} beta=16 density 0.25
N,e=circulant(24,[1,4,11]); add("Circulant C_24(1,4,11), density 0.25; beta=16 vs N^2/25=23.04",N,e)

with open("named_candidates.json","w") as f: json.dump(cands,f,indent=1)
for c in cands:
    print(c["description"][:55], "| N",c["N"],"e",len(c["edges"]),"beta",c["claimed_beta"],"dens",c["claimed_density"],"tf",c["tri_free"],"ratio",c["ratio_to_Nsq25"])
print("saved named_candidates.json")
