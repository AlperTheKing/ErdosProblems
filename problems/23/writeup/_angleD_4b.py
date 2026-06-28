"""4b disjoint blocks: two vertex-disjoint single-cycle bad-edge supports => H = direct sum, PSD iff
   each N>=ell_i.  Direct algebraic check on a synthetic block-diagonal H built from two cycles."""
from fractions import Fraction as F
from _gcd import a_bar, is_psd_exact, float_mineig

def two_cycle_H(ell1, ell2, N):
    assert N>=ell1+ell2
    H=[[F(0)]*N for _ in range(N)]
    ab1=a_bar(ell1)
    for i in range(ell1):
        j=(i+1)%ell1; H[i][i]+=ab1;H[j][j]+=ab1;H[i][j]-=ab1;H[j][i]-=ab1
    ab2=a_bar(ell2); base=ell1
    for i in range(ell2):
        a=base+i; b=base+(i+1)%ell2; H[a][a]+=ab2;H[b][b]+=ab2;H[a][b]-=ab2;H[b][a]-=ab2
    for v in range(N):
        T = ell1 if v<ell1 else (ell2 if v<ell1+ell2 else 0)
        H[v][v]+=F(N)-T
    return H

if __name__=="__main__":
    print("=== 4b: two vertex-disjoint odd cycles, H=block-diag, PSD iff N>=max(ell1,ell2) per block ===")
    for ell1,ell2,N in [(5,5,10),(5,7,12),(5,7,14),(7,9,16),(5,5,11)]:
        H=two_cycle_H(ell1,ell2,N)
        print(f"  ell1={ell1} ell2={ell2} N={N}: PSD={is_psd_exact(H,N)} mineig={float_mineig(H,N):+.4f} "
              f"predicted min(N-ell1,N-ell2)={min(N-ell1,N-ell2)}",flush=True)
