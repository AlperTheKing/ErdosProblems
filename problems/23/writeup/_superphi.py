"""Codex ASK (block 12): explicit Collatz-Wielandt supersolution phi for rho(K)<=N (bypasses Schur inverse).
K=P P^T, T=K1, N=n, O={T>N}, Q={T<=N}, u[q]=N-T[q] (>=0 on Q).
phi[o]=1 (o in O); phi[q]=1 - u[q]/N - (sum_{q' in Q} K[q,q'] u[q'])/N^2 (q in Q).
(A) phi[v]>=0 all v, and phi[v]>0 wherever K-row(v) nonzero;
(B) (K phi)[v] <= N phi[v] for all v.
(A)+(B) => rho(K)<=N (Perron-Frobenius) => SPEC => Gamma<=N^2. EXACT Fraction. Report any violation."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact

def build(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    return K,T,N,n

def phivec(K,T,N,n):
    O=set(v for v in range(n) if T[v]>N)
    Q=[v for v in range(n) if T[v]<=N]
    u={q:F(N)-T[q] for q in Q}
    phi=[F(0)]*n
    for v in range(n):
        if v in O: phi[v]=F(1)
        else:
            s=sum(K[v][q]*u[q] for q in Q)
            phi[v]=F(1)-u[v]/N - s/(N*N)
    return phi,O,Q

def test(info):
    K,T,N,n=build(info)
    phi,O,Q=phivec(K,T,N,n)
    # (A) phi>=0, and phi>0 where K-row nonzero
    minphi=min(phi)
    A_supp_ok=True; minphi_active=None
    for v in range(n):
        rownz = any(K[v][w]!=0 for w in range(n))
        if rownz:
            if minphi_active is None or phi[v]<minphi_active: minphi_active=phi[v]
            if phi[v]<=0: A_supp_ok=False
    # (B) Kphi <= N phi
    maxB=None
    for v in range(n):
        val=sum(K[v][w]*phi[w] for w in range(n)) - N*phi[v]
        if maxB is None or val>maxB: maxB=val
    fails=[]
    if minphi<0: fails.append('phi_neg')
    if not A_supp_ok: fails.append('phi_zero_on_active')
    if maxB>0: fails.append('Kphi>Nphi')
    return dict(minphi=minphi, minphi_active=minphi_active, maxB=maxB, fails=fails, hasO=len(O)>0)

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

def run_census(Nmax,Nmin=7,stride=1):
    for nn in range(Nmin,Nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        nt=0; fails=0; worstB=None; wg=None; minphiA=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; d=test(info)
            if d['fails']:
                fails+=1
                if wg is None: wg=(g6,d['fails'])
            if worstB is None or d['maxB']>worstB: worstB=d['maxB']
            if d['minphi_active'] is not None and (minphiA is None or d['minphi_active']<minphiA): minphiA=d['minphi_active']
        print(f"  N={nn}(str{stride}): cfg={nt} | FAILS:{fails}{' @'+str(wg) if wg else ''} | max(Kphi-Nphi)={float(worstB):+.4g} | min phi(active)={float(minphiA):+.4g}",flush=True)

if __name__=="__main__":
    print("=== explicit supersolution phi: (A) phi>=0 & (B) Kphi<=Nphi ? ===")
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E); d=test(info)
        print(f"  {g6:13} N={n}: fails={d['fails']} maxB={float(d['maxB']):+.4g} minphi(active)={float(d['minphi_active']):+.4g} hasO={d['hasO']}")
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("J?`@C_W{Ck?",2),("H?AFBo]",2)]:
        nn,EE=blow(g6,t)
        if nn>22: continue
        info=loads(nn,EE)
        if info: d=test(info); print(f"  {g6}[{t}] N={nn}: fails={d['fails']} maxB={float(d['maxB']):+.4g} minphi(active)={float(d['minphi_active']):+.4g}")
    run_census(9,7,1)
    run_census(10,10,4)
    run_census(11,11,20)
