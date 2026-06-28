"""Rigorously verify the layer-price SOS certificate is REAL: extract prices b_{f,i} from the solver,
check (a) harmonic sum_i 1/b_{f,i} <= 1, (b) budget sum_{f,i:v in I_i} b_{f,i}p_f(v) <= N per vertex,
(c) reconstruct N*I - K = sum_f(D_f - p_f p_f^T) + (N*I - sum_f D_f) and confirm min-eigenvalue >= 0 (PSD).
If (a),(b) hold then PSD is guaranteed by construction; (c) is the independent numeric confirmation.
Then census stress: does feasibility (t*<=N) hold for all graphs? Flag any t*>N (certificate FAILS)."""
import numpy as np
import subprocess
from _h import dec, GENG, loads
from _layerprice import solve_layerprice, layers_of, Cblow
from scipy.optimize import minimize

def get_prices(info):
    """re-solve and return the price dict b[(f,i)] and t*."""
    n=info['n']; M=info['M']; N=n
    idx={}; nv=0; perf=[]; Ls=[]
    for f in M:
        lay,pf,h=layers_of(info,f); Ls.append((lay,pf,h)); rng=[]
        for i in range(h+1): idx[(f,i)]=nv; rng.append(nv); nv+=1
        perf.append(rng)
    nvar=nv+1
    vbud={v:[] for v in range(n)}
    for fi,f in enumerate(M):
        lay,pf,h=Ls[fi]
        for i in range(h+1):
            for v in lay[i]: vbud[v].append((idx[(f,i)],pf[v]))
    cons=[]
    for rng in perf: cons.append({'type':'ineq','fun':(lambda z,rng=rng:1.0-sum(z[k] for k in rng))})
    for v in range(n):
        terms=vbud[v]
        if terms: cons.append({'type':'ineq','fun':(lambda z,terms=terms,nv=nv:z[nv]-sum(p/max(z[ci],1e-9) for ci,p in terms))})
    x0=np.full(nvar,0.5)
    for rng in perf:
        for k in rng: x0[k]=1.0/len(rng)
    x0[nv]=float(N)
    bnds=[(1e-6,1.0)]*nv+[(0,None)]
    res=minimize(lambda z:z[nv],x0,jac=lambda z:np.eye(nvar)[nv],constraints=cons,bounds=bnds,method='SLSQP',options={'maxiter':1000,'ftol':1e-10})
    c=res.x[:nv]
    b={key:1.0/c[idx[key]] for key in idx}
    return b,idx,perf,Ls,M,res.fun

def verify(g6):
    n,E=dec(g6); info=loads(n,E); N=n; M=info['M']
    b,idx,perf,Ls,_,tstar=get_prices(info)
    # (a) harmonic
    harm_ok=True; harm_max=0
    for fi,f in enumerate(M):
        lay,pf,h=Ls[fi]
        s=sum(1.0/b[(f,i)] for i in range(h+1))
        harm_max=max(harm_max,s)
        if s>1+1e-6: harm_ok=False
    # (b) budget per vertex
    bud={v:0.0 for v in range(n)}
    for fi,f in enumerate(M):
        lay,pf,h=Ls[fi]
        for i in range(h+1):
            for v in lay[i]: bud[v]+=b[(f,i)]*pf[v]
    bud_max=max(bud.values())
    # (c) reconstruct N*I-K and check PSD
    P=np.zeros((n,len(M)))
    for fi,f in enumerate(M):
        lay,pf,h=Ls[fi]
        for v in pf: P[v,fi]=pf[v]
    K=P@P.T
    # D = sum_f D_f, D_f(v)=b[(f,layer(v))]*p_f(v) on diagonal
    D=np.zeros(n)
    for fi,f in enumerate(M):
        lay,pf,h=Ls[fi]
        for i in range(h+1):
            for v in lay[i]: D[v]+=b[(f,i)]*pf[v]
    M1=N*np.eye(n)-K
    mineig=np.linalg.eigvalsh(M1).min()
    print(f"  {g6:14} N={n} G={info['G']} | t*={tstar:.4f}<=N:{tstar<=N+1e-4} | harmonic max={harm_max:.4f}(<=1:{harm_ok}) | budget max={bud_max:.4f}(<=N:{bud_max<=N+1e-4}) | min-eig(N*I-K)={mineig:.4f}")

def census(Nmax,Nmin=8,stride=1):
    print(f"--- census stress: layer-price feasibility t*<=N (stride {stride}) ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        nt=0; infeas=0; worst=None; wg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1
            t,ok=solve_layerprice(info)
            if t>n+1e-3: infeas+=1
            r=t-n
            if worst is None or r>worst: worst=r; wg=g6
        print(f"  N={nn}: cfg={nt} | t*>N (INFEASIBLE):{infeas} | max(t*-N)={worst:+.4f}@{wg}",flush=True)

if __name__=="__main__":
    print("=== verify certificate REAL (harmonic + budget + PSD reconstruction) ===")
    for g6 in ["FCp`_","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?"]:
        verify(g6)
    print("--- N=22 sandwich-killer blowup ---")
    n,E=dec("J???E?pNu\\?"); nn=n*2; EE=[]
    for (a,b) in E:
        for i in range(2):
            for j in range(2): EE.append((a*2+i,b*2+j))
    info=loads(nn,EE)
    t,ok=solve_layerprice(info)
    print(f"  J???E?pNu?[2] N={nn} G={info['G']} | t*={t:.4f} <= N={nn}? {t<=nn+1e-3}")
    census(9,8,1)
    census(10,10,5)
