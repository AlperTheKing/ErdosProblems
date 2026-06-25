#!/usr/bin/env python3
"""GPT path (A) FIRST COMPUTATION: the (8,9) conditional-profile Gram PSD spectral audit.
P_R(A,B;q) = sum_J q_J * count_{J,R,A,B} / 90 (all ordered pairs, edge+nonedge). For a real graphon P_R >= 0 (PSD).
Report per-root lambda_min(P_R), lambdahat_R = lambda_min / Pr_q(R), and the headline min_R lambdahat_R, plus the
total negative spectral mass N_{8,9}(q). Audit the order-10 WITNESS q (pseudo-state) AND the i.i.d. laws of
C5/C7/Petersen (must be PSD up to numerical noise). If min_R lambdahat_R << 0 on the witness => the pseudo-state
violates conditional i.i.d. of the two profile draws => the (8,9) cuts are the right tightener.
"""
import numpy as np, pickle, time, sys
from math import factorial
import flag_engine as fe
from compute_U8 import canon_label

def build_PR_from_q(decomp, Rprof, nR, q):
    """P[rid] = dict-based matrix over profiles; returns list of (rid, profiles_list, Pmatrix, prq)."""
    # accumulate raw counts weighted by q
    acc=[dict() for _ in range(nR)]; prq=np.zeros(nR)
    sup=np.where(q>1e-13)[0]
    for jj in sup:
        qj=float(q[jj])
        for (rid,A,B) in decomp[jj]:
            acc[rid][(A,B)]=acc[rid].get((A,B),0.0)+qj/90.0
            prq[rid]+=qj/90.0
    out=[]
    for rid in range(nR):
        if not acc[rid]: continue
        profs=sorted(set(tuple(p) for p in Rprof[rid]) | set(a for (a,b) in acc[rid]) | set(b for (a,b) in acc[rid]))
        idx={p:i for i,p in enumerate(profs)}; m=len(profs)
        P=np.zeros((m,m))
        for (A,B),w in acc[rid].items():
            P[idx[tuple(A)],idx[tuple(B)]]+=w
        P=0.5*(P+P.T)
        out.append((rid,profs,P,prq[rid]))
    return out

def audit(q, decomp, Rprof, nR, label):
    PRs=build_PR_from_q(decomp,Rprof,nR,q)
    worst=1e9; worst_rid=-1; negmass=0.0; nneg=0
    for (rid,profs,P,pr) in PRs:
        ev=np.linalg.eigvalsh(P); lmin=float(ev[0])
        negmass += -ev[ev<0].sum()
        lh = lmin/pr if pr>1e-13 else 0.0
        if lh<worst: worst=lh; worst_rid=rid
        if lmin<-1e-12: nneg+=1
    print(f"  [{label}] roots active={len(PRs)}  min_R lambdahat = {worst:+.4e} (rid {worst_rid})  "
          f"N_8,9={negmass:.4e}  #roots with lambda_min<-1e-12: {nneg}",flush=True)
    return worst, negmass

# ---- i.i.d. law of a finite graph G via blow-up enumeration (for PSD validation) ----
def comps(total,parts):
    if parts==1: yield (total,); return
    for f in range(total+1):
        for rest in comps(total-f,parts-1): yield (f,)+rest

def blowup(counts,T):
    parts=[]
    for p,c in enumerate(counts): parts+=[p]*c
    n=len(parts); A=[0]*n
    for u in range(n):
        for w in range(u+1,n):
            if parts[u]!=parts[w] and (T[parts[u]]>>parts[w])&1: A[u]|=1<<w; A[w]|=1<<u
    return n,A

def PR_graph_iid(m,T,alpha):
    """build P_R for the i.i.d. law of blow-up template (m parts, adj T, weights alpha). Returns min_R lambdahat."""
    from fractions import Fraction as F
    acc={}; prq={}; memo={}
    for counts in comps(10,m):
        w=factorial(10)
        for c in counts: w//=factorial(c)
        wt=float(w)
        for p,c in enumerate(counts): wt*=float(alpha[p])**c
        if wt==0: continue
        n,A=blowup(counts,T)
        for i in range(10):
            Ai=A[i]
            for je in range(10):
                if i==je: continue
                anch=[v for v in range(10) if v!=i and v!=je]
                Radj=[0]*8
                for p in range(8):
                    for qd in range(p+1,8):
                        if (A[anch[p]]>>anch[qd])&1: Radj[p]|=1<<qd; Radj[qd]|=1<<p
                rk=tuple(Radj); mm=memo.get(rk)
                if mm is None: mm=canon_label(8,Radj); memo[rk]=mm
                key,inv=mm
                Aset=tuple(sorted(inv[p] for p,v in enumerate(anch) if (Ai>>v)&1))
                Bset=tuple(sorted(inv[p] for p,v in enumerate(anch) if (A[je]>>v)&1))
                acc.setdefault(key,{}); acc[key][(Aset,Bset)]=acc[key].get((Aset,Bset),0.0)+wt/90.0
                prq[key]=prq.get(key,0.0)+wt/90.0
    worst=1e9
    for key,d in acc.items():
        profs=sorted(set(a for (a,b) in d)|set(b for (a,b) in d)); idx={p:i for i,p in enumerate(profs)}
        P=np.zeros((len(profs),len(profs)))
        for (A,B),w in d.items(): P[idx[A],idx[B]]+=w
        P=0.5*(P+P.T); lmin=float(np.linalg.eigvalsh(P)[0]); lh=lmin/prq[key] if prq[key]>1e-13 else 0
        worst=min(worst,lh)
    return worst

def cyc(m):
    A=[0]*m
    for i in range(m): A[i]|=1<<((i+1)%m); A[i]|=1<<((i-1)%m)
    return A
def petersen():
    A=[0]*10
    def e(u,v): A[u]|=1<<v; A[v]|=1<<u
    for i in range(5): e(i,(i+1)%5); e(5+i,5+((i+2)%5)); e(i,5+i)
    return A

def main():
    D=pickle.load(open("u8_decomp_all.pkl","rb")); decomp=D["decomp"]; nR=D["nR"]; Rprof=D["Rprofiles"]
    print(f"loaded all-pairs decomp: nR={nR}",flush=True)
    wit=np.load("witness.npz",allow_pickle=True); qw=wit["q"]
    print("=== WITNESS q (pseudo-state) ===",flush=True)
    audit(qw, decomp, Rprof, nR, "witness")
    print("=== validation: real-graph i.i.d. laws (must be PSD, min_R lambdahat ~ 0) ===",flush=True)
    from fractions import Fraction as F
    for (name,m,T) in [("C5",5,cyc(5)),("C7",7,cyc(7)),("Petersen",10,petersen())]:
        t0=time.time(); w=PR_graph_iid(m,T,[F(1,m)]*m)
        print(f"  [{name}] min_R lambdahat = {w:+.4e}  [{time.time()-t0:.0f}s]",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
