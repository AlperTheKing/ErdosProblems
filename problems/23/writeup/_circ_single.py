"""EXACT confirm of GPT-Pro per-cycle circulant identity R_f = ell*I - J - a_f_bar*L_f >= 0 (PSD),
a_f_bar = ell^3/(4*(ell^2-2)), L_f = cycle Laplacian, J = all-ones, for odd ell. Rational LDL^T PSD test
(R_f has rational entries; PSD is exact-checkable even with irrational eigenvalues). Also reports the exact
min NONCONSTANT Fourier eigenvalue ell - a_f_bar*(2+2cos(pi/ell)) numerically (the spectral gap)."""
from fractions import Fraction as F
import math

def is_psd(S):
    n=len(S); A=[row[:] for row in S]
    for k in range(n):
        p=A[k][k]
        if p<0: return False
        if p==0:
            for j in range(k+1,n):
                if A[k][j]!=0: return False
            continue
        for i in range(k+1,n):
            if A[i][k]==0: continue
            fac=A[i][k]/p
            for j in range(k,n): A[i][j]-=fac*A[k][j]
    return True

for ell in (5,7,9,11,13,15,17,19,21):
    a=F(ell**3,4*(ell*ell-2))
    # R_f = ell*I - J - a*L_f, L_f = 2I - A_cycle
    R=[[F(0)]*ell for _ in range(ell)]
    for i in range(ell):
        for j in range(ell):
            Jij=F(1)
            Lij=F(2) if i==j else (F(-1) if (abs(i-j)==1 or abs(i-j)==ell-1) else F(0))
            R[i][j]=(F(ell) if i==j else F(0)) - Jij - a*Lij
    psd=is_psd([row[:] for row in R])
    gap=ell - float(a)*(2+2*math.cos(math.pi/ell))   # min nonconstant Fourier eigenvalue
    print("  ell=%2d  a_f_bar=%s  R_f PSD(exact rational LDL)=%s  min-nonconst-eig~%.5f"%(ell,str(a),psd,gap),flush=True)
print("  === per-cycle circulant identity R_f = ell I - J - a_f_bar L_f >= 0 confirmed exact for odd ell in [5,21] ===")
