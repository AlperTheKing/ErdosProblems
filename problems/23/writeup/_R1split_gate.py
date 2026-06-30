"""Gate Codex 399 R1 two-budget sub-split on GAMMA-MIN cuts, all k:
   (E4) E_k <= (4L/25)*D_k            [endpoint DG curvature <= (4/5) deficit at k=0]
   (C1) delta_P*max(0,L^2-k^2) <= (L/25)*D_k   [path AM-GM deficit C_L <= (1/5) deficit at k=0]
   (E4)+(C1) => R1 = (L/5)D_k - Tax_k >= 0.  Exact Fraction; report failures + worst ratios.
"""
import subprocess
from fractions import Fraction as F
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, mycielski
from _codex_interval_failure_switch_lab import n26_graph

def run(name,n,adj,E,cuts,acc):
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        N=F(n)
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
                for k in range(n):
                    Gamma_k=sum(max(0,ell[g]**2-k*k) for g in M)
                    D_k=N*N-k*k-Gamma_k
                    Ek=sum((2*r+1)*chiP[r] for r in range(k,n))
                    Cpart=deltaP*max(0,L*L-k*k)
                    acc['k']+=1
                    e_rhs=F(4*L,25)*D_k; c_rhs=F(L,25)*D_k
                    if Ek>e_rhs:
                        acc['E4_fail']+=1
                        if acc['E4_ex'] is None: acc['E4_ex']=(name,n,tuple(P),k,str(Ek),str(e_rhs))
                    elif e_rhs>0:
                        m=Ek/e_rhs
                        if acc['E4_max'] is None or m>acc['E4_max']: acc['E4_max']=m
                    if Cpart>c_rhs:
                        acc['C1_fail']+=1
                        if acc['C1_ex'] is None: acc['C1_ex']=(name,n,tuple(P),k,str(Cpart),str(c_rhs))
                    elif c_rhs>0:
                        m=Cpart/c_rhs
                        if acc['C1_max'] is None or m>acc['C1_max']: acc['C1_max']=m

def fam(name,n,E,acc):
    adj,cuts=gmins(n,E); run(name,n,adj,E,cuts,acc)

def main():
    acc=dict(k=0,E4_fail=0,C1_fail=0,E4_ex=None,C1_ex=None,E4_max=None,C1_max=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: k=%d E4=%d C1=%d"%(nn,acc['k'],acc['E4_fail'],acc['C1_fail']),flush=True)
    for g6 in ["G?Fw","G?bFw","G?rFw","H?AFBo]"]:
        try:
            n,E=dec(g6); fam("thw",n,E,acc)
        except Exception: pass
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9)
    for (a,b,br) in [((n5,E5),(n5,E5),[(0,5)]),((n5,E5),(n7,E7),[(0,5)]),((n7,E7),(n5,E5),[(0,7)]),((n5,E5),(n9,E9),[(0,5)])]:
        nn,EE=union_disjoint(a,b); EE=EE+br
        if nn<=12: fam("glue",nn,EE,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3)]:
        nn,EE=odd_blowup(5,list(sizes))
        if nn<=12: fam("blow",nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    n26,E26=n26_graph(); adj26=[set() for _ in range(n26)]
    for x,y in E26: adj26[x].add(y); adj26[y].add(x)
    run("N26",n26,adj26,E26,[[v%2 for v in range(n26)]],acc)
    print("="*55)
    print("k-checks:",acc['k'])
    print("(E4) E_k<=(4L/25)D_k failures:",acc['E4_fail'],acc['E4_ex'] or '',"  max ratio:",str(acc['E4_max']))
    print("(C1) C_part<=(L/25)D_k failures:",acc['C1_fail'],acc['C1_ex'] or '',"  max ratio:",str(acc['C1_max']))
    ok=(acc['E4_fail']==0 and acc['C1_fail']==0)
    print("VERDICT:", "R1 SUB-SPLIT (E4)+(C1) HOLD on gamma-min" if ok else "FAILS")

if __name__=="__main__":
    main()
