"""Corrected (A) coarea LP with the CANONICAL LARGER switch family (GPT-Pro answer 2):
   W = {x_i:i in J} cup S,  J oriented cyclic interval on P, S any subset of off-row vertices with B_W connected
   (not just whole off-row components).  No M2, theta-subgradient over active minimizers.  Float linprog.
   Usage: python _coareaA_lp3.py [Nmax]
"""
import sys, subprocess, itertools, random
from fractions import Fraction as F
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import deltas, flip, gamma_of
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, mycielski
import numpy as np
from scipy.optimize import linprog

def big_family(n,P,maxsub=18):
    L=len(P); Pset=set(P)
    nonpath=[v for v in range(n) if v not in Pset]
    intervals=[]
    for s in range(L):
        cur=[]
        for ln in range(1,L):
            cur=cur+[(s+ln-1)%L]
            intervals.append(frozenset(P[idx] for idx in cur))
    seen=set(); Js=[]
    for I in intervals:
        if I not in seen: seen.add(I); Js.append(I)
    cap = len(nonpath)<=maxsub
    rng = nonpath[:maxsub]
    out=set()
    for I in Js:
        for mask in range(1<<len(rng)):
            S=set(rng[j] for j in range(len(rng)) if (mask>>j)&1)
            out.add(frozenset(I|S))
    return [W for W in out if W]

def test_row(n,adj,side,M,ell,T,cyc,f,P):
    L=ell[f]; N=F(n); Gamma=sum(ell[g]**2 for g in M)
    h=[T[P[i]]/N for i in range(L)]; S=sum(h)
    prods=[h[i]*h[(i+1)%L] for i in range(L)]; q=min(prods)
    A=[r for r in range(L) if prods[r]==q]
    L2delta=S*S-L*L*q
    chiP=[0]*n
    for end in (P[0],P[-1]):
        ch=endpt_chi(n,adj,side,end,M,n)
        for rr in range(n): chiP[rr]+=ch[rr]
    E0=sum((2*rr+1)*chiP[rr] for rr in range(n))
    TARGET=F(L,5)*(N*N-Gamma)-E0-L2delta
    cols=[]
    for W in big_family(n,P):
        s2=flip(side,W)
        if not Bconn(n,adj,s2): continue
        g1=gamma_of(n,adj,s2)
        if g1 is None: continue
        dB,dM=deltas(n,adj,side,W); sigma=dB-dM
        if sigma<0: continue
        cols.append((sigma,[1 if P[i] in W else 0 for i in range(L)],g1-Gamma))
    if not cols: return None
    m=len(cols); na=len(A); nv=m+na
    rows=[]; b=[]
    row=[0.0]*nv
    for j in range(na): row[m+j]=1.0
    rows.append(row); b.append(1.0)
    rows.append([float(cols[k][0]) for k in range(m)]+[0.0]*na); b.append(0.0)
    rhs=F(L,5)-S/N
    for i in range(L):
        r0=[float(cols[k][1][i]) for k in range(m)]
        for r in A:
            coef=-(F(L*L,2*N))*((h[(r+1)%L] if i==r else 0)+(h[r] if i==(r+1)%L else 0))
            r0.append(float(coef))
        rows.append(r0); b.append(float(rhs))
    rows.append([float(cols[k][2]) for k in range(m)]+[0.0]*na); b.append(float(TARGET))
    res=linprog(c=np.zeros(nv),A_eq=np.array(rows),b_eq=np.array(b),bounds=[(0,None)]*nv,method='highs')
    return res.success

def run_graph(name,n,E,acc,cuts=None):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    if cuts is None:
        try: _,cuts=gmins(n,E)
        except Exception: return
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        for f in M:
            if ell[f]%2==0: continue
            for P in cyc[f]:
                if len(P)!=ell[f]: continue
                fe=test_row(n,adj,side,M,ell,T,cyc,f,list(P))
                acc['rows']+=1
                if fe is None: acc['nocol']+=1
                elif fe: acc['feas']+=1
                else:
                    acc['infeas']+=1
                    if acc['ex'] is None: acc['ex']=(name,n,tuple(P))

def main():
    Nmax=int(sys.argv[1]) if len(sys.argv)>1 else 7
    acc=dict(rows=0,feas=0,infeas=0,nocol=0,ex=None)
    for nn in range(5,Nmax+1):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); run_graph("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d feas=%d infeas=%d nocol=%d %s"%(nn,acc['rows'],acc['feas'],acc['infeas'],acc['nocol'],acc['ex'] or ''),flush=True)
    print("VERDICT(bigfamily):", "FEASIBLE all" if acc['infeas']==0 and acc['feas']>0 else "INFEASIBLE remain: %s"%(acc['ex'],))

if __name__=="__main__":
    main()
