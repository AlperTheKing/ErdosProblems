import json
from fastbeta import min5drop_fast
def es(E): return sorted(set(tuple(sorted((min(u,v),max(u,v)))) for u,v in E))
def tf(n,E):
    adj=[0]*n
    for u,v in E: adj[u]|=1<<v; adj[v]|=1<<u
    for u,v in E:
        if adj[u]&adj[v]: return False
    return True
def stat(n,E):
    E=es(E); assert tf(n,E),"not TF"
    md,S,bG=min5drop_fast(n,E); return E,bG,md

C={}
# 1. Mycielskian(C7) - high odd girth, 15 vtx, random search never hits
M=[]
for i in range(7): M.append((i,(i+1)%7))
for i in range(7): M.append((7+i,(i+1)%7)); M.append((7+i,(i-1)%7))
for i in range(7): M.append((14,7+i))
C["Mycielskian_C7"]=(15,M)

# 2. GP(7,2)+apex(0,2,4)
def gp(m,k,ap):
    E=[]
    for i in range(m): E+=[(i,(i+1)%m),(i,m+i),(m+i,m+(i+k)%m)]
    for c in ap: E.append((2*m,c))
    return E
C["GP72_apex024"]=(15,gp(7,2,[0,2,4]))
# 3. GP(7,3)+apex
C["GP73_apex035"]=(15,gp(7,3,[0,3,5]))

# 4. C5[3] minus perfect matching between consecutive parts (diagonal removed)
E=[]
for i in range(5):
    j=(i+1)%5
    for a in range(3):
        for b in range(3):
            if a==b: continue
            E.append((3*i+a,3*j+b))
C["C5b3_minus_matching"]=(15,E)

# 5. C15 cycle + chords step4 (odd girth, vertex-transitive, "spread")
E=[]
for i in range(15): E.append((i,(i+1)%15))
for i in range(15): E.append((i,(i+4)%15))
C["C15_plus_chord4"]=(15,E)

# 6. Cayley Z15 [2,3] (4-regular, vtx-transitive)
E=[]
for v in range(15):
    for s in [2,3]: E.append((v,(v+s)%15))
C["Cayley_Z15_2_3"]=(15,E)

# 7. C5[3] twist layer 4 (beta=6 dense, breaks C5-transversal symmetry)
E=[]
for i in range(5):
    j=(i+1)%5
    for a in range(3):
        for b in range(3):
            if i==4 and a==b: continue
            E.append((3*i+a,3*j+b))
C["C5b3_twist_layer4"]=(15,E)

# 8. Mycielskian(C5)=Grotzsch + C4 pad (chromatic-4 fragment)
G=[]
for i in range(5): G.append((i,(i+1)%5))
for i in range(5): G.append((5+i,(i+1)%5)); G.append((5+i,(i-1)%5))
for i in range(5): G.append((10,5+i))
G+=[(11,12),(12,13),(13,14),(14,11)]
C["Grotzsch_plus_C4"]=(15,G)

# 9. EXTREMAL reference: C5[3] itself (tight at thr)
E=[]
for i in range(5):
    j=(i+1)%5
    for a in range(3):
        for b in range(3): E.append((3*i+a,3*j+b))
C["C5_blowup_3_EXTREMAL"]=(15,E)

out=[]
for name,(n,E) in C.items():
    Ee,bG,md=stat(n,E)
    print(f"{name}: n={n} m={len(Ee)} beta={bG} min5drop={md} (thr={2*(n//5)-1})")
    out.append((name,n,Ee,bG,md))
# dump json edge lists for the report
with open("final_cands.json","w") as f:
    json.dump([{"name":nm,"n":n,"edges":[list(e) for e in E],"beta":b,"min5drop":m} for nm,n,E,b,m in out],f)
print("saved final_cands.json")
