import subprocess
import _crux_extract as cx
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side

tot=0; negrows=0; okx=0; failx=0; nonmin=0; failex=None
for nn in range(5,11):
    for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
        n,E=dec(g6); adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        mc,cuts=cx.all_max_cuts(n,adj,E)
        structs=[]
        for side in cuts:
            if not Bconn(n,adj,side): continue
            st=struct_for_side(n,adj,side)
            if st is None: continue
            structs.append((side,st,sum(st[2])))
        if not structs: continue
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
                    tot+=1
                    if mintail<0:
                        negrows+=1
                        if G>gmin: nonmin+=1
                        ok,dg,sz=cx.test_extraction(n,adj,side,M,G,P)
                        if ok: okx+=1
                        else:
                            failx+=1
                            if failex is None: failex=(g6,n,ell[f],tuple(P),str(mintail),G>gmin)
    print('through N=%d: rows=%d Tail<0=%d (nonmin=%d) ok=%d fail=%d'%(nn,tot,negrows,nonmin,okx,failx),flush=True)
print('DONE: total rows=%d, Tail<0 rows=%d, extract_ok=%d, extract_fail=%d'%(tot,negrows,okx,failx))
print('fail example:', failex)
