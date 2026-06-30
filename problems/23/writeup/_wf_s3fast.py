"""Fast S3' test on the STRUCTURED killers (Mycielskians N<=23, blow-ups, glued), skip slow N=11 census.
S3': ell_f * max_{v in supp f} S(v) <= N."""
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for x in range(off[i],off[i+1]):
            for y in range(off[j],off[j+1]): EE.append((min(x,y),max(x,y)))
    return nn,EE
def bridge(b1,b2,u,v):
    n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]

S3p=[0,0]; ff=None; Smaxf=[0,0]
def per(n,adj,s):
    global ff
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    for f in M:
        if len(cyc[f])<2: continue
        d=pf[f]; ll=sum(d.values()); b=max(S[v] for v in d)
        S3p[1]+=1
        if ll*b<=F(n): S3p[0]+=1
        elif ff is None: ff=(n,f,'ell='+str(ll),'b='+str(b),'ellb='+str(ll*b))
        Smaxf[1]+=1
        if b<=F(n): Smaxf[0]+=1

extras=[('C5[2]',)+blowup([2,2,2,2,2]),('C5[3]',)+blowup([3,3,3,3,3]),
        ('C5[4]',)+blowup([4,4,4,4,4]),('C5unbal',)+blowup([1,5,2,2,5]),
        ('C5[1,6,2,2,6]',)+blowup([1,6,2,2,6]),('C5[1,48,6,8,48]',)+blowup([1,48,6,8,48]),
        ('M(C9)',)+mycielski(9,Cn(9)),('M(C11)',)+mycielski(11,Cn(11)),
        ('Grot11',)+mycielski(5,Cn(5)),
        ('C7brgGrot',)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
        ('M(Grot)23',)+mycielski(*mycielski(5,Cn(5)))]
for nm,n,E in extras:
    adj,cuts=gmins(n,E)
    for s in cuts: per(n,adj,s)
    print('done',nm,'S3p=',S3p,'first=',ff,flush=True)
print('FINAL S3p (ell*Smax<=N):',S3p,'FIRSTFAIL',ff,' Smax<=N:',Smaxf)
