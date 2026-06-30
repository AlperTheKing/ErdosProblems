"""Diverse Tail<0 witnesses + zero-margin concentration on glued islands + nonuniform blowups +
   sampled census N=11 -- BOUNDED straddler completions (cap), to avoid the dense-theta blow-up.
   Reports any q>0 finite-price witness (nontrivial concentration) and any F<0 with Z0>=0 (falsifier).
"""
import subprocess, itertools
from fractions import Fraction as F
import _crux_extract as cx
from _crux_extract import parity_interval_switches
from _wf_deficit_farkas import deltas, flip, gamma_of, odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint

CAP = 1 << 14

def margin_profile(n, adj, side, Gamma, P):
    Zq = {}; seen=set(); cnt=0
    for W in parity_interval_switches(n, adj, side, P):
        if not W or W in seen: continue
        seen.add(W); cnt+=1
        if cnt > CAP: break
        dB,dM=deltas(n,adj,side,W); q=dB-dM
        if q<0: continue
        s2=flip(side,W)
        if not Bconn(n,adj,s2): continue
        g1=gamma_of(n,adj,s2)
        if g1 is None: continue
        d=g1-Gamma
        if q not in Zq or d<Zq[q]: Zq[q]=d
    return Zq

def run(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    mc,cuts=cx.all_max_cuts(n,adj,E)
    structs=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        structs.append((side,st,sum(st[2])))
    if not structs: return
    gmin=min(g for (_,_,g) in structs)
    for (side,st,G) in structs:
        if G<=gmin: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        for f in M:
            if ell[f]%2==0: continue
            for P in cyc[f]:
                if len(P)!=ell[f]: continue
                _,_,Z,lhs,rhs=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                mintail=min(sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n))
                if mintail>=0: continue
                acc['neg']+=1
                Zq=margin_profile(n,adj,side,G,P)
                if not Zq: continue
                Fval=min(Zq[q]+25*q for q in Zq); Z0=Zq.get(0,None)
                argmin_q=min(Zq, key=lambda q: Zq[q]+25*q)
                if argmin_q>0: acc['qpos']+=1
                if Fval<0:
                    if Z0 is not None and Z0<0: acc['ok']+=1
                    else:
                        acc['fail']+=1
                        if acc['ex'] is None: acc['ex']=(name,n,tuple(P),str(Fval),str(Z0),sorted(Zq.items()))
                if argmin_q>0 and len(acc['qpos_ex'])<6:
                    acc['qpos_ex'].append((name,n,tuple(P),str(mintail),'argminq=%d'%argmin_q,str(Fval),str(Z0)))

def main():
    acc=dict(neg=0,ok=0,fail=0,qpos=0,ex=None,qpos_ex=[])
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9)
    glues=[((n5,E5),(n5,E5),[(0,5)]),((n5,E5),(n7,E7),[(0,5)]),((n5,E5),(n7,E7),[(0,5),(2,8)]),
           ((n7,E7),(n5,E5),[(0,7)]),((n5,E5),(n5,E5),[(0,5),(2,7)]),((n5,E5),(n7,E7),[(1,6)]),
           ((n5,E5),(n9,E9),[(0,5)]),((n7,E7),(n7,E7),[(0,7)])]
    for (a,b,br) in glues:
        n,E=union_disjoint(a,b); E=E+br
        if n<=14: run("glue",n,E,acc)
    print("glued: neg=%d ok=%d fail=%d qpos=%d"%(acc['neg'],acc['ok'],acc['fail'],acc['qpos']),flush=True)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,1,1),(3,1,2,1,2),(2,2,1,2,2)]:
        n,E=odd_blowup(5,list(sizes))
        if n<=12: run("blow",n,E,acc)
    print("blowups: neg=%d ok=%d fail=%d qpos=%d"%(acc['neg'],acc['ok'],acc['fail'],acc['qpos']),flush=True)
    print("="*55)
    print("Tail<0 rows:%d  F<0=>Z0<0 ok:%d fail:%d  q>0-finite-price-best:%d"%(acc['neg'],acc['ok'],acc['fail'],acc['qpos']))
    print("falsifier:", acc['ex'])
    print("q>0 nontrivial-concentration witnesses:")
    for w in acc['qpos_ex']: print("  ", w)
    print("VERDICT:", "CONCENTRATION HOLDS on diverse families" if acc['fail']==0 and acc['neg']>0 else
          ("no diverse Tail<0 witnesses" if acc['neg']==0 else "FALSIFIED"))

if __name__=="__main__":
    main()
