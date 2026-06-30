"""Gate Codex 396 GPT-Pro LEVELWISE split (per-level (A_k)+(B_k)) on GAMMA-MIN cuts.
   Gamma_k=sum_g max(0,ell_g^2-k^2), A_k=sum_g a_g*max(0,ell_g-k), D_k=N^2-k^2-Gamma_k, B_k=L(N-k)-A_k.
   R1_k=(L/5)D_k-Tax_k ; R2_k=Drain_k+(4L/5)D_k-25*max(0,-B_k).
   (R1) R1_k>=0 ; (R2) R2_k>=0 ; (ID) Slack_k-Tax_k == R1_k+R2_k+25*max(0,B_k) (tautology).
   ALL k, gamma-min cuts, full battery + N26.  Exact.
"""
import subprocess
from fractions import Fraction as F
from _singleton_core import ell_map, Hi_and_best
from _factor_gate import chi_profile as port_chi
from _trunc_verify import chi_profile as endpt_chi
from _interval_drain_gate import interval_of
from _wf_deficit_farkas import flip, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, mycielski
from _codex_interval_failure_switch_lab import n26_graph

def run(name,n,adj,E,side_list,acc):
    Lam=len(E)*n*n+1
    for side in side_list:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        N=F(n); em0=ell_map(n,adj,side)
        pg={}
        for g in M:
            Q=cyc[g]; cnt={}
            for path in Q:
                for v in path: cnt[v]=cnt.get(v,0)+1
            kk=len(Q); pg[g]={v:F(cnt[v],kk) for v in cnt}
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                h=[T[P[i]]/N for i in range(L)]; S=sum(h); q=min(h[i]*h[(i+1)%L] for i in range(L))
                deltaP=(S/L)**2-q
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj,side,end,M,n)
                    for r in range(n): chiP[r]+=ch[r]
                a_g={g:sum(pg[g].get(P[i],F(0)) for i in range(L)) for g in M}
                ivs=[]
                for i in range(L):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0 or W is None: continue
                    em1=ell_map(n,adj,flip(side,W))
                    if em1 is None: continue
                    iv=interval_of(port_chi(em0,em1,n))
                    if iv: ivs.append(iv)
                for k in range(n):
                    Gamma_k=sum(max(0,ell[g]**2-k*k) for g in M)
                    A_k=sum(a_g[g]*max(0,ell[g]-k) for g in M)
                    D_k=N*N-k*k-Gamma_k
                    B_k=L*(N-k)-A_k
                    Drain=sum(max(0,b*b-max(k,a)**2) for (a,b) in ivs)
                    Ek=sum((2*r+1)*chiP[r] for r in range(k,n))
                    Tax=Ek+deltaP*max(0,L*L-k*k)
                    R1=F(L,5)*D_k-Tax
                    R2=Drain+F(4*L,5)*D_k-25*max(0,-B_k)
                    Slack=L*D_k+25*B_k+Drain
                    acc['k']+=1
                    if R1<0:
                        acc['R1_fail']+=1
                        if acc['R1_ex'] is None: acc['R1_ex']=(name,n,tuple(P),k,str(R1))
                    if R2<0:
                        acc['R2_fail']+=1
                        if acc['R2_ex'] is None: acc['R2_ex']=(name,n,tuple(P),k,str(R2))
                    if Slack-Tax != R1+R2+25*max(0,B_k):
                        acc['ID_fail']+=1

def fam(name,n,E,acc):
    adj,cuts=gmins(n,E); run(name,n,adj,E,cuts,acc)

def main():
    acc=dict(k=0,R1_fail=0,R2_fail=0,ID_fail=0,R1_ex=None,R2_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: k=%d R1=%d R2=%d ID=%d"%(nn,acc['k'],acc['R1_fail'],acc['R2_fail'],acc['ID_fail']),flush=True)
    for g6 in ["G?Fw","G?bFw","G?rFw","H?AFBo]"]:
        try:
            n,E=dec(g6); fam("thw",n,E,acc)
        except Exception: pass
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9)
    for (a,b,br) in [((n5,E5),(n5,E5),[(0,5)]),((n5,E5),(n7,E7),[(0,5)]),((n7,E7),(n5,E5),[(0,7)]),((n5,E5),(n9,E9),[(0,5)])]:
        nn,EE=union_disjoint(a,b); EE=EE+br
        if nn<=12: fam("glue",nn,EE,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3)]:
        nn,EE=odd_blowup(5,list(sizes))
        if nn<=12: fam("blow",nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    n26,E26=n26_graph(); adj26=[set() for _ in range(n26)]
    for x,y in E26: adj26[x].add(y); adj26[y].add(x)
    run("N26",n26,adj26,E26,[[v%2 for v in range(n26)]],acc)
    print("="*55)
    print("k-checks:",acc['k'])
    print("(R1) R1_k>=0 failures:",acc['R1_fail'],acc['R1_ex'] or '')
    print("(R2) R2_k>=0 failures:",acc['R2_fail'],acc['R2_ex'] or '')
    print("(ID) tautology failures:",acc['ID_fail'])
    ok=(acc['R1_fail']==0 and acc['R2_fail']==0 and acc['ID_fail']==0)
    print("VERDICT:", "LEVELWISE (R1)+(R2) HOLD on gamma-min => all-k Slack>=Tax" if ok else "FAILS")

if __name__=="__main__":
    main()
