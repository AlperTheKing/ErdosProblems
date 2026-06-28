"""Codex ASK (block 15): HALF sublemma for k2. For overloaded o:
  sum_f p_f(o) H_f  >=  (N^2/2) sum_f p_f(o)(ell(f)-4).
H_f=sum_{q in Q} p_f(q) psi(q), psi(q)=N u(q)+(K_QQ u)(q), u=N-T on Q.
Simplification: sum_f p_f(o)H_f = sum_{q in Q} K[o,q] psi(q); RHS = (N^2/2)(T(o)-4 S(o)).
HALF => k2 for o with T(o)+4 S(o) <= 2N (low regime). Exact-test HALF (all o) + coverage."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _superphi import build, blow
from _schur_spec import pf_exact

def analyze(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
    u={q:F(N)-T[q] for q in Q}
    W={q:sum(K[q][q2]*u[q2] for q2 in Q) for q in Q}
    psi={q:F(N)*u[q]+W[q] for q in Q}
    Sf=[{v:p for v,p in d.items()} for d in P]
    # S(o)=sum_f p_f(o)
    res=[]
    for o in O:
        S_o=sum(d.get(o,F(0)) for d in P)
        lhs=sum(K[o][q]*psi[q] for q in Q)          # sum_f p_f(o) H_f
        rhs=F(N*N,2)*(T[o]-4*S_o)
        half_margin=lhs-rhs
        low = (T[o]+4*S_o <= 2*N)
        # k2 margin*N^2 = N^2(N-T[o]) + sum_f p_f(o)H_f
        k2m=F(N*N)*(F(N)-T[o]) + lhs
        res.append((o,half_margin,low,k2m,S_o,T[o]))
    return res,N

def run(Nmax,Nmin=8,stride=1):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        nO=0; halfbad=0; worsthalf=None; wg=None; low=0; lowk2bad=0; minlowk2=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            res,N=analyze(info)
            for (o,hm,islow,k2m,So,To) in res:
                nO+=1
                if hm<0: halfbad+=1
                if worsthalf is None or hm<worsthalf: worsthalf=hm; wg=(g6,o)
                if islow:
                    low+=1
                    if k2m<0: lowk2bad+=1
                    if minlowk2 is None or k2m<minlowk2: minlowk2=k2m
        print(f"  N={nn}(str{stride}): overloaded-verts={nO} | HALF fails:{halfbad} (min margin={float(worsthalf):+.3f}@{wg}) | low-regime(T+4S<=2N):{low} closed-by-HALF, k2 bad in low:{lowk2bad} | high-regime={nO-low}",flush=True)

if __name__=="__main__":
    print("=== HALF sublemma test + coverage (low regime T+4S<=2N closed by HALF) ===")
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); info=loads(n,E); res,N=analyze(info)
        hb=sum(1 for r in res if r[1]<0); lo=sum(1 for r in res if r[2]); hi=len(res)-lo
        print(f"  {g6:13} N={n}: |O|={len(res)} HALF-fails={hb} min-margin={float(min((r[1] for r in res),default=0)):+.3f} | low(closed)={lo} high={hi}")
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("J?`@C_W{Ck?",2)]:
        nn,EE=blow(g6,t)
        if nn>22: continue
        info=loads(nn,EE)
        if info is None: continue
        res,N=analyze(info); hb=sum(1 for r in res if r[1]<0); lo=sum(1 for r in res if r[2])
        print(f"  {g6}[{t}] N={nn}: |O|={len(res)} HALF-fails={hb} low(closed)={lo} high={len(res)-lo}")
    run(9,8,1); run(10,10,4); run(11,11,15)
