"""Separate validity-row real-graphon nonneg check for moment-only vs localizer rows."""
import pickle, numpy as np, random
from math import factorial
from fractions import Fraction as F
import prove_cert as pc
ns,dedge,rows,provtypes,v=pickle.load(open("cp_cache.pkl","rb"))
C=pc.load(9); states=C["states"]
mom_idx=[i for i in range(len(rows)) if provtypes[i]=="moment"]
loc_idx=[i for i in range(len(rows)) if provtypes[i]=="localizer"]
print("moment rows:",len(mom_idx),"localizer rows:",len(loc_idx),"loc indices:",loc_idx)
Rmom=np.array([np.asarray(rows[i]) for i in mom_idx])
Rloc=np.array([np.asarray(rows[i]) for i in loc_idx])
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
    if parts==1: yield (total,); return
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
templates=[("C5",5,cyc(5)),("C7",7,cyc(7)),("C9",9,cyc(9))]
random.seed(11)
mom_worst=1e9; loc_worst=1e9; mom_neg_inband=0; loc_neg_inband=0; ninband=0
mom_worst_inband=1e9
for (nm,n,A) in templates:
    trials=[[F(1,n)]*n]
    for _ in range(40):
        raw=[random.randint(1,9) for _ in range(n)]; s=sum(raw); trials.append([F(r,s) for r in raw])
    for vw in trials:
        x=profile9(n,A,vw); ed=dedge@x
        inband = LO<=ed<=HI
        mn_m=(Rmom@x).min(); mn_l=(Rloc@x).min()
        mom_worst=min(mom_worst,mn_m); loc_worst=min(loc_worst,mn_l)
        if inband:
            ninband+=1
            mom_worst_inband=min(mom_worst_inband,mn_m)
            if mn_m<-1e-9: mom_neg_inband+=1
            if mn_l<-1e-9: loc_neg_inband+=1
print("MOMENT rows: worst min-val(all)=%.4e ; worst in-band=%.4e ; in-band negatives=%d/%d"%(mom_worst,mom_worst_inband,mom_neg_inband,ninband))
print("LOCALIZER rows: worst min-val(all)=%.4e ; in-band negatives=%d/%d"%(loc_worst,loc_neg_inband,ninband))
