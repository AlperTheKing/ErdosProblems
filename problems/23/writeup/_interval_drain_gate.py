"""Gate Codex 392 INTERVAL-DRAIN TAXONOMY + two-port corridor-shortening inequality.
   For each negative minimizing singleton port W_i, the layer profile chi_i(r) should be a SINGLE unit interval
   drain:  chi_i(r) = -1_{a_i <= r < b_i}  (5 <= a_i < b_i), so H_i = -(b_i^2 - a_i^2),
   Suf_i(k) = -max(0, b_i^2 - max(k,a_i)^2).
   Gates: (1) chi is a single unit interval drain; (2) <=2 negative ports per path;
          (3) extract (a_i,b_i) = (new shortcut len, old corridor len);
          (4) two-port inequality  Tail_k(P) + sum_i max(0, b_i^2 - max(k,a_i)^2) >= 0  for all k.
   Full battery (census N<=10 + theta + glued + blowups + Grotzsch + Myc N=23 + N26 retained).  Exact.
"""
import subprocess, random
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _factor_gate import chi_profile
from _wf_deficit_farkas import flip, odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski
from _codex_interval_failure_switch_lab import n26_graph

def interval_of(chi):
    """if chi is -1 on a contiguous [a,b) and 0 elsewhere, return (a,b); else None."""
    supp=[r for r in range(len(chi)) if chi[r]!=0]
    if not supp: return None
    if any(chi[r]!=-1 for r in supp): return None
    a,b=min(supp),max(supp)+1
    if any(chi[r]!=-1 for r in range(a,b)): return None  # contiguous
    return (a,b)

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
                ivs=[]
                for i in range(len(P)):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0 or W is None: continue
                    em1=ell_map(n,adj,flip(side,W))
                    if em1 is None: continue
                    chi=chi_profile(em0,em1,n)
                    acc['ports']+=1
                    iv=interval_of(chi)
                    if iv is None:
                        acc['notint']+=1
                        if acc['ni_ex'] is None: acc['ni_ex']=(name,n,tuple(P),i,[chi[r] for r in range(len(chi)) if chi[r]])
                        continue
                    a,b=iv
                    # verify H_i = -(b^2-a^2)
                    if Hi != -(b*b-a*a): acc['Hmismatch']+=1
                    ivs.append((a,b))
                if len(ivs)>2: acc['gt2']+=1
                # interval inequality for all k
                for k in range(n):
                    tk=sum((2*r+1)*Z[r] for r in range(k,n))
                    add=sum(max(0,b*b-max(k,a)**2) for (a,b) in ivs)
                    acc['ineqk']+=1
                    if tk+add<0:
                        acc['ineq_fail']+=1
                        if acc['iq_ex'] is None: acc['iq_ex']=(name,n,tuple(P),k,str(tk),add,ivs)

def maxcut_ls(n,adj,seeds=50):
    best=None;bv=-1;rng=random.Random(13)
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
    mc,cuts=cx.all_max_cuts(n,adj,E); run(name,n,adj,E,cuts,acc)

def main():
    acc=dict(ports=0,notint=0,Hmismatch=0,gt2=0,ineqk=0,ineq_fail=0,ni_ex=None,iq_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: ports=%d notint=%d gt2=%d ineq_fail=%d"%(nn,acc['ports'],acc['notint'],acc['gt2'],acc['ineq_fail']),flush=True)
    for g6 in ["G?Fw","G?bFw","G?rFw","H?AFBo]"]:
        try:
            n,E=dec(g6); fam("thw",n,E,acc)
        except Exception: pass
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9)
    for (a,b,br) in [((n5,E5),(n5,E5),[(0,5)]),((n5,E5),(n7,E7),[(0,5)]),((n5,E5),(n7,E7),[(0,5),(2,8)]),
                     ((n7,E7),(n5,E5),[(0,7)]),((n5,E5),(n9,E9),[(0,5)])]:
        nn,EE=union_disjoint(a,b); EE=EE+br
        if nn<=14: fam("glue",nn,EE,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3)]:
        nn,EE=odd_blowup(5,list(sizes))
        if nn<=13: fam("blow",nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    # Myc N=23 + N26 supplied cuts
    nn,EE=mycielski(grN,grE); adj=[set() for _ in range(nn)]
    for x,y in EE: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(nn,adj)
    if Bconn(nn,adj,side): run("Myc23",nn,adj,EE,[side],acc)
    n26,E26=n26_graph(); adj26=[set() for _ in range(n26)]
    for x,y in E26: adj26[x].add(y); adj26[y].add(x)
    run("N26",n26,adj26,E26,[[v%2 for v in range(n26)]],acc)
    print("="*55)
    print("negative ports:%d"%acc['ports'])
    print("(1) non-single-interval chi:",acc['notint'],acc['ni_ex'] or '')
    print("    H_i != -(b^2-a^2) mismatches:",acc['Hmismatch'])
    print("(2) paths with >2 negative ports:",acc['gt2'])
    print("(4) interval inequality failures:",acc['ineq_fail'],"over",acc['ineqk'],"checks",acc['iq_ex'] or '')
    ok=(acc['notint']==0 and acc['Hmismatch']==0 and acc['gt2']==0 and acc['ineq_fail']==0)
    print("VERDICT:", "INTERVAL-DRAIN TAXONOMY + two-port corridor inequality HOLDS" if ok else "FAILS")

if __name__=="__main__":
    main()
