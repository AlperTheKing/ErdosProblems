"""End-to-end EXACT verification of the CW chain + handle the T_v=0 (or S_v=0) zero-support issue.
Collatz-Wielandt: for K>=0 entrywise and d>0 (strictly positive), rho(K) <= max_v (Kd)_v/d_v.
ISSUE: T_v=0 for vertices on NO geodesic. But such vertices have K row = 0 too (K_vw=sum_f p_f(v)p_f(w),
and T_v=0 => p_f(v)=0 for all f => K row v =0 AND K col v=0). So K restricted to supp(T) is the only nonzero
block; rho(K)=rho(K|_supp). On supp(T), T>0, apply CW. So zeros are harmless. VERIFY: supp(T)==supp(S)==
{v: K row nonzero}, and on that support d=T>0, CW gives rho<=N. Also confirm numeric rho(K)<=N (eig)."""
import subprocess
import numpy as np
from fractions import Fraction as F
from _h import dec, GENG, loads

def build(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']; cyc=info['cyc']; m=len(M)
    pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    K=[[F(0)]*n for _ in range(n)]
    for d in pf:
        for v,pv in d.items():
            for w,pw in d.items(): K[v][w]+=pv*pw
    T=[sum(F(ell[M[g]])*pf[g].get(v,F(0)) for g in range(m)) for v in range(n)]
    S=[sum(pf[g].get(v,F(0)) for g in range(m)) for v in range(n)]
    return n,N,K,T,S

def check(info):
    n,N,K,T,S=build(info)
    # support consistency
    suppT=set(v for v in range(n) if T[v]!=0)
    suppS=set(v for v in range(n) if S[v]!=0)
    suppKrow=set(v for v in range(n) if any(K[v][w]!=0 for w in range(n)))
    ok_supp=(suppT==suppS==suppKrow)
    # zero-row vertices have zero K row AND col
    zero_ok=all((all(K[v][w]==0 for w in range(n)) and all(K[w][v]==0 for w in range(n)))
                for v in range(n) if v not in suppT)
    # CW on support with d=T
    maxr=F(0)
    for v in suppT:
        kd=sum(K[v][w]*T[w] for w in range(n))
        r=kd/T[v]
        if r>maxr: maxr=r
    cw_ok=(maxr<=F(N))
    # numeric rho(K)
    Kn=np.array([[float(K[v][w]) for w in range(n)] for v in range(n)])
    rho=max(abs(np.linalg.eigvalsh(Kn)))  # K symmetric PSD
    return ok_supp,zero_ok,cw_ok,float(maxr),rho,N

def cycle_blowup(L,q):
    nn=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
    return nn,E

def run():
    print("=== chain verify: supp consistency, zero-row harmless, CW d=T => rho<=N, numeric rho ===")
    bad_supp=0; bad_zero=0; bad_cw=0; bad_rho=0; ng=0; worst_rho_over_N=0.0
    for nn in range(7,11):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            ng+=1
            os_,zo,cw,mr,rho,N=check(info)
            if not os_: bad_supp+=1
            if not zo: bad_zero+=1
            if not cw: bad_cw+=1
            if rho>N+1e-9: bad_rho+=1
            if rho/N>worst_rho_over_N: worst_rho_over_N=rho/N
    print(f"  census N=7..10 graphs={ng}: supp-inconsistent={bad_supp} zero-row-not-harmless={bad_zero} CW-fail={bad_cw} numeric-rho>N={bad_rho}")
    print(f"  worst numeric rho(K)/N = {worst_rho_over_N:.6f}")

if __name__=="__main__":
    run()
    print("--- blowups (extremal, rho should =N) ---")
    for L,q in [(5,3),(5,4),(7,2),(7,3),(9,2)]:
        nn=L*q
        n,E=cycle_blowup(L,q); info=loads(n,E)
        if info is None: continue
        os_,zo,cw,mr,rho,N=check(info)
        print(f"  C{L}[{q}] N={nn}: supp_ok={os_} zero_ok={zo} CW(d=T)max={mr:.4f}<=N CW_ok={cw} numeric rho={rho:.5f} (=N={nn}? {abs(rho-nn)<1e-6})")
