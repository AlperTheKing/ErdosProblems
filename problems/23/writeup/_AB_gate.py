"""Gate Codex 395 two-part k=0 split (the FINAL inequalities -- only k=0 is needed for the atom):
   D_all = N^2-Gamma,  D_path = N*(L-S),  Drain_0 = sum_i(b_i^2-a_i^2),  Tax_0 = E_0 + delta_P*L^2.
   (A)  Tax_0 <= (1/5)*L*D_all.
   (B)  25*max(0,-D_path) <= Drain_0 + (4/5)*L*D_all.
   (A)+(B) => Slack_0 = L*D_all + 25*D_path + Drain_0 >= Tax_0  (Codex's case split on sign of D_path)
            => Tail_0 >= sum H_i^-  => (gamma-min: all H_i>=0, DGsum>=0) B_L = Tail_0+DGsum >= 0 => atom.
   ONLY k=0 needed (B_L = Tail_0 + DGsum), so monotone-ratio is NOT required.
   Full battery incl N26 + Myc N=23.  Exact.  Reports min margins.
"""
import subprocess, random
from fractions import Fraction as F
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _factor_gate import chi_profile as port_chi
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
        N=F(n); em0=ell_map(n,adj,side); Gamma=sum(ell[g]**2 for g in M)
        for f in M:
            if ell[f]%2==0: continue
            Lf=ell[f]
            for P in cyc[f]:
                if len(P)!=Lf: continue
                h=[T[P[i]]/N for i in range(Lf)]; S=sum(h); q=min(h[i]*h[(i+1)%Lf] for i in range(Lf))
                deltaP=(S/Lf)**2-q
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj,side,end,M,n)
                    for r in range(n): chiP[r]+=ch[r]
                E0=sum((2*r+1)*chiP[r] for r in range(n))
                ivs=[]
                for i in range(Lf):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0 or W is None: continue
                    em1=ell_map(n,adj,flip(side,W))
                    if em1 is None: continue
                    iv=interval_of(port_chi(em0,em1,n))
                    if iv: ivs.append(iv)
                D_all=N*N-Gamma
                D_path=N*(Lf-S)
                Drain0=sum(b*b-a*a for (a,b) in ivs)
                Tax0=E0+deltaP*Lf*Lf
                acc['rows']+=1
                # (A) Tax0 <= L*D_all/5
                Argt=F(Lf,5)*D_all
                if Tax0>Argt:
                    acc['A_fail']+=1
                    if acc['A_ex'] is None: acc['A_ex']=(name,n,tuple(P),str(Tax0),str(Argt))
                elif Argt>0:
                    m=Tax0/Argt
                    if acc['A_max'] is None or m>acc['A_max']: acc['A_max']=m
                # (B) 25*max(0,-D_path) <= Drain0 + (4/5)*L*D_all
                Bl=25*max(0,-D_path); Br=Drain0+F(4,5)*Lf*D_all
                if Bl>Br:
                    acc['B_fail']+=1
                    if acc['B_ex'] is None: acc['B_ex']=(name,n,tuple(P),str(Bl),str(Br))
                elif Br>0:
                    m=Bl/Br
                    if acc['B_max'] is None or m>acc['B_max']: acc['B_max']=m

def maxcut_ls(n,adj,seeds=50):
    best=None;bv=-1;rng=random.Random(23)
    for _ in range(seeds):
        s=[rng.randint(0,1) for _ in range(n)];imp=True
        while imp:
            imp=False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w]==s[v])>sum(1 for w in adj[v] if s[w]!=s[v]):s[v]^=1;imp=True
        val=sum(1 for v in range(n) for w in adj[v] if w>v and s[v]!=s[w])
        if val>bv:bv=val;best=s[:]
    return best

from _stark1 import gmins
def fam(name,n,E,acc):
    adj,cuts=gmins(n,E)   # GAMMA-MIN cuts only (the cuts the atom is about)
    run(name,n,adj,E,cuts,acc)

def main():
    acc=dict(rows=0,A_fail=0,B_fail=0,A_ex=None,B_ex=None,A_max=None,B_max=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d A_fail=%d B_fail=%d"%(nn,acc['rows'],acc['A_fail'],acc['B_fail']),flush=True)
    for g6 in ["G?Fw","G?bFw","G?rFw","H?AFBo]"]:
        try:
            n,E=dec(g6); fam("thw",n,E,acc)
        except Exception: pass
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9)
    for (a,b,br) in [((n5,E5),(n5,E5),[(0,5)]),((n5,E5),(n7,E7),[(0,5)]),((n7,E7),(n5,E5),[(0,7)]),((n5,E5),(n9,E9),[(0,5)])]:
        nn,EE=union_disjoint(a,b); EE=EE+br
        if nn<=14: fam("glue",nn,EE,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3)]:
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
    print("(A) Tax_0 <= L*D_all/5 failures:",acc['A_fail'],acc['A_ex'] or '',"  max ratio:",str(acc['A_max']))
    print("(B) 25*max(0,-D_path) <= Drain_0 + (4/5)L*D_all failures:",acc['B_fail'],acc['B_ex'] or '',"  max ratio:",str(acc['B_max']))
    ok=(acc['A_fail']==0 and acc['B_fail']==0)
    print("VERDICT:", "(A)+(B) HOLD => k=0 Slack_0>=Tax_0 => atom (only k=0 needed)" if ok else "FAILS")

if __name__=="__main__":
    main()
