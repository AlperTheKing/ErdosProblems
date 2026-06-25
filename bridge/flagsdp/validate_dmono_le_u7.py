#!/usr/bin/env python3
"""SOUNDNESS GATE for the PUBLISHED object: d_mono(W_G) <= U_7(W_G) on real triangle-free graphs.
U_7 = the SEVEN-anchor per-root-MaxCut envelope (matches envelope_k7.py / envelope_k7_cert.pkl: 7-vertex roots,
order-9 = 7 roots + 2 fresh vertices). For each 9-vertex sample (blow-up law), each ordered fresh pair (i,j):
anchors = other 7, R = canon(G[anchors]) (7-vertex), A=prof(i),B=prof(j) over the 7 anchors; U_7 = sum_R min_c
(per-R profile MaxCut monochromatic density). d_mono(W_G)=2(e-maxcut)/n^2 (graphon maxcut=integer, multilinear).
Tests: cycle/Petersen zoo + C11 killer + EXHAUSTIVE all triangle-free graphs on n=6,7. Memoized canon_label.
"""
import itertools, time, sys
from math import factorial
from fractions import Fraction as F
from compute_U8 import canon_label, maxcut, popcount
import flag_engine as fe

def cyc(m):
    A=[0]*m
    for i in range(m): A[i]|=1<<((i+1)%m); A[i]|=1<<((i-1)%m)
    return A
def petersen():
    A=[0]*10
    def e(u,v): A[u]|=1<<v; A[v]|=1<<u
    for i in range(5): e(i,(i+1)%5); e(5+i,5+((i+2)%5)); e(i,5+i)
    return A
def path(n):
    A=[0]*n
    for i in range(n-1): A[i]|=1<<(i+1); A[i+1]|=1<<i
    return A
def disjoint(A1,n1,A2,n2):
    A=[0]*(n1+n2)
    for i in range(n1): A[i]=A1[i]
    for i in range(n2): A[n1+i]=A2[i]<<n1
    return A,n1+n2

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
def maxcut_graph(n,A):
    best=0
    for mask in range(1<<(n-1)):
        c=0
        for u in range(n):
            au=A[u]
            for w in range(u+1,n):
                if (au>>w)&1 and ((mask>>u)&1)!=((mask>>w)&1): c+=1
        if c>best: best=c
    return best
def dmono(n,A):
    e=sum(popcount(A[v]) for v in range(n))//2; return 2*(e-maxcut_graph(n,A))/(n*n)
def tri_free(n,A):
    for u in range(n):
        for v in range(u+1,n):
            if (A[u]>>v)&1 and (A[u]&A[v]): return False
    return True

_memo={}
def canon7(R):
    rk=tuple(R); v=_memo.get(rk)
    if v is None: v=canon_label(7,R); _memo[rk]=v
    return v

def U7_graphon(m,T,alpha):
    """U_7 of the blow-up graphon via 9-vertex i.i.d. sampling, 7 anchors."""
    W={}
    for counts in comps(9,m):
        w=factorial(9)
        for c in counts: w//=factorial(c)
        wt=w
        for p,c in enumerate(counts): wt*=float(alpha[p])**c
        if wt==0: continue
        n,A=blowup(counts,T)   # n=9
        for i in range(9):
            Ai=A[i]
            for je in range(9):
                if i==je or not ((Ai>>je)&1): continue   # EDGES only (monochromatic-edge density)
                anch=[v for v in range(9) if v!=i and v!=je]   # 7 anchors
                idx={v:p for p,v in enumerate(anch)}
                R=[0]*7
                for p in range(7):
                    for qd in range(p+1,7):
                        if (A[anch[p]]>>anch[qd])&1: R[p]|=1<<qd; R[qd]|=1<<p
                key,inv=canon7(R)
                Aset=frozenset(inv[idx[v]] for v in anch if (Ai>>v)&1)
                Bset=frozenset(inv[idx[v]] for v in anch if (A[je]>>v)&1)
                W.setdefault(key,{}); W[key][(Aset,Bset)]=W[key].get((Aset,Bset),0.0)+wt/72.0
    U7=0.0
    for key,ed in W.items():
        offdiag={}; sl=0.0; profs=set()
        for (Aset,Bset),w in ed.items():
            profs.add(Aset); profs.add(Bset)
            if Aset==Bset: sl+=w
            else:
                a,b=tuple(sorted([Aset,Bset],key=lambda s:(len(s),sorted(s)))); offdiag[(a,b)]=offdiag.get((a,b),0.0)+w
        mc=maxcut(list(profs),offdiag) if offdiag else 0.0
        U7 += sl + (sum(offdiag.values())-mc)
    return U7

def main():
    C5C5,_=disjoint(cyc(5),5,cyc(5),5)
    zoo=[("C5",5,cyc(5)),("C7",7,cyc(7)),("C9",9,cyc(9)),("C11",11,cyc(11)),("C13",13,cyc(13)),
         ("P5",5,path(5)),("C5uC5",10,C5C5),("Petersen",10,petersen())]
    print(f"=== d_mono <= U_7 (SEVEN-anchor, matches published cert) ===",flush=True)
    print(f"{'graph':9s}{'d_mono':>11s}{'U_7':>13s}{'U7>=dm':>8s}{'ratio':>8s}{'t(s)':>6s}",flush=True)
    worst=1e9
    for (name,n,A) in zoo:
        if not tri_free(n,A): print(f"{name}: not tri-free"); continue
        dm=dmono(n,A); t0=time.time(); U7=float(U7_graphon(n,A,[F(1,n)]*n))
        ok=U7>=dm-1e-12; worst=min(worst,U7-dm)
        print(f"{name:9s}{dm:11.6f}{U7:13.6e}{str(ok):>8s}{(U7/dm if dm>0 else float('inf')):8.3f}{time.time()-t0:6.0f}",flush=True)
    # EXHAUSTIVE n=6,7
    for nn in [6,7]:
        gs=fe.enumerate_graphs(nn,triangle_free=True); viol=0; tight=0; t0=time.time()
        for (k,A) in gs:
            dm=dmono(nn,A); U7=float(U7_graphon(nn,A,[F(1,nn)]*nn))
            if U7 < dm-1e-9: viol+=1; print(f"  VIOLATION n={nn}: A={A} dm={dm} U7={U7}",flush=True)
            if abs(U7-dm)<1e-9: tight+=1
            worst=min(worst,U7-dm)
        print(f"  n={nn} exhaustive: {len(gs)} tri-free graphs, {viol} violations, {tight} tight [{time.time()-t0:.0f}s]",flush=True)
    print(f"\nWORST U_7 - d_mono = {worst:+.3e}  => d_mono<=U_7 holds for ALL ? {worst>=-1e-9}",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
