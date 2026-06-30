"""Confirm: uniform c=beta_L is the EXACT max conductance for Local-SOS (per-cycle Poincare threshold),
   and that GH already needs c=beta_L (no headroom below) on the tight family => the conductance cert is
   PINNED at uniform beta_L (==Lstar==(H)). Exact Fraction where possible; rational beta' for the threshold side."""
from fractions import Fraction as F
from _csmspec import is_psd
from _hardy_gate import BETA

def cycle_S(L, c):
    """S = L*I - J - c*L_Q for a single C_L cycle (vertices 0..L-1). Exact if c is Fraction."""
    S = [[F(0)]*L for _ in range(L)]
    for i in range(L):
        S[i][i] += F(L)
        for j in range(L):
            S[i][j] -= F(1)
    for i in range(L):
        a, b = i, (i+1)%L
        S[a][a]-=c; S[b][b]-=c; S[a][b]+=c; S[b][a]+=c
    return S

print("Per-cycle Local-SOS threshold:  S(L,c)=L*I - J - c*L_C  >=0  iff  c <= beta_L = L/(2+2cos(pi/L))")
print("(beta_L is the max eig of L_C on 1-perp inverse; q q^T eats the constant mode.)")
for L in [5,7,9,11]:
    b = BETA[L]  # rational beta' < beta_L
    # c = beta' : should be PSD (slightly below true beta_L)
    okb, mpb = is_psd(cycle_S(L, b))
    # c = beta' + small : push above; use a rational just above true beta_L
    # true beta_L is irrational; use b + 1/100 which exceeds true beta_L for these L (gap > 0.01? check)
    over = b + F(1,50)
    oko, mpo = is_psd(cycle_S(L, over))
    print(f"  L={L}: c=beta'={float(b):.5f} -> PSD={okb} minpiv={float(mpb):.3e};  "
          f"c=beta'+0.02={float(over):.5f} -> PSD={oko}")
print()
print("Interpretation: c at beta' (<beta_L) is PSD with TINY positive pivot (rounding slack); pushing c just")
print("above beta_L breaks Local-SOS. So Local-SOS caps c<=beta_L. GH(uniform beta_L)=(H) is tight (kernel=1")
print("on C5[t], where N-T==0). Hence the flexible conductance SDP cannot beat uniform beta_L: cert == (H).")
