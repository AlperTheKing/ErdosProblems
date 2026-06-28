"""CRUX analysis: the constant mode of N I - K.
1^T (N I - K) 1 = N^2 - 1^T K 1 = N^2 - sum_{v,w} K_vw = N^2 - sum_v T_v = N^2 - Gamma.
So the quadratic form on the constant vector equals EXACTLY N^2 - Gamma. Hence:
  (N I - K) PSD  =>  N^2 - Gamma >= 0  (taking x=1), i.e. SPEC => Gamma<=N^2 (the reduction we use).
  BUT to PROVE (N I - K) PSD we need ALL x, including x=1, and the x=1 case IS the conjecture.
This shows SPEC and Gamma<=N^2 are TItangled: the constant mode of SPEC = the conjecture.

KEY QUESTION: is the constant vector the MINIMIZER of the Rayleigh quotient x^T(N I-K)x / x^T x?
If YES (constant = bottom eigenvector ALWAYS), then lam_min(N I-K) = (N^2-Gamma)/N, and SPEC <=> Gamma<=N^2
with NO extra content -- the spectral route is EXACTLY as hard as the conjecture (no easier).
If NO (constant not always the bottom eigvec; sometimes a non-constant x gives smaller Rayleigh), then SPEC
is STRICTLY STRONGER than Gamma<=N^2 on those graphs, and proving SPEC needs more than the conjecture --
which would make the spectral route a RED HERRING (harder than needed).

TEST: compare (a) Rayleigh of constant = (N^2-Gamma)/N  vs  (b) true lam_min(N I-K).
If (b) < (a) strictly on some graph => constant is NOT the minimizer => the binding constraint is a
NON-constant mode => SPEC is strictly stronger than the conjecture there (potential obstruction / red herring).
If (b) == (a) always (constant always the minimizer) => SPEC <=> conjecture, equal difficulty.
Report census-wide: max over graphs of [ (N^2-Gamma)/N - lam_min ]  (>0 means non-const mode is lower)."""
import numpy as np
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads, blow

def Kfloat(info):
    n=info['n']; M=info['M']; cyc=info['cyc']
    P=np.zeros((n,len(M)))
    for j,f in enumerate(M):
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        for v,c in cnt.items(): P[v,j]=c/nf
    return P@P.T

def analyze(info):
    n=info['n']; N=n
    K=Kfloat(info)
    Gamma=float(info['G'])
    rayl_const=(N*N-Gamma)/n   # x=1: (N^2-Gamma)/||1||^2 = (N^2-Gamma)/n
    lam_min=np.linalg.eigvalsh(N*np.eye(n)-K).min()
    return rayl_const, lam_min, Gamma, N

def census(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit: out=out[:limit]
    nt=0; worst=None; wg=None  # max (rayl_const - lam_min): >0 => const NOT minimizer
    cnt_nonconst=0
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1
        rc,lm,G,N=analyze(info)
        gap=rc-lm
        if worst is None or gap>worst: worst=gap; wg=g6
        if gap>1e-7: cnt_nonconst+=1
    print(f"N={nn}: cfg={nt} | max[(N^2-Gamma)/n - lam_min(N I-K)]={worst:+.5e}@{wg} | #graphs where NON-const mode is the binding one={cnt_nonconst}")

if __name__=="__main__":
    print("=== Is the constant vector the bottom eigenvector of N I - K? (i.e. is SPEC == conjecture?) ===")
    print("    max[(N^2-Gamma)/n - lam_min] > 0  =>  a NON-constant mode is lower  =>  SPEC strictly stronger\n")
    for nn in [7,8,9,10]:
        census(nn, limit=(None if nn<=9 else 2000))
    print("\n=== blowups ===")
    for t in [2,3,4]:
        nn,E=blow(t); info=loads(nn,E)
        rc,lm,G,N=analyze(info)
        print(f"  C5[{t}] N={nn}: (N^2-G)/n={rc:+.4e}  lam_min={lm:+.4e}  diff={rc-lm:+.4e}  Gamma={G}")
