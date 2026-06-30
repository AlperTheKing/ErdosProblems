"""Scale-gate the one-way contrapositive  (all singleton ports closed: H_i>=0 for all i)  =>  Tail_k>=0
   on stress families RICH in non-gamma-min max cuts + census N=11.  Reports any row with min_i H_i>=0 but
   Tail_k<0 (a falsifier of the one-port proof route).  Reuses _singleton_core helpers.
"""
import subprocess
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski

def run(name,n,E,acc):
    Lam=len(E)*n*n+1
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    mc,cuts=cx.all_max_cuts(n,adj,E)
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        em0=ell_map(n,adj,side)
        for f in M:
            if ell[f]%2==0: continue
            for P in cyc[f]:
                if len(P)!=ell[f]: continue
                _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                mintail=min(sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n))
                acc['rows']+=1
                minH=None
                for i in range(len(P)):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None: continue
                    if minH is None or Hi<minH: minH=Hi
                if mintail<0: acc['neg']+=1
                if (minH is None or minH>=0) and mintail<0:
                    acc['viol']+=1
                    if acc['ex'] is None: acc['ex']=(name,n,tuple(P),str(mintail),str(minH))

def main():
    acc=dict(rows=0,neg=0,viol=0,ex=None)
    # theta
    for g6 in ["G?Fw","G?bFw","G?rFw","H?AFBo]"]:
        try:
            n,E=dec(g6); run("thw-"+g6,n,E,acc)
        except Exception: pass
    print("theta: rows=%d neg=%d viol=%d"%(acc['rows'],acc['neg'],acc['viol']),flush=True)
    # glued islands
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9)
    for (a,b,br) in [((n5,E5),(n5,E5),[(0,5)]),((n5,E5),(n7,E7),[(0,5)]),((n5,E5),(n7,E7),[(0,5),(2,8)]),
                     ((n7,E7),(n5,E5),[(0,7)]),((n5,E5),(n9,E9),[(0,5)]),((n7,E7),(n7,E7),[(0,7)])]:
        n,E=union_disjoint(a,b); E=E+br
        if n<=14: run("glue",n,E,acc)
    print("glued: rows=%d neg=%d viol=%d"%(acc['rows'],acc['neg'],acc['viol']),flush=True)
    # blowups
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,1,1),(3,1,2,1,2)]:
        n,E=odd_blowup(5,list(sizes))
        if n<=12: run("blow",n,E,acc)
    grN,grE=mycielski(5,Cn(5)); run("Grotzsch",grN,grE,acc)
    print("blow+Grotzsch: rows=%d neg=%d viol=%d"%(acc['rows'],acc['neg'],acc['viol']),flush=True)
    # census N=11
    for g6 in subprocess.run([GENG,'-tc','11'],capture_output=True,text=True).stdout.split():
        n,E=dec(g6); run("cen11",n,E,acc)
    print("="*55)
    print("TOTAL rows:%d  Tail<0:%d  CONTRAPOSITIVE violations (minH>=0 & Tail<0):%d"%(acc['rows'],acc['neg'],acc['viol']))
    print("falsifier:", acc['ex'])
    print("VERDICT:", "ONE-WAY (all ports closed => Tail>=0) HOLDS on stress+N11" if acc['viol']==0 else "FALSIFIED")

if __name__=="__main__":
    main()
