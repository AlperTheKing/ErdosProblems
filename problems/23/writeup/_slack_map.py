"""Map the slack: for many graphs compare rho(K), N, maxT, and the layer-CS structure.
Goal: find which quantity the proof needs, and whether a *modified diagonal* (super-Perron)
with explicit formula closes the maxT->N gap. Key new candidate phi:
  phi(v) = sum_f p_f(v)*c_f  for per-edge constants c_f to be chosen so K phi <= N phi.
Equivalently look for c in R^M_{>0} with (for all v) sum_f p_f(v) <p_f, P c> <= N sum_f p_f(v) c_f
i.e. P (O c) <= N P c entrywise... = P(O - N I)c <= 0. Since rows of P are >=0, sufficient: (O-NI)c<=0
i.e. O c <= N c entrywise: a super-Perron vector for O (in edge space)!
So: rho(K)=rho(O)<=N  <=>  exists c>0 in edge-space with O c <= N c (Collatz-Wielandt on O).
ROWSUM-O is exactly the case c=1 (O 1 = rowsums <= N). Test whether c=1 is feasible (=ROWSUM-O)
and what O 1 looks like vs the optimal c."""
from fractions import Fraction as F
from _h import dec, loads
from _schur_spec import pf_exact
import subprocess, numpy as np
GENG='E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe'

def buildO(info):
    P,M,ell,n=pf_exact(info)
    m=len(M)
    O=[[sum(P[i].get(v,F(0))*P[j].get(v,F(0)) for v in range(n)) for j in range(m)] for i in range(m)]
    return O,M,ell,n

if __name__=="__main__":
    # over census, compute max O-rowsum (=ROWSUM-O LHS max) / N, and rho(O)/N
    for nn in [8,9,10,11]:
        out=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        stride=1 if nn<=9 else (4 if nn==10 else 30)
        worst_rs=None; worst_rho=None; cnt=0
        for g6 in out[::stride]:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            cnt+=1
            O,M,ell,n=buildO(info)
            m=len(M)
            if m==0: continue
            rs=[sum(O[i]) for i in range(m)]
            mrs=max(rs)
            if worst_rs is None or F(mrs,n)>worst_rs[0]:
                worst_rs=(F(mrs,n),g6,str(mrs),n,sorted(set(ell.values())))
            Of=np.array([[float(x) for x in row] for row in O])
            rho=max(np.linalg.eigvalsh(Of)) if m>0 else 0
            if worst_rho is None or rho/n>worst_rho[0]:
                worst_rho=(rho/n,g6,rho,n)
        print('N=%d (%d graphs): worst O-rowsum/N=%.4f (g6=%s rs=%s ell=%s) | worst rho(O)/N=%.4f'%(
            nn,cnt,float(worst_rs[0]),worst_rs[1],worst_rs[2],worst_rs[4],worst_rho[0]))
