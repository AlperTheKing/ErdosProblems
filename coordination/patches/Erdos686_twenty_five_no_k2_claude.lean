import FormalConjectures.Util.ProblemImports

namespace Erdos686

/-- The number `25` cannot be written as a ratio of two products of `2` consecutive
integers with `m ≥ n + 2`: the `k = 2` (degenerate Pell) obstruction.
`(m+1)(m+2) = 25(n+1)(n+2)` is impossible because the target lies strictly between
`(5n+6)(5n+7)` and `(5n+7)(5n+8)`. -/
theorem erdos_686_twenty_five_no_k2 :
    ¬ ∃ᵉ (n : ℕ) (m ≥ n + 2),
      (25 : ℚ) = (∏ i ∈ Finset.Icc 1 2, (m + i)) / (∏ i ∈ Finset.Icc 1 2, (n + i)) := by
  simp only [Finset.prod_Icc_succ_top (by decide : 1 ≤ 2), Finset.Icc_self,
    Finset.prod_singleton]
  push_neg
  intro n m hm
  rw [ne_eq, eq_div_iff (by positivity : (↑((n + 1) * (n + (1 + 1))) : ℚ) ≠ 0)]
  push_cast
  intro h
  have h' : 25 * ((n + 1) * (n + 2)) = (m + 1) * (m + 2) := by exact_mod_cast h
  by_cases hc : m ≤ 5 * n + 5 <;> nlinarith [h', hm, hc]

end Erdos686

#print axioms Erdos686.erdos_686_twenty_five_no_k2
