"""Spectral reformulation. P_{vf}=p_f(v) (geodesic-incidence). O=P^T P (Gram, PSD), O_{fg}=<p_f,p_g>.
ell=(ell(f)). Hierarchy of sufficient conditions for Gamma<=N^2 (each => next):
  rho(O)=lambda_max(O) <= N    [cleanest: spectral radius of overlap operator <= N; => (SM) since O PSD]
  ell^T O ell <= N ell^T ell   [= (SM), exact-verified]
  O ell <= N ell  componentwise[= (Cycle-SM), exact-verified]
Test rho(O)<=N census N<=11 (numpy eig). Report rho(O)/N (tightness), and whether ell ~ Perron vector.
If rho(O)<=N holds with margin => cleanest crux. If rho(O)>N somewhere (but (SM) still holds), then ell
matters (Rayleigh of the SPECIFIC ell < rho)."""
import numpy as np
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads

def build_O(info):
    n=info['n']; M=info['M']; cyc=info['cyc']; ell=info['ell']
    m=len(M)
    P=np.zeros((n,m))
    for j,f in enumerate(M):
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        for v,c in cnt.items(): P[v,j]=c/nf
    O=P.T@P
    lvec=np.array([ell[f] for f in M],dtype=float)
    return O,lvec,P

def run(Nmax,Nmin=5):
    print("--- rho(O)=lambda_max(O) <= N ?  (cleanest sufficient cond) ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; rho_bad=0; max_ratio=None; mg=None; perron_align=[]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; O,lvec,P=build_O(info); N=n
            w,V=np.linalg.eigh(O)
            rho=w[-1]
            if rho>N+1e-9: rho_bad+=1
            r=rho/N
            if max_ratio is None or r>max_ratio: max_ratio=r; mg=g6
            # alignment of ell with top eigenvector (cosine^2)
            top=V[:,-1];
            if np.linalg.norm(lvec)>0:
                cos=abs(top@lvec)/(np.linalg.norm(top)*np.linalg.norm(lvec))
                perron_align.append(cos)
        pa=np.mean(perron_align) if perron_align else 0
        print(f"  N={nn}: cfg={nt} | rho(O)>N count:{rho_bad} | max rho(O)/N={max_ratio:.4f} @ {mg} | mean|cos(ell,Perron)|={pa:.3f}",flush=True)

if __name__=="__main__":
    run(11,5)
