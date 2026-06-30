"""Confirm Codex 429: K0 (Slack_0>=Tax_0 in _monotone_k0_gate) is EXACTLY B0 (Tail_0>=-24*e(P)).
   Per negative-port row: Tail_0 = sum_r(2r+1)Z_r (Zr_row).  Slack_0,Tax_0,Drain0 from monotone_k0 closed form.
   e(P)=#neg endpoint ports.  Check:  Slack_0 - Tax_0 == Tail_0 + Drain0  AND  Drain0 == 24*e(P)
   => K0 (Slack_0>=Tax_0) <=> Tail_0 >= -Drain0 = -24*e(P) = B0.  Exact.  theta + census N<=8.
"""
import subprocess
from fractions import Fraction as F
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _factor_gate import chi_profile as port_chi
from _layer_gate import Zr_row
from _trunc_verify import chi_profile as endpt_chi
from _interval_drain_gate import interval_of
from _wf_deficit_farkas import flip
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side

def scan(name,n,adj,E,cuts,acc):
    Lam=len(E)*n*n+1
    for side in cuts:
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
            Lf=ell[f]
            if Lf%2==0: continue
            for P in cyc[f]:
                if len(P)!=Lf: continue
                _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                Tail0=sum((2*r+1)*Z[r] for r in range(n))
                h=[T[P[i]]/N for i in range(Lf)]; S=sum(h); q=min(h[i]*h[(i+1)%Lf] for i in range(Lf))
                deltaP=(S/Lf)**2-q
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj,side,end,M,n)
                    for r in range(n): chiP[r]+=ch[r]
                a_g={g:sum(pg[g].get(P[i],F(0)) for i in range(Lf)) for g in M}
                ivs=[]; e=0
                for i in range(Lf):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0 or W is None: continue
                    em1=ell_map(n,adj,flip(side,W))
                    if em1 is None: continue
                    iv=interval_of(port_chi(em0,em1,n))
                    if iv: ivs.append(iv)
                    if i in (0,Lf-1): e+=1
                Gamma=sum(ell[g]**2 for g in M)
                Drain0=sum(b*b-a*a for (a,b) in ivs)
                E0=sum((2*r+1)*chiP[r] for r in range(n))
                Slack0=Lf*(N*N-Gamma)+25*N*(Lf-S)+Drain0
                Tax0=E0+deltaP*Lf*Lf
                acc['rows']+=1
                if not ivs: continue   # only negative-port rows are the K0/B0 binding ones
                acc['portrows']+=1
                # identity 1: Slack0 - Tax0 == Tail0 + Drain0
                if Slack0-Tax0 != Tail0+Drain0:
                    acc['id1_fail']+=1
                    if acc['ex1'] is None: acc['ex1']=(name,tuple(P),str(Slack0-Tax0),str(Tail0+Drain0))
                # identity 2: Drain0 == 24*e
                if Drain0 != 24*e:
                    acc['id2_fail']+=1
                    if acc['ex2'] is None: acc['ex2']=(name,tuple(P),str(Drain0),e)
                # equivalence: (Slack0>=Tax0) == (Tail0 >= -24*e)
                if (Slack0>=Tax0) != (Tail0 >= -24*e):
                    acc['equiv_fail']+=1
                    if acc['exq'] is None: acc['exq']=(name,tuple(P),str(Slack0-Tax0),str(Tail0+24*e))

def fam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    _,cuts=cx.all_max_cuts(n,adj,E); scan(name,n,adj,E,cuts,acc)

def main():
    acc=dict(rows=0,portrows=0,id1_fail=0,id2_fail=0,equiv_fail=0,ex1=None,ex2=None,exq=None)
    n,E=dec("H?AFBo]"); fam("thw",n,E,acc)
    for nn in range(5,9):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
    print("rows:",acc['rows']," negative-port rows:",acc['portrows'])
    print("identity Slack0-Tax0 == Tail0+Drain0  failures:",acc['id1_fail'],acc['ex1'] or '')
    print("identity Drain0 == 24*e(P)            failures:",acc['id2_fail'],acc['ex2'] or '')
    print("EQUIVALENCE K0(Slack0>=Tax0) <=> B0(Tail0>=-24e) failures:",acc['equiv_fail'],acc['exq'] or '')
    print("VERDICT:", "K0 == B0 EXACTLY" if acc['id1_fail']==acc['id2_fail']==acc['equiv_fail']==0 else "NOT EQUIVALENT")

if __name__=="__main__":
    main()
