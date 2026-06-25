#!/usr/bin/env python3
"""Adversarial sweep: test d_mono(W) <= U_8(W) on ALL triangle-free graphs n<=7 (uniform graphon),
   plus random weighted blow-ups of small triangle-free templates."""
import itertools, time, random
from fractions import Fraction as F
from math import factorial
from compute_U8 import canon_label, maxcut, popcount
import flag_engine as fe

_memo={}
def canon_memo(Radj):
    rk=tuple(Radj); v=_memo.get(rk)
    if v is None: v=canon_label(8,Radj); _memo[rk]=v
    return v

def comps(total, parts):
    if parts==1: yield (total,); return
    for f in range(total+1):
        for rest in comps(total-f,parts-1): yield (f,)+rest

def U8_from_graph_weighted(n, A, vw):
    W={}
    for counts in comps(10,n):
        wt=F(factorial(10))
        for c in counts: wt/=F(factorial(c))
        for p,c in enumerate(counts): wt*=vw[p]**c
        if wt==0: continue
        parts=[]
        for p,c in enumerate(counts): parts+=[p]*c
        BN=10; B=[0]*BN
        for u in range(BN):
            for w in range(u+1,BN):
                if parts[u]!=parts[w] and (A[parts[u]]>>parts[w])&1: B[u]|=1<<w; B[w]|=1<<u
        for i in range(10):
            Bi=B[i]
            for j in range(10):
                if i!=j and (Bi>>j)&1:
                    anch=[v for v in range(10) if v!=i and v!=j]
                    idx={v:p for p,v in enumerate(anch)}
                    Radj=[0]*8
                    for p in range(8):
                        for qd in range(p+1,8):
                            if (B[anch[p]]>>anch[qd])&1: Radj[p]|=1<<qd; Radj[qd]|=1<<p
                    key,inv=canon_memo(Radj)
                    Aset=frozenset(inv[idx[v]] for v in anch if (B[i]>>v)&1)
                    Bset=frozenset(inv[idx[v]] for v in anch if (B[j]>>v)&1)
                    W.setdefault(key,{}); W[key][(Aset,Bset)]=W[key].get((Aset,Bset),F(0))+wt/90
    U8=F(0)
    for key,ed in W.items():
        offdiag={}; sl=F(0); profiles=set()
        for (Aset,Bset),w in ed.items():
            profiles.add(Aset); profiles.add(Bset)
            if Aset==Bset: sl+=w
            else:
                a,b=tuple(sorted([Aset,Bset],key=lambda s:(len(s),sorted(s))))
                offdiag[(a,b)]=offdiag.get((a,b),F(0))+w
        offf={k:float(v) for k,v in offdiag.items()}
        mc=maxcut(list(profiles),offf) if offf else 0.0
        # subtract the float maxcut as a tight rational approx (we only need U8 numerically here)
        U8 += sl + (sum(offdiag.values())-F(mc).limit_denominator(10**12))
    return float(U8)

def dmono_weighted(n, A, vw):
    """min over block 2-colorings of monochromatic ordered-edge mass (graphon d_mono)."""
    best=None
    for mask in range(1<<n):
        m=F(0)
        for u in range(n):
            for v in range(n):
                if u!=v and (A[u]>>v)&1 and ((mask>>u)&1)==((mask>>v)&1):
                    m+=vw[u]*vw[v]
        if best is None or m<best: best=m
    return float(best)

def tri_free(n,A):
    for u in range(n):
        for v in range(u+1,n):
            if (A[u]>>v)&1 and (A[u]&A[v]): return False
    return True

def main():
    random.seed(1)
    worst=1e9; worstdesc=None; nviol=0; ntest=0
    for n in [5,6,7]:
        for (nn,Aadj) in fe.enumerate_graphs(n, triangle_free=True):
            vw=[F(1,nn)]*nn
            dm=dmono_weighted(nn,Aadj,vw)
            if dm<=1e-15: continue
            U8=U8_from_graph_weighted(nn,Aadj,vw)
            ntest+=1
            gap=U8-dm
            if gap<worst: worst=gap; worstdesc=("uniform",nn,Aadj)
            if gap< -1e-9:
                nviol+=1
                print("VIOLATION uniform n=%d A=%s d_mono=%.6e U8=%.6e gap=%.3e"%(nn,Aadj,dm,U8,gap),flush=True)
    print("uniform sweep: %d non-bipartite tested, %d violations, worst gap=%.4e"%(ntest,nviol,worst),flush=True)
    from validate_dmono_le_u8 import cyc, petersen
    C5C5=[0]*10
    for i in range(5):
        C5C5[i]|=1<<((i+1)%5); C5C5[(i+1)%5]|=1<<i
        C5C5[5+i]|=1<<(5+(i+1)%5); C5C5[5+(i+1)%5]|=1<<(5+i)
    templates=[("C5",5,cyc(5)),("C7",7,cyc(7)),("Petersen",10,petersen()),("C5uC5",10,C5C5)]
    for (nm,n,A) in templates:
        for trial in range(15):
            raw=[random.randint(1,9) for _ in range(n)]
            s=sum(raw); vw=[F(r,s) for r in raw]
            dm=dmono_weighted(n,A,vw)
            if dm<=1e-15: continue
            U8=U8_from_graph_weighted(n,A,vw)
            gap=U8-dm; ntest+=1
            if gap<worst: worst=gap; worstdesc=(nm,"random",[str(x) for x in vw])
            if gap< -1e-9:
                nviol+=1
                print("VIOLATION %s weights=%s d_mono=%.6e U8=%.6e gap=%.3e"%(nm,[str(x) for x in vw],dm,U8,gap),flush=True)
    print("\nTOTAL tested=%d violations=%d WORST gap (U8-d_mono)=%.4e"%(ntest,nviol,worst),flush=True)
    print("worst case desc: %s"%(str(worstdesc)),flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
