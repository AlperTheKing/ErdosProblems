"""PATH-LRS proof decomposition + EXACT validation of each intermediate claim, hunting counterexamples
on the standing gate (census gamma-min N<=11, two-lane, iterated Mycielskians N<=23, blow-ups).

PATH-LRS:  sum_{v in P} T(v) <= ell(f) * (N + N^2/25 - |M|)   for every bad edge f, geodesic P of f.
Equivalently avg load along P <= N + N^2/25 - |M|.

Decompose:  sum_{v in P} T(v) = sum_g ell(g) * w_g(P),  w_g(P) := sum_{v in P} p_g(v) (p_g-mass P collects from g).

Intermediate claims to test EXACTLY (each must hold or be reported as refuted):
 (I1) w_f(P) for the OWN bad edge f:  sum_{v in P} p_f(v).  P is one geodesic; layer mass of f is 1 per layer.
      Claim test: 1 <= w_f(P) <= ell(f)?  and what is its actual distribution (=ell(f) iff unique geodesic).
 (I2) per-other-g collection: w_g(P) <= ell(g)  (P collects at most g's total mass)? trivially yes since p_g<=1 ...
      sharper: w_g(P) <= |P cap supp(p_g)| and per-layer-of-g at most 1.
 (I3) The KEY decomposition into a 'path-vertex-load' bound: define for the path the quantity
      L(P) = sum_{v in P} T(v). We want L(P) <= ell(f)*N + ell(f)*(N^2/25 - |M|).
      Test the two-piece split:  (a) sum_{v in P} (T(v)-N) <= ell(f)*(N^2/25 - |M|)  [the deficit form]
      and whether (T(v)-N) summed over P relates to a max-cut SWITCH gain on the corridor.
 (I4) Per-vertex 'budget': is T(v) <= 2N (B2)? and max_{v in P} T(v)?
 (I5) The C5[t] extremal: T==N everywhere, |M|=t^2, N=5t, N^2/25=t^2=|M| => RHS deficit part=0,
      so PATH-LRS is sum_{v in P} N <= ell*N exactly tight (ell=5). Confirm equality.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn

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
    defi=F(N*N,25)-m   # the slack budget N^2/25 - |M|
    for f in M:
        for P in cyc[f]:
            Pset=set(P)
            # path-load decomposition
            L=sum(T[v] for v in P)
            # I1: own-edge mass on this path
            wf=sum(pf[f][v] for v in P)
            # I2: collected mass per g, and check w_g(P) <= |P cap supp g| and <= ell(g)
            for g in M:
                wg=sum(pf[g].get(v,F(0)) for v in P)
                cap=sum(1 for v in P if pf[g].get(v,F(0))>0)
                if wg>cap+F(0): acc['I2cap']+=1   # impossible since each p<=1
                if wg>ell[g]: acc['I2ell']+=1
            # I3a: deficit form
            lhs_def = sum(T[v]-N for v in P)   # = L - ell*N
            rhs_def = ell[f]*defi
            mar = rhs_def - lhs_def
            acc['paths']+=1
            if mar<acc['minmar'][0]: acc['minmar']=(mar,name,n,m,f,ell[f],str(lhs_def),str(rhs_def))
            if mar<0:
                acc['viol']+=1
                if acc['first'] is None: acc['first']=(name,n,m,f,ell[f],str(L),str(rhs_def))
            # I1 record: wf range
            if wf<acc['wf_min'][0]: acc['wf_min']=(wf,name,f,ell[f])
            if F(wf)/ell[f] > acc['wf_frac_max'][0]: acc['wf_frac_max']=(F(wf)/ell[f],name,f,ell[f])
            # max T on path vs 2N
            mxT=max(T[v] for v in P)
            if F(mxT)/N > acc['maxT_frac'][0]: acc['maxT_frac']=(F(mxT)/N,name,f)
            # count overloaded vertices on the path
            nover=sum(1 for v in P if T[v]>N)
            acc['nover_max']=max(acc['nover_max'],nover)

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
    from _verify_two_lane import build_two_lane
    acc=dict(paths=0,viol=0,first=None,I2cap=0,I2ell=0,
             minmar=(F(10**9),'','','','','','',''),
             wf_min=(F(10**9),'','',''),wf_frac_max=(F(-1),'','',''),
             maxT_frac=(F(-1),'',''),nover_max=0)
    print("=== PATH-LRS proof decomposition: deficit form sum_{v in P}(T-N) <= ell*(N^2/25-|M|) ===",flush=True)
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); analyze("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    print("  two-lane done (min-deficit-margin=%s)"%float(acc['minmar'][0]),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: analyze("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (viol=%d)"%(nn,acc['viol']-v0),flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): analyze("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): analyze("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)N23",mycg),("M(C7)",mycielski(7,Cn(7)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: analyze(name,nn,adj,s,acc)
    print("\n  total paths=%d  PATH-LRS(deficit form) VIOL=%d  I2cap-viol=%d  I2ell-viol=%d"%(
        acc['paths'],acc['viol'],acc['I2cap'],acc['I2ell']),flush=True)
    print("  MIN deficit margin = %s at %s"%(float(acc['minmar'][0]),acc['minmar'][1:]),flush=True)
    if acc['first']: print("  first viol: %s"%(acc['first'],),flush=True)
    print("  I1: min w_f(P)=%s at %s ; max w_f(P)/ell=%s at %s"%(
        str(acc['wf_min'][0]),acc['wf_min'][1:],float(acc['wf_frac_max'][0]),acc['wf_frac_max'][1:]),flush=True)
    print("  max_T(v)/N over path vertices = %s at %s  (B2 says <=2)"%(float(acc['maxT_frac'][0]),acc['maxT_frac'][1:]),flush=True)
    print("  max #overloaded vertices on a single geodesic path = %d"%acc['nover_max'],flush=True)
