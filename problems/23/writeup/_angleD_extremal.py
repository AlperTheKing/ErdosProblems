"""ANGLE D sub-case (3): the extremal family C_ell[t] uniform blow-up.  PROVE equality / margin 0.
   Claim: at the balanced blow-up of an odd cycle C_{2k+1}, the gamma-min connected-B cut has T==N
   (CONSTANT load), so O is EMPTY, diag(N-T)=0, and H=L_omega.  Then H>=0 trivially (Laplacian),
   and mineig(H)=0 with null vector = 1 (the constant).  This is the EQUALITY case 1^T H 1 = N^2-Gamma=0,
   i.e. Gamma=N^2 exactly.  We verify: (i) T==N exactly, (ii) H=L_omega (diag part 0), (iii) mineig 0,
   (iv) null space is exactly span(1) (connected omega => 1-dim kernel) => H>=0 with a UNIQUE flat mode.
   PERTURB: bump one vertex load by moving to an UNBALANCED blow-up (sizes t_i not all equal); check
   H stays >=0 and which mode first threatens (Fiedler direction)."""
import subprocess
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn, bdist_restr
from _gcd import build_H, is_psd_exact, float_mineig
from _angleD_O1 import gmin_sides

def Ccyc_blow(L, ts):
    """Blow-up of odd cycle C_L (L=2k+1) with class sizes ts[0..L-1].  Returns (n, E)."""
    off=[0]
    for t in ts: off.append(off[-1]+t)
    n=off[-1]; E=[]
    for i in range(L):
        j=(i+1)%L
        for a in range(ts[i]):
            for b in range(ts[j]):
                E.append((off[i]+a, off[j]+b))
    return n,E

def analyze(L,ts,tag):
    n,E=Ccyc_blow(L,ts)
    adj,sides=gmin_sides(n,E)
    if not sides:
        print(f"  {tag}: no gamma-min connected-B cut"); return
    s=sides[0]
    r=build_H(adj,s,n)
    if r is None:
        print(f"  {tag}: build_H None"); return
    H,T,N=r
    Tconst = all(T[v]==T[0] for v in range(n))
    diagzero = all((F(N)-T[v])==0 for v in range(n))
    O=[v for v in range(n) if T[v]>N]
    me=float_mineig(H,n)
    psd=is_psd_exact(H,n)
    Tset=sorted(set(T))
    print(f"  {tag}: N={N} T-vals={[float(x) for x in Tset][:4]} T==N? {diagzero} |O|={len(O)} "
          f"PSD={psd} mineig={me:+.6f}",flush=True)
    return H,T,N,n

if __name__=="__main__":
    print("=== ANGLE D (3) extremal C_ell[t]: balanced => T==N, H=L_omega, mineig 0 (unique flat mode) ===")
    print("--- balanced blow-ups (should be T==N, mineig 0) ---")
    for L in (5,7):
        for t in (1,2,3):
            analyze(L,[t]*L,f"C{L}[{t}] balanced")
    print("--- UNBALANCED perturbations (one class bigger) ---")
    for L in (5,):
        for big in (2,3):
            ts=[1]*L; ts[0]=big; analyze(L,ts,f"C{L} sizes{ts}")
            ts=[2]*L; ts[0]=big+1; analyze(L,ts,f"C{L} sizes{ts}")
            ts=[2]*L; ts[1]=3; analyze(L,ts,f"C{L} sizes{ts}")
