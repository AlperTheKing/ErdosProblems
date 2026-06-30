"""Escalate the switch-extraction crux on families RICH in non-gamma-min max cuts:
   theta-witnesses, glued islands (many independent-island max cuts), census N=11.
   Tests: every Tail_k<0 row has a neutral connected Gamma-decreasing parity-interval switch.
"""
import subprocess
import _crux_extract as cx
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski
from _wf_deficit_farkas import odd_blowup

def run(name, n, E, acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    mc,cuts=cx.all_max_cuts(n,adj,E)
    structs=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        structs.append((side,st,sum(st[2])))
    if not structs: return
    gmin=min(g for (_,_,g) in structs)
    for (side,st,G) in structs:
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        for f in M:
            if ell[f]%2==0: continue
            for P in cyc[f]:
                if len(P)!=ell[f]: continue
                _,_,Z,lhs,rhs=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                mintail=min(sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n))
                acc['rows']+=1
                if mintail<0:
                    acc['neg']+=1
                    if G>gmin: acc['nonmin']+=1
                    ok,dg,sz=cx.test_extraction(n,adj,side,M,G,P)
                    if ok: acc['ok']+=1
                    else:
                        acc['fail']+=1
                        if acc['ex'] is None: acc['ex']=(name,n,ell[f],tuple(P),str(mintail))

def main():
    acc=dict(rows=0,neg=0,nonmin=0,ok=0,fail=0,ex=None)
    # theta witnesses
    for g6 in ["G?Fw","G?bFw","G?rFw","H?AFBo]"]:
        try:
            n,E=dec(g6); run("thw-"+g6,n,E,acc)
        except Exception: pass
    print("after theta: rows=%d neg=%d ok=%d fail=%d"%(acc['rows'],acc['neg'],acc['ok'],acc['fail']),flush=True)
    # glued islands (N<=12 so all_max_cuts feasible)
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9)
    for (a,b,br) in [((n5,E5),(n5,E5),[(0,5)]), ((n5,E5),(n7,E7),[(0,5)]),
                     ((n5,E5),(n7,E7),[(0,5),(2,8)]), ((n7,E7),(n5,E5),[(0,7)]),
                     ((n5,E5),(n5,E5),[(0,5),(2,7)]), ((n5,E5),(n7,E7),[(1,6)])]:
        n,E=union_disjoint(a,b); E=E+br
        if n<=12: run("glue",n,E,acc)
    print("after glued: rows=%d neg=%d nonmin=%d ok=%d fail=%d"%(acc['rows'],acc['neg'],acc['nonmin'],acc['ok'],acc['fail']),flush=True)
    # small blowups (non-uniform -> non-gamma-min max cuts)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,1,1)]:
        n,E=odd_blowup(5,list(sizes))
        if n<=12: run("C5blow",n,E,acc)
    print("after blowups: rows=%d neg=%d nonmin=%d ok=%d fail=%d"%(acc['rows'],acc['neg'],acc['nonmin'],acc['ok'],acc['fail']),flush=True)
    # census N=11
    for g6 in subprocess.run([GENG,'-tc','11'],capture_output=True,text=True).stdout.split():
        n,E=dec(g6); run("cen11",n,E,acc)
    print("="*55)
    print("TOTAL rows:%d  Tail<0:%d (nonmin:%d)  extract_ok:%d  extract_fail:%d"%(acc['rows'],acc['neg'],acc['nonmin'],acc['ok'],acc['fail']))
    print("fail example:", acc['ex'])
    print("VERDICT:", "EVERY Tail<0 row extracts a neutral Gamma-decreasing switch" if acc['fail']==0 and acc['neg']>0 else ("no Tail<0 witnesses" if acc['neg']==0 else "FALSIFIED"))

if __name__=="__main__":
    main()
