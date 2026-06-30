"""What generator would FIX Grotzsch infeasibility? Test augmenting the local cone with candidate
extra generators and re-check feasibility per-instance (Grotzsch, all 5 gamma-min cuts).
Candidates:
  (C5all_i)  per-layer-pair slack  s_i = (sum n)^2 - 25 n_i n_{i+1}  for EACH i (not just min)  [>=0]
  (CUTany)   delta_B(U)-delta_M(U) for ALL vertex subsets U up to size 3 (non-path-local long-range)
  (SWany)    Gamma(s^W)-Gamma(s) for ALL neutral single/double flips anywhere (non-local switch)
"""
import itertools
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
import _wf_dualcert_adv as M
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _h import Bconn

def base_rows(nn,adj,s):
    st=struct_for_side(nn,adj,s); Mb,ell,T,mu,cyc=st; Gamma=sum(T)
    rows=[]
    for f in Mb:
        if ell[f]!=5: continue
        for P in cyc[f]:
            FP=M.Fofp(nn,T,ell,f,P,Gamma)
            gens,nl=M.gen_generators(nn,adj,s,Mb,ell,T,cyc,f,P)
            rows.append((f,tuple(P),FP,dict(gens),nl,P))
    return rows,Mb,ell,T,cyc,Gamma

def add_C5all(nn,adj,s,rows):
    """add per-i C5 slab slacks s_i = (sum n)^2 - 25 n_i n_{i+1} for each i."""
    for ri,(f,P,FP,g,nl,Pl) in enumerate(rows):
        L=5; sumn=sum(nl.get(i,0) for i in range(L))
        for i in range(L):
            si=sumn*sumn-25*nl.get(i,0)*nl.get((i+1)%L,0)
            g[('C5i',i)]=F(si)

def add_CUTany(nn,adj,s,rows,maxsz=3):
    """add cut margins for ALL subsets U up to size maxsz (long-range)."""
    Vs=list(range(nn))
    subsets=[]
    for k in range(1,maxsz+1):
        for U in itertools.combinations(Vs,k): subsets.append(U)
    cache={}
    for U in subsets:
        dB,dM=M.deltaB_M(nn,adj,s,list(U)); cache[U]=F(dB-dM)
    for ri,(f,P,FP,g,nl,Pl) in enumerate(rows):
        for U in subsets:
            g[('CUTany',U)]=cache[U]

def add_SWany(nn,adj,s,rows):
    """add Gamma-gap for ALL neutral single+double flips anywhere (global switches)."""
    G0=None
    # base gamma
    st=struct_for_side(nn,adj,s); G0=sum(st[2])
    gaps={}
    for v in range(nn):
        dB,dM=M.deltaB_M(nn,adj,s,[v])
        if dB==dM:
            s2=s[:]; s2[v]=1-s2[v]
            if Bconn(nn,adj,s2):
                g2=M.gamma_of_side(nn,adj,s2)
                if g2 is not None: gaps[('SWany',v)]=F(g2-G0)
    for u in range(nn):
        for v in range(u+1,nn):
            dB,dM=M.deltaB_M(nn,adj,s,[u,v])
            if dB==dM:
                s2=s[:]; s2[u]=1-s2[u]; s2[v]=1-s2[v]
                if Bconn(nn,adj,s2):
                    g2=M.gamma_of_side(nn,adj,s2)
                    if g2 is not None: gaps[('SWany',u,v)]=F(g2-G0)
    for ri,(f,P,FP,g,nl,Pl) in enumerate(rows):
        for k,val in gaps.items(): g[k]=val

def feas(rows):
    labels=sorted({k for _,_,_,g,_,_ in rows for k in g},key=str)
    li={l:i for i,l in enumerate(labels)}
    A=np.zeros((len(rows),len(labels))); b=np.zeros(len(rows))
    for ri,(f,P,FP,g,nl,Pl) in enumerate(rows):
        b[ri]=float(FP)
        for k,v in g.items(): A[ri,li[k]]=float(v)
    res=linprog(c=np.zeros(len(labels)),A_eq=A,b_eq=b,bounds=[(0,None)]*len(labels),method='highs')
    okexact=None
    if res.success:
        lam=[F(x).limit_denominator(10**7) for x in res.x]
        okexact=all(sum(v*lam[li[k]] for k,v in g.items())==FP for f,P,FP,g,nl,Pl in rows)
    return res.success, okexact, len(labels)

nn,E=mycielski(5,Cn(5)); adj,cuts=gmins(nn,E); s=cuts[0]
import copy
rows0,Mb,ell,T,cyc,Gamma=base_rows(nn,adj,s)
print("Grotzsch cut0: %d L=5 rows"%len(rows0),flush=True)
def trial(name,augfn):
    rows=[(f,P,FP,dict(g),nl,Pl) for f,P,FP,g,nl,Pl in rows0]
    if augfn: augfn(nn,adj,s,rows)
    ok,okx,nl=feas(rows)
    print("  +%-12s feasible=%s exact=%s labels=%d"%(name,ok,okx,nl),flush=True)

trial("BASE",None)
trial("C5all_i",add_C5all)
trial("CUTany<=3",lambda a,b,c,r:add_CUTany(a,b,c,r,3))
trial("SWany",add_SWany)
def both(a,b,c,r): add_C5all(a,b,c,r); add_SWany(a,b,c,r)
trial("C5all+SWany",both)
def allthree(a,b,c,r): add_C5all(a,b,c,r); add_SWany(a,b,c,r); add_CUTany(a,b,c,r,2)
trial("ALL3(cut<=2)",allthree)
