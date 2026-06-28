"""Codex ASK (block 5): KKT-core support-complexity of the LPD optimizer.
Maximize L(y)=sum_f (sum_i sqrt(w_fi))^2, w_fi=sum_{v in I_i(f)} y_v p_f(v), over simplex {y>=0, sum y=1}.
y* = maximizer (the KKT core), lambda=L(y*) (<=N by LPD). KKT budget B(v)=sum_{f,i:v in I_i}(A_f/sqrt(w_fi))p_f(v),
A_f=sum_i sqrt(w_fi); = lambda on supp(y*).
Tests:
 (A) overload-in-support: does y* support contain every v with T(v)>N?
 (B) single-interval reduction: is max_y L = max_f [max over y supported in supp(p_f) of L]?  gap if not.
 (C) two-interval reduction: ... over supp(p_f) U supp(p_g).
Numeric (multi-start SLSQP). Falsification/structure only."""
import numpy as np, subprocess
from scipy.optimize import minimize
from _h import dec, GENG, loads
from _layerprice import layers_of

EPS=1e-12

def setup(info):
    n=info['n']; M=info['M']
    L=[(f,)+layers_of(info,f) for f in M]
    return L,n,M

def Lval(L,y):
    tot=0.0
    for (f,lay,pf,h) in L:
        s=0.0
        for i in range(h+1):
            w=sum(y[v]*pf[v] for v in lay[i])
            s+=np.sqrt(max(w,0.0))
        tot+=s*s
    return tot

def maximizeL(L,n,allowed=None,restarts=8):
    """max L over simplex; allowed=set of vertices y may use (others forced 0)."""
    idx=list(range(n)) if allowed is None else sorted(allowed)
    m=len(idx)
    if m==0: return 0.0,np.zeros(n)
    rng=np.random.default_rng(1)
    cons=[{'type':'eq','fun':lambda z: z.sum()-1.0}]
    bnds=[(0.0,1.0)]*m
    best=-1.0; bz=None
    def neg(z):
        y=np.zeros(n)
        for k,v in enumerate(idx): y[v]=max(z[k],0.0)
        return -Lval(L,y)
    starts=[np.full(m,1.0/m)]+[rng.dirichlet(np.ones(m)) for _ in range(restarts)]
    for z0 in starts:
        r=minimize(neg,z0,method='SLSQP',bounds=bnds,constraints=cons,options={'maxiter':300,'ftol':1e-10})
        val=-r.fun
        if val>best: best=val; bz=r.x
    y=np.zeros(n)
    for k,v in enumerate(idx): y[v]=max(bz[k],0.0)
    return best,y

def run(g6,info):
    L,n,M=setup(info); N=n; T=[float(t) for t in info['T']]
    gmax,ystar=maximizeL(L,n)
    over=[v for v in range(n) if T[v]>N+1e-9]
    A_ok=all(ystar[v]>1e-6 for v in over)
    # (B) single interval
    supps=[set(pf.keys()) for (f,lay,pf,h) in L]
    best1=-1.0; b1f=None
    for ei,supp in enumerate(supps):
        v1,_=maximizeL(L,n,allowed=supp,restarts=4)
        if v1>best1: best1=v1; b1f=M[ei]
    gapB=gmax-best1
    return gmax,N,A_ok,over,best1,gapB,b1f,ystar

if __name__=="__main__":
    print("=== KKT-core support complexity: max L(y) over simplex, lambda<=N, (A) overload-in-supp, (B) single-edge ===")
    for g6 in ["FCp`_","H?bB@_W","J?AEB?oE?W?","I?BD@g]Qo","I?ABCc]}?","I?rFf_{N?"]:
        n,E=dec(g6); info=loads(n,E)
        gmax,N,A_ok,over,best1,gapB,b1f,ystar=run(g6,info)
        print(f"  {g6:13} N={n} G={info['G']} | maxL={gmax:.4f}(<=N:{gmax<=N+1e-4}) | (A)overload-in-supp:{A_ok} (#over={len(over)}) | (B)single-edge maxL={best1:.4f} gap={gapB:+.4f} @{b1f}")
    # N=22
    n,E=dec("J???E?pNu\\?"); nn=n*2; EE=[]
    for (a,b) in E:
        for i in range(2):
            for j in range(2): EE.append((a*2+i,b*2+j))
    info=loads(nn,EE); gmax,N,A_ok,over,best1,gapB,b1f,ystar=run("J???E?pNu?[2]",info)
    print(f"  J???E?pNu?[2] N={nn} | maxL={gmax:.3f}(<=N:{gmax<=N+1e-3}) | (A):{A_ok}(#over={len(over)}) | (B)gap={gapB:+.4f}")
    # census N=8,9: (A) failures, (B) gap stats
    for nn2 in (8,9):
        out=subprocess.run([GENG,"-tc",str(nn2)],capture_output=True,text=True).stdout.split()
        Afail=0; Bgapmax=None; Bg6=None; nt=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; gmax,N,A_ok,over,best1,gapB,b1f,ystar=run(g6,info)
            if not A_ok: Afail+=1
            if Bgapmax is None or gapB>Bgapmax: Bgapmax=gapB; Bg6=g6
        print(f"  census N={nn2}: cfg={nt} | (A) overload-in-supp FAILS:{Afail} | (B) max single-edge gap={Bgapmax:+.4f}@{Bg6} (gap=0 => single-edge reduction holds)",flush=True)
