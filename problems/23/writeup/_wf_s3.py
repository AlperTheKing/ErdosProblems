"""Test S3 in clean form: ell_f * (max_{v in supp(f)} S(v)) <= N  for every nonunique bad edge f.
If TRUE -> BD-TARGET follows from ell(b-mu)(mu-a) <= ell(b-mu)*N... wait, need product decomposition:
  BD-TARGET: ell(b-mu)(mu-a) <= N(N-row).
  S3':  ell*b <= N   (i.e. ell(b-mu) <= N - ell*mu = N - row).
  Then ell(b-mu)(mu-a) <= (N-row)(mu-a) <= (N-row)*N   iff  mu-a <= N.
  mu-a <= b - a <= b <= N (if b<=N). So need also b<=N (Smax<=N). Both -> BD-TARGET.
So the two atoms are:  S3': ell*Smax_supp <= N   and   Smax<=N.  Test BOTH exactly on full battery.
Also test the FAN-version per geodesic in case S3' fails: maybe ell*Smax over a SINGLE geodesic only."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def per_side(n, adj, s, agg, firsts):
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
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); m=row/ll
        Sv=[S[v] for v in d]; a=min(Sv); b=max(Sv)
        # S3': ell*b <= N
        agg['S3p'][1]+=1
        if ll*b<=F(n): agg['S3p'][0]+=1
        elif firsts['S3p'] is None:
            firsts['S3p']=(f, 'ell='+str(ll),'b='+str(b),'ell*b='+str(ll*b),'N='+str(n),'row='+str(row))
        # Smax<=N
        agg['Smax'][1]+=1
        if b<=F(n): agg['Smax'][0]+=1
        elif firsts['Smax'] is None: firsts['Smax']=(f,str(b),n)
        # per-geodesic version: max over a single geodesic of S, times ell, <= N ?
        gmax=max(sum(F(1) for _ in [0]) and max(S[v] for v in P) for P in cyc[f])  # max over geodesics of (max S on that geodesic) = b anyway
        # better: min over geodesics of (max S on geodesic)
        permax=[max(S[v] for v in P) for P in cyc[f]]
        bmin=min(permax)  # smallest per-geodesic max
        agg['S3p_min'][1]+=1
        if ll*bmin<=F(n): agg['S3p_min'][0]+=1
        elif firsts['S3p_min'] is None: firsts['S3p_min']=(f,'ell*bmin='+str(ll*bmin),n)

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

if __name__=="__main__":
    agg={'S3p':[0,0],'Smax':[0,0],'S3p_min':[0,0]}; firsts={'S3p':None,'Smax':None,'S3p_min':None}
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: per_side(n,adj,s,agg,firsts)
        print(f"done N={nn}: S3p={agg['S3p']} Smax={agg['Smax']} S3p_min={agg['S3p_min']}",flush=True)
    extra=[("M(C7)",)+mycielski(7,Cn(7)),("M(C9)",)+mycielski(9,Cn(9)),
           ("M(C11)",)+mycielski(11,Cn(11)),("M(Grot)23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7brgGrot",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C5[2]",)+blowup([2,2,2,2,2]),("C5[3]",)+blowup([3,3,3,3,3]),("C5[4]",)+blowup([4,4,4,4,4]),
           ("C5unbal",)+blowup([1,5,2,2,5]),("C5[1,6,2,2,6]",)+blowup([1,6,2,2,6]),
           ("C5[1,48,6,8,48]",)+blowup([1,48,6,8,48])]
    for nm,n,E in extra:
        adj,cuts=gmins(n,E)
        for s in cuts: per_side(n,adj,s,agg,firsts)
    print("\n=== FINAL ===")
    print("S3' (ell*Smax_supp <= N):", agg['S3p'], "FIRSTFAIL", firsts['S3p'])
    print("Smax<=N:", agg['Smax'], "FIRSTFAIL", firsts['Smax'])
    print("S3'_min (ell*min-per-geo-max <= N):", agg['S3p_min'], "FIRSTFAIL", firsts['S3p_min'])
