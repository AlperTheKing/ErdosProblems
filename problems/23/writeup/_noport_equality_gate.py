"""Classify the no-port atom EQUALITY geometry (Codex 406). No-port row = all singleton H_i>=0 (gamma-min-like).
   Equality: Tail_k(P)=0 for some k. Report: which configs achieve equality (Gamma, N, #bad edges, lengths),
   whether all equality rows are extremal (Gamma=N^2), and the min POSITIVE no-port Tail margin.
"""
import subprocess
from fractions import Fraction as F
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski

def run(name,n,adj,E,acc):
    mc,cuts=cx.all_max_cuts(n,adj,E); Lam=len(E)*n*n+1
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        em0=ell_map(n,adj,side); Gamma=sum(ell[g]**2 for g in M)
        for f in M:
            if ell[f]%2==0: continue
            for P in cyc[f]:
                if len(P)!=ell[f]: continue
                # no-port check
                hasneg=False
                for i in range(len(P)):
                    Hi,W,d=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is not None and Hi<0: hasneg=True; break
                if hasneg: continue
                _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                lens=tuple(sorted(ell[g] for g in M))
                for k in range(n):
                    tk=sum((2*r+1)*Z[r] for r in range(k,n))
                    acc['rows']+=1
                    if tk==0:
                        acc['eq']+=1
                        extremal=(Gamma==n*n)
                        key=(extremal,len(M),lens,Gamma==n*n)
                        acc['eq_extremal' if extremal else 'eq_nonextremal']+=1
                        sig=(name.split('-')[0],n,len(M),lens,str(Gamma),'Gamma==N^2' if extremal else 'Gamma<N^2(=%d vs %d)'%(Gamma,n*n))
                        acc['eq_sigs'][sig]=acc['eq_sigs'].get(sig,0)+1
                        if not extremal and acc['noneq_ex'] is None:
                            acc['noneq_ex']=(name,n,tuple(P),len(M),lens,str(Gamma),str(n*n))
                    elif tk>0:
                        if acc['minpos'] is None or tk<acc['minpos']:
                            acc['minpos']=tk; acc['mp_row']=(name,n,tuple(P),k,len(M),lens,str(Gamma))

def fam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    run(name,n,adj,E,acc)

def main():
    acc=dict(rows=0,eq=0,eq_extremal=0,eq_nonextremal=0,eq_sigs={},minpos=None,mp_row=None,noneq_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d-%s"%(nn,g6),n,E,acc)
        print("census N=%d: rows=%d eq=%d (extremal=%d nonextremal=%d)"%(nn,acc['rows'],acc['eq'],acc['eq_extremal'],acc['eq_nonextremal']),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw-"+g6,n,E,acc)
    for sizes in [(1,1,1,1,1),(2,2,2,2,2),(2,1,2,1,2),(2,1,2,1,3)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    for sizes in [(1,1,1,1,1,1,1)]:
        nn,EE=odd_blowup(7,list(sizes)); fam("C7%s"%(sizes,),nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    print("="*55)
    print("no-port rows-k:",acc['rows']," equality rows:",acc['eq']," (extremal Gamma=N^2:",acc['eq_extremal'],", NON-extremal:",acc['eq_nonextremal'],")")
    print("min POSITIVE no-port Tail margin:",str(acc['minpos']),"at",acc['mp_row'])
    if acc['noneq_ex']: print("FIRST NON-EXTREMAL EQUALITY:",acc['noneq_ex'])
    print("\nequality signatures (family, N, #bad, lengths, Gamma):")
    for sig,c in sorted(acc['eq_sigs'].items(), key=lambda x:-x[1])[:15]:
        print("  %dx  %s"%(c,sig))
    print("\nVERDICT:", "ALL equality rows are EXTREMAL (Gamma=N^2)" if acc['eq_nonextremal']==0 else "NON-EXTREMAL equality rows EXIST")

if __name__=="__main__":
    main()
