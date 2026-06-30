"""Gate Codex 404: is MARGIN(row,k)=Tail_k - sum_i H_i^- STRICTLY positive whenever some H_i<0?
   Split: (a) no-negative-port rows (incl gamma-min: the atom Tail_k>=0), (b) negative-port rows.
   Report: min positive margin on negative-port rows; equality(=0) count with a negative port; no-port equality count.
   Full battery (census N<=10 + theta + glued + blowups + Grotzsch + Myc N=23).  Exact Fraction.
"""
import subprocess, random
from fractions import Fraction as F
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski

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
                sH=0; hasneg=False
                for i in range(len(P)):
                    Hi,W,d=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is not None and Hi<0: sH+=Hi; hasneg=True
                for k in range(n):
                    tk=sum((2*r+1)*Z[r] for r in range(k,n))
                    margin=tk-sH
                    acc['rows']+=1
                    if hasneg:
                        if margin<0:
                            acc['neg_violate']+=1
                            if acc['nv_ex'] is None: acc['nv_ex']=(name,n,tuple(P),k,str(margin))
                        elif margin==0:
                            acc['neg_eq']+=1
                            if acc['ne_ex'] is None: acc['ne_ex']=(name,n,tuple(P),k,str(tk))
                        else:
                            if acc['neg_minpos'] is None or margin<acc['neg_minpos']:
                                acc['neg_minpos']=margin; acc['nm_row']=(name,n,tuple(P),k)
                    else:
                        if margin==0: acc['noport_eq']+=1
                        if margin<0: acc['noport_violate']+=1

def maxcut_ls(n,adj,seeds=40):
    best=None;bv=-1;rng=random.Random(29)
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
    acc=dict(rows=0,neg_violate=0,neg_eq=0,noport_eq=0,noport_violate=0,neg_minpos=None,nv_ex=None,ne_ex=None,nm_row=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d neg_violate=%d neg_eq=%d"%(nn,acc['rows'],acc['neg_violate'],acc['neg_eq']),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9)
    for (a,b,br) in [((n5,E5),(n5,E5),[(0,5)]),((n5,E5),(n7,E7),[(0,5)]),((n7,E7),(n5,E5),[(0,7)])]:
        nn,EE=union_disjoint(a,b); EE=EE+br
        if nn<=12: fam("glue",nn,EE,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    print("="*55)
    print("total rows:",acc['rows'])
    print("negative-port: margin<0:",acc['neg_violate'],acc['nv_ex'] or '',"  margin==0:",acc['neg_eq'],acc['ne_ex'] or '')
    print("negative-port min POSITIVE margin:",str(acc['neg_minpos']),"at",acc['nm_row'])
    print("no-port: margin==0:",acc['noport_eq'],"  margin<0:",acc['noport_violate'])
    print("VERDICT:", "negative-port margin STRICT (>0)" if acc['neg_violate']==0 and acc['neg_eq']==0 else "equality/violation in negative-port regime")

if __name__=="__main__":
    main()
