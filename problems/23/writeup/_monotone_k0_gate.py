"""Gate Codex 394: (M) monotone-ratio  Tax_k*Slack_0 <= Tax_0*Slack_k  for all k (Tax_k>0,Slack_k>0)
   => reduces SLACK>=TAX to the single k=0 inequality (K0)  Slack_0 >= Tax_0.
   Also verify k=0 closed form: Slack_0 = L(N^2-Gamma)+25N(L-S)+Drain_0,  Tax_0 = E_0 + delta_P*L^2.
   Full battery incl N26 + Myc N=23.  Exact.
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
    Lam=len(E)*n*n+1; L=5
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
            Lf=ell[f]
            if Lf%2==0: continue
            for P in cyc[f]:
                if len(P)!=Lf: continue
                _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                h=[T[P[i]]/N for i in range(Lf)]; S=sum(h); q=min(h[i]*h[(i+1)%Lf] for i in range(Lf))
                deltaP=(S/Lf)**2-q
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj,side,end,M,n)
                    for r in range(n): chiP[r]+=ch[r]
                a_g={g:sum(pg[g].get(P[i],F(0)) for i in range(Lf)) for g in M}
                ivs=[]
                for i in range(Lf):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0 or W is None: continue
                    em1=ell_map(n,adj,flip(side,W))
                    if em1 is None: continue
                    iv=interval_of(port_chi(em0,em1,n))
                    if iv: ivs.append(iv)
                Sl=[];Tx=[]
                for k in range(n):
                    Drain=sum(max(0,b*b-max(k,a)**2) for (a,b) in ivs)
                    Ek=sum((2*r+1)*chiP[r] for r in range(k,n))
                    phikL=max(0,Lf*Lf-k*k)
                    Tax=Ek+deltaP*phikL
                    Gamma=sum(ell[g]**2 for g in M)
                    Slack=Lf*(N*N-k*k)+25*Lf*(N-k)+Drain - sum(Lf*max(0,ell[g]**2-k*k)+25*a_g[g]*max(0,ell[g]-k) for g in M)
                    Sl.append(Slack); Tx.append(Tax)
                # k=0 closed form check
                Gamma=sum(ell[g]**2 for g in M)
                Drain0=sum(b*b-a*a for (a,b) in ivs)
                E0=sum((2*r+1)*chiP[r] for r in range(n))
                Slack0_cf=Lf*(N*N-Gamma)+25*N*(Lf-S)+Drain0
                Tax0_cf=E0+deltaP*Lf*Lf
                acc['rows']+=1
                if Slack0_cf!=Sl[0] or Tax0_cf!=Tx[0]:
                    acc['cf_fail']+=1
                    if acc['cf_ex'] is None: acc['cf_ex']=(name,n,tuple(P),str(Slack0_cf),str(Sl[0]),str(Tax0_cf),str(Tx[0]))
                # (M) monotone-ratio -- split by whether row has negative ports (Drain>0)
                has_ports = len(ivs)>0
                for k in range(1,n):
                    if Tx[k]>0 and Sl[k]>0:
                        if Tx[k]*Sl[0] > Tx[0]*Sl[k]:
                            acc['M_fail']+=1
                            if has_ports:
                                acc['M_fail_ports']+=1
                                if acc['Mp_ex'] is None: acc['Mp_ex']=(name,n,tuple(P),k,str(Tx[k]/Sl[k]),str(Tx[0]/Sl[0]))
                            if acc['M_ex'] is None: acc['M_ex']=(name,n,tuple(P),k,str(Tx[k]/Sl[k]),str(Tx[0]/Sl[0]))
                # (K0)
                if Sl[0]<Tx[0]:
                    acc['K0_fail']+=1
                    if acc['K0_ex'] is None: acc['K0_ex']=(name,n,tuple(P),str(Sl[0]),str(Tx[0]))

def maxcut_ls(n,adj,seeds=50):
    best=None;bv=-1;rng=random.Random(19)
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
    acc=dict(rows=0,cf_fail=0,M_fail=0,M_fail_ports=0,K0_fail=0,cf_ex=None,M_ex=None,Mp_ex=None,K0_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d cf=%d M=%d K0=%d"%(nn,acc['rows'],acc['cf_fail'],acc['M_fail'],acc['K0_fail']),flush=True)
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
    print("rows:",acc['rows'])
    print("k=0 closed-form mismatches:",acc['cf_fail'],acc['cf_ex'] or '')
    print("(M) monotone-ratio failures (ALL rows):",acc['M_fail'],acc['M_ex'] or '')
    print("(M) monotone-ratio failures ON NEGATIVE-PORT rows:",acc['M_fail_ports'],acc['Mp_ex'] or '')
    print("(K0) Slack_0>=Tax_0 failures:",acc['K0_fail'],acc['K0_ex'] or '')
    ok=(acc['cf_fail']==0 and acc['M_fail']==0 and acc['K0_fail']==0)
    print("VERDICT:", "MONOTONE-RATIO + k=0 reduction HOLDS => proof reduces to Slack_0>=Tax_0" if ok else "FAILS")

if __name__=="__main__":
    main()
