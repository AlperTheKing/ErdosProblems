"""Final stress of the reduction rho(O)<=N (equiv ROWSUM-O, op-norm form) on big blowups N up to ~25,
plus record the key structural facts found:
  - p_f factorizes via shortest-path counts (betweenness) [proven 0-mismatch]
  - S(v)<=deg_B(v) holds except tiny (0.143) misses -> NOT a clean lemma
  - rho(O)=N tight ONLY at odd-cycle blowups (circulant), C7 has degB=2 but rho=7 -> no local cert
"""
import subprocess
import numpy as np
from fractions import Fraction as F
from _h import dec, loads

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def rho_over_N(info):
    M=info['M']; n=info['n']; m=len(M)
    if m==0: return 0.0
    pfs=[pf_vec(info,f) for f in M]
    P=np.zeros((n,m))
    for j,d in enumerate(pfs):
        for v,val in d.items(): P[v,j]=float(val)
    return np.linalg.eigvalsh(P.T@P)[-1]/n

def Cblow(k,q):
    L=2*k+1; m=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
    return m,E

def blowup_g6(g6,t):
    n,E=dec(g6); nn=n*t; EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return nn,EE

if __name__=="__main__":
    print("=== rho(O)/N on stress blowups (must be <=1; =1 at odd-cycle extremals) ===")
    for (k,q) in [(2,5),(3,3),(4,2),(2,4)]:
        m,E=Cblow(k,q); info=loads(m,E)
        if info: print(f"  C{2*k+1}[{q}] N={m}: rho/N={rho_over_N(info):.5f}",flush=True)
    for g6,t in [("J???E?pNu\\?",2),("J?AEB?oE?W?",2),("H?bB@_W",2),("I?rFf_{N?",2),("I?BD@g]Qo",2)]:
        try:
            nn,EE=blowup_g6(g6,t); info=loads(nn,EE)
            if info: print(f"  {g6}[{t}] N={nn}: rho/N={rho_over_N(info):.5f}",flush=True)
        except Exception as e:
            print(f"  {g6}[{t}]: {e}")
