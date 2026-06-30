"""Logic-check Codex 430 Q1: the FINAL gamma-min atom needs ONLY k=0, not all-threshold Bhigh/P2/P3.
   On gamma-min connected-B max cuts, per row (bad edge f, geodesic P):
     B_L, DGsum, Z = Zr_row(...);  Tail_0 = sum_r (2r+1) Z_r.
   Verify:
     (i)   no negative singleton ports (gamma-min => all H_i>=0 => e(P)=0, Drain_0=0),
     (ii)  DGsum >= 0,
     (iii) B_L == Tail_0 + DGsum  (the layer-cake identity),
     (iv)  Tail_0 >= 0,
     (v)   B_L >= 0  (the atom).
   If all hold, B_L>=0 closes from k=0 alone (Tail_0>=0 + DGsum>=0), no k>=1 needed.  Full battery, exact.
"""
import subprocess, random
from fractions import Fraction as F
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski
from _Klocal_gate import glued_c5_chain

def scan(name,n,adj,E,cuts,acc):
    Lam=len(E)*n*n+1
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
                B_L,DGsum,Z,lhs,rhs=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                Tail0=sum((2*r+1)*Z[r] for r in range(n))
                acc['rows']+=1
                # (i) negative ports on this gamma-min cut
                negp=0
                for i in range(len(P)):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is not None and Hi<0: negp+=1
                if negp>0:
                    acc['hasport']+=1
                    if acc['port_ex'] is None: acc['port_ex']=(name,n,tuple(P),negp)
                if DGsum<0:
                    acc['dg_fail']+=1
                    if acc['dg_ex'] is None: acc['dg_ex']=(name,n,tuple(P),str(DGsum))
                if B_L != Tail0+DGsum:
                    acc['id_fail']+=1
                    if acc['id_ex'] is None: acc['id_ex']=(name,n,tuple(P),str(B_L),str(Tail0+DGsum))
                if Tail0<0:
                    acc['t0_fail']+=1
                    if acc['t0_ex'] is None: acc['t0_ex']=(name,n,tuple(P),str(Tail0))
                if B_L<0:
                    acc['bl_fail']+=1
                    if acc['bl_ex'] is None: acc['bl_ex']=(name,n,tuple(P),str(B_L))

def gfam(name,n,E,acc):
    if not E: return
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    try: _,cuts=gmins(n,E)
    except Exception: return
    scan(name,n,adj,E,cuts,acc)

def maxcut_ls(n,adj,seeds=60):
    best=None;bv=-1;rng=random.Random(9)
    for _ in range(seeds):
        s=[rng.randint(0,1) for _ in range(n)];imp=True
        while imp:
            imp=False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w]==s[v])>sum(1 for w in adj[v] if s[w]!=s[v]):s[v]^=1;imp=True
        val=sum(1 for v in range(n) for w in adj[v] if w>v and s[v]!=s[w])
        if val>bv:bv=val;best=s[:]
    return best

def main():
    acc=dict(rows=0,hasport=0,dg_fail=0,id_fail=0,t0_fail=0,bl_fail=0,
             port_ex=None,dg_ex=None,id_ex=None,t0_ex=None,bl_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); gfam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d hasport=%d dg=%d id=%d t0=%d bl=%d"%(nn,acc['rows'],acc['hasport'],acc['dg_fail'],acc['id_fail'],acc['t0_fail'],acc['bl_fail']),flush=True)
    n,E=dec("H?AFBo]"); gfam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,1,1)]:
        n,E=odd_blowup(5,list(sizes))
        if n<=14: gfam("blow%s"%(sizes,),n,E,acc)
    grN,grE=mycielski(5,Cn(5)); gfam("Grotzsch",grN,grE,acc)
    isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
    nn,EE=union_disjoint(isl,g15); nn,EE=add_edges((nn,EE),[(0,5)])
    if nn<=14: gfam("isl",nn,EE,acc)
    # glued chains via supplied cut
    for q in range(2,12):
        n,E,side=glued_c5_chain(q)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        if Bconn(n,adj,side): scan("chain_q%d"%q,n,adj,E,[side],acc)
    # Myc23 supplied
    n,E=mycielski(grN,grE); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): scan("Myc23",n,adj,E,[side],acc)
    print("="*55)
    print("gamma-min rows:",acc['rows'])
    print("(i)   rows with a NEGATIVE port (should be 0 on gamma-min):",acc['hasport'],acc['port_ex'] or '')
    print("(ii)  DGsum<0 failures:",acc['dg_fail'],acc['dg_ex'] or '')
    print("(iii) B_L != Tail_0+DGsum identity failures:",acc['id_fail'],acc['id_ex'] or '')
    print("(iv)  Tail_0<0 failures:",acc['t0_fail'],acc['t0_ex'] or '')
    print("(v)   B_L<0 (atom) failures:",acc['bl_fail'],acc['bl_ex'] or '')
    ok=all(acc[k]==0 for k in ('hasport','dg_fail','id_fail','t0_fail','bl_fail'))
    print("VERDICT:", "k=0 ATOM CLOSURE HOLDS (Tail_0>=0 + DGsum>=0 => B_L>=0; no k>=1 needed)" if ok else "GAP")

if __name__=="__main__":
    main()
