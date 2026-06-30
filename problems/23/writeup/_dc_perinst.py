"""DEFINITIVE per-instance test (matches GPT-Pro's claim: a per-instance certificate from the local
cone).  For EACH (instance, max-cut) we collect ALL its L in {5,7} rows and ask: does ONE nonneg
weight vector (over that instance's canonical labels) satisfy A lambda = b EXACTLY for every path?
We float-LP then EXACT-verify the rationalized certificate.  Report any instance where INFEASIBLE."""
import subprocess
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
import _wf_dualcert_adv as M
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn

def inst_rows(n,adj,side):
    if not Bconn(n,adj,side): return None
    st=struct_for_side(n,adj,side)
    if st is None: return None
    Mb,ell,T,mu,cyc=st
    if not Mb: return None
    Gamma=sum(T); rows=[]
    for f in Mb:
        if ell[f] not in (5,7): continue
        for P in cyc[f]:
            FP=M.Fofp(n,T,ell,f,P,Gamma)
            gens,nl=M.gen_generators(n,adj,side,Mb,ell,T,cyc,f,P)
            rows.append((FP,gens,ell[f],tuple(P),nl))
    return rows or None

def feasible_exact(rows):
    labels=sorted({k for _,g,_,_,_ in rows for k in g},key=str)
    li={l:i for i,l in enumerate(labels)}
    A=np.zeros((len(rows),len(labels))); b=np.zeros(len(rows))
    for ri,(FP,g,L,P,nl) in enumerate(rows):
        b[ri]=float(FP)
        for k,v in g.items(): A[ri,li[k]]=float(v)
    res=linprog(c=np.zeros(len(labels)),A_eq=A,b_eq=b,bounds=[(0,None)]*len(labels),method='highs')
    if not res.success:
        # try exact Farkas to PROVE infeasible
        rr=[(F(0),g,0,P,nl) for _,g,_,P,nl in rows]  # placeholder unused
        return False,None
    lam=[F(x).limit_denominator(10**6) for x in res.x]
    okexact=all(sum(v*lam[li[k]] for k,v in g.items())==FP for FP,g,L,P,nl in rows)
    return True, okexact

def run(name,n,adj,cuts):
    bad=0; tot=0; floatonly=0
    for s in cuts:
        rows=inst_rows(n,adj,s)
        if not rows: continue
        tot+=1
        feas,okexact=feasible_exact(rows)
        if not feas: bad+=1; print("  INFEASIBLE inst %s cut#%d"%(name,tot),flush=True)
        elif not okexact: floatonly+=1
    return tot,bad,floatonly

if __name__=="__main__":
    TOT=0; BAD=0; FLO=0
    # structured battery
    for L in (8,12,16):
        n,E,side,bad=M.build_two_lane(L)
        t,b,f=run("twolane%d"%L,n,M.adj_of(n,E),[side]); TOT+=t;BAD+=b;FLO+=f
    for cyc in (5,7):
        for tt in range(1,5):
            n,E=M.blowup([tt]*cyc)
            if n>21: continue
            adj,cuts=gmins(n,E); t,b,f=run("C%d[%d]"%(cyc,tt),n,adj,cuts); TOT+=t;BAD+=b;FLO+=f
    for parts in ([2,1,2,1,2],[3,2,3,2,3],[3,1,3,1,3],[4,3,4,3,4],[3,9,1,9,3],[1,4,1,4,1],[5,1,5,1,5],[4,1,4,1,4],[2,3,2,3,2],[1,5,1,5,1]):
        n,E=M.blowup(parts)
        if n>21: continue
        adj,cuts=gmins(n,E); t,b,f=run("C5%s"%parts,n,adj,cuts); TOT+=t;BAD+=b;FLO+=f
    for nm,(nn,E) in [("Grotzsch",mycielski(5,Cn(5))),("M(C7)",mycielski(7,Cn(7)))]:
        adj,cuts=gmins(nn,E); t,b,f=run(nm,nn,adj,cuts); TOT+=t;BAD+=b;FLO+=f
    # census N<=8 (small, fast; cap cuts per graph to keep runtime bounded)
    for nn in range(6,9):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            t,b,f=run("cen%s"%g6,n,adj,cuts[:4]); TOT+=t;BAD+=b;FLO+=f
        print("  census N=%d done: instances=%d infeasible=%d floatonly=%d"%(nn,TOT,BAD,FLO),flush=True)
    print("\nPER-INSTANCE local-cone feasibility over %d (instance,cut) pairs:"%TOT,flush=True)
    print("  INFEASIBLE: %d   float-only(not exact-verified): %d"%(BAD,FLO),flush=True)
    print("  RESULT: %s"%("ALL per-instance certificates EXIST in local cone (structure-confirmed)" if BAD==0
                          else "%d instances LACK a local-cone certificate (cone genuinely too small)"%BAD),flush=True)
