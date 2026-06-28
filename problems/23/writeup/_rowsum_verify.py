"""MY OWN independent EXACT verification of the workflow's ROWSUM-O breakthrough (4th check; false-closure discipline).
Claim: for every bad edge f, (O1)_f := sum_g O_fg = sum_v p_f(v) S(v) <= N, S(v)=sum_g p_g(v).
Then O entrywise>=0 symmetric => rho(O) <= max_f (O1)_f <= N => ell^T O ell = sum_v T^2 <= N*Gamma
=> (Cauchy-Schwarz) Gamma <= N^2. I recompute O EXACTLY with Fractions (NOT the agents' scripts, NOT numpy)."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def exact_O_rowsums(info):
    """return list over bad edges f of (O1)_f = sum_v p_f(v) S(v), exact. Also Gamma, N."""
    n=info['n']; M=info['M']; cyc=info['cyc']; N=n
    # p_f(v) exact = count_f(v)/nf
    pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for P in Ps:
            for v in P: cnt[v]=cnt.get(v,0)+1
        pf.append({v: F(cnt[v],nf) for v in cnt})
    # S(v) = sum_f p_f(v)
    S={}
    for d in pf:
        for v,val in d.items(): S[v]=S.get(v,F(0))+val
    rowsums=[]
    for d in pf:
        rs=sum(val*S[v] for v,val in d.items())   # sum_v p_f(v) S(v) = sum_g <p_f,p_g>
        rowsums.append(rs)
    return rowsums, info['G'], N

def blowup(n,E,t):
    nn=n*t; EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return nn,EE

def run_census(Nmax,Nmin=5):
    print("--- MY exact ROWSUM-O: max_f (O1)_f <= N ? (census) ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; viol=0; worst=None; wg=None; gam_bad=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1
            rs,G,N=exact_O_rowsums(info)
            mx=max(rs) if rs else F(0)
            if mx>N: viol+=1
            if worst is None or (mx-N)>worst: worst=mx-N; wg=g6
            if G>N*N: gam_bad+=1   # sanity: Gamma<=N^2 must hold
        print(f"  N={nn}: graphs-with-bad={nt} | ROWSUM-O violations(max O1 > N):{viol} | max(O1-N)={float(worst):+.4f}@{wg} | Gamma>N^2:{gam_bad}",flush=True)

if __name__=="__main__":
    print("=== KEY witnesses (exact) ===")
    # N=22 sandwich-killer + tight extremals + blowups
    cases=[("J???E?pNu\\?",2),("J?AEB?oE?W?",2),("H?bB@_W",2),("I?rFf_{N?",2)]
    for g6,t in cases:
        n,E=dec(g6); nn,EE=blowup(n,E,t)
        info=loads(nn,EE)
        if info is None: print(f"  {g6}[{t}]: skip"); continue
        rs,G,N=exact_O_rowsums(info); mx=max(rs)
        print(f"  {g6}[{t}] N={nn} Gamma={G} N^2={nn*nn} | max(O1)={float(mx):.4f} <= N={nn}? {mx<=nn} | (O1-N)={float(mx-nn):+.4f}")
    # big C5/C7 blowups
    def Cblow(k,q):
        L=2*k+1; m=L*q; E=[]
        for i in range(L):
            for a in range(q):
                for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
        return m,E
    for (k,q) in [(2,4),(3,3),(4,2)]:   # N=20,21,18 (maxcut_all feasible <=~22)
        m,E=Cblow(k,q)
        info=loads(m,E)
        if info is None: print(f"  C{2*k+1}[{q}] N={m}: skip (maxcut too big?)"); continue
        rs,G,N=exact_O_rowsums(info); mx=max(rs)
        print(f"  C{2*k+1}[{q}] N={m} Gamma={G} | max(O1)={float(mx):.4f} (=N={m}? {mx==m})")
    run_census(11,5)
