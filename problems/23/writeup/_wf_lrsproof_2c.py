"""Test whether the GAMMA-form  25*excess(P) <= ell(f)*(N^2 - Gamma)  is a NON-CIRCULAR lever, i.e.
whether assuming it (for the worst f,P) ALREADY forces Gamma <= N^2 by a clean averaging -- OR whether
it could hold with Gamma > N^2 (in which case proving it is NOT equivalent to Erdos, i.e. genuinely a
proof obligation that, IF proven by a switch argument, yields Erdos).

We also test the cleanest candidate that AVOIDS the -Gamma on the RHS entirely:

  Reformulate the TARGET path-LRS as a deficit-pooling statement that is provable per-vertex.
  excess(P)=sum_{v in P}(T(v)-N).  Use sum_v T(v)=Gamma (load identity).  Average target over ALL geodesics:
  This is exactly ROW-LRS -> LRS, already an identity chain. So the ONLY open atom is path-LRS itself.

  Question: is there a per-vertex charge c(v)>=0 with sum_{v} c(v) <= N^2/25 - |M| (global) such that
  T(v) - N <= ell(f)/ell(f) ... no.  Instead test the 'overload is rare on a geodesic' structural facts:
    - For each path P, list the overloaded vertices and their (T-N); is the TOTAL overload on P
      <= (N^2/25 - |M|)*ell(f) tight only when?  Record the equality locus.
    - Does excess(P) > 0 ONLY occur when |M| is small (sparse, two-lane-like)?  print (excess,|M|,N^2/25).
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
    Gamma=sum(ell[g]**2 for g in M)
    for f in M:
        for P in cyc[f]:
            excess=sum(T[v]-N for v in P)
            if excess>0:
                # record the GLOBAL context of every positive-excess path
                acc['rows'].append((str(name),N,m,F(N*N,25),Gamma,ell[f],str(excess),
                                    str(F(ell[f])*(F(N*N,25)-m)),  # target RHS
                                    str(F(ell[f]*(N*N-Gamma),25)))) # gamma RHS
            # equality locus of the TRUE target
            target=F(ell[f])*(F(N*N,25)-m)
            if target==excess and excess!=0:
                acc['eqpos'].append((str(name),N,m,ell[f],str(excess)))

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
    acc=dict(rows=[],eqpos=[])
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
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)N23",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: analyze(name,nn,adj,s,acc)
    print("=== positive-excess paths (the NON-trivial cases) ===",flush=True)
    print("  count=%d"%len(acc['rows']),flush=True)
    seen=set()
    for r in acc['rows']:
        key=(r[0],r[1],r[2],r[5],r[6])
        if key in seen: continue
        seen.add(key)
        print("  %-16s N=%d |M|=%d N^2/25=%s Gamma=%d ell=%d excess=%s targetRHS=%s gammaRHS=%s"%r,flush=True)
    print("=== TRUE-target equality at positive excess (proof must be tight here) ===",flush=True)
    for e in acc['eqpos'][:20]: print("  ",e,flush=True)
    print("  (none above => target equality only at excess=0, i.e. C5[t] / uniform-load)" if not acc['eqpos'] else "",flush=True)
