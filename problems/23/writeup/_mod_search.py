"""Search for a PSD-dominating model operator Mod (Mod - K >= 0) with rho(Mod)=N, tight at C5[t].
Candidates built from B-graph structure:
  Mod1 = diag(T)               (Mod1-K = B-Laplacian-type, PSD, but rho(Mod1)=maxT can be >N)  -- not rho=N
  Mod2 = (N/maxdeg?) ...
Better: test whether K <= sum_f ell(f) * Pi_f where Pi_f = (1/ell) 1_supp 1_supp^T  (rank1 avg on support)
Actually p_f p_f^T <= ?  Let's directly test PSD-domination of K by candidate operators and report
min eigenvalue of (Mod - K) exactly-ish (float) on census + Myc.
Most principled: Mod = sum_f ell(f) * u_f u_f^T  where u_f = p_f/||p_f||_? ... we want sum to have rho<=N.
Test: does K <= sum_f p_f p_f^T trivially (equality). We need an UPPER model.
Key test: is N*I - K = L_B (the weighted B-Laplacian with edge weights = mu/2)? i.e. does the traffic
handshake give N*I-K as a Laplacian?  Test (N*I-K) vs Laplacian of B with weights w(e)=mu(e)."""
from fractions import Fraction as F
from _h import dec, loads, blow
from _schur_spec import pf_exact
from _zmu import mu_edges  # cut-edge traffic
import numpy as np, subprocess
GENG='E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe'

def buildK(info):
    P,M,ell,n=pf_exact(info)
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        items=list(d.items())
        for a in range(len(items)):
            va,pa=items[a]
            for b in range(len(items)):
                vb,pb=items[b]
                K[va][vb]+=pa*pb
    T=[sum(ell[M[fi]]*P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    return K,T,P,M,ell,n

if __name__=="__main__":
    # Test: is N*I - K PSD AND does diag(T)-K (=:B0) relate to a B-graph Laplacian?
    # B0 = diag(T)-K. K1=T so B0 1 = 0: B0 is a zero-row-sum symmetric PSD (Laplacian-type) matrix.
    # Then N*I-K = (N*I - diag(T)) + B0. The first term is diag(N-T), NEGATIVE at overloaded v.
    # So N*I-K = B0 - diag(T-N). Need B0 >= diag(T-N) on the overloaded coordinates. Test eigen.
    for src in ['C5[2]','C5[3]','census9-overload']:
        if src.startswith('C5'):
            t=int(src[3]); nn,EE=blow(t); info=loads(nn,EE)
        else:
            out=subprocess.run([GENG,'-tc','9'],capture_output=True,text=True).stdout.split()
            info=None
            for g6 in out:
                n,E=dec(g6); ii=loads(n,E)
                if ii is None: continue
                Pp,Mm,ll,nn2=pf_exact(ii)
                Tt=[sum(ll[Mm[fi]]*Pp[fi].get(v,F(0)) for fi in range(len(Mm))) for v in range(nn2)]
                if max(Tt)>nn2: info=ii; break
        K,T,P,M,ell,n=buildK(info); N=n
        Kf=np.array([[float(x) for x in row] for row in K])
        B0=np.diag([float(t) for t in T])-Kf
        wB0=sorted(np.linalg.eigvalsh(B0))
        A=N*np.eye(n)-Kf
        wA=sorted(np.linalg.eigvalsh(A))
        print('%s N=%d: min eig(diag(T)-K)=%.4f (Laplacian, should >=0), min eig(N*I-K)=%.4f, rho(K)=%.4f maxT=%.3f'%(
            src,n,wB0[0],wA[0],max(np.linalg.eigvalsh(Kf)),max(float(t) for t in T)))
