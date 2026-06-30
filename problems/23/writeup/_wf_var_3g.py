"""Inspect the binding row MGrot23 f=(21,22) and the rows with main-margin near 0.
Print full per-row: N,row,ell,var,margin, and S-distribution on supp(f), Smax,Smin, and
the actual S values + p_f values, to see the structure that makes BD bound exact and what
proven quantity bounds the spread."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
import _wf_var_3 as W

def rows_for(name,n,E, want_margin_le=None):
    out=[]
    adj,cuts=gmins(n,E)
    for s in cuts:
        b=W.build(n,adj,s)
        if b is None: continue
        M,ell,cyc,P,S=b
        for f in M:
            if len(cyc[f])<2: continue
            d=P[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
            Q=sum(d[v]*S[v]*S[v] for v in d); var=Q-row*row/ll
            N=F(n); margin=N*(N-row)-var
            if want_margin_le is None or margin<=want_margin_le:
                supp=sorted(d.items())
                Svals=sorted(set(S[v] for v in d))
                out.append((n,f,ll,row,var,margin, Svals, [(v,str(d[v]),str(S[v])) for v in d]))
    return out

n,E=mycielski(*mycielski(5,Cn(5)))
r=rows_for("MGrot23",n,E, want_margin_le=F(1,1000000000)*0)  # exact zero-margin rows
print("MGrot23 zero-margin rows:",len(r))
for rec in r[:4]:
    nn,f,ll,row,var,margin,Sv,detail=rec
    print(f"  f={f} ell={ll} row={row} var={var} margin={margin}")
    print(f"    distinct S on supp: {[str(x) for x in Sv]}")
    print(f"    (v,p_f,S): {detail}")
# also globally smallest positive margins across battery
print("--- scanning battery for smallest margins ---")
import _wf_var_3d_data as D
def marg(r):
    nm,nn,f,ll,row,Q,var,Smax,Smin,pfmin=r; return F(nn)*(F(nn)-row)-var
sm=sorted(D.data, key=marg)[:8]
for rec in sm:
    nm,nn,f,ll,row,Q,var,Smax,Smin,pfmin=rec
    N=F(nn); margin=N*(N-row)-var
    print(f"  {nm} f={f} n={nn} ell={ll} row={row} var={var} margin={margin} Smax={Smax} Smin={Smin}")
