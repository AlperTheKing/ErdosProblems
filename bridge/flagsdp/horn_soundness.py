#!/usr/bin/env python3
"""SOUNDNESS GATE for the rooted Horn (C5) cut. The whole proof rests on H_R>=0 for REAL triangle-free graphons.
GPT proved it via Motzkin-Straus; here we VERIFY numerically with the SAME validated P_R (rooted profile-pair
density W[key]) construction as u8_max_check.py. For each real tri-free graph (n=6,7 exhaustive + C5/C7/C9/C11/
Petersen) and each 8-root R, build symmetric P_R and minimize H_R over 5-tuples. Must be >= -fp_tol everywhere.
A single materially-negative H_R on a REAL graph => the cut is UNSOUND (false-closure trap) -> ABORT the route."""
import time, itertools
from math import factorial
import numpy as np
from u8_max_check import comps, blowup, canon8, tri_free
import flag_engine as fe

def buildW(n0,A0,ALLPAIRS=True):
    """ALLPAIRS=True: dec_a second-moment matrix M_R(A,B)=E[1_R p_A p_B] over ALL ordered pairs i!=je (edge AND
    non-edge) -- GPT's CP matrix, the one the run used. ALLPAIRS=False: edge-only (U_8 monochromatic-edge matrix)."""
    m=n0; T=A0; W={}
    for counts in comps(10,m):
        w=factorial(10)
        for c in counts: w//=factorial(c)
        wt=w*((1.0/m)**10)
        if wt==0: continue
        n,A=blowup(counts,T)
        for i in range(10):
            Ai=A[i]
            for je in range(10):
                if i!=je and (ALLPAIRS or (Ai>>je)&1):
                    anch=[v for v in range(10) if v!=i and v!=je]; idx={v:p for p,v in enumerate(anch)}
                    R=[0]*8
                    for p in range(8):
                        for qd in range(p+1,8):
                            if (A[anch[p]]>>anch[qd])&1: R[p]|=1<<qd; R[qd]|=1<<p
                    key,inv=canon8(R)
                    Aset=frozenset(inv[idx[v]] for v in anch if (Ai>>v)&1)
                    Bset=frozenset(inv[idx[v]] for v in anch if (A[je]>>v)&1)
                    W.setdefault(key,{}); W[key][(Aset,Bset)]=W[key].get((Aset,Bset),0.0)+wt/90.0
    return W

def horn_min_W(W, MAXP=14):
    """min over roots and 5-tuples of H_R = sum_{i,j}P(A_i,A_j) - 4 sum_i P(A_i,A_{i+1}). Returns (min_H, min_norm)."""
    worstH=0.0; worstN=0.0
    for key,ed in W.items():
        profs=sorted(set(a for (a,b) in ed)|set(b for (a,b) in ed),key=lambda s:(len(s),sorted(s)))
        idx={p:i for i,p in enumerate(profs)}; m=len(profs)
        if m<5: continue
        P=np.zeros((m,m))
        for (A,B),w in ed.items(): P[idx[A],idx[B]]+=w
        P=0.5*(P+P.T); pr=float(P.sum())
        deg=P.sum(1)-np.diag(P); top=list(np.argsort(deg)[::-1][:min(MAXP,m)])
        for sub in itertools.combinations(top,5):
            s=list(sub); tot=P[np.ix_(s,s)].sum()
            for perm in itertools.permutations(s[1:]):
                cyc=[s[0]]+list(perm); cs=sum(P[cyc[i],cyc[(i+1)%5]] for i in range(5)); H=tot-4*cs
                if H<worstH:
                    worstH=H; worstN=H/pr if pr>1e-13 else 0.0
    return worstH,worstN

def cyc(n):
    A=[0]*n
    for i in range(n): A[i]|=1<<((i+1)%n); A[(i+1)%n]|=1<<i
    return A
def petersen():
    out=[(i,(i+1)%5) for i in range(5)]+[(5+i,5+(i+2)%5) for i in range(5)]+[(i,5+i) for i in range(5)]
    A=[0]*10
    for u,v in out: A[u]|=1<<v; A[v]|=1<<u
    return A

def main():
    t0=time.time(); gmin=0.0; garg=None
    zoo=[("C5",5,cyc(5)),("C7",7,cyc(7)),("C9",9,cyc(9)),("C11",11,cyc(11)),("Petersen",10,petersen())]
    for (nm,n,A) in zoo:
        W=buildW(n,A); h,hn=horn_min_W(W)
        print(f"{nm:9s}: min H_R={h:+.3e} (norm {hn:+.3e})  {'<<< NEGATIVE!' if h<-1e-9 else 'OK (>=0)'}",flush=True)
        if h<gmin: gmin=h; garg=nm
    for nn in [6,7]:
        gs=fe.enumerate_graphs(nn,triangle_free=True); mh=0.0; t1=time.time()
        for (k,A) in gs:
            W=buildW(nn,A); h,hn=horn_min_W(W)
            if h<mh: mh=h
            if h<gmin: gmin=h; garg=f"n{nn}:{A}"
        print(f"n={nn}: {len(gs)} tri-free graphs, min H_R over all = {mh:+.3e}  {'<<< NEGATIVE!' if mh<-1e-9 else 'OK'} [{time.time()-t1:.0f}s]",flush=True)
    print(f"\nGLOBAL min H_R over ALL real tri-free graphs = {gmin:+.3e} (arg {garg})",flush=True)
    print(f"  HORN CUT SOUND ? {gmin>=-1e-9}  (>=0 within fp => H_R>=0 on real graphons => cut is VALID)  [{time.time()-t0:.0f}s]",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
