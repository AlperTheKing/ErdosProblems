"""Confirm the variance inequality CAN fail for UNIQUE rows (justifies the nonunique restriction).
Doc: 'the global variance died at the UNIQUE row K??CB@OBDOAp'. Check ALL rows on its gamma-min cuts."""
from fractions import Fraction as F
from _h import dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side

g6="K??CB@OBDOAp"
n,E=dec(g6); adj,cuts=gmins(n,E)
worst_all=None; worst_uniq=None; worst_nonuniq=None
for s in cuts:
    st=struct_for_side(n,adj,s)
    if st is None: continue
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    for f in M:
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); mean=row/ll
        var=sum(d[v]*(S[v]-mean)**2 for v in d)
        marg=F(n)*(F(n)-row)-var
        uniq=len(cyc[f])<2
        rec=(marg,f,uniq,str(row),str(var))
        if worst_all is None or marg<worst_all[0]: worst_all=rec
        if uniq and (worst_uniq is None or marg<worst_uniq[0]): worst_uniq=rec
        if (not uniq) and (worst_nonuniq is None or marg<worst_nonuniq[0]): worst_nonuniq=rec
print("n=",n)
print("worst over ALL f:    ",worst_all)
print("worst over UNIQUE f: ",worst_uniq)
print("worst over NONUNIQ f:",worst_nonuniq)
