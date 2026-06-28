"""STAR-K1 and the sharpened STAR-K1-6/5 (Codex blocks 94,96), exact. Lean: Codex's sharp family
   C5(1,m,m/2,2,m) (ratio->6/5 as m->inf) + census N=9..11 |O|=1 + Mycielskians + glued.
   STAR-K1:     LB1_K := sum_{q: a_q>0,R_q>0} a_q R_q/(a_q+R_q) >= D       (sufficient for cond3|O1)
   STAR-K1-6/5: LB1_K >= (6/5) D."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _opencap import build_K
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _stark1 import odd_blowup, gmins   # reuse construction + gamma-min cut finder

def stark1_ratio(adj, side, n):
    r=build_K(adj,side,n)
    if r is None: return None
    K,T=r; N=n
    O=[v for v in range(n) if T[v]>N]
    if len(O)!=1: return None
    o=O[0]; D=T[o]-N
    if D<=0: return None
    LB1=F(0)
    for q in range(n):
        if q==o: continue
        aq=K[o][q]; Rq=F(N)-T[q]
        if aq>0 and Rq>0: LB1+=aq*Rq/(aq+Rq)
    return dict(o=o,D=D,LB1=LB1,ratio=LB1/D, ok1=(LB1>=D), ok65=(LB1>=F(6,5)*D))

if __name__=="__main__":
    print("=== STAR-K1 / STAR-K1-6/5 (pure-K |O|=1) exact ===",flush=True)
    print("--- Codex sharp family C5(1,m,m/2,2,m) ---",flush=True)
    for m in (4,8,20,50,100,400):
        if m%2!=0: continue
        sizes=[1,m,m//2,2,m]; n=sum(sizes)
        nn,E,adj,side=odd_blowup(5,sizes)
        d=stark1_ratio(adj,side,nn)
        if d is None: print(f"  C5(1,{m},{m//2},2,{m}) N={n}: not |O|=1"); continue
        print(f"  C5(1,{m},{m//2},2,{m}) N={n}: ratio={float(d['ratio']):.6f} STAR-K1={d['ok1']} STAR-K1-6/5={d['ok65']} (ratio-6/5={float(d['ratio']-F(6,5)):+.3e})",flush=True)
    # the original killer family
    nn,E,adj,side=odd_blowup(5,[1,48,6,8,48])
    d=stark1_ratio(adj,side,nn)
    print(f"  C5(1,48,6,8,48) N={nn}: ratio={float(d['ratio']):.6f} STAR-K1={d['ok1']} STAR-K1-6/5={d['ok65']}",flush=True)
    # Mycielskians + glued + census
    def run(nm,n,E,acc):
        adj,cuts=gmins(n,E)
        for s in cuts:
            d=stark1_ratio(adj,s,n)
            if d is None: continue
            acc['tot']+=1
            if not d['ok1']: acc['f1']+=1
            if not d['ok65']: acc['f65']+=1
            if acc['minr'] is None or d['ratio']<acc['minr']: acc['minr']=d['ratio']; acc['wit']=(nm,d['o'])
    cur=(5,Cn(5)); accm={'tot':0,'f1':0,'f65':0,'minr':None,'wit':None}
    for _ in range(2): cur=mycielski(*cur); run(f"Myc{cur[0]}",cur[0],cur[1],accm)
    cur=(7,Cn(7)); cur=mycielski(*cur); run("MycC7",cur[0],cur[1],accm)
    print(f"  Mycielskians: |O|=1 cuts={accm['tot']} STAR-K1-FAIL={accm['f1']} 6/5-FAIL={accm['f65']} min-ratio={float(accm['minr']) if accm['minr'] else None}",flush=True)
    accg={'tot':0,'f1':0,'f65':0,'minr':None,'wit':None}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}",n,E,accg)
    print(f"  glued battery: |O|=1 cuts={accg['tot']} STAR-K1-FAIL={accg['f1']} 6/5-FAIL={accg['f65']} min-ratio={float(accg['minr']) if accg['minr'] else None}",flush=True)
    for nnn in range(9,12):
        outg=subprocess.run([GENG,"-tc",str(nnn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'f1':0,'f65':0,'minr':None,'wit':None}
        for g6 in outg:
            n,E=dec(g6); run(g6,n,E,acc)
        print(f"  census N={nnn}: |O|=1 cuts={acc['tot']} STAR-K1-FAIL={acc['f1']} 6/5-FAIL={acc['f65']} min-ratio={float(acc['minr']) if acc['minr'] else None} wit={acc['wit']}",flush=True)
