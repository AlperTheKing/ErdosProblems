"""PSD/SOS certificate analysis for (SPEC) rho(O)<=N <=> N*I-K PSD (K=P P^T, K_vw=sum_f p_f(v)p_f(w), row sums T(v)).
Task: (1) confirm N*I-K PSD everywhere, report min lambda_min, tight graphs, tight eigenvector.
      (2) structured PSD decomps: diag dominance fail; D=diag(T) pieces; Collatz-Wielandt sum_w K_vw T_w<=N T_v.
      (3) sign/low-rank structure of N*I-K near-tight.
Exact rational where a claimed inequality is asserted (fractions.Fraction)."""
import numpy as np
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads, blow
from _crofton_lp import overlap_matrix

np.set_printoptions(precision=4, suppress=True, linewidth=200)

def Kmat_exact(info):
    """Exact rational K = P P^T over vertices: K[v,w] = sum_f p_f(v) p_f(w). p_f(v)=count/nf (Fraction)."""
    n=info['n']; M=info['M']; cyc=info['cyc']
    # build pf as Fractions
    pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    K=[[F(0) for _ in range(n)] for _ in range(n)]
    for d in pf:
        for v,pv in d.items():
            for w,pw in d.items():
                K[v][w]+=pv*pw
    return K, pf

def Kmat_float(info):
    O,P,pf = overlap_matrix(info)   # P is n x m, P[v,f]=p_f(v)
    K = P @ P.T                      # n x n vertex coincidence
    return K, O, P, pf

def Tvec(info):
    return [float(t) for t in info['T']]

def analyze(info, g6=None, label=None):
    n=info['n']; N=n
    K, O, P, pf = Kmat_float(info)
    T=np.array([float(t) for t in info['T']])
    # row sums of K should equal T
    rowsumK = K.sum(axis=1)
    rs_err = np.max(np.abs(rowsumK - T))
    # N*I - K
    A = N*np.eye(n) - K
    eig = np.linalg.eigvalsh(A)
    lam_min = eig.min()
    # rho(O) and rho(K) (same nonzero spectrum)
    eigO = np.linalg.eigvalsh(O)
    rhoO = eigO.max()
    # Collatz-Wielandt with weight T: max_v (K T)_v / T_v  (should be <= N iff CW cert holds)
    KT = K @ T
    cw = np.array([KT[v]/T[v] if T[v]>1e-12 else 0.0 for v in range(n)])
    cw_max = cw.max()
    # diagonal dominance for N*I-K: A_vv - sum_{w!=v}|A_vw| = (N-K_vv) - sum_{w!=v}|K_vw|
    # = N - K_vv - sum_{w!=v} K_vw  (K>=0 entrywise since p_f>=0) = N - sum_w K_vw = N - T_v
    dd = N - T   # diagonal dominance margin per row = N - T_v
    maxT = T.max()
    return dict(n=n,N=N,lam_min=lam_min,rhoO=rhoO,cw_max=cw_max,maxT=maxT,
                rs_err=rs_err,dd_min=dd.min(),G=float(info['G']),Gamma_over_N2=float(info['G'])/(N*N),
                eig=eig, A=A, K=K, T=T, O=O)

def census(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit: out=out[:limit]
    nt=0
    worst_lam=None; worst_lam_g=None
    worst_cw=None; worst_cw_g=None   # max cw_max (closest to / above N)
    max_maxT=None; max_maxT_g=None
    tight=[]  # graphs with lam_min ~ 0
    max_rs=0.0
    cw_violations=0
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1
        r=analyze(info,g6)
        max_rs=max(max_rs,r['rs_err'])
        if worst_lam is None or r['lam_min']<worst_lam: worst_lam=r['lam_min']; worst_lam_g=g6
        cwslack = nn - r['cw_max']   # >=0 means CW holds (KT)_v<=N T_v
        if worst_cw is None or cwslack<worst_cw: worst_cw=cwslack; worst_cw_g=g6
        if r['cw_max'] > nn + 1e-9: cw_violations+=1
        if max_maxT is None or r['maxT']>max_maxT: max_maxT=r['maxT']; max_maxT_g=g6
        if r['lam_min']<1e-6: tight.append((g6,r['lam_min'],r['Gamma_over_N2']))
    print(f"N={nn}: cfg={nt} | min lam_min(N*I-K)={worst_lam:+.6e}@{worst_lam_g} | min CW-slack(N-max KT/T)={worst_cw:+.6e}@{worst_cw_g} (#CW-viol={cw_violations}) | max maxT={max_maxT:.4f}@{max_maxT_g} (N={nn}) | rowsumK err={max_rs:.2e}")
    return tight

if __name__=="__main__":
    print("=== CENSUS N=8,9,10 ===")
    allt=[]
    for nn in [8,9,10]:
        t=census(nn, limit=(None if nn<=9 else 1500))
        allt+=[(nn,)+x for x in t]
    print("\n=== TIGHT graphs (lam_min ~ 0 found in census) ===")
    for x in allt[:40]:
        print("  ",x)

    print("\n=== KNOWN TIGHT graphs (T==N, Gamma=N^2) ===")
    for g6 in ["H?bB@_W","I?rFf_{N?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E)
        r=analyze(info,g6)
        print(f"  {g6}: N={r['N']} lam_min={r['lam_min']:+.6e} rhoO={r['rhoO']:.5f} cw_max={r['cw_max']:.5f} maxT={r['maxT']:.4f} G/N^2={r['Gamma_over_N2']:.5f}")
        # tight eigenvector of N*I-K
        w,V=np.linalg.eigh(r['A'])
        v0=V[:,0]
        print(f"     tight eigvec (lam={w[0]:+.4e}): {np.round(v0/ (v0[np.argmax(np.abs(v0))]),4)}")
        print(f"     T vec = {np.round(r['T'],4)}  (is tight eigvec ~ constant? T uniform?)")

    print("\n=== BLOW-UPS C5[t] to N=15,20 (t=3,4) ===")
    for t in [2,3,4]:
        nn,E=blow(t); info=loads(nn,E)
        if info is None: print(f"  t={t} N={nn}: loads None"); continue
        r=analyze(info)
        print(f"  C5[{t}] N={nn}: lam_min={r['lam_min']:+.6e} rhoO={r['rhoO']:.5f} cw_max={r['cw_max']:.5f} maxT={r['maxT']:.4f} G/N^2={r['Gamma_over_N2']:.5f}")
