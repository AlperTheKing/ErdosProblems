"""Drill: WHY is Grotzsch per-instance infeasible? Find the exact Farkas separator over its L=5 rows,
identify which path-row(s) carry the separation, and what local generator is missing."""
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
import _wf_dualcert_adv as M
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn

nn,E=mycielski(5,Cn(5))
adj,cuts=gmins(nn,E)
s=cuts[0]
st=struct_for_side(nn,adj,s); Mb,ell,T,mu,cyc=st
Gamma=sum(T)
print("Grotzsch N=%d Gamma=%s ncuts=%d badedges=%d ell=%s"%(nn,str(Gamma),len(cuts),len(Mb),sorted(set(ell.values()))),flush=True)
rows=[]
for f in Mb:
    if ell[f]!=5: continue
    for P in cyc[f]:
        FP=M.Fofp(nn,T,ell,f,P,Gamma)
        gens,nl=M.gen_generators(nn,adj,s,Mb,ell,T,cyc,f,P)
        rows.append((f,tuple(P),FP,gens,nl))
print("L=5 rows: %d"%len(rows),flush=True)
labels=sorted({k for _,_,_,g,_ in rows for k in g},key=str)
li={l:i for i,l in enumerate(labels)}
A=np.zeros((len(rows),len(labels))); b=np.zeros(len(rows))
for ri,(f,P,FP,g,nl) in enumerate(rows):
    b[ri]=float(FP)
    for k,v in g.items(): A[ri,li[k]]=float(v)
res=linprog(c=np.zeros(len(labels)),A_eq=A,b_eq=b,bounds=[(0,None)]*len(labels),method='highs')
print("float feasible=%s msg=%s"%(res.success,res.message),flush=True)
# exact Farkas: y with A^T y<=0, b^T y>0
r2=linprog(c=-b,A_ub=A.T,b_ub=np.zeros(len(labels)),bounds=[(-1,1)]*len(rows),method='highs')
y=r2.x
yq=[F(round(yi*5040),5040) for yi in y]
bty=sum(rows[ri][2]*yq[ri] for ri in range(len(rows)))
maxcol=F(-10**9); argmax=None
for k in labels:
    sv=sum((rows[ri][3].get(k,F(0)))*yq[ri] for ri in range(len(rows)))
    if sv>maxcol: maxcol=sv; argmax=k
print("EXACT Farkas: b.y=%s (need>0)  maxcol=%s (need<=0)  proven_infeasible=%s"%(
    str(bty),str(maxcol),(bty>0 and maxcol<=0)),flush=True)
# which rows carry the separation (largest |y_r * F_r| contribution)
contrib=sorted(range(len(rows)),key=lambda ri:-abs(float(rows[ri][2]*yq[ri])))[:6]
print("\nRows carrying the Farkas separation (y_r != 0, sorted by |y_r*F_r|):",flush=True)
for ri in contrib:
    f,P,FP,g,nl=rows[ri]
    pos=sorted([(str(k),str(v)) for k,v in g.items() if v>0],key=lambda x:x[0])
    print("  f=%s P=%s F=%s y=%s nlay=%s npos=%d C5=%s"%(f,P,str(FP),str(yq[ri]),nl,len(pos),str(g.get(('C5',)))),flush=True)
# also: the MINIMAL F rows and their available positive generators
print("\nTightest L=5 rows in Grotzsch:",flush=True)
for f,P,FP,g,nl in sorted(rows,key=lambda r:r[2])[:6]:
    posnames=sorted([str(k) for k,v in g.items() if v>0])
    print("  F=%s f=%s P=%s nlay=%s posgen=%s C5=%s"%(str(FP),f,P,nl,posnames[:8],str(g.get(('C5',)))),flush=True)
