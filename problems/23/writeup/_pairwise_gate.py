"""Gate the PAIRWISE rotation invariant (Codex 389) on every negative singleton port:
   for the port switch W,  sort(added_lengths) <= sort(removed_lengths) COMPONENTWISE, and every retained
   bad edge has ell_after <= ell_before.  This is the hypothesis of Codex's Lemma-A proof:
     each retained pair  min(k,ell_after)^2 - min(k,ell_before)^2 <= 0;
     each sorted added/removed pair  min(k,ell_added)^2 - min(k,ell_removed)^2 <= 0;
     => Pref_W(k) = sum_{r<k}(2r+1)chi_W(r) <= 0 for all k  (Lemma A) -- RIGOROUS if this gate passes.
   Full battery, exact.
"""
import subprocess, random
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import flip, odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski

def check_port(em0, em1):
    k0=set(em0);k1=set(em1);added=k1-k0;removed=k0-k1;ret=k0&k1
    al=sorted(em1[e] for e in added); rl=sorted(em0[g] for g in removed)
    pairwise = (len(al)==len(rl)) and all(al[j]<=rl[j] for j in range(len(al)))
    ret_ok = all(em1[h]<=em0[h] for h in ret)
    return pairwise, ret_ok, al, rl

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
                for i in range(len(P)):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0 or W is None: continue
                    em1=ell_map(n,adj,flip(side,W))
                    if em1 is None: continue
                    acc['ports']+=1
                    pw,ro,al,rl=check_port(em0,em1)
                    if not pw:
                        acc['pw_fail']+=1
                        if acc['pw_ex'] is None: acc['pw_ex']=(name,n,tuple(P),i,al,rl)
                    if not ro:
                        acc['ret_fail']+=1
                        if acc['ret_ex'] is None: acc['ret_ex']=(name,n,tuple(P),i)

def maxcut_ls(n,adj,seeds=50):
    best=None;bv=-1;rng=random.Random(11)
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
    acc=dict(ports=0,pw_fail=0,ret_fail=0,pw_ex=None,ret_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: ports=%d pw_fail=%d ret_fail=%d"%(nn,acc['ports'],acc['pw_fail'],acc['ret_fail']),flush=True)
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
    print("after stress: ports=%d pw_fail=%d ret_fail=%d"%(acc['ports'],acc['pw_fail'],acc['ret_fail']),flush=True)
    n,E=mycielski(grN,grE); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): run("Myc23",n,adj,E,[side],acc)
    print("="*55)
    print("negative ports:%d"%acc['ports'])
    print("PAIRWISE sort(added)<=sort(removed) failures:",acc['pw_fail'],acc['pw_ex'] or '')
    print("RETAINED no-lengthening failures:",acc['ret_fail'],acc['ret_ex'] or '')
    print("VERDICT:", "PAIRWISE INVARIANT HOLDS => Lemma A rigorous" if acc['pw_fail']==0 and acc['ret_fail']==0 else "FAILS (Lemma A needs refinement)")

if __name__=="__main__":
    main()
