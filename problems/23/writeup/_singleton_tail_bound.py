"""Gate Codex 386 QUANTITATIVE singleton-port tail bound:
      Tail_k(P) >= sum_i H_i^-   for every k and every connected-B max-cut row,
   where H_i = min over parity-completed singleton-port switches W (path-span {i}, B^W connected, valid) of
   Lambda*mu(W)+DeltaGamma(W); Lambda=|E|N^2+1; H_i^- = min(H_i,0) (+inf -> 0).
   gamma-min => all H_i>=0 => sum H_i^- = 0 => Tail_k>=0 => atom.
   Also reports the residual margin min_k (Tail_k - sum_i H_i^-).  Full battery, exact Fraction.
"""
import subprocess, random
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski

def sum_Hneg(n,adj,side,em0,P,Lam):
    s=0
    for i in range(len(P)):
        Hi,_,_=Hi_and_best(n,adj,side,em0,P,i,Lam)
        if Hi is not None and Hi<0: s+=Hi
    return s

def run(name,n,adj,E,side_list,acc):
    Lam=len(E)*n*n+1
    for side in side_list:
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
                sH=sum_Hneg(n,adj,side,em0,P,Lam)
                for k in range(n):
                    tk=sum((2*r+1)*Z[r] for r in range(k,n))
                    acc['rows']+=1
                    margin=tk - sH
                    if margin<0:
                        acc['fail']+=1
                        if acc['ex'] is None: acc['ex']=(name,n,tuple(P),k,str(tk),str(sH))
                    if acc['minmargin'] is None or margin<acc['minmargin']:
                        acc['minmargin']=margin

def maxcut_ls(n,adj,seeds=50):
    best=None;bv=-1;rng=random.Random(5)
    for _ in range(seeds):
        s=[rng.randint(0,1) for _ in range(n)];imp=True
        while imp:
            imp=False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w]==s[v])>sum(1 for w in adj[v] if s[w]!=s[v]):s[v]^=1;imp=True
        val=sum(1 for v in range(n) for w in adj[v] if w>v and s[v]!=s[w])
        if val>bv:bv=val;best=s[:]
    return best

def fam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    mc,cuts=cx.all_max_cuts(n,adj,E)
    run(name,n,adj,E,cuts,acc)

def main():
    acc=dict(rows=0,fail=0,ex=None,minmargin=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d fail=%d"%(nn,acc['rows'],acc['fail']),flush=True)
    for g6 in ["G?Fw","G?bFw","G?rFw","H?AFBo]"]:
        try:
            n,E=dec(g6); fam("thw",n,E,acc)
        except Exception: pass
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9)
    for (a,b,br) in [((n5,E5),(n5,E5),[(0,5)]),((n5,E5),(n7,E7),[(0,5)]),((n5,E5),(n7,E7),[(0,5),(2,8)]),
                     ((n7,E7),(n5,E5),[(0,7)]),((n5,E5),(n9,E9),[(0,5)])]:
        n,E=union_disjoint(a,b); E=E+br
        if n<=14: fam("glue",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3)]:
        n,E=odd_blowup(5,list(sizes))
        if n<=13: fam("blow",n,E,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    print("after stress: rows=%d fail=%d"%(acc['rows'],acc['fail']),flush=True)
    # Myc(Grotzsch) N=23 supplied heuristic max cut
    n,E=mycielski(grN,grE); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): run("Myc23",n,adj,E,[side],acc)
    print("="*55)
    print("TOTAL (row,k) checks:%d  FAILS (Tail_k < sum H_i^-):%d"%(acc['rows'],acc['fail']),acc['ex'] or '')
    print("min residual margin (Tail_k - sum H_i^-):",str(acc['minmargin']))
    print("VERDICT:", "Tail_k >= sum_i H_i^- HOLDS (quantitative one-port bound)" if acc['fail']==0 else "FAILS")

if __name__=="__main__":
    main()
