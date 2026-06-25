"""Test: every validity (moment/localizer) row must be >= 0 at REAL order-9 graphon profiles.
If any validity row goes NEGATIVE at a real profile => that row is NOT a valid graphon inequality => could
wrongly exclude reality => unsound (eta too small)."""
import pickle, numpy as np, random
from math import factorial
from fractions import Fraction as F
import prove_cert as pc

ns,dedge,rows,provtypes,v=pickle.load(open("cp_cache.pkl","rb"))
C=pc.load(9); states=C["states"]; assert len(states)==ns
val_idx=[i for i in range(len(rows)) if provtypes[i] not in ("deficit","deficit_pmap")]
R=np.array([np.asarray(rows[i]) for i in val_idx])

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
assert len(keymap)==ns

def comps(total,parts):
    if parts==1: yield (total,); return
    for f in range(total+1):
        for rest in comps(total-f,parts-1): yield (f,)+rest

def profile9_blowup(ntemplate,Tadj,vw):
    x=np.zeros(ns)
    for counts in comps(9,ntemplate):
        wt=F(factorial(9))
        for c in counts: wt/=F(factorial(c))
        for p,c in enumerate(counts): wt*=vw[p]**c
        if wt==0: continue
        parts=[]
        for p,c in enumerate(counts): parts+=[p]*c
        BN=9; B=[0]*BN
        for u in range(BN):
            for w in range(u+1,BN):
                if parts[u]!=parts[w] and (Tadj[parts[u]]>>parts[w])&1: B[u]|=1<<w; B[w]|=1<<u
        idx=keymap.get(key9(9,B),-1)
        assert idx>=0, "order-9 induced state not found"
        x[idx]+=float(wt)
    return x

def cyc(m):
    A=[0]*m
    for i in range(m): A[i]|=1<<((i+1)%m); A[i]|=1<<((i-1)%m)
    return A

templates=[("C5",5,cyc(5)),("C7",7,cyc(7)),("C9",9,cyc(9))]
random.seed(3)
worst=1e9; worstinfo=None; nneg=0; ntot=0
for (nm,n,A) in templates:
    trials=[[F(1,n)]*n]
    for _ in range(15):
        raw=[random.randint(1,9) for _ in range(n)]; s=sum(raw); trials.append([F(r,s) for r in raw])
    for vw in trials:
        x=profile9_blowup(n,A,vw)
        # sanity: profile sums to 1
        assert abs(x.sum()-1.0)<1e-9, x.sum()
        vals=R@x
        mn=vals.min(); ntot+=1
        if mn<-1e-9:
            nneg+=1
            bad=int(np.argmin(vals))
            print("NEG VALIDITY ROW template %s row#%d (%s) val=%.3e"%(nm,val_idx[bad],provtypes[val_idx[bad]],mn),flush=True)
        if mn<worst: worst=mn; worstinfo=(nm,provtypes[val_idx[int(np.argmin(vals))]])
print("validity-row real-graphon check: %d profiles, %d negative; worst min row-val=%.4e (%s)"%(ntot,nneg,worst,str(worstinfo)),flush=True)
# also check band: dedge.x in [LO,HI]? not required (these are off-band templates), just report edge density
print("DONE",flush=True)
