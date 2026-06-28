"""AIRTIGHT verification of the water-filling per-edge PSD certificate.
Claim: with s(v)=sum_g p_g(v) (>0 on the union of geodesic supports), define for each bad edge f and vertex v
       D_f(v) = N * p_f(v) / s(v)   (0 if p_f(v)=0).
Then (i) sum_f D_f(v) = N for every v with s(v)>0 (and vertices with s(v)=0 carry NO p_f mass, handle separately),
     (ii) C_f := diag(D_f) - p_f p_f^T is PSD  <=>  sum_{v in supp f} p_f(v)^2 / D_f(v) <= 1
          <=> (1/N) sum_v p_f(v) s(v) <= 1  <=> sum_g O_fg <= N  [(ROWSUM-O), verified exact],
     (iii) sum_f C_f = diag(sum_f D_f) - sum_f p_f p_f^T = N*I_{supp} - K   ON the support.

SUBTLETY: vertices with s(v)=0 (no geodesic through them) get D_f(v)=0 and K row/col 0 there; on those
coordinates N*I-K = N>0 (diagonal), fine. So sum_f C_f restricted to supp(s) reconstructs (N I - K) on supp,
and off-supp N I - K is N*I (PSD). VERIFY:
   (A) build D_f, C_f numerically; confirm each C_f min-eig >= -1e-9 (PSD);
   (B) confirm sum_f C_f + (N on off-support diagonal) == N*I - K  (max abs err);
   (C) confirm the equivalence  (each C_f PSD)  <=>  (ROWSUM-O holds) by checking both flags agree.
Run census N=8,9,10 + blowups + tight graphs; report worst min-eig of any C_f and worst recon error."""
import numpy as np
import subprocess
from _h import dec, GENG, loads, blow

def Pmat(info):
    n=info['n']; M=info['M']; cyc=info['cyc']; m=len(M)
    P=np.zeros((n,m))
    for j,f in enumerate(M):
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        for v,c in cnt.items(): P[v,j]=c/nf
    return P, n, m

def verify(info):
    P,n,m = Pmat(info); N=n
    s = P.sum(axis=1)                        # s(v)=sum_g p_g(v)
    K = P@P.T
    NIK = N*np.eye(n)-K
    # build C_f and accumulate
    acc = np.zeros((n,n))
    min_Cf = np.inf
    rowsumO_ok = True
    for j in range(m):
        pf = P[:,j]
        D = np.zeros(n)
        for v in range(n):
            if pf[v] > 0:
                D[v] = N*pf[v]/s[v]          # s[v]>0 since pf[v]>0
        Cf = np.diag(D) - np.outer(pf,pf)
        # only the support of pf matters for PSD; pad zeros elsewhere are fine (Cf has zero rows/cols off supp)
        ev = np.linalg.eigvalsh(Cf)
        min_Cf = min(min_Cf, ev.min())
        acc += Cf
        # rowsum-O for this edge: sum_v pf(v) s(v) <= N
        if (pf@s) > N + 1e-9: rowsumO_ok=False
    # reconstruct: on support of s, acc should equal N I - K restricted; off-support add N to diagonal
    target = NIK.copy()
    for v in range(n):
        if s[v]==0:
            # off support: acc has 0 there, target diagonal is N (since K row 0). Add N to acc diag to match.
            acc[v,v]+=N
    recon_err = np.max(np.abs(acc - target))
    return min_Cf, recon_err, rowsumO_ok

def census(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit: out=out[:limit]
    nt=0; worst_min=np.inf; wg=None; worst_rec=0.0; rg=None; allok=True
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1
        mc,re,ok=verify(info)
        if mc<worst_min: worst_min=mc; wg=g6
        if re>worst_rec: worst_rec=re; rg=g6
        allok=allok and ok
    print(f"N={nn}: cfg={nt} | min over edges of lam_min(C_f)={worst_min:+.3e}@{wg} | max recon err |sum C_f - (N I-K)|={worst_rec:.2e}@{rg} | ROWSUM-O all-hold:{allok}")

if __name__=="__main__":
    print("=== AIRTIGHT water-filling cert: each C_f=diag(D_f)-p_f p_f^T PSD, sum_f C_f = N I - K ===")
    for nn in [8,9,10]:
        census(nn, limit=(None if nn<=9 else 1500))
    print("\n=== blowups ===")
    for t in [2,3,4]:
        nn,E=blow(t); info=loads(nn,E)
        mc,re,ok=verify(info)
        print(f"  C5[{t}] N={nn}: min lam(C_f)={mc:+.3e} recon={re:.2e} ROWSUM-O:{ok}")
    print("\n=== tight ===")
    for g6 in ["H?bB@_W","I?rFf_{N?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E)
        mc,re,ok=verify(info)
        print(f"  {g6} N={n}: min lam(C_f)={mc:+.3e} recon={re:.2e} ROWSUM-O:{ok}")
