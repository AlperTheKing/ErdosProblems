"""Gate Codex 393 closed-form split of interval-drain Lemma B.
   Tax_k = E_k + delta_P*phi_k(L),  E_k=sum_{r>=k}(2r+1)chi_P(r) (endpoint DG profile), phi_k(L)=max(0,L^2-k^2),
           delta_P=((sum_i T(x_i)/N)/L)^2 - min_i h_i h_{i+1}.
   Drain_k = sum_{neg ports} max(0, b_i^2 - max(k,a_i)^2).
   Slack_k = L(N^2-k^2) + 25*L*(N-k) + Drain_k - sum_g [ L*max(0,ell_g^2-k^2) + 25*a_g*max(0,ell_g-k) ],
   a_g = sum_{v in P} p_g(v).
   Gates: (A) Tail_k + Drain_k == Slack_k - Tax_k;  (B) Slack_k>=0;  (C) Tax_k<=Slack_k (when Tax_k>0),
   and report min Slack_k/Tax_k vs 7/9.  Full battery incl N26 + Myc N=23.  Exact.
"""
import subprocess, random
from fractions import Fraction as F
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _factor_gate import chi_profile as port_chi
from _layer_gate import Zr_row
from _trunc_verify import chi_profile as endpt_chi
from _interval_drain_gate import interval_of
from _wf_deficit_farkas import flip, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski
from _codex_interval_failure_switch_lab import n26_graph

def run(name,n,adj,E,side_list,acc):
    Lam=len(E)*n*n+1; L_=5
    for side in side_list:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        N=F(n); em0=ell_map(n,adj,side)
        # p_g
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
                _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                # delta_P, chi_P (endpoints)
                h=[T[P[i]]/N for i in range(L)]; S=sum(h); q=min(h[i]*h[(i+1)%L] for i in range(L))
                deltaP=(S/L)**2-q
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj,side,end,M,n)
                    for r in range(n): chiP[r]+=ch[r]
                a_g={g:sum(pg[g].get(P[i],F(0)) for i in range(L)) for g in M}
                # negative-port intervals
                ivs=[]
                for i in range(L):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0 or W is None: continue
                    em1=ell_map(n,adj,flip(side,W))
                    if em1 is None: continue
                    iv=interval_of(port_chi(em0,em1,n))
                    if iv: ivs.append(iv)
                for k in range(n):
                    Tail_k=sum((2*r+1)*Z[r] for r in range(k,n))
                    Drain_k=sum(max(0,b*b-max(k,a)**2) for (a,b) in ivs)
                    Ek=sum((2*r+1)*chiP[r] for r in range(k,n))
                    phikL=max(0,L*L-k*k)
                    Tax_k=Ek+deltaP*phikL
                    Slack_k=L*(N*N-k*k)+25*L*(N-k)+Drain_k - sum(L*max(0,ell[g]**2-k*k)+25*a_g[g]*max(0,ell[g]-k) for g in M)
                    acc['k']+=1
                    if Tail_k+Drain_k != Slack_k-Tax_k:
                        acc['A_fail']+=1
                        if acc['A_ex'] is None: acc['A_ex']=(name,n,tuple(P),k)
                    if Slack_k<0:
                        acc['B_fail']+=1
                        if acc['B_ex'] is None: acc['B_ex']=(name,n,tuple(P),k,str(Slack_k))
                    if Tax_k>0:
                        if Tax_k>Slack_k:
                            acc['C_fail']+=1
                            if acc['C_ex'] is None: acc['C_ex']=(name,n,tuple(P),k,str(Tax_k),str(Slack_k))
                        rt=Tax_k/Slack_k if Slack_k!=0 else None
                        if rt is not None and (acc['maxratio'] is None or rt>acc['maxratio']):
                            acc['maxratio']=rt; acc['mr_row']=(name,n,tuple(P),k)

def maxcut_ls(n,adj,seeds=50):
    best=None;bv=-1;rng=random.Random(17)
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
    acc=dict(k=0,A_fail=0,B_fail=0,C_fail=0,A_ex=None,B_ex=None,C_ex=None,maxratio=None,mr_row=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: k=%d A=%d B=%d C=%d"%(nn,acc['k'],acc['A_fail'],acc['B_fail'],acc['C_fail']),flush=True)
    for g6 in ["G?Fw","G?bFw","G?rFw","H?AFBo]"]:
        try:
            n,E=dec(g6); fam("thw",n,E,acc)
        except Exception: pass
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9)
    for (a,b,br) in [((n5,E5),(n5,E5),[(0,5)]),((n5,E5),(n7,E7),[(0,5)]),((n7,E7),(n5,E5),[(0,7)]),((n5,E5),(n9,E9),[(0,5)])]:
        nn,EE=union_disjoint(a,b); EE=EE+br
        if nn<=14: fam("glue",nn,EE,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3)]:
        nn,EE=odd_blowup(5,list(sizes))
        if nn<=13: fam("blow",nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    nn,EE=mycielski(grN,grE); adj=[set() for _ in range(nn)]
    for x,y in EE: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(nn,adj)
    if Bconn(nn,adj,side): run("Myc23",nn,adj,EE,[side],acc)
    n26,E26=n26_graph(); adj26=[set() for _ in range(n26)]
    for x,y in E26: adj26[x].add(y); adj26[y].add(x)
    run("N26",n26,adj26,E26,[[v%2 for v in range(n26)]],acc)
    print("="*55)
    print("(A) identity failures:",acc['A_fail'],acc['A_ex'] or '')
    print("(B) Slack_k>=0 failures:",acc['B_fail'],acc['B_ex'] or '')
    print("(C) Tax_k<=Slack_k failures:",acc['C_fail'],acc['C_ex'] or '')
    print("max Tax_k/Slack_k ratio:",str(acc['maxratio']),float(acc['maxratio']) if acc['maxratio'] else None,"(7/9=%.4f) at"%(7/9),acc['mr_row'])
    ok=(acc['A_fail']==0 and acc['B_fail']==0 and acc['C_fail']==0)
    print("VERDICT:", "SLACK-PAYS-TAX split HOLDS (Slack_k>=Tax_k)" if ok else "FAILS")

if __name__=="__main__":
    main()
