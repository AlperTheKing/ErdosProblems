"""ROUTE A lever-hunt. EXACT (Fraction). For each battery graph + gamma-min cut, build p_f(v)=frac of bad-edge
f's shortest alt-geodesics through v; s(v)=Sum_f p_f(v) (UNWEIGHTED congestion); T(v)=Sum_f p_f(v)*ell(f).
ROWSUM-O target: rowsum_O(f) = Sum_v p_f(v) s(v) = (O.1)(f) <= N for every bad edge f  => rho(O)<=N => Gamma<=N^2.
Confirm <=N on battery; dump GLOBAL argmax structure + test candidate analytic levers:
  (Q1) s(v) <= N always?  max s(v)/N.
  (Q2) Is rowsum_O(f) <= L_f * max_{v in supp p_f} s(v)?  (trivial) and is that <=N?
  (Q3) per-edge support size |supp p_f| and L_f=Sum p_f vs N.
  (Q4) DECOMPOSE argmax: list (v, p_f(v), s(v), T(v), p_f*s) sorted by contribution."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def build_ps(n,M,cyc):
    P={}  # P[f] = dict v->Fraction
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        P[f]={v:F(c,nf) for v,c in cnt.items()}
    s=[F(0)]*n
    for f in M:
        for v,pv in P[f].items(): s[v]+=pv
    return P,s

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    P,s=build_ps(n,M,cyc)
    # max s
    smax=max(s) if s else F(0)
    if smax>acc['smax'][0]: acc['smax']=(smax,name,n)
    for f in M:
        pf=P[f]
        rs=sum(pv*s[v] for v,pv in pf.items())   # rowsum_O(f) = <p_f, s>
        Lf=sum(pf.values())
        ratio=rs/F(n)
        if ratio>acc['best'][0]:
            supp=sorted(pf.keys())
            decomp=sorted(([str(pf[v]),str(s[v]),str(T[v]),str(pf[v]*s[v]),v] for v in supp),
                          key=lambda d:-(F(d[3])))
            acc['best']=(ratio,name,n,str(rs),str(Lf),len(supp),decomp,ell[f])
        if rs>F(n):
            acc['viol']+=1
            if acc['fviol'] is None: acc['fviol']=(name,n,str(rs))

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
    acc=dict(best=(F(-1),'',0,'','',0,[],0),viol=0,fviol=None,smax=(F(0),'',0))
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
        print("  census N=%d done (viol=%d, best ratio=%s)"%(nn,acc['viol'],str(float(acc['best'][0]))[:7]),flush=True)
    b=acc['best']
    print("\n  ROWSUM-O: rowsum_O(f)<=N violations=%d %s"%(acc['viol'],acc['fviol'] or ''),flush=True)
    print("  max s(v)/N = %s = %s  @ %s N=%d"%(str(acc['smax'][0]),str(float(acc['smax'][0]))[:7],acc['smax'][1],acc['smax'][2]),flush=True)
    print("  GLOBAL argmax rowsum_O: ratio=%s=%s @ %s N=%d  rs=%s L_f=%s ell_f=%s |supp|=%d"%(
        str(b[0]),str(float(b[0]))[:7],b[1],b[2],b[3],b[4],b[7],b[5]),flush=True)
    print("  decomp (p_f(v), s(v), T(v), p_f*s, v) sorted by contribution:",flush=True)
    for d in b[6][:20]: print("    pf=%s s=%s T=%s contrib=%s v=%d"%(d[0],d[1],d[2],d[3],d[4]),flush=True)
    print("  === ROWSUM-O %s ==="%("HOLDS (rho(O)<=N) on full battery" if acc['viol']==0 else "FAILS"),flush=True)
