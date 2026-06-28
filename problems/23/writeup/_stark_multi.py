"""GENERAL |O|>=2 multi-port analog of STAR-K1 -- a SUFFICIENT matrix condition for cond3 (no full inverse).
   A_QQ = N I_Q - K_QQ = L_{K[Q]} + diag(R_q + s_q) >= diag(R_q+s_q), s_q=sum_{o in O}K[o,q], R_q=N-T(q).
   => K_OQ A_QQ^{-1} K_QO <= sum_q k_q k_q^T/(R_q+s_q), k_q=(K[o,q])_{o in O}.
   So Schur(A/A_QQ) = (N I_O - K_OO) - K_OQ A_QQ^{-1} K_QO >= Z := N I_O - K_OO - sum_q k_q k_q^T/(R_q+s_q).
   (STAR-K-multi):  Z >= 0 (PSD)  ==> cond3. Exact Fraction. Compare vs full-g (which always holds)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _opencap import build_K, opencap
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _stark1 import odd_blowup, gmins
from _gcd import is_psd_exact

def stark_multi(adj, side, n):
    r=build_K(adj,side,n)
    if r is None: return None
    K,T=r; N=n
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    if not O: return dict(skip=True)
    m=len(O); oi={o:i for i,o in enumerate(O)}
    # Z = N I_O - K_OO - sum_q k_q k_q^T/(R_q+s_q)
    Z=[[ (F(N) if O[i]==O[j] else F(0)) - K[O[i]][O[j]] for j in range(m)] for i in range(m)]
    denbad=0
    for q in Q:
        s_q=sum(K[o][q] for o in O); R_q=F(N)-T[q]; den=R_q+s_q
        if den<=0:
            denbad+=1; continue
        kq=[K[o][q] for o in O]
        for i in range(m):
            if kq[i]==0: continue
            for j in range(m):
                if kq[j]==0: continue
                Z[i][j]-=kq[i]*kq[j]/den
    psd=is_psd_exact(Z,m)
    return dict(O=m,psd=psd,denbad=denbad)

def run(nm,n,E,acc,report=False):
    adj,cuts=gmins(n,E)
    for s in cuts:
        d=stark_multi(adj,s,n)
        if d is None or d.get('skip'): continue
        acc['tot']+=1
        if not d['psd']: acc['fail']+=1;
        if d['denbad']: acc['denbad']+=1
        acc['maxO']=max(acc['maxO'],d['O'])
    if report and acc['tot']:
        print(f"  {nm} N={n}: O-cuts={acc['tot']} STARK-MULTI-FAIL={acc['fail']} maxO={acc['maxO']} denbad={acc['denbad']}",flush=True)

if __name__=="__main__":
    print("=== STAR-K-multi: Z=N I_O - K_OO - sum_q k_q k_q^T/(R_q+s_q) >= 0  (sufficient for cond3) ===",flush=True)
    # Mycielskians incl N=23 (|O|=2 there) + blow-ups (|O|>1)
    cur=(5,Cn(5))
    for nm in ["Grotzsch=N11","Myc2(C5)=N23"]:
        cur=mycielski(*cur); a={'tot':0,'fail':0,'denbad':0,'maxO':0}; run(nm,cur[0],cur[1],a,True)
    cur=(7,Cn(7)); cur=mycielski(*cur); a={'tot':0,'fail':0,'denbad':0,'maxO':0}; run("MycC7=N15",cur[0],cur[1],a,True)
    # overloaded blow-ups (|O| large)
    from _superphi import blow
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t); a={'tot':0,'fail':0,'denbad':0,'maxO':0}; run(f"{g6}[{t}]",nn,EE,a,True)
    # uniform extremal C5[t], C7[t] (T==N, O empty -> skip) and NON-uniform blow-ups (|O|=1 mostly)
    for sizes in [[2,2,2,2,3],[3,3,2,2,3],[1,8,4,2,8]]:
        nn,E,adj,side=odd_blowup(5,sizes)
        d=stark_multi(adj,side,sum(sizes))
        if d and not d.get('skip'): print(f"  C5{sizes} N={sum(sizes)}: O={d['O']} STARK-MULTI-PSD={d['psd']} denbad={d['denbad']}",flush=True)
    # glued battery
    ag={'tot':0,'fail':0,'denbad':0,'maxO':0}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}",n,E,ag)
    print(f"  glued battery: O-cuts={ag['tot']} STARK-MULTI-FAIL={ag['fail']} maxO={ag['maxO']} denbad={ag['denbad']}",flush=True)
    # census N=8..11
    for nnn in range(8,12):
        outg=subprocess.run([GENG,"-tc",str(nnn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'fail':0,'denbad':0,'maxO':0}
        for g6 in outg:
            n,E=dec(g6); run(g6,n,E,acc)
        print(f"  census N={nnn}: O-cuts={acc['tot']} STARK-MULTI-FAIL={acc['fail']} maxO={acc['maxO']} denbad={acc['denbad']}",flush=True)
