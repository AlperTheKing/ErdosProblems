"""Inspect the EQUALITY cases (margin=0): C5[2] blow-up and friends.
Equality case reveals the proof structure."""
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from fractions import Fraction as F

def blowup(parts):
    m=len(parts); off=[0]*(m+1)
    for i in range(m): off[i+1]=off[i]+parts[i]
    nn=off[m]; EE=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,EE

def show(nm,n,E):
    adj,cuts=gmins(n,E)
    print(f"=== {nm} N={n} cuts={len(cuts)} ===")
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
        eqrows=[]
        for f in M:
            if len(cyc[f])<2: continue
            d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
            m=row/ll; var=sum(d[v]*(S[v]-m)**2 for v in d)
            margin=F(n)*(F(n)-row)-var
            if margin==0:
                UPO=[sum(S[v] for v in P) for P in cyc[f]]
                eqrows.append((f,len(cyc[f]),str(ll),str(row),str(var),[str(u) for u in UPO]))
        if eqrows:
            print(' side=',s,' sumS=',str(sum(S)),' S=',[str(x) for x in S])
            for f,k,ll,row,var,UPO in eqrows:
                print('   EQ f=',f,'k=',k,'ell=',ll,'row=',row,'var=',var)
                print('      UPOs=',UPO,' -> all equal?',len(set(UPO))==1)
        break  # one representative cut

show("C5[2]",*blowup([2,2,2,2,2]))
show("C5[1]=C5",*blowup([1,1,1,1,1]))
show("C5unbal[1,5,2,2,5]",*blowup([1,5,2,2,5]))
