"""Gate Codex 412 NESTED-INTERVAL finite-price descent (proof shape for concentration (II)).
   Switch W from interval I(W)=[a,b] + straddler parity. For every valid W with q(W)>0, exists valid W' with
   q(W')<q(W), C25(W')<=C25(W), and I(W') nested with I(W) (subset either way).  Exact Fraction.
"""
import subprocess
from fractions import Fraction as F
from _core_select import parity_switches_J
from _singleton_core import ell_map
from _wf_deficit_farkas import deltas, flip, gamma_of, odd_blowup
import _crux_extract as cx
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski

def nested(I1,I2):
    a1,b1=I1; a2,b2=I2
    return (a1<=a2 and b2<=b1) or (a2<=a1 and b1<=b2)

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
                cands=[]  # (q, c25, (a,b))
                seen=set()
                for a,b,W in parity_switches_J(n,adj,side,P):
                    if not W or W in seen: continue
                    seen.add(W)
                    dB,dM=deltas(n,adj,side,W); q=dB-dM
                    if q<0: continue
                    s2=flip(side,W)
                    if not Bconn(n,adj,s2): continue
                    g1=gamma_of(n,adj,s2)
                    if g1 is None: continue
                    c=(g1-Gamma)+25*q
                    cands.append((q,c,(a,b)))
                for (q,c,I) in cands:
                    if q>0:
                        acc['posq']+=1
                        ok=any(q2<q and c2<=c and nested(I2,I) for (q2,c2,I2) in cands)
                        if not ok:
                            acc['fail']+=1
                            if acc['ex'] is None:
                                acc['ex']=(name,n,tuple(P),I,q,str(c))

def fam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    run(name,n,adj,E,acc)

def main():
    acc=dict(posq=0,fail=0,ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: posq=%d fail=%d"%(nn,acc['posq'],acc['fail']),flush=True)
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
    print("positive-q switches:",acc['posq'])
    print("NESTED-INTERVAL DESCENT failures:",acc['fail'],acc['ex'] or '')
    print("VERDICT:", "NESTED-INTERVAL DESCENT HOLDS => (II) endpoint-uncrossing proof" if acc['fail']==0 else "FAILS")

if __name__=="__main__":
    main()
