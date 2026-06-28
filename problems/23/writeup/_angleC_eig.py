"""ANGLE C: structure of A_f = a_bar(L) L_{tau_f} - L diag(p_f) on a SINGLE odd ell-cycle (unique geodesic).
For C_L (single shortest geodesic, tau_f = indicator of the L cycle edges, p_f = uniform 1/1 on L vertices
since k=1 path => p_f(v)=1 for each cycle vertex), compute exact eigenvalues.

On a clean odd cycle C_L: L_{tau_f}=L_{C_L} circulant, p_f = 1 on all L vertices (each vertex on the
single geodesic-or-the-bad-edge-endpoints). Then
   A_f = a_bar(L) L_{C_L} - L I_L.
Eigenvalues: a_bar(L)*2(1-cos(2 pi j/L)) - L,  j=0..L-1.
  j=0: -L  (constant mode).
  j!=0: 2 a_bar(L)(1-cos) - L.  Max at cos=-1-ish.
So A_f has ONE eigenvalue -L on constant mode, and the rest = a_bar gap - L.
The negative directions are: constant mode (-L) PLUS any j with 2 a_bar(1-cos 2pi j/L) < L.

This explains why B_f=A_f+p_f p_f^T fails: p_f=1=constant only kills the j=0 mode partially,
but several low-j modes are also negative. We compute how many negative eigenvalues A_f has and
their span, to see the TRUE rank of the negative part = what must be charged to N*I globally.
"""
import sys,io,math
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
from fractions import Fraction as F
def a_bar(L): return F(L**3,4*(L*L-2))
def a_star(L): return L/(2+2*math.cos(math.pi/L))  # sharp

print("=== A_f eigenvalues on a clean odd cycle C_L:  2 a_bar(L)(1-cos 2pi j/L) - L ===")
for L in (5,7,9,11):
    ab=a_bar(L); abf=float(ab); ast=a_star(L)
    eigs=[]
    for j in range(L):
        e=2*abf*(1-math.cos(2*math.pi*j/L))-L
        eigs.append(e)
    eigs_sorted=sorted(eigs)
    nneg=sum(1 for e in eigs if e<-1e-12)
    print(f"  L={L}: a_bar={abf:.4f} a_star={ast:.4f}  #neg-eig(A_f)={nneg}  "
          f"min={min(eigs):+.4f} eigs(sorted)={[round(e,3) for e in eigs_sorted]}")
    # the sharp a_star version: does A_f^* = a_star L_C - L I have only constant-mode negative?
    eigs_star=[2*ast*(1-math.cos(2*math.pi*j/L))-L for j in range(L)]
    nneg_star=sum(1 for e in eigs_star if e<-1e-9)
    print(f"        SHARP a_star: #neg-eig={nneg_star} min={min(eigs_star):+.4f} "
          f"(j!=0 min={min(eigs_star[1:]):+.4f}) eigs={[round(e,3) for e in sorted(eigs_star)]}")
print()
print("KEY: with a_star, the j!=0 eigenvalues 2 a_star(1-cos 2pi j/L)-L.  At j=(L±1)/2, "
      "2 a_star(1-cos(pi(L±1)/L)); is min over j!=0 >=0?  That is the LOCAL-half (LC) circulant fact"
      " in the form A_f^* + p_f p_f^T? No -- LC is J+a L <= ell I i.e. a L >= ell I - J = ell(I - (1/?)..).")
