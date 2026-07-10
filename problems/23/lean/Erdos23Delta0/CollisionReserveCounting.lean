import Mathlib

/-!
# Collision-reserve counting

This is the graph-independent counting atom in the collision-reserve route.
For a chosen family of length-five rows through a vertex, `A` is their vertex
union and `Nbr` is the internal off-support neighborhood of that vertex.

`5*r - |A|` is the duplicate count and `|A ∩ Nbr|` is the hit correction.
The union bound gives their sum enough mass to pay the endpoint degree after
ordinary vertex slack.  No bank-token existence or legality is asserted here.
-/

namespace Erdos23Delta0
namespace CollisionReserveCounting

open scoped BigOperators

variable {V Ω : Type*} [Fintype V] [DecidableEq V]

/-- Pointwise duplicate-plus-hit inequality. -/
theorem duplicate_add_hit_ge (r : Nat) (A Nbr : Finset V) :
    5 * (r : ℚ) - (A.card : ℚ) + ((A ∩ Nbr).card : ℚ) ≥
      5 * (r : ℚ) + (Nbr.card : ℚ) - (Fintype.card V : ℚ) := by
  have hU : (A ∪ Nbr).card ≤ Fintype.card V :=
    Finset.card_le_card (Finset.subset_univ (A ∪ Nbr))
  have hsum := Finset.card_union_add_card_inter A Nbr
  have hNat : A.card + Nbr.card ≤ Fintype.card V + (A ∩ Nbr).card := by
    omega
  have hQ : (A.card : ℚ) + (Nbr.card : ℚ) ≤
      (Fintype.card V : ℚ) + ((A ∩ Nbr).card : ℚ) := by
    exact_mod_cast hNat
  linarith

/-- Summed form over any finite family of row selections. -/
theorem sum_duplicate_add_hit_ge [Fintype Ω]
    (r : Ω → Nat) (A : Ω → Finset V) (Nbr : Finset V) :
    (∑ w : Ω,
        (5 * (r w : ℚ) - ((A w).card : ℚ) +
          (((A w) ∩ Nbr).card : ℚ))) ≥
      5 * (∑ w : Ω, (r w : ℚ)) +
        (Fintype.card Ω : ℚ) *
          ((Nbr.card : ℚ) - (Fintype.card V : ℚ)) := by
  calc
    (∑ w : Ω,
        (5 * (r w : ℚ) - ((A w).card : ℚ) +
          (((A w) ∩ Nbr).card : ℚ))) ≥
        ∑ w : Ω,
          (5 * (r w : ℚ) + (Nbr.card : ℚ) -
            (Fintype.card V : ℚ)) := by
      exact Finset.sum_le_sum fun w _ => duplicate_add_hit_ge (r w) (A w) Nbr
    _ = 5 * (∑ w : Ω, (r w : ℚ)) +
        (Fintype.card Ω : ℚ) *
          ((Nbr.card : ℚ) - (Fintype.card V : ℚ)) := by
      simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib,
        Finset.sum_const, nsmul_eq_mul, Finset.card_univ]
      rw [Finset.mul_sum]
      ring

/-- Uniform average of a rational-valued finite family. -/
noncomputable def uniformMean [Fintype Ω] (f : Ω → ℚ) : ℚ :=
  (∑ w : Ω, f w) / (Fintype.card Ω : ℚ)

/-- Averaged collision inequality. -/
theorem uniformMean_duplicate_add_hit_ge [Fintype Ω] [Nonempty Ω]
    (r : Ω → Nat) (A : Ω → Finset V) (Nbr : Finset V) :
    uniformMean (fun w =>
        5 * (r w : ℚ) - ((A w).card : ℚ) +
          (((A w) ∩ Nbr).card : ℚ)) ≥
      5 * uniformMean (fun w => (r w : ℚ)) +
        (Nbr.card : ℚ) - (Fintype.card V : ℚ) := by
  have hnNat : 0 < Fintype.card Ω := Fintype.card_pos
  have hn : (0 : ℚ) < (Fintype.card Ω : ℚ) := by exact_mod_cast hnNat
  have hsum := sum_duplicate_add_hit_ge r A Nbr
  unfold uniformMean
  have hrewrite :
      5 * ((∑ w : Ω, (r w : ℚ)) / (Fintype.card Ω : ℚ)) +
          (Nbr.card : ℚ) - (Fintype.card V : ℚ) =
        (5 * (∑ w : Ω, (r w : ℚ)) +
          (Fintype.card Ω : ℚ) *
            ((Nbr.card : ℚ) - (Fintype.card V : ℚ))) /
          (Fintype.card Ω : ℚ) := by
    field_simp
    ring
  rw [hrewrite]
  exact (div_le_div_iff_of_pos_right hn).2 hsum

/-- Rewriting the ambient term as ordinary vertex slack. -/
theorem ge_degree_sub_slack_of_ge_load_add_degree_sub_N
    {reserve load degree N : ℚ}
    (h : load + degree - N ≤ reserve) :
    degree - max 0 (N - load) ≤ reserve := by
  by_cases hload : load ≤ N
  · rw [max_eq_right (sub_nonneg.mpr hload)]
    linarith
  · have hsub : N - load ≤ 0 := by linarith
    rw [max_eq_left hsub]
    linarith

/-- The averaged duplicate-plus-hit reserve pays endpoint degree after slack. -/
theorem uniformMean_collision_pays_degree_after_slack
    [Fintype Ω] [Nonempty Ω]
    (r : Ω → Nat) (A : Ω → Finset V) (Nbr : Finset V) :
    (Nbr.card : ℚ) -
        max 0 ((Fintype.card V : ℚ) -
          5 * uniformMean (fun w => (r w : ℚ))) ≤
      uniformMean (fun w =>
        5 * (r w : ℚ) - ((A w).card : ℚ) +
          (((A w) ∩ Nbr).card : ℚ)) := by
  apply ge_degree_sub_slack_of_ge_load_add_degree_sub_N
  exact uniformMean_duplicate_add_hit_ge r A Nbr

#print axioms duplicate_add_hit_ge
#print axioms sum_duplicate_add_hit_ge
#print axioms uniformMean_duplicate_add_hit_ge
#print axioms uniformMean_collision_pays_degree_after_slack

end CollisionReserveCounting
end Erdos23Delta0
