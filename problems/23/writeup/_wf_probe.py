from _bdef_construct import mycielski, Cn
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from fractions import Fraction as F
n,E=mycielski(5,Cn(5))
adj,cuts=gmins(n,E)
for s in cuts[:1]:
  st=struct_for_side(n,adj,s)
  M,ell,T,mu,cyc=st
  S=[F(0)]*n; pf={}
  for g in M:
    Ps=cyc[g]; k=len(Ps); d={}
    for P in Ps:
      for v in P: d[v]=d.get(v,F(0))+F(1,k)
    pf[g]=d
    for v,pv in d.items(): S[v]+=pv
  print('side=',s)
  print('S=',[str(x) for x in S])
  print('sum S=',str(sum(S)))
  for f in M:
    d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
    m=row/ll; var=sum(d[v]*(S[v]-m)**2 for v in d)
    UPO=[sum(S[v] for v in P) for P in cyc[f]]
    print('f=',f,'k=',len(cyc[f]),'ell=',str(ll),'row=',str(row),'var=',str(var),'margin=',str(F(n)*(F(n)-row)-var))
    print('   UPOs=',[str(u) for u in UPO])
