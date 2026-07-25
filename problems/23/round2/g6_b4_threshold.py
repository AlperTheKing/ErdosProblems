"""G6 adversary audit of the THRESHOLD ARITHMETIC behind (B4)/(B6).

(B4) as stated:  bip(G) <= bip(G-v) + floor(d(v)/2), hence "if some vertex has
d(v) <= (4N-2)/25 the conjecture at N follows from it at N-1", hence a minimal
counterexample has delta(G) > (4N-2)/25.

The one-vertex reduction actually succeeds iff
        floor(d(v)/2) <= B(N)
where B(N) is the budget.  Three candidate budgets, in increasing strength:

  B_real(N)  = N^2/25 - (N-1)^2/25 = (2N-1)/25          (real-valued budget)
  B_int(N)   = floor(N^2/25) - floor((N-1)^2/25)        (integrality of bip used)

Because floor(d/2) is an integer, "floor(d/2) <= B" is equivalent to
d <= 2*floor(B) + 1.  So the *exact* degree thresholds are

  T_claim(N) = floor((4N-2)/25)                          <- what (B4) claims
  T_real(N)  = 2*floor((2N-1)/25) + 1                    <- exact, real budget
  T_int(N)   = 2*(floor(N^2/25) - floor((N-1)^2/25)) + 1 <- exact, integer budget

All arithmetic here is exact integer arithmetic (Fraction only for display).
"""
from fractions import Fraction

def T_claim(N):
    # "d(v) <= (4N-2)/25"  with d integer
    return (4 * N - 2) // 25

def T_real(N):
    return 2 * ((2 * N - 1) // 25) + 1

def T_int(N):
    return 2 * (N * N // 25 - (N - 1) * (N - 1) // 25) + 1

def check_soundness(N, d):
    """Exact check that d(v)=d really lets the induction go through at N:
       need  floor((N-1)^2/25) + floor(d/2) <= floor(N^2/25)."""
    return (N - 1) ** 2 // 25 + d // 2 <= N * N // 25

def main():
    print("N    T_claim  T_real  T_int   gain_real  gain_int   (2N-1)mod25")
    rows = []
    for N in range(2, 401):
        tc, tr, ti = T_claim(N), T_real(N), T_int(N)
        rows.append((N, tc, tr, ti))
        if N <= 60 or N % 25 == 0:
            print(f"{N:<4} {tc:<8} {tr:<7} {ti:<7} {tr-tc:<10} {ti-tc:<9} {(2*N-1)%25}")

    # ---- soundness of every claimed threshold (no over-claim anywhere) ----
    bad_claim = [ (N,tc) for (N,tc,tr,ti) in rows if tc >= 0 and not check_soundness(N,tc) ]
    bad_real  = [ (N,tr) for (N,tc,tr,ti) in rows if not check_soundness(N,tr) ]
    bad_int   = [ (N,ti) for (N,tc,tr,ti) in rows if not check_soundness(N,ti) ]
    print()
    print("unsound N for T_claim :", bad_claim[:10], "count", len(bad_claim))
    print("unsound N for T_real  :", bad_real[:10],  "count", len(bad_real))
    print("unsound N for T_int   :", bad_int[:10],   "count", len(bad_int))

    # ---- maximality: T+1 must FAIL for the threshold to be exact ----
    notmax_int = [ (N,ti) for (N,tc,tr,ti) in rows if check_soundness(N, ti+1) ]
    print("T_int not maximal at  :", notmax_int[:10], "count", len(notmax_int))

    # ---- how much strength (B4) leaves on the table ----
    gains_r = [ tr-tc for (N,tc,tr,ti) in rows ]
    gains_i = [ ti-tc for (N,tc,tr,ti) in rows ]
    print()
    print("T_real - T_claim : min %d max %d ; #N in 2..400 with gain>0 : %d"
          % (min(gains_r), max(gains_r), sum(1 for g in gains_r if g > 0)))
    print("T_int  - T_claim : min %d max %d ; #N in 2..400 with gain>0 : %d"
          % (min(gains_i), max(gains_i), sum(1 for g in gains_i if g > 0)))

    # ---- explicit witnesses ----
    print()
    print("Explicit witnesses where (B4)'s stated threshold is strictly weaker than the truth:")
    shown = 0
    for (N, tc, tr, ti) in rows:
        if ti - tc >= 2 and shown < 12:
            print(f"  N={N}: (B4) allows only d(v)<={tc}; but d(v)={ti} already works: "
                  f"floor(({N}-1)^2/25)={(N-1)**2//25} + floor({ti}/2)={ti//2} "
                  f"= {(N-1)**2//25 + ti//2} <= floor({N}^2/25)={N*N//25}")
            shown += 1

    # ---- resulting minimum-degree lower bound for a minimal counterexample ----
    print()
    print("Minimum-degree lower bound for a minimal counterexample (delta >= value):")
    print("N      claimed (B6)   exact (integral)")
    for N in [41, 50, 100, 200, 201, 250, 300, 400]:
        print(f"{N:<6} {T_claim(N)+1:<14} {T_int(N)+1}")

    # ---- asymptotic constants ----
    print()
    print("asymptotics: T_claim(N)/N -> 4/25 = %.6f ; T_int(N)/N -> 4/25 = %.6f (same slope,"
          " the gain is an additive O(1), never a better constant)"
          % (0.16, 0.16))
    for N in [1000, 10000, 100000]:
        print(f"  N={N}: T_claim={T_claim(N)} T_int={T_int(N)} diff={T_int(N)-T_claim(N)}"
              f"  T_int/N={Fraction(T_int(N),N)} = {T_int(N)/N:.8f}")

if __name__ == "__main__":
    main()
