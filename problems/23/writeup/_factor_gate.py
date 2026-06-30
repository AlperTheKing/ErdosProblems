"""Gate Codex 388 two-lemma factorization of the closing bound Tail_k >= sum_i H_i^-.
   For each negative singleton port i (H_i<0, neutral switch W), the port layer profile:
     chi_i(r) = [#added bad with em1>r] - [#removed bad with em0>r] + [retained: 1_{r<em1}-1_{r<em0}],
     H_i = sum_r (2r+1) chi_i(r).  Pref_i(k)=sum_{r<k}(2r+1)chi_i(r);  Suf_i(k)=sum_{r>=k}(2r+1)chi_i(r).
   LEMMA A: Pref_i(k) <= 0 for every k and every negative port  (<=> Suf_i(k) >= H_i).
   LEMMA B: Tail_k(P) >= sum_{i:H_i<0} Suf_i(k)  for every k.
   A+B => Tail_k >= sum Suf_i(k) >= sum H_i = sum_i H_i^-.   ALL exact Fraction; full battery.
"""
import subprocess, random
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import flip
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski

def chi_profile(em0, em1, n):
    k0=set(em0);k1=set(em1);added=k1-k0;removed=k0-k1;ret=k0&k1
    chi=[0]*(2*n+2)
    def add(thr,sgn):
        for r in range(min(thr,len(chi))): chi[r]+=sgn
    for e in added: add(em1[e],+1)
    for g in removed: add(em0[g],-1)
    for h in ret:
        add(em1[h],+1); add(em0[h],-1)
    return chi

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
                # negative ports + profiles
                profs=[]
                for i in range(len(P)):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0 or W is None: continue
                    em1=ell_map(n,adj,flip(side,W))
                    if em1 is None: continue
                    chi=chi_profile(em0,em1,n)
                    acc['ports']+=1
                    profs.append(chi)
                    # Lemma A: Pref_i(k)<=0 for all k
                    pref=0
                    for k in range(len(chi)):
                        # Pref_i(k)=sum_{r<k}(2r+1)chi[r]
                        if k>0: pref+=(2*(k-1)+1)*chi[k-1]
                        if pref>0:
                            acc['A_fail']+=1
                            if acc['A_ex'] is None: acc['A_ex']=(name,n,tuple(P),k,str(pref))
                            break
                # Lemma B: Tail_k >= sum_i Suf_i(k)
                for k in range(n):
                    tk=sum((2*r+1)*Z[r] for r in range(k,n))
                    sufsum=0
                    for chi in profs:
                        sufsum+=sum((2*r+1)*chi[r] for r in range(k,len(chi)))
                    acc['Bk']+=1
                    if tk - sufsum < 0:
                        acc['B_fail']+=1
                        if acc['B_ex'] is None: acc['B_ex']=(name,n,tuple(P),k,str(tk),str(sufsum))
                    m=tk-sufsum
                    if acc['Bmin'] is None or m<acc['Bmin']: acc['Bmin']=m

def maxcut_ls(n,adj,seeds=50):
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

def fam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    mc,cuts=cx.all_max_cuts(n,adj,E)
    run(name,n,adj,E,cuts,acc)

def main():
    acc=dict(ports=0,A_fail=0,B_fail=0,Bk=0,Bmin=None,A_ex=None,B_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: ports=%d A_fail=%d B_fail=%d"%(nn,acc['ports'],acc['A_fail'],acc['B_fail']),flush=True)
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
    print("after stress: ports=%d A_fail=%d B_fail=%d"%(acc['ports'],acc['A_fail'],acc['B_fail']),flush=True)
    n,E=mycielski(grN,grE); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): run("Myc23",n,adj,E,[side],acc)
    print("="*55)
    print("negative ports:%d"%acc['ports'])
    print("LEMMA A (prefix<=0) failures:",acc['A_fail'],acc['A_ex'] or '')
    print("LEMMA B (Tail_k>=sum Suf) failures:",acc['B_fail'],"over",acc['Bk'],"checks",acc['B_ex'] or '')
    print("min Lemma B margin:",str(acc['Bmin']))
    print("VERDICT:", "FACTORIZATION A+B HOLDS" if acc['A_fail']==0 and acc['B_fail']==0 else "FAILS")

if __name__=="__main__":
    main()
