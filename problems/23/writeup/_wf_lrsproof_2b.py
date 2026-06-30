"""PATH-LRS proof — probe the LOCALITY of the deficit excess(P)=sum_{v in P}(T-N).
Goal: find a NON-CIRCULAR upper bound on excess(P) (no Gamma<=N^2, no |M|<=N^2/25, no Erdos).

excess(P) = sum_g ell(g) w_g(P) - N*ell(f),  w_g(P)=sum_{v in P} p_g(v).

Test candidate LOCAL bounds on excess(P):
 (M) LOCAL-MEET:   excess(P) <= ell(f) * nmeet / 25,  nmeet=#{g: supp(p_g) meets P}.
                   (replaces global |M| budget with the LOCAL count of bad edges seen by P)
 (G) GAMMA-form:   excess(P) <= ell(f) * (N^2 - Gamma)/25   (still global Gamma; circular-ish but a check)
 (T) TARGET:       excess(P) <= ell(f) * (N^2/25 - |M|).
We report min margins on the standing gate and whether (M) survives (would be a genuinely local lever).
Also: distribution of w_g(P) per g vs ell(g)/N (the 'fair share' at the C5[t] extremal)."""
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
    Gamma=sum(ell[g]**2 for g in M)
    for f in M:
        for P in cyc[f]:
            excess=sum(T[v]-N for v in P)
            meet=[g for g in M if any(pf[g].get(v,F(0))>0 for v in P)]
            nmeet=len(meet)
            cand_meet=F(ell[f]*nmeet,25)
            cand_gam=F(ell[f]*(N*N-Gamma),25)
            target=F(ell[f])*(F(N*N,25)-m)
            acc['paths']+=1
            if excess>0:
                acc['pos']+=1
                r1=cand_meet-excess
                r2=cand_gam-excess
                if r1<acc['min_meet'][0]: acc['min_meet']=(r1,name,n,m,str(f),str(excess),nmeet,ell[f])
                if r2<acc['min_gam'][0]: acc['min_gam']=(r2,name,n,m,str(f),str(excess),Gamma)
            rt=target-excess
            if rt<acc['min_t'][0]: acc['min_t']=(rt,name,n,m,str(f))

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
    acc=dict(paths=0,pos=0,
             min_meet=(F(10**9),'','','','','',0,0),
             min_gam=(F(10**9),'','','','','',0),
             min_t=(F(10**9),'','','',''))
    print("=== PATH-LRS: locality of excess(P)=sum_{v in P}(T-N) ===",flush=True)
    for L in range(8,17,2):
        n,E,side,_=build_two_lane(L); analyze("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    print("  two-lane done min_meet=%s"%float(acc['min_meet'][0]),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: analyze("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done min_meet=%s"%(nn,float(acc['min_meet'][0])),flush=True)
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
    print("\n  total paths=%d  positive-excess paths=%d"%(acc['paths'],acc['pos']),flush=True)
    print("  TARGET (true) min margin = %s at %s"%(float(acc['min_t'][0]),acc['min_t'][1:]),flush=True)
    print("  LOCAL-MEET (excess<=ell*nmeet/25) min margin = %s at %s"%(float(acc['min_meet'][0]),acc['min_meet'][1:]),flush=True)
    print("  GAMMA-form (excess<=ell*(N^2-Gamma)/25) min margin = %s at %s"%(float(acc['min_gam'][0]),acc['min_gam'][1:]),flush=True)
