"""Independent cross-check: for overloaded cases, verify (Schur conditions PASS) ==> (A = N*I-K truly PSD)
by an INDEPENDENT exact PSD test (LDL^T / leading-principal-minor signs via exact Fraction Cholesky-like).
A symmetric matrix is PSD iff its symmetric Gaussian elimination (LDL^T) has all pivots >= 0 with no
breakdown requiring negative compensation. We use exact rational LDL with pivoting-free check:
  - If a zero pivot appears with nonzero remaining row -> handle via rank check.
We instead use the robust exact test: A PSD  <=>  for the ordered principal minors via LDL all d_i>=0 AND
the matrix equals L D L^T (congruence). To be safe against zero pivots we test PSD by:
  A PSD  iff  x^T A x >= 0 for all x  -- we certify NON-PSD by exhibiting a rational x with x^T A x < 0
  (search via eigenvector of float A then rationalize), and certify PSD via exact LDL^T with all pivots>=0.
Goal: find ANY graph where Schur says PASS but A is NOT PSD (would be a fatal bug)."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _audit_stress import full_test, build_K, blow

def ldl_psd(A):
    """Exact LDL^T for symmetric A. Returns (is_psd, pivots) treating zero pivots carefully.
    Standard: symmetric A is PSD iff it has an LDL^T decomposition (with symmetric pivoting if needed)
    with D>=0. We do NO pivoting; if a zero pivot is hit we fall back to leading-minor/perturbation.
    For our purpose we compute the no-pivot LDL; if a zero diagonal with nonzero below appears we report
    'indef-structure' and rely on minor test."""
    import copy
    n=len(A); M=[[A[i][j] for j in range(n)] for i in range(n)]; D=[]
    L=[[F(1) if i==j else F(0) for j in range(n)] for i in range(n)]
    for k in range(n):
        d=M[k][k]; D.append(d)
        if d==0:
            # if any below nonzero -> cannot continue plain; check if whole remaining col is zero
            if any(M[i][k]!=0 for i in range(k+1,n)):
                return (None,D)  # needs pivoting; ambiguous
            else:
                continue
        for i in range(k+1,n):
            L[i][k]=M[i][k]/d
        for i in range(k+1,n):
            for j in range(k+1,n):
                M[i][j]=M[i][j]-L[i][k]*d*L[j][k]
    is_psd=all(x>=0 for x in D)
    return (is_psd,D)

def leading_minors_psd(A):
    """A PSD check robust to zero pivots: use the fact that for symmetric A, A PSD iff
    all principal minors (not just leading) >=0. Too expensive. Instead: test A + eps I PD for symbolic eps>0
    by checking all leading principal minors of A are >=0 AND rank-consistent. We use a practical exact route:
    compute LDL with full diagonal pivoting (symmetric). Returns is_psd bool or None."""
    n=len(A);
    import itertools
    P=list(range(n)); M=[[A[i][j] for j in range(n)] for i in range(n)]; D=[]
    for k in range(n):
        # pick pivot = largest remaining diagonal (to avoid zero); for PSD a zero diag forces its row/col zero
        piv=max(range(k,n), key=lambda i: M[i][i])
        if M[piv][piv]<0: return False
        # swap k<->piv symmetric
        if piv!=k:
            M[k],M[piv]=M[piv],M[k]
            for r in range(n): M[r][k],M[r][piv]=M[r][piv],M[r][k]
        d=M[k][k]; D.append(d)
        if d==0:
            if any(M[i][k]!=0 for i in range(n) if i!=k):
                # zero diagonal but nonzero off => not PSD
                return False
            continue
        for i in range(k+1,n):
            f=M[i][k]/d
            for j in range(k+1,n):
                M[i][j]=M[i][j]-f*M[k][j]
            M[i][k]=F(0); M[k][i]=F(0)
    return all(x>=0 for x in D)

def run(base_list,t,cap,tag):
    mism=0; tested=0; schur_pass_notpsd=[];
    worstgap=None
    for g6 in base_list:
        nbase,_=dec(g6); N=nbase*t
        if N>cap: continue
        nn,EE=blow(g6,t); info=loads(nn,EE)
        if info is None: continue
        res=full_test(info)
        if res['status']=='noO': continue
        K,T,Nn,n=build_K(info)
        A=[[(F(Nn) if i==j else F(0))-K[i][j] for j in range(n)] for i in range(n)]
        psd=leading_minors_psd(A)
        tested+=1
        if res['status']=='ok' and not psd:
            schur_pass_notpsd.append((g6,t,nn)); print(f"  !!! FATAL {g6}[{t}] N={nn}: Schur PASS but A NOT PSD",flush=True)
        if res['status']=='ok' and psd:
            pass
    print(f"  {tag}: tested {tested} | Schur-pass-but-A-not-PSD: {len(schur_pass_notpsd)}",flush=True)
    return schur_pass_notpsd

if __name__=="__main__":
    def overloaded(nn,stride=1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        ov=[]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            if any(t>n for t in info['T']): ov.append(g6)
        return ov
    print("=== cross-check: Schur PASS ==> A PSD (independent exact LDL) ===",flush=True)
    ov8=overloaded(8); run(ov8,2,16,"N=8 t=2")
    ov9=overloaded(9); run(ov9,2,18,"N=9 t=2")
    ov10=overloaded(10); run(ov10,2,20,"N=10 t=2")
