"""Gate Codex 403 / GPT-Pro TAIL-ROT combinatorial bridge for the switch-extraction crux.
   For Tail_k(P)<0 rows over ALL connected-B max cuts, over parity-completed interval switches U:
   rotation-feasible(U): len(Added)<=len(Removed); sorted-increasing added[j]<=removed[j]; retained nonincreasing.
   phi_k(t)=max(0,t^2-k^2). Drop_k(U) = pair sorted-DECREASING added<->removed:
     sum_paired (phi_k(removed_g)-phi_k(added_e)) + sum_unpaired-removed phi_k(g) + sum_ret (phi_k(em0_h)-phi_k(em1_h)).
   C_k(P) = min over feasible U with Drop_k>0 of (-Drop_k);  +inf if none.
   TAIL-ROT:  Tail_k<0 => C_k(P) <= Tail_k(P)   (i.e. some feasible U has Drop_k >= -Tail_k).
   Exact Fraction.  Reports failures / first witness; whether existing neutral switch has Drop_k<-Tail or is
   rotation-infeasible.
"""
import subprocess
from fractions import Fraction as F
import _crux_extract as cx
from _crux_extract import parity_interval_switches
from _singleton_core import ell_map
from _wf_deficit_farkas import deltas, flip, gamma_of, odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski

def phi(t,k): return max(0,t*t-k*k)

def rot_feasible_and_drop(em0,em1,k):
    M0=set(em0);M1=set(em1);Added=M1-M0;Removed=M0-M1;Ret=M0&M1
    al=sorted(em1[e] for e in Added); rl=sorted(em0[g] for g in Removed)
    if len(al)>len(rl): return None
    if any(al[j]>rl[j] for j in range(len(al))): return None
    if any(em1[h]>em0[h] for h in Ret): return None
    # Drop_k: pair sorted-decreasing
    ad=sorted((em1[e] for e in Added),reverse=True); rd=sorted((em0[g] for g in Removed),reverse=True)
    drop=F(0)
    for j in range(len(rd)):
        if j<len(ad): drop+=phi(rd[j],k)-phi(ad[j],k)
        else: drop+=phi(rd[j],k)
    for h in Ret: drop+=phi(em0[h],k)-phi(em1[h],k)
    return drop

def run(name,n,adj,E,acc):
    mc,cuts=cx.all_max_cuts(n,adj,E)
    structs=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        structs.append((side,st))
    for (side,st) in structs:
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        em0=ell_map(n,adj,side)
        for f in M:
            if ell[f]%2==0: continue
            for P in cyc[f]:
                if len(P)!=ell[f]: continue
                _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                for k in range(n):
                    tk=sum((2*r+1)*Z[r] for r in range(k,n))
                    if tk>=0: continue
                    acc['neg']+=1
                    Ck=None; seen=set()
                    for U in parity_interval_switches(n,adj,side,P):
                        if not U or U in seen: continue
                        seen.add(U)
                        s2=flip(side,U)
                        if not Bconn(n,adj,s2): continue
                        st2=struct_for_side(n,adj,s2)
                        if st2 is None: continue
                        em1=ell_map(n,adj,s2)
                        drop=rot_feasible_and_drop(em0,em1,k)
                        if drop is None or drop<=0: continue
                        c=-drop
                        if Ck is None or c<Ck: Ck=c
                    if Ck is None or Ck>tk:
                        acc['fail']+=1
                        if acc['ex'] is None: acc['ex']=(name,n,tuple(P),k,str(tk),str(Ck))

def fam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    run(name,n,adj,E,acc)

def main():
    acc=dict(neg=0,fail=0,ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: neg=%d fail=%d"%(nn,acc['neg'],acc['fail']),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    print("="*55)
    print("Tail_k<0 rows:",acc['neg'])
    print("TAIL-ROT failures (Tail<0 but no feasible U with Drop_k>=-Tail):",acc['fail'],acc['ex'] or '')
    print("VERDICT:", "TAIL-ROT HOLDS => combinatorial bridge to switch-extraction" if acc['fail']==0 and acc['neg']>0 else ("no Tail<0" if acc['neg']==0 else "FAILS"))

if __name__=="__main__":
    main()
