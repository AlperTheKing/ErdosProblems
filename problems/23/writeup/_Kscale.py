"""rho(O)=rho(K), K_{vw}=sum_f p_f(v)p_f(w) entrywise>=0, row sums T(v). max T(v) can exceed N.
Perron-Frobenius: rho(K)<=N iff EXISTS positive d>0 with (K d)_v <= N d_v for all v (Collatz-Wielandt on K).
Find such d. Natural candidates: d=1 (=> row sums T<=N, FALSE), d=T, d=S, d=1/(N-T)_+...
Test d=T: (K T)_v = sum_w K_{vw}T(w) <= N T(v)?   K T = sum_f p_f (p_f . T) = sum_f p_f <p_f,T> = sum_f p_f C2(f)
  where C2(f)=<p_f,T>=(O ell)_f... wait <p_f,T>=sum_w p_f(w)T(w). Hmm (KT)(v)=sum_f p_f(v)<p_f,T>.
  Cycle-SM says <p_f,T><=N ell(f). So (KT)(v) <= N sum_f p_f(v) ell(f) = N T(v). => CW cert with d=T !!
  So Cycle-SM (<p_f,T><=N ell(f)) <=> (K T <= N T) componentwise => rho(K)<=N. CLEAN.
So Cycle-SM and ROWSUM-O are BOTH Collatz-Wielandt certs for rho(K)<=N (d=T resp via O-side d=1).
Test d candidates on K for ROBUST (strict) slack, and see if any positive d certifies with margin even at extremal.
Also: the eigenvector for rho(K)=N at extremal is T (KT=NT). Confirm."""
import subprocess
import numpy as np
from fractions import Fraction as F
from _h import dec, GENG, loads

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def build(info):
    M=info['M']; n=info['n']
    pfs=[pf_vec(info,f) for f in M]
    P=np.zeros((n,len(M)))
    for j,d in enumerate(pfs):
        for v,val in d.items(): P[v,j]=float(val)
    return P, np.array([info['ell'][f] for f in M],dtype=float)

if __name__=="__main__":
    print("=== K-side: confirm KT=NT at extremal, Cycle-SM<=>KT<=NT, and search robust d ===")
    for nn in [7,9,10]:
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        # just the tight extremal(s)
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            P,ell=build(info)
            K=P@P.T; T=K.sum(axis=1)
            lam=np.linalg.eigvalsh(P.T@P)[-1]
            if abs(lam-nn)<1e-6:
                KT=K@T
                ratio=KT/np.maximum(T,1e-12)
                print(f"  N={nn} {g6}: rho={lam:.4f} | max (KT/T)={ratio.max():.5f} (=N? {nn}) | T range [{T.min():.2f},{T.max():.2f}]")
                break
