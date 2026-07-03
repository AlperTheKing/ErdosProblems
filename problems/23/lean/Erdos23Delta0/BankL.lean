/-
Erdős #23 δ=0 — L3: Bank-L case arithmetic (the proven scalar cores).
Mirrors BANKL_LOW_LENGTH_LANE_COAREA_GPTPRO.md:
  • L ≥ 13 case: packet exchange (m−1 ≤ r²/25 + d/2) + spacing (d ≤ 2r) close Bank-L;
  • P_Q ≤ 0 case: the pressure identity −Δ_Q = ρ_Q − P_Q with ρ_Q ≥ 0 closes Bank-L;
  • the pressure quantity P_Q = 25(p−1) + 25(d+h)/2 − 2Lr;
  • sparse m = 1 bypass (already in Skeleton, restated here in ℚ).
All statements are ℚ-arithmetic; the combinatorial inputs (packet exchange, spacing,
ρ_Q ≥ 0) enter as hypotheses proven elsewhere in the chain.
-/

import Mathlib

namespace Erdos23Delta0
namespace BankL

/-- The pressure quantity P_Q. -/
def pressure (p d h L r : ℚ) : ℚ := 25*(p - 1) + 25*(d + h)/2 - 2*L*r

/-- Bank-L target: 25m ≤ N² − L² + 25, phrased as −Δ_Q ≥ 0 with
    −Δ_Q = N² − L² + 25 − 25m. -/
def negDelta (N L m : ℚ) : ℚ := N^2 - L^2 + 25 - 25*m

/-- CASE L ≥ 13 (proven): packet exchange m − 1 ≤ r²/25 + d/2 and spacing d ≤ 2r
    give m − 1 ≤ r²/25 + 2Lr/25, i.e. the r-quadratic Bank-L bound. -/
theorem bankL_of_L13 (L r d m : ℚ) (hL : 13 ≤ L) (hr : 0 ≤ r)
    (hspace : d ≤ 2*r) (hpe : m - 1 ≤ r^2/25 + d/2) :
    m - 1 ≤ r^2/25 + 2*L*r/25 := by
  have h1 : d/2 ≤ r := by linarith
  have h2 : r ≤ 2*L*r/25 := by nlinarith
  linarith

/-- The r-quadratic bound closes Bank-L when N ≥ L + r (row plus its distinct
    row-neighbors fit in the graph): N² − L² + 25 − 25m ≥ 0. -/
theorem bankL_target_of_quadratic (N L r m : ℚ) (hN : L + r ≤ N)
    (hL : 0 ≤ L) (hr : 0 ≤ r) (hLr : 25 ≤ 2*L)
    (hq : m - 1 ≤ r^2/25 + 2*L*r/25) :
    0 ≤ negDelta N L m := by
  unfold negDelta
  have hexp : (L + r)^2 = L^2 + 2*L*r + r^2 := by ring
  have hN2 : L^2 + 2*L*r + r^2 ≤ N^2 := by
    have h0 : 0 ≤ L + r := by linarith
    nlinarith
  nlinarith

/-- CASE P_Q ≤ 0 (proven): the pressure identity −Δ_Q = ρ_Q − P_Q together with
    ρ_Q ≥ 0 (packet exchange at V(Q)) and P_Q ≤ 0 closes Bank-L. -/
theorem bankL_of_pressure_nonpos (negDeltaQ rhoQ PQ : ℚ)
    (hid : negDeltaQ = rhoQ - PQ) (hrho : 0 ≤ rhoQ) (hP : PQ ≤ 0) :
    0 ≤ negDeltaQ := by
  rw [hid]
  linarith

/-- Sparse identity in ℚ (m = 1 bypass): −Δ_Q = (N−L)² − 25(m−1) + 2L(N−L);
    at m = 1 this is (N−L)² + 2L(N−L) ≥ 0 for N ≥ L ≥ 0. -/
theorem sparse_m1_bypass (N L : ℚ) (hL : 0 ≤ L) (hNL : L ≤ N) :
    0 ≤ negDelta N L 1 := by
  unfold negDelta
  nlinarith [sq_nonneg (N - L)]

/-- The lane-coarea constants: κ_L · μ_L = 25 for L ∈ {7, 9, 11}. -/
example : ((25 - 2*7 : ℚ)/4) * (100/(25 - 2*7)) = 25 := by norm_num
example : ((25 - 2*9 : ℚ)/4) * (100/(25 - 2*9)) = 25 := by norm_num
example : ((25 - 2*11 : ℚ)/4) * (100/(25 - 2*11)) = 25 := by norm_num

/-- Hard-set pressure bound: for p = 1, h = 0 rows, P_Q = 25d/2 − 2Lr, and
    spacing d ≤ 2r makes P_Q > 0 possible only for L ≤ 12 (2L < 25). -/
theorem hard_set_L_le_12 (d L r : ℚ) (hr : 0 < r) (hd : d ≤ 2*r)
    (hP : 0 < pressure 1 d 0 L r) : 2*L < 25 := by
  unfold pressure at hP
  nlinarith

end BankL
end Erdos23Delta0
