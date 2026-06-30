"""Sanity: within ONE instance (balanced C5[2], a single gamma-min cut), can the local cone reach
F(P) for the L=5 paths? Print F(P) and ALL generator values exactly, then do exact 1-instance LP."""
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
import _wf_dualcert_adv as m
from _satzmu_conn import struct_for_side

def show(parts, tag):
    n,E=m.blowup(parts); adj,cuts=m.gmins(n,E)
    s=cuts[0]
    st=struct_for_side(n,adj,s); M,ell,T,mu,cyc=st
    Gamma=sum(T)
    print("== %s N=%d Gamma=%s cuts=%d =="%(tag,n,str(Gamma),len(cuts)),flush=True)
    rows=[]
    for f in M:
        if ell[f]!=5: continue
        for P in cyc[f]:
            FP=m.Fofp(n,T,ell,f,P,Gamma)
            gens,nlay=m.gen_generators(n,adj,s,M,ell,T,cyc,f,P)
            rows.append((f,P,FP,gens,nlay))
    if not rows:
        print("  no L=5 rows"); return
    # show first row generators
    f,P,FP,gens,nlay=rows[0]
    print("  row0 f=%s P=%s F=%s nlay=%s"%(f,P,str(FP),nlay),flush=True)
    posg={k:v for k,v in gens.items() if v>0}
    print("  positive generators (%d): %s"%(len(posg),{str(k):str(v) for k,v in list(posg.items())[:12]}),flush=True)
    print("  C5 gen=%s"%(str(gens.get(('C5',)))),flush=True)
    # single-instance uniform over its own L=5 rows
    labels=sorted({k for _,_,_,g,_ in rows for k in g},key=str)
    li={l:i for i,l in enumerate(labels)}
    A=np.zeros((len(rows),len(labels))); b=np.zeros(len(rows))
    for ri,(f,P,FP,g,nl) in enumerate(rows):
        b[ri]=float(FP)
        for k,v in g.items(): A[ri,li[k]]=float(v)
    res=linprog(c=np.zeros(len(labels)),A_eq=A,b_eq=b,bounds=[(0,None)]*len(labels),method='highs')
    print("  single-instance L=5 uniform feasible=%s rows=%d labels=%d"%(res.success,len(rows),len(labels)),flush=True)

for parts,tag in (([1,1,1,1,1],"C5[1]"),([2,2,2,2,2],"C5[2]"),([3,3,3,3,3],"C5[3]"),
                  ([3,9,1,9,3],"fan-3,9,1,9,3"),([2,1,2,1,2],"C5[2,1,2,1,2]")):
    show(parts,tag)
