"""Lemma-B transport structure dump (Codex 390 proof-discovery).
   D_r = Z_r(P) - sum_{i:H_i<0} chi_i(r);  Lemma B == suffix sums sum_{r>=k} (2r+1) D_r >= 0 for all k.
   On H?AFBo] negative-port rows: dump D_r, w_r*D_r, suffix sums, and the source/demand layer split, plus the
   bad-edge composition of each Z_r layer (m_r contributors) and the port composition of each chi layer,
   so the canonical atom labels can be designed.  Exact Fraction.
"""
from fractions import Fraction as F
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _factor_gate import chi_profile
from _wf_deficit_farkas import flip
from _h import dec, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side

n,E=dec("H?AFBo]")
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
Lam=len(E)*n*n+1
mc,cuts=cx.all_max_cuts(n,adj,E)
structs=[]
for side in cuts:
    if not Bconn(n,adj,side): continue
    st=struct_for_side(n,adj,side)
    if st is None: continue
    structs.append((side,st,sum(st[2])))
gmin=min(g for (_,_,g) in structs)
shown=0
for (side,st,G) in structs:
    if G<=gmin or shown>=3: continue
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: continue
    em0=ell_map(n,adj,side)
    for f in M:
        if ell[f]%2==0: continue
        for P in cyc[f]:
            if len(P)!=ell[f] or shown>=3: continue
            _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
            if min(sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n))>=0: continue
            # negative ports + chi
            negports=[]
            for i in range(len(P)):
                Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                if Hi is None or Hi>=0 or W is None: continue
                em1=ell_map(n,adj,flip(side,W))
                chi=chi_profile(em0,em1,n)
                negports.append((i,sorted(W),chi))
            # D_r
            D=[Z[r]-sum(ch[r] for (_,_,ch) in negports if r<len(ch)) for r in range(n)]
            print("="*60)
            print("side=%s f=%s P=%s Gamma=%d"%(''.join(map(str,side)),f,tuple(P),G))
            print("bad edges (g:ell):", [(tuple(sorted(e)),ell[e]) for e in M])
            print("negative ports (i, W):", [(i,W) for (i,W,_) in negports])
            print("layer r | Z_r | sum_chi_r | D_r | w_r*D_r | suffix>=r")
            for r in range(n):
                sc=sum(ch[r] for (_,_,ch) in negports if r<len(ch))
                suf=sum((2*rr+1)*D[rr] for rr in range(r,n))
                if Z[r]!=0 or sc!=0 or D[r]!=0:
                    print("  r=%d | %s | %s | %s | %s | %s"%(r,str(Z[r]),str(sc),str(D[r]),str((2*r+1)*D[r]),str(suf)))
            shown+=1
print("\n(dumped %d H?AFBo] negative-port rows)"%shown)
