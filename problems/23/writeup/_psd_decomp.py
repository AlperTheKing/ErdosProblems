"""Structured PSD decomposition of N*I - K. Task item 2.
Write N*I - K = (N*I - diag(T)) + (diag(T) - K).
  Piece B := diag(T) - K.  K=P P^T with P[v,f]=p_f(v), so K_vv=sum_f p_f(v)^2, K row sums = T.
  diag(T)-K is a 'generalized Laplacian': (diag(T)-K)_vv = T_v - sum_f p_f(v)^2,
  off-diag = -K_vw = -sum_f p_f(v)p_f(w) <=0.  Row sums of B = T_v - T_v = 0 -> B 1 = 0 (B has const nullvec).
  Is B PSD? B = diag(T) - P P^T. Test lambda_min(B) over census.
  Piece A := N*I - diag(T) is diagonal with entries N - T_v; PSD iff all T_v<=N -> FAILS (overloaded vertices).
So the naive split fails on A. BUT: maybe B is PSD and 'absorbs' the overload. Test: is B PSD? and is
   N*I - K = B + (N*I - diag(T))   with the bad diagonal compensated by B's structure.
ALTERNATIVE split using the geodesic Laplacian. For each bad edge f, p_f is supported on f's geodesic
'interval'; define rank-1 term R_f = ell(f) * (e_f-stuff)... Explore:
   Claim: K = sum_f p_f p_f^T  (rank-m PSD, =P P^T). N*I - K = N*I - sum_f p_f p_f^T.
   Per bad edge contribution to K has top eigenvalue ||p_f||^2 = O_ff <= ell(f) (since p_f(v)<=1, sum p_f=ell(f)).
   So a UNION bound rho(K) <= sum_f ||p_f||^2 = trace(O) is too weak. Need overlap cancellation.
Report: lam_min(B), lam_min(A) (=N-maxT), and whether B PSD => then N*I-K = B + A but A indefinite.
Also test the 'right' diagonal: find diagonal D>=0 with N*I-K = (D - K) + (N*I - D), (D-K) PSD and (N*I-D) PSD,
i.e. need D>=K-as-quadratic and D<=N*I. D=diag(d), d_v<=N, and diag(d)-K PSD. Does such d exist? That is a
diagonal-scaling feasibility (a tiny SDP); test if d=T works (it gives B PSD?) but T_v>N sometimes so the
SECOND condition d<=N fails. Resolve the tension: is there d with K <= diag(d) <= N*I (Loewner)? """
import numpy as np
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads, blow
from _crofton_lp import overlap_matrix

np.set_printoptions(precision=3, suppress=True, linewidth=200)

def pieces(info):
    n=info['n']; N=n
    O,P,pf=overlap_matrix(info)
    K=P@P.T
    T=np.array([float(t) for t in info['T']])
    B=np.diag(T)-K                 # generalized Laplacian, row sums 0
    A=N*np.eye(n)-np.diag(T)       # diagonal N-T_v
    lamB=np.linalg.eigvalsh(B)
    lamA=N-T
    NIK=N*np.eye(n)-K
    lamNIK=np.linalg.eigvalsh(NIK)
    return dict(n=n,N=N,T=T,K=K,B=B,lamB=lamB,lamA=lamA,lamNIK=lamNIK,maxT=T.max())

def feasible_diag(info):
    """Does there exist diagonal d with K <= diag(d) <= N I (Loewner)?  Need diag(d)-K PSD and d_v<=N.
    Necessary: d_v>=K_vv (diag of K) is NOT sufficient. Solve small SDP-free check via:
    diag(d)-K PSD with d<=N. Since K PSD with rho(K)<=N, choose d... we test d=T (gives B, but T may exceed N),
    and we test the SDP feasibility numerically by a simple eigen-pushed iteration. Cheap proxy:
    is rho(K) <= N AND is there d in [K_vv, N] making diag(d)-K PSD? The minimal such (Loewner) needs
    diag(d) >= K in PSD order; the smallest feasible diagonal is not closed-form. We just check the
    BINARY fact: min over census of (N - rho(K)) and whether d=N*1 trivially works (diag(N)-K = N I - K PSD,
    yes always!). So d=N*1 ALWAYS satisfies BOTH K<=diag(N)<=N I trivially => decomposition is vacuous.
    The CONTENT must be a NON-diagonal certificate. Conclusion check only."""
    n=info['n']; N=n
    O,P,pf=overlap_matrix(info)
    K=P@P.T
    rhoK=np.linalg.eigvalsh(K).max()
    return N-rhoK

def census(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit: out=out[:limit]
    nt=0; minlamB=None; mlBg=None; minNmrhoK=None; g2=None; cntBneg=0
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1
        pc=pieces(info)
        lb=pc['lamB'].min()
        if minlamB is None or lb<minlamB: minlamB=lb; mlBg=g6
        if lb<-1e-7: cntBneg+=1
        nm=feasible_diag(info)
        if minNmrhoK is None or nm<minNmrhoK: minNmrhoK=nm; g2=g6
    print(f"N={nn}: cfg={nt} | min lam_min(B=diag(T)-K)={minlamB:+.6e}@{mlBg} (#B-indef={cntBneg}) | min (N-rho(K))={minNmrhoK:+.6e}@{g2}")

if __name__=="__main__":
    print("=== Is B = diag(T)-K PSD? (generalized geodesic Laplacian, B1=0) ===")
    for nn in [7,8,9,10]:
        census(nn, limit=(None if nn<=9 else 1500))
    print("\n=== blowups ===")
    for t in [2,3,4]:
        nn,E=blow(t); info=loads(nn,E)
        pc=pieces(info)
        print(f"  C5[{t}] N={nn}: lam_min(B)={pc['lamB'].min():+.4e} maxT={pc['maxT']:.3f} (overload {pc['maxT']>nn}) lam_min(N I-K)={pc['lamNIK'].min():+.4e}")
    print("\n=== tight graphs: full eigen-structure of B and N I-K ===")
    for g6 in ["H?bB@_W","I?rFf_{N?"]:
        n,E=dec(g6); info=loads(n,E)
        pc=pieces(info)
        print(f"  {g6} N={n}: lam(B)={np.round(pc['lamB'],3)}  lam(N I-K)={np.round(pc['lamNIK'],3)}  T={np.round(pc['T'],2)}")
