"""Gate Codex 405 BALLOT-D (sign-order of the residual layer profile) + honest scope check.
   D_r = Z_r(P) - sum_{i:H_i<0} chi_i(r).  BALLOT-D: (1) sign-order (no r<s with D_r>0 and D_s<0);
   (2) total sum_r (2r+1) D_r >= 0.  => all suffixes >=0 (Lemma B).
   Gate on negative-port rows AND no-port rows (where D_r=Z_r, the ATOM layer profile) separately, to show
   whether the sign-order also holds on the hard no-port core.  Exact Fraction.
"""
import subprocess, random
from fractions import Fraction as F
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _factor_gate import chi_profile as port_chi
from _wf_deficit_farkas import flip, odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski

def sign_ok(D):
    last_pos=-1; first_after=None
    seen_pos=False
    for r in range(len(D)):
        if D[r]>0: seen_pos=True
        elif D[r]<0 and seen_pos: return False
    return True

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
                profs=[]
                for i in range(len(P)):
                    Hi,W,d=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0 or W is None: continue
                    em1=ell_map(n,adj,flip(side,W))
                    profs.append(port_chi(em0,em1,n))
                D=[Z[r]-sum(ch[r] for ch in profs if r<len(ch)) for r in range(n)]
                total=sum((2*r+1)*D[r] for r in range(n))
                so=sign_ok(D)
                tag='neg' if profs else 'noport'
                acc[tag+'_rows']+=1
                if not so:
                    acc[tag+'_signfail']+=1
                    if acc[tag+'_ex'] is None: acc[tag+'_ex']=(name,n,tuple(P),[str(D[r]) for r in range(n) if D[r]!=0])
                if total<0:
                    acc[tag+'_totalfail']+=1

def maxcut_ls(n,adj,seeds=40):
    best=None;bv=-1;rng=random.Random(31)
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
    acc=dict(neg_rows=0,neg_signfail=0,neg_totalfail=0,neg_ex=None,
             noport_rows=0,noport_signfail=0,noport_totalfail=0,noport_ex=None)
    for nn in range(5,10):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: neg_rows=%d neg_signfail=%d noport_signfail=%d"%(nn,acc['neg_rows'],acc['neg_signfail'],acc['noport_signfail']),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2),(1,1,1,1,1)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    print("="*55)
    print("NEGATIVE-PORT rows:",acc['neg_rows']," sign-order fails:",acc['neg_signfail'],acc['neg_ex'] or '',"  total<0:",acc['neg_totalfail'])
    print("NO-PORT rows:",acc['noport_rows']," sign-order fails:",acc['noport_signfail'],acc['noport_ex'] or '',"  total<0(=atom viol):",acc['noport_totalfail'])

if __name__=="__main__":
    main()
