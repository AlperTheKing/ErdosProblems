import pickle, numpy as np, random
from math import factorial
from fractions import Fraction as F
import prove_cert as pc
ns,dedge,rows,provtypes,v=pickle.load(open("cp_cache.pkl","rb"))
C=pc.load(9); states=C["states"]
val_idx=[i for i in range(len(rows)) if provtypes[i] not in ("deficit","deficit_pmap")]
print("row#321 provtype:", provtypes[321], "is in val_idx:", 321 in val_idx)
r321=np.asarray(rows[321])
def popcount(x): return bin(x).count("1")
def wl_inv(n,A,rounds=5):
    col=[popcount(A[v]) for v in range(n)]
    for _ in range(rounds):
        newc=[(col[v],tuple(sorted(col[u] for u in range(n) if (A[v]>>u)&1))) for v in range(n)]
        uniq={c:i for i,c in enumerate(sorted(set(newc)))}; col=[uniq[c] for c in newc]
    ep=tuple(sorted((min(col[u],col[v]),max(col[u],col[v])) for u in range(n) for v in range(u+1,n) if (A[u]>>v)&1))
    return (tuple(sorted(col)),ep)
def walkcounts(n,A):
    M=[[1 if (A[u]>>v)&1 else 0 for v in range(n)] for u in range(n)]
    def mm(X,Y): return [[sum(X[i][k]*Y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    A2=mm(M,M);A3=mm(A2,M);A4=mm(A3,M)
    return tuple(sorted((sum(A2[v]),sum(A3[v]),sum(A4[v]),A2[v][v],A3[v][v],A4[v][v]) for v in range(n)))
def key9(n,A): return (wl_inv(n,A),walkcounts(n,A))
keymap={key9(n,A):i for i,(n,A) in enumerate(states)}
def comps(total,parts):
    if parts==1: yield (total,);return
    for f in range(total+1):
        for rest in comps(total-f,parts-1): yield (f,)+rest
def profile9(ntemplate,Tadj,vw):
    x=np.zeros(ns)
    for counts in comps(9,ntemplate):
        wt=F(factorial(9))
        for c in counts: wt/=F(factorial(c))
        for p,c in enumerate(counts): wt*=vw[p]**c
        if wt==0: continue
        parts=[]
        for p,c in enumerate(counts): parts+=[p]*c
        B=[0]*9
        for u in range(9):
            for w in range(u+1,9):
                if parts[u]!=parts[w] and (Tadj[parts[u]]>>parts[w])&1: B[u]|=1<<w;B[w]|=1<<u
        idx=keymap[key9(9,B)]; x[idx]+=float(wt)
    return x
def cyc(m):
    A=[0]*m
    for i in range(m): A[i]|=1<<((i+1)%m);A[i]|=1<<((i-1)%m)
    return A
LO,HI=0.2486,0.3197
# exact uniform C5 profile
xC5=profile9(5,cyc(5),[F(1,5)]*5)
print("uniform C5: dedge.x=%.6f in-band=%s  row321.x=%.6e"%(dedge@xC5, LO<=dedge@xC5<=HI, r321@xC5))
# random C5 blowups -- report dedge and row321 and whether in band
random.seed(3)
for _ in range(8):
    raw=[random.randint(1,9) for _ in range(5)]; s=sum(raw); vw=[F(r,s) for r in raw]
    x=profile9(5,cyc(5),vw); ed=dedge@x; rv=r321@x
    print("C5 vw=%s dedge=%.5f in-band=%s row321=%.3e"%([str(z) for z in vw],ed,LO<=ed<=HI,rv))
