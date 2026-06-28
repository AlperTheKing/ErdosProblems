"""Two |O|=1 tests: (a) my CRUDE bound sum_q a_q R_q >= N*D (denominator-free sufficient cond for P5),
   (b) Codex's support-Hall (block 98) sum_{f in F'} c_f <= |union supp(p_f)| for subsets F' (full enum when |M| small).
   c_f = x_f^2 + sum_{q!=o} psi(q)(ell-4 x_f) p_f(q), psi(q)=a_q/(N-4a_q), x_f=p_f(o). Full-set Hall == P5."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG
from _opencap import build_K
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _stark1 import odd_blowup, gmins

def analyze(adj, side, n, hall_maxM=16):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    # K, T via build_K (consistent)
    r=build_K(adj,side,n)
    K,Tv=r; N=n
    O=[v for v in range(n) if Tv[v]>N]
    if len(O)!=1: return None
    o=O[0]; D=Tv[o]-N
    if D<=0: return None
    a={q:K[o][q] for q in range(n) if q!=o}
    R={q:F(N)-Tv[q] for q in range(n) if q!=o}
    # (a) crude bound
    crude=sum(a[q]*R[q] for q in a)   # >= N*D ?
    crude_ok = crude >= F(N)*D
    # (b) support-Hall: pf per bad edge, c_f, supp
    psi={q:(a[q]/(F(N)-4*a[q])) for q in a if a[q]>0}
    res={'o':o,'D':D,'crude':crude,'crudeND':F(N)*D,'crude_ok':crude_ok,'nbad':len(M)}
    pf={}; supp={}; cf={}
    for f in M:
        Ps=cyc[f]; k=len(Ps); L=ell[f]
        d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[f]=d; supp[f]=frozenset(d.keys())
        xf=d.get(o,F(0))
        c=xf*xf
        for q,pq in d.items():
            if q==o: continue
            c += psi.get(q,F(0))*(F(L)-4*xf)*pq
        cf[f]=c
    # full-set Hall == P5
    fullc=sum(cf.values()); fullsupp=len(set().union(*supp.values())) if supp else 0
    res['fullset_ok']=(fullc<=fullsupp); res['fullc']=fullc; res['fullsupp']=fullsupp
    # subset Hall (full enum if small)
    res['hall_fails']=0; res['hall_enum']=False
    Mlist=list(M)
    if len(Mlist)<=hall_maxM:
        res['hall_enum']=True
        for rmask in range(1,1<<len(Mlist)):
            Fp=[Mlist[i] for i in range(len(Mlist)) if rmask>>i&1]
            lhs=sum(cf[f] for f in Fp)
            rhs=len(set().union(*[supp[f] for f in Fp]))
            if lhs>rhs: res['hall_fails']+=1
    return res

def run(nm,n,E,acc,hall=True):
    adj,cuts=gmins(n,E)
    for s in cuts:
        d=analyze(adj,s,n)
        if d is None: continue
        acc['tot']+=1
        if not d['crude_ok']: acc['crude_fail']+=1
        if not d['fullset_ok']: acc['p5_fail']+=1
        if hall and d['hall_enum'] and d['hall_fails']>0: acc['hall_fail']+=1
        if not d['hall_enum']: acc['hall_skip']+=1
        if acc['maxM']<d['nbad']: acc['maxM']=d['nbad']

if __name__=="__main__":
    print("=== |O|=1: (a) CRUDE sum a_q R_q>=N D  (b) support-Hall (P5) ===",flush=True)
    # sharp family + killer: crude + full-set P5 (no enum for large M)
    for sizes in [[1,4,2,2,4],[1,8,4,2,8],[1,20,10,2,20],[1,48,6,8,48]]:
        nn,E,adj,side=odd_blowup(5,sizes)
        d=analyze(adj,side,sum(sizes),hall_maxM=0)
        if d: print(f"  C5{sizes} N={sum(sizes)}: crude_ok={d['crude_ok']} (crude={float(d['crude']):.1f} vs N*D={float(d['crudeND']):.1f}) P5_ok={d['fullset_ok']} maxM={d['nbad']}",flush=True)
    accm={'tot':0,'crude_fail':0,'p5_fail':0,'hall_fail':0,'hall_skip':0,'maxM':0}
    cur=(5,Cn(5))
    for _ in range(2): cur=mycielski(*cur); run(f"Myc{cur[0]}",cur[0],cur[1],accm)
    cur=(7,Cn(7)); cur=mycielski(*cur); run("MycC7",cur[0],cur[1],accm)
    print(f"  Mycielskians: |O|=1={accm['tot']} CRUDE-FAIL={accm['crude_fail']} P5-FAIL={accm['p5_fail']} HALL-FAIL={accm['hall_fail']} hall-skip={accm['hall_skip']} maxM={accm['maxM']}",flush=True)
    accg={'tot':0,'crude_fail':0,'p5_fail':0,'hall_fail':0,'hall_skip':0,'maxM':0}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}",n,E,accg)
    print(f"  glued battery: |O|=1={accg['tot']} CRUDE-FAIL={accg['crude_fail']} P5-FAIL={accg['p5_fail']} HALL-FAIL={accg['hall_fail']} hall-skip={accg['hall_skip']} maxM={accg['maxM']}",flush=True)
    for nnn in range(9,12):
        outg=subprocess.run([GENG,"-tc",str(nnn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'crude_fail':0,'p5_fail':0,'hall_fail':0,'hall_skip':0,'maxM':0}
        for g6 in outg:
            n,E=dec(g6); run(g6,n,E,acc)
        print(f"  census N={nnn}: |O|=1={acc['tot']} CRUDE-FAIL={acc['crude_fail']} P5-FAIL={acc['p5_fail']} HALL-FAIL={acc['hall_fail']} hall-skip={acc['hall_skip']} maxM={acc['maxM']}",flush=True)
