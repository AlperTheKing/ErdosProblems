"""Verify EXACTLY:
 (BD)  var_f <= ell_f * (Smax - <S>) * (<S> - Smin)    [Bhatia-Davis on prob measure p_f/ell]
 (BD0) var_f <= ell_f * (Smax - <S>) * <S>             [Smin>=0 relaxation]
 (bridge) var_f + n*row_f <= row_f*(Smax + n - <S>)    [== BD0 since row=ell<S>]
Hence:  STRONG (row*(Smax+n-<S>)<=n^2)  =>  target n^2>=var+n*row.
Report any case where BD or BD0 or bridge FAILS (should be 0).  Also where STRONG holds but BD0 is loose
(measure slack of BD0 vs actual var, to see if Smin matters at equality).
Battery census<=10 + blowups + Myc(C7),Myc(C9).
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _wf_var_0 import build

def blowup(parts):
    m=len(parts); off=[0]*(m+1)
    for i in range(m): off[i+1]=off[i]+parts[i]
    nn=off[m]; EE=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,EE

def cases():
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: yield (f"c{nn}:{g6}",n,adj,s)
    for parts in [[2,2,2,2,2],[3,3,3,3,3],[1,5,2,2,5],[1,2,1,2,1,2,1],[1,6,2,2,6]]:
        nn,EE=blowup(parts); adj,cuts=gmins(nn,EE)
        for s in cuts: yield (f"blow{parts}",nn,adj,s)
    for nm,(nn,EE) in [("MycC7",mycielski(7,Cn(7))),("MycC9",mycielski(9,Cn(9))),("MycC11",mycielski(11,Cn(11)))]:
        adj,cuts=gmins(nn,EE)
        for s in cuts: yield (nm,nn,adj,s)

if __name__=="__main__":
    print("=== Bhatia-Davis bridge verification (exact) ===",flush=True)
    nrows=0; f_BD=0; f_BD0=0; f_bridge=0
    bd0_eq_at_strong_eq=[]  # at STRONG-equality, is BD0 also tight?
    for nm,n,adj,s in cases():
        b=build(n,adj,s)
        if b is None: continue
        M,ell,T,mu,cyc,S,pf=b
        for f in M:
            if len(cyc[f])<2: continue
            d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); mean=row/ll
            var=sum(d[v]*(S[v]-mean)**2 for v in d)
            Smax=max(S[v] for v in d); Smin=min(S[v] for v in d)
            nrows+=1
            BD = ll*(Smax-mean)*(mean-Smin)
            BD0= ll*(Smax-mean)*mean
            if var>BD: f_BD+=1
            if var>BD0: f_BD0+=1
            # bridge: var+n*row <= row*(Smax+n-mean) == BD0 + n*row ?
            lhs=var+F(n)*row; rhs=row*(Smax+F(n)-mean)
            if lhs>rhs: f_bridge+=1
            # strong slack
            strong_slack=F(n)**2-rhs
            if strong_slack==0:
                bd0_eq_at_strong_eq.append((nm,f,n,str(var),str(BD0),str(Smin)))
    print("nonunique rows:",nrows)
    print(f"BD (var<=ell(Smax-<S>)(<S>-Smin)) fails: {f_BD}")
    print(f"BD0 (var<=ell(Smax-<S>)<S>) fails: {f_BD0}")
    print(f"bridge (var+n row <= row(Smax+n-<S>)) fails: {f_bridge}")
    print(f"#STRONG-equality rows: {len(bd0_eq_at_strong_eq)} (sample {bd0_eq_at_strong_eq[:3]})")
