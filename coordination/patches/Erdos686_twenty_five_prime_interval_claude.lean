import FormalConjectures.Util.ProblemImports

namespace Erdos686

/-- **Prime-interval / smoothness necessary condition** for a `25`-representation.
If `∏_{i=1}^k (m+i) = 25 · ∏_{i=1}^k (n+i)` (the cleared-denominator form of the target),
then every prime `p ≠ 5` dividing the numerator product must be `≤ n + k`.
Equivalently: the numerator interval `[m+1, m+k]` must be `(n+k)`-smooth apart from
powers of `5`. In particular the largest factor `m+k` cannot be a prime `> n+k`. -/
theorem erdos_686_twenty_five_prime_interval
    (k n m : ℕ)
    (heq : ∏ i ∈ Finset.Icc 1 k, (m + i) = 25 * ∏ i ∈ Finset.Icc 1 k, (n + i))
    (p : ℕ) (hp : p.Prime) (hp5 : p ≠ 5)
    (hdvd : p ∣ ∏ i ∈ Finset.Icc 1 k, (m + i)) :
    p ≤ n + k := by
  rw [heq] at hdvd
  have hp25 : ¬ p ∣ 25 := by
    intro hd
    have h5 : p ∣ 5 := by
      have h25 : (25 : ℕ) = 5 ^ 2 := by norm_num
      rw [h25] at hd
      exact hp.prime.dvd_of_dvd_pow hd
    exact hp5 ((Nat.prime_dvd_prime_iff_eq hp (by norm_num)).mp h5)
  have hdvdprod : p ∣ ∏ i ∈ Finset.Icc 1 k, (n + i) := by
    rcases (Nat.Prime.dvd_mul hp).mp hdvd with h | h
    · exact absurd h hp25
    · exact h
  obtain ⟨j, hj, hjdvd⟩ := (Prime.dvd_finset_prod_iff hp.prime _).mp hdvdprod
  have hj1 : 1 ≤ j := (Finset.mem_Icc.mp hj).1
  have hjk : j ≤ k := (Finset.mem_Icc.mp hj).2
  have hple : p ≤ n + j := Nat.le_of_dvd (by omega) hjdvd
  omega

/-- Immediate consequence: in any `25`-representation the top factor `m + k` is **not**
a prime exceeding `n + k`. (It must be `(n+k)`-smooth apart from `5`.) -/
theorem erdos_686_twenty_five_top_not_large_prime
    (k n m : ℕ) (hk : 1 ≤ k)
    (heq : ∏ i ∈ Finset.Icc 1 k, (m + i) = 25 * ∏ i ∈ Finset.Icc 1 k, (n + i))
    (hp : (m + k).Prime) (hp5 : m + k ≠ 5) :
    m + k ≤ n + k := by
  apply erdos_686_twenty_five_prime_interval k n m heq (m + k) hp hp5
  exact Finset.dvd_prod_of_mem _ (Finset.mem_Icc.mpr ⟨hk, le_refl k⟩)

/-- **Prime-free interval condition.** In any `25`-representation with `m ≥ n + k`, every
element `m + i` of the numerator interval that is prime must equal `5`. Since `m + i ≥ n+k+1`,
this means `[m+1, m+k]` is a run of `k` consecutive **composite** integers (a prime gap of
length `≥ k`) — apart from the degenerate possibility `m + i = 5`. Together with
`erdos_686_twenty_five_prime_interval` (smoothness), this forces any witness to sit inside a
large prime gap whose entries are all `(n+k)`-smooth, explaining the absence of small witnesses. -/
theorem erdos_686_twenty_five_interval_prime_free
    (k n m : ℕ) (hmn : n + k ≤ m)
    (heq : ∏ i ∈ Finset.Icc 1 k, (m + i) = 25 * ∏ i ∈ Finset.Icc 1 k, (n + i))
    (i : ℕ) (hi : i ∈ Finset.Icc 1 k) (hp : (m + i).Prime) :
    m + i = 5 := by
  by_contra hne
  have hdvd : (m + i) ∣ ∏ j ∈ Finset.Icc 1 k, (m + j) := Finset.dvd_prod_of_mem _ hi
  have hle := erdos_686_twenty_five_prime_interval k n m heq (m + i) hp hne hdvd
  have hi1 : 1 ≤ i := (Finset.mem_Icc.mp hi).1
  omega

end Erdos686

#print axioms Erdos686.erdos_686_twenty_five_prime_interval
#print axioms Erdos686.erdos_686_twenty_five_top_not_large_prime
#print axioms Erdos686.erdos_686_twenty_five_interval_prime_free
