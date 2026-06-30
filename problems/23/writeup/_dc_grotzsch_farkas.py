"""Confirm EXACT Farkas separator for the MAXIMALLY enriched cone on Grotzsch:
   generators = path-local CUT + ALL subsets-cut<=3 + ALL C5_i slabs + ALL neutral switches anywhere.
   If exact Farkas (b.y>0, all gen-cols .y <=0) holds => obstruction is rigorous, NOT a missing
   generator of these families."""
import itertools
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
import _wf_dualcert_adv as M
from _dc_grotzsch_fix import base_rows, add_C5all, add_CUTany, add_SWany
from _stark1 import gmins
from _bdef_construct import mycielski, Cn

nn,E=mycielski(5,Cn(5)); adj,cuts=gmins(nn,E); s=cuts[0]
rows0,Mb,ell,T,cyc,Gamma=base_rows(nn,adj,s)
rows=[(f,P,FP,dict(g),nl,Pl) for f,P,FP,g,nl,Pl in rows0]
add_C5all(nn,adj,s,rows); add_SWany(nn,adj,s,rows); add_CUTany(nn,adj,s,rows,3)
labels=sorted({k for _,_,_,g,_,_ in rows for k in g},key=str)
li={l:i for i,l in enumerate(labels)}
m=len(rows); d=len(labels)
A=np.zeros((m,d)); b=np.zeros(m)
for ri,(f,P,FP,g,nl,Pl) in enumerate(rows):
    b[ri]=float(FP)
    for k,v in g.items(): A[ri,li[k]]=float(v)
print("enriched: rows=%d generator-labels=%d"%(m,d),flush=True)
res=linprog(c=np.zeros(d),A_eq=A,b_eq=b,bounds=[(0,None)]*d,method='highs')
print("float feasible=%s"%res.success,flush=True)
# Farkas separator
r2=linprog(c=-b,A_ub=A.T,b_ub=np.zeros(d),bounds=[(-1,1)]*m,method='highs')
y=r2.x
# rationalize with several denominators, verify EXACT
proven=False
for den in (5040,2520,1260,840,27720,55440):
    yq=[F(round(yi*den),den) for yi in y]
    bty=sum(rows[ri][2]*yq[ri] for ri in range(m))
    maxcol=F(-10**9)
    for k in labels:
        sv=sum((rows[ri][3].get(k,F(0)))*yq[ri] for ri in range(m))
        if sv>maxcol: maxcol=sv
    if bty>0 and maxcol<=0:
        proven=True
        print("EXACT Farkas (den=%d): b.y=%s>0  maxcol=%s<=0  => PROVEN INFEASIBLE on enriched cone"%(den,str(bty),str(maxcol)),flush=True)
        break
    else:
        print("  den=%d: b.y=%s maxcol=%s (not yet clean)"%(den,str(bty),str(maxcol)),flush=True)
if not proven:
    print("Could not rationalize a clean exact Farkas; float says feasible=%s"%res.success,flush=True)
