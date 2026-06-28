"""Look for a GEODESIC-LOCALIZED sufficient form of (POIN) that is provable per-bad-edge.
K = sum_f p_f p_f^T. For each f, p_f supported on f's geodesic interval (B-distance layers 0..ell(f)-1 from
endpoint). Define the per-edge Laplacian L_f := diag(p_f-rowsum) ... but p_f p_f^T is rank-1, its 'Laplacian'
within the support is B_f := diag(s_f) - p_f p_f^T where s_f(v)=p_f(v)*||p_f||_1 = p_f(v)*ell(f)? No:
rowsum of p_f p_f^T at v = p_f(v)*sum_w p_f(w) = p_f(v)*ell(f). So define B_f := diag(ell(f) p_f) - p_f p_f^T;
then B = sum_f B_f (since diag(T)=diag(sum_f ell(f)p_f) and K=sum_f p_f p_f^T). Each B_f is PSD?
B_f = ell(f) diag(p_f) - p_f p_f^T. For nonneg p_f with sum=ell(f): is ell(f)diag(p_f)-p_f p_f^T PSD?
That's a classic 'diagonal minus rank-1': PSD iff p_f^T diag(p_f)^{-1} p_f <= ell(f) on support, i.e.
sum_{v:p_f(v)>0} p_f(v)^2/p_f(v) = sum p_f(v) = ell(f) <= ell(f). EQUALITY -> B_f is PSD with a null direction!
(Schur: ell diag(p) - p p^T PSD <=> for x supported on supp(p): (sum p_v x_v)^2 <= ell sum p_v x_v^2,
 Cauchy-Schwarz: (sum p_v x_v)^2 = (sum sqrt(p_v) sqrt(p_v) x_v)^2 <= (sum p_v)(sum p_v x_v^2)=ell*sum p_v x_v^2. YES.)
So EACH B_f is PSD by Cauchy-Schwarz, hence B=sum_f B_f PSD. CLEANER PROOF of B PSD (no Laplacian needed)!

So we have TWO proofs that B = diag(T)-K is PSD:
  (i) weighted graph Laplacian (off-diag<=0, zero row sums);
  (ii) B = sum_f [ell(f)diag(p_f) - p_f p_f^T], each term PSD by Cauchy-Schwarz (sum p_f = ell(f)).
VERIFY (ii) EXACTLY: B = sum_f (ell(f)diag(p_f) - p_f p_f^T) and each summand PSD (min eig>=0).

THEN the remaining gap N I - K = sum_f B_f + (N I - diag(T)) still needs the overload control.
Test the alternative grouping: can we instead show  N I - K = sum_f C_f  with each C_f PSD, where
C_f distributes a share of the N*I 'budget' to edge f? Natural share: each f 'owns' budget proportional to
its load. Define C_f := (N ell(f)/Gamma) ... no. Try: since rho(O)<=N is the eigen-statement, and the
tight eigvec is constant, consider the CENTERED form: on x perp 1, is N I - K >> 0 with a gap? Report the
SECOND-smallest eigenvalue (spectral gap above the constant mode) census-wide -- if uniformly bounded below
that's the real spectral fact."""
import numpy as np
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads, blow

def pf_exact(info):
    M=info['M']; cyc=info['cyc']; pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    return pf

def verify_per_edge_PSD(info):
    """EXACT: B = sum_f (ell(f) diag(p_f) - p_f p_f^T); each term PSD via sum_v p_f(v)=ell(f) (Cauchy-Schwarz).
    Returns: max reconstruction error of B, and whether each per-edge term is PSD (checked via the C-S
    identity sum p_f(v)=ell(f) exactly, the rigorous PSD witness)."""
    n=info['n']; M=info['M']; ell=info['ell']; m=len(M)
    pf=pf_exact(info)
    # exact K, T, B
    K=[[F(0)]*n for _ in range(n)]
    for d in pf:
        for v,pv in d.items():
            for w,pw in d.items():
                K[v][w]+=pv*pw
    T=[sum(ell[M[g]]*pf[g].get(v,F(0)) for g in range(m)) for v in range(n)]
    Btrue=[[ (T[v]-K[v][v]) if v==w else -K[v][w] for w in range(n)] for v in range(n)]
    # per-edge sum
    Bsum=[[F(0)]*n for _ in range(n)]
    cs_ok=True
    for j,f in enumerate(M):
        d=pf[j]; L=ell[f]
        # CS witness: sum_v p_f(v) == ell(f) EXACTLY  => ell diag(p)-p p^T PSD (rigorous)
        if sum(d.values())!=L: cs_ok=False
        for v,pv in d.items():
            Bsum[v][v]+=L*pv
            for w,pw in d.items():
                Bsum[v][w]-=pv*pw
    rec_err=max(abs(Bsum[v][w]-Btrue[v][w]) for v in range(n) for w in range(n))
    return rec_err, cs_ok

def gap2(info):
    """second-smallest eigenvalue of N I - K (spectral gap above the constant/tight mode)."""
    n=info['n']; N=n; M=info['M']; cyc=info['cyc']
    P=np.zeros((n,len(M)))
    for j,f in enumerate(M):
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        for v,c in cnt.items(): P[v,j]=c/nf
    K=P@P.T
    w=np.linalg.eigvalsh(N*np.eye(n)-K)
    return w

def census(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit: out=out[:limit]
    nt=0; maxrec=F(0); allcs=True
    minlam1=None; g1=None     # smallest eig
    minlam2=None; g2=None     # second smallest among NONZERO-ish (gap above tight mode)
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1
        re,cs=verify_per_edge_PSD(info)
        if re>maxrec: maxrec=re
        allcs=allcs and cs
        w=gap2(info)
        if minlam1 is None or w[0]<minlam1: minlam1=w[0]; g1=g6
        # second smallest
        s2=w[1]
        if minlam2 is None or s2<minlam2: minlam2=s2; g2=g6
    print(f"N={nn}: cfg={nt} | per-edge B recon err={maxrec} | each-term-PSD(C-S sum p=ell):{allcs} | min lam1={minlam1:+.4e}@{g1} | min lam2(gap above tight)={minlam2:+.4e}@{g2}")

if __name__=="__main__":
    print("=== EXACT: B = sum_f (ell(f)diag(p_f)-p_f p_f^T), each term PSD by Cauchy-Schwarz ===")
    for nn in [7,8,9,10,11]:
        census(nn, limit=(None if nn<=10 else 1200))
    print("\n=== blowups: spectral gap (lam2) above the constant tight mode ===")
    for t in [2,3,4]:
        nn,E=blow(t); info=loads(nn,E)
        re,cs=verify_per_edge_PSD(info); w=gap2(info)
        print(f"  C5[{t}] N={nn}: per-edge recon={re} CS:{cs} | lam1={w[0]:+.4e} lam2={w[1]:+.4e}")
    print("\n=== tight graphs ===")
    for g6 in ["H?bB@_W","I?rFf_{N?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E)
        re,cs=verify_per_edge_PSD(info); w=gap2(info)
        print(f"  {g6} N={n}: recon={re} CS:{cs} lam1={w[0]:+.4e} lam2={w[1]:+.4e}")
