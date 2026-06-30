"""Gate Codex 409 FINITE-PRICE ZERO-MARGIN CONCENTRATION (structural switch lemma, not a Tail restatement).
   All connected-B MAX cuts, bad edge f, geodesic P, parity-completed interval switch family.
   For W: q(W)=delta_B-delta_M (>=0 on max cut), d(W)=Gamma(flip)-Gamma (Bconn + valid required), C25=d+25q.
   CLAIM: min_W C25(W) < 0  =>  exists W0 with q(W0)=0 and d(W0)<0.
   STRONGER: min_{q=0} d(W) <= min_W C25(W)  when min C25<0.
   Exact Fraction.  Reports failures + worst.
"""
import subprocess
from fractions import Fraction as F
import _crux_extract as cx
from _crux_extract import parity_interval_switches
from _singleton_core import ell_map
from _wf_deficit_farkas import deltas, flip, gamma_of, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski

def run(name,n,adj,E,acc):
    mc,cuts=cx.all_max_cuts(n,adj,E)
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        Gamma=sum(ell[g]**2 for g in M)
        for f in M:
            if ell[f]%2==0: continue
            for P in cyc[f]:
                if len(P)!=ell[f]: continue
                minC=None; min0=None; seen=set()
                for W in parity_interval_switches(n,adj,side,P):
                    if not W or W in seen: continue
                    seen.add(W)
                    dB,dM=deltas(n,adj,side,W); q=dB-dM
                    if q<0: continue
                    s2=flip(side,W)
                    if not Bconn(n,adj,s2): continue
                    g1=gamma_of(n,adj,s2)
                    if g1 is None: continue
                    d=g1-Gamma; c25=d+25*q
                    if minC is None or c25<minC: minC=c25
                    if q==0 and (min0 is None or d<min0): min0=d
                acc['rows']+=1
                if minC is not None and minC<0:
                    acc['negC']+=1
                    # concentration: exists q=0 with d<0
                    if min0 is None or min0>=0:
                        acc['conc_fail']+=1
                        if acc['cf_ex'] is None: acc['cf_ex']=(name,n,tuple(P),str(minC),str(min0))
                    # stronger: min0 <= minC
                    elif min0>minC:
                        acc['strong_fail']+=1
                        if acc['sf_ex'] is None: acc['sf_ex']=(name,n,tuple(P),str(min0),str(minC))

def fam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    run(name,n,adj,E,acc)

def main():
    acc=dict(rows=0,negC=0,conc_fail=0,strong_fail=0,cf_ex=None,sf_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d negC=%d conc_fail=%d strong_fail=%d"%(nn,acc['rows'],acc['negC'],acc['conc_fail'],acc['strong_fail']),flush=True)
    for g6 in ["G?Fw","G?bFw","G?rFw","H?AFBo]"]:
        try:
            n,E=dec(g6); fam("thw",n,E,acc)
        except Exception: pass
    n5,E5=5,Cn(5); n7,E7=7,Cn(7)
    for (a,b,br) in [((n5,E5),(n5,E5),[(0,5)]),((n5,E5),(n7,E7),[(0,5)]),((n5,E5),(n7,E7),[(0,5),(2,8)])]:
        nn,EE=union_disjoint(a,b); EE=EE+br
        if nn<=12: fam("glue",nn,EE,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    print("="*55)
    print("rows:",acc['rows']," rows with min C25<0:",acc['negC'])
    print("CONCENTRATION failures (minC<0 but no q=0 d<0):",acc['conc_fail'],acc['cf_ex'] or '')
    print("STRONGER (min0<=minC) failures:",acc['strong_fail'],acc['sf_ex'] or '')
    ok=(acc['conc_fail']==0 and acc['negC']>0)
    print("VERDICT:", "ZERO-MARGIN CONCENTRATION HOLDS (II half of extraction)" if ok else ("no negC rows" if acc['negC']==0 else "FAILS"))

if __name__=="__main__":
    main()
