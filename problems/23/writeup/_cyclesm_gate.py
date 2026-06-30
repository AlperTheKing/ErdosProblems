"""ROUTE A, tight form. EXACT (Fraction). CYCLE-SM: for every bad edge f,
    Sum_v p_f(v) T(v) <= N * ell(f)     <=>   Sum_v p_f(v)(T(v)-N) <= 0   <=>   E_{v~p_f}[T(v)] <= N.
Since all of f's shortest alt-geodesics share length ell(f), Sum_v p_f(v)=ell(f); so this is exactly:
  the p_f-weighted average geodesic load is <= N.  Collatz-Wielandt with x=ell (Perron at extremal) =>
  rho(O)<=N => (SM) Sum T^2<=N*Gamma => Gamma<=N^2 => #23.
Gate Cycle-SM on full battery; report max ratio (Sum p_f T)/(N ell_f), argmax. Dump argmax geodesic T-profile
to expose anti-concentration (overloaded vtxs carry small p_f). Also test per-geodesic balance lever:
  (BAL) Sum_v p_f(v)(T(v)-N)_+ <= Sum_v p_f(v)(N-T(v))_+   [== Cycle-SM, the overload<=underload-along-geodesic form]."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def build_ps(n,M,cyc):
    P={}
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        P[f]={v:F(c,nf) for v,c in cnt.items()}
    return P

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    P=build_ps(n,M,cyc)
    for f in M:
        pf=P[f]
        num=sum(pv*T[v] for v,pv in pf.items())      # Sum p_f T
        Lf=sum(pf.values())                           # = ell(f)
        den=F(n)*ell[f]
        ratio=num/den
        if ratio>acc['best'][0]:
            prof=sorted(([str(pf[v]),str(T[v]),str(T[v]-F(n)),str(pf[v]*(T[v]-F(n))),v] for v in pf),
                        key=lambda d:-(F(d[1])))
            acc['best']=(ratio,name,n,str(num),str(Lf),ell[f],prof)
        if num>den:
            acc['viol']+=1
            if acc['fviol'] is None: acc['fviol']=(name,n,str(num),str(den))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc=dict(best=(F(-1),'',0,'','',0,[]),viol=0,fviol=None)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for ss in (cuts[:2] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,ss,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0)),("C5|C5",bridge((5,Cn(5)),(5,Cn(5)),0,0))]:
        adj,cuts=gmins(nn,E)
        for ss in cuts[:3]: chk(nm,nn,adj,ss,acc)
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for ss in cuts: chk("cen%s"%g6,n,adj,ss,acc)
        print("  census N=%d done (viol=%d, best=%s)"%(nn,acc['viol'],str(float(acc['best'][0]))[:7]),flush=True)
    b=acc['best']
    print("\n  CYCLE-SM: Sum p_f T <= N ell_f  violations=%d %s"%(acc['viol'],acc['fviol'] or ''),flush=True)
    print("  GLOBAL argmax ratio=%s=%s @ %s N=%d  Sum_pT=%s ell_f=%d"%(str(b[0]),str(float(b[0]))[:7],b[1],b[2],b[3],b[5]),flush=True)
    print("  argmax geodesic T-profile (p_f(v), T(v), T-N, p_f*(T-N), v) sorted by T desc:",flush=True)
    over=F(0); under=F(0)
    for d in b[6][:25]:
        print("    pf=%s T=%s T-N=%s contrib=%s v=%d"%(d[0],d[1],d[2],d[3],d[4]),flush=True)
    for d in b[6]:
        c=F(d[3])
        if c>0: over+=c
        else: under+=-c
    print("  argmax: overload-mass Sum p_f(T-N)_+ = %s ; underload-mass Sum p_f(N-T)_+ = %s ; (BAL over<=under: %s)"%(
        str(over),str(under),"YES" if over<=under else "NO"),flush=True)
    print("  === CYCLE-SM %s ==="%("HOLDS (=> rho(O)<=N => Gamma<=N^2) on full battery" if acc['viol']==0 else "FAILS"),flush=True)
