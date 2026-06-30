"""Verify the LOGICAL BRIDGE of Codex 422 skeleton on the binding rows:
   for every NEGATIVE singleton port i (H_i<0):
     (i)  mu_i = delta_B(W_i)-delta_M(W_i) == 0   (neutral; forced by max-cut + huge Lambda),
     (ii) H_i == sum_r (2r+1) chi_i(r)  (= DeltaGamma), so the chi-profile faithfully represents H_i,
     (iii) LEMMA A: Pref_i(k)=sum_{r<k}(2r+1)chi_i(r) <= 0 for all k,
   and per row LEMMA B: Tail_k >= sum_{i in NPort} Suf_i(k) for all k.
   Run on theta H?AFBo] (the 12 binding Tail<0 rows) + census N<=8 quick.  Exact Fraction.
"""
import subprocess
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best, singleton_completions
from _wf_deficit_farkas import deltas, flip
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _factor_gate import chi_profile

def check(name,n,adj,E,cuts,acc):
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
                _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                profs=[]
                for i in range(len(P)):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0 or W is None: continue
                    acc['ports']+=1
                    # (i) neutrality
                    dB,dM=deltas(n,adj,side,W); mu=dB-dM
                    if mu!=0:
                        acc['mu_fail']+=1
                        if acc['mu_ex'] is None: acc['mu_ex']=(name,tuple(P),i,mu,str(Hi))
                    # (ii) identity H_i == sum (2r+1) chi
                    em1=ell_map(n,adj,flip(side,W))
                    chi=chi_profile(em0,em1,n)
                    sm=sum((2*r+1)*chi[r] for r in range(len(chi)))
                    if sm!=Hi:
                        acc['id_fail']+=1
                        if acc['id_ex'] is None: acc['id_ex']=(name,tuple(P),i,str(Hi),str(sm))
                    # (iii) Lemma A prefix<=0
                    pref=0
                    for k in range(1,len(chi)+1):
                        pref+=(2*(k-1)+1)*chi[k-1]
                        if pref>0:
                            acc['A_fail']+=1
                            if acc['A_ex'] is None: acc['A_ex']=(name,tuple(P),i,k,str(pref));
                            break
                    profs.append(chi)
                # Lemma B
                for k in range(n):
                    tk=sum((2*r+1)*Z[r] for r in range(k,n))
                    sufsum=sum(sum((2*r+1)*chi[r] for r in range(k,len(chi))) for chi in profs)
                    acc['Bk']+=1
                    if tk-sufsum<0:
                        acc['B_fail']+=1
                        if acc['B_ex'] is None: acc['B_ex']=(name,tuple(P),k,str(tk),str(sufsum))
                    if acc['Bmin'] is None or tk-sufsum<acc['Bmin']: acc['Bmin']=tk-sufsum

def fam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    mc,cuts=cx.all_max_cuts(n,adj,E)
    check(name,n,adj,E,cuts,acc)

def main():
    acc=dict(ports=0,mu_fail=0,id_fail=0,A_fail=0,B_fail=0,Bk=0,Bmin=None,
             mu_ex=None,id_ex=None,A_ex=None,B_ex=None)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    print("theta: ports=%d mu_fail=%d id_fail=%d A_fail=%d B_fail=%d Bmin=%s"%(acc['ports'],acc['mu_fail'],acc['id_fail'],acc['A_fail'],acc['B_fail'],str(acc['Bmin'])),flush=True)
    for nn in range(5,9):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
    print("="*55)
    print("negative ports:",acc['ports'])
    print("(i)  mu!=0 (non-neutral negative port) failures:",acc['mu_fail'],acc['mu_ex'] or '')
    print("(ii) H_i != sum(2r+1)chi identity failures:",acc['id_fail'],acc['id_ex'] or '')
    print("(iii)LEMMA A prefix<=0 failures:",acc['A_fail'],acc['A_ex'] or '')
    print("LEMMA B Tail_k>=sum Suf_i failures:",acc['B_fail'],"over",acc['Bk'],"checks",acc['B_ex'] or '')
    print("min Lemma B margin:",str(acc['Bmin']))
    print("VERDICT:", "SKELETON BRIDGE VALID (neutral ports, H_i=chi-sum, A, B all hold)" if acc['mu_fail']==acc['id_fail']==acc['A_fail']==acc['B_fail']==0 else "BRIDGE BROKEN")

if __name__=="__main__":
    main()
