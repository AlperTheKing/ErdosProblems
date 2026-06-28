"""Codex ASK (block 10): finite-depth Neumann strengthening of the Schur row-sum (condition 3).
K=PP^T, T=K1, O={T>N}, Q=V\\O, r=N-T (>=0 on Q, <0 on O). g_k = sum_{t=0}^{k-1} (K_QQ/N)^t (r_Q/N) = first k
Neumann terms of (N I - K_QQ)^{-1} r_Q. Test: for every o in O, r[o] + K[o,Q]·g_k >= 0. Is k=2 always enough?
(k=infinity is the exact Schur E row-sum, already verified >=0.) If k=2 fails, find smallest k (<=12) that passes.
EXACT Fraction."""
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
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    return K,T,O,Q,N,n

def neumann_resid(K,T,O,Q,N,n,kmax):
    """return min over o of (r[o]+K[o,Q].g_k) for k=1..kmax; dict k->min."""
    r={v:F(N)-T[v] for v in range(n)}
    rQ=[r[q] for q in Q]
    # g accumulates; term_t = (K_QQ/N)^t (r_Q/N)
    KQQ=[[K[Q[i]][Q[j]] for j in range(len(Q))] for i in range(len(Q))]
    term=[x/N for x in rQ]   # t=0 term: r_Q/N
    g=[F(0)]*len(Q)
    out={}
    for k in range(1,kmax+1):
        for i in range(len(Q)): g[i]=g[i]+term[i]
        # min over o of r[o] + sum_q K[o,q] g[q]
        mn=None
        for o in O:
            val=r[o]+sum(K[o][Q[j]]*g[j] for j in range(len(Q)))
            if mn is None or val<mn: mn=val
        out[k]=mn
        # next term = (K_QQ/N) * term
        nt=[sum(KQQ[i][j]*term[j] for j in range(len(Q)))/N for i in range(len(Q))]
        term=nt
    return out

def test(info,kmax=12):
    K,T,O,Q,N,n=build(info)
    if not O: return ('noO',{})
    out=neumann_resid(K,T,O,Q,N,n,kmax)
    return ('ok',out)

def run_census(Nmax,Nmin=7,stride=1):
    for nn in range(Nmin,Nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        nt=0; k2fail=0; worst2=None; wg=None; maxk=1
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            st,out=test(info)
            if st=='noO': continue
            nt+=1
            if out[2]<0:
                k2fail+=1
                # smallest k passing
                ks=next((k for k in sorted(out) if out[k]>=0),None)
                if ks: maxk=max(maxk,ks)
                if worst2 is None or out[2]<worst2: worst2=out[2]; wg=(g6,ks)
        print(f"  N={nn}(str{stride}): graphs-with-O={nt} | k=2 FAILS:{k2fail}{(' worst k2='+str(float(worst2))+' smallest-k-pass='+str(wg)) if worst2 is not None else ''} | max k needed={maxk}",flush=True)

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

if __name__=="__main__":
    print("=== Neumann depth: is k=2 enough for Schur row-sum >=0 ? (min over o of r[o]+K[o,Q].g_k) ===")
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?"]:
        n,E=dec(g6); info=loads(n,E); st,out=test(info)
        print(f"  {g6:13} N={n}: k=2 min={float(out[2]):+.4f} (k1={float(out[1]):+.3f} k3={float(out[3]):+.3f}) {'OK' if out[2]>=0 else 'k2 FAIL'}")
    nn,EE=blow("J???E?pNu\\?",2); info=loads(nn,EE); st,out=test(info)
    print(f"  J???E?pNu?[2] N={nn}: k=2 min={float(out[2]):+.4f} {'OK' if out[2]>=0 else 'k2 FAIL'}")
    for g6 in ["I?BD@g]Qo","J?`@C_W{Ck?"]:
        nn,EE=blow(g6,2); info=loads(nn,EE)
        if info and nn<=22:
            st,out=test(info); print(f"  {g6}[2] N={nn}: k=2 min={float(out[2]):+.4f} {'OK' if out[2]>=0 else 'k2 FAIL'}")
    run_census(9,7,1)
    run_census(10,10,5)
    run_census(11,11,30)
