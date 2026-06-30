"""FINAL decisive test for a SWITCH/CD-realizable (local) proof of path-LRS.

A max-cut switch on a corridor around P can only certify quantities that are LOCAL to that corridor
(bounded by #bad edges and #B-edges touching the corridor, times O(1)). We already refuted LOCAL-MEET
(excess <= ell*nmeet/25). Here we test ALL remaining local-realizable upper bounds on excess(P) and confirm
each is broken by the two-lane (sparse, |M|=4, but huge excess). If every local bound breaks, a pure
switch/CD proof of path-LRS is IMPOSSIBLE -> path-LRS is not provable locally; it inherits the global
second-moment hardness. Report exact min margins.

Local-realizable candidates C(P) (each a quantity a corridor switch could produce), test excess(P)<=C(P):
 (L1) ell(f) * nmeet / 25         [#bad edges meeting P]            -- already dead, recheck
 (L2) ell(f) * dB(corridor)/ something   approximate by ell(f)*deg-sum local
 (L3) sum over overloaded v in P of (local cross-degree budget)  : sum_{v in P}(crossdeg_B(v)) ?
 (L4) ell(f) * (#B-edges incident to P)/25
 (L5) ell(f)^2 / 25 * (something O(1))    pure length term  : test excess <= ell(f)^2/25? (a LOCAL length bound!)
      -- this is interesting: ell(f)^2/25 is local to f. If excess(P)<=ell(f)^2/25 held, that's a local proof.
 (L6) sum_{g meets P} ell(g)^2/25   [Gamma restricted to bad edges meeting P]  -- semi-local
Report which (if any) survive the standing gate.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _verify_two_lane import build_two_lane

def pf_field(M,cyc):
    pf={}
    for g in M:
        k=len(cyc[g]); d={}
        for P in cyc[g]:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    return pf

def analyze(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    N=n; m=len(M)
    pf=pf_field(M,cyc)
    # cross-degree in B for each vertex
    crossdeg={}
    for v in range(n):
        crossdeg[v]=sum(1 for w in adj[v] if side[w]!=side[v])
    for f in M:
        for P in cyc[f]:
            Pset=set(P)
            excess=sum(T[v]-N for v in P)
            if excess<=0: continue
            meet=[g for g in M if any(pf[g].get(v,F(0))>0 for v in P)]
            nmeet=len(meet)
            # L1
            L1=F(ell[f]*nmeet,25)
            # L3: sum of cross-degrees on P
            L3=F(sum(crossdeg[v] for v in P))
            # L4: B-edges incident to P
            bedgesP=set()
            for v in P:
                for w in adj[v]:
                    if side[w]!=side[v]: bedgesP.add((min(v,w),max(v,w)))
            L4=F(ell[f]*len(bedgesP),25)
            # L5: pure local length term
            L5=F(ell[f]*ell[f],25)
            # L6: semi-local Gamma over meeting bad edges
            L6=F(sum(ell[g]**2 for g in meet),25)
            for key,val in [('L1',L1),('L3',L3),('L4',L4),('L5',L5),('L6',L6)]:
                mar=val-excess
                if mar<acc[key][0]: acc[key]=(mar,name,N,m,str(f),str(excess),str(val))
                if mar<0: acc[key+'_v']+=1

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

if __name__=="__main__":
    keys=['L1','L3','L4','L5','L6']
    acc={k:(F(10**9),'','','','','','') for k in keys}
    for k in keys: acc[k+'_v']=0
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); analyze("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: analyze("cen%s"%g6,n,adj,s,acc)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): analyze("C%d[%d]"%(cyc,t),n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)N23",mycg),("M(C7)",mycielski(7,Cn(7)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: analyze(name,nn,adj,s,acc)
    print("=== LOCAL-realizable candidate bounds on excess(P) (proof-by-switch test) ===",flush=True)
    desc={'L1':'ell*nmeet/25','L3':'sum crossdeg_B on P','L4':'ell*#Bedges(P)/25','L5':'ell^2/25 (pure local length)','L6':'Gamma|meet /25'}
    for k in keys:
        print("  %-4s (%s): min margin=%s viol=%d at %s"%(k,desc[k],float(acc[k][0]),acc[k+'_v'],acc[k][1:]),flush=True)
    print("\n  => Any candidate with viol>0 CANNOT be a local switch-realizable proof of path-LRS.",flush=True)
