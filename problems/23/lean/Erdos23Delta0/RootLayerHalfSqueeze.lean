import Erdos23Delta0.BankedWallLP

/-!
# Fractional half-layer dual squeeze

This module isolates the exact LP algebra behind the proposed root-layer
argument.  It deliberately assumes the two pieces of concrete geometry that
are not yet represented by a compiled extractor object:

* every positive-alpha atom is covered twice by the listed wall rows;
* the half-layer short and port loads have a legal bank routing.

No existence theorem for a root layer, petal shores, or mandatory Doors is
claimed here.
-/

namespace Erdos23Delta0
namespace Wall

open scoped BigOperators

variable {I : BankedWallLP}

/-- Multiplicity-sensitive weight obtained by assigning `1 / 2` to every
listed wall row.  Repeated rows are counted with their multiplicity. -/
noncomputable def halfLayerWeight {q : Nat} (walls : Fin q → I.Cut) (X : I.Cut) : ℚ :=
  by
    classical
    exact (1 / 2 : ℚ) * ∑ i : Fin q, if walls i = X then 1 else 0

/-- The exact routing/capacity obligations for the fractional half-layer. -/
structure HalfLayerRouted {q : Nat} (I : BankedWallLP) (walls : Fin q → I.Cut) where
  rho : I.Port → I.Sink → ℚ
  rho_nonneg : ∀ p s, 0 ≤ rho p s
  rho_legal : ∀ p s, rho p s ≠ 0 → I.legal p s
  short_half_le : ∀ f : I.Short,
    (1 / 2 : ℚ) * ∑ i : Fin q, I.useShort (walls i) f ≤ 1
  port_half_routed : ∀ p : I.Port,
    (1 / 2 : ℚ) * ∑ i : Fin q, I.cutPort (walls i) p ≤ ∑ s : I.Sink, rho p s
  sink_capacity : ∀ s : I.Sink, (∑ p : I.Port, rho p s) ≤ I.cap s

private lemma sum_halfLayerWeight_mul {q : Nat} (walls : Fin q → I.Cut)
    (f : I.Cut → ℚ) :
    (∑ X : I.Cut, halfLayerWeight walls X * f X) =
      (1 / 2 : ℚ) * ∑ i : Fin q, f (walls i) := by
  classical
  unfold halfLayerWeight
  calc
    (∑ X : I.Cut,
        ((1 / 2 : ℚ) * ∑ i : Fin q, if walls i = X then 1 else 0) * f X) =
        (1 / 2 : ℚ) * ∑ X : I.Cut,
          (∑ i : Fin q, if walls i = X then 1 else 0) * f X := by
            simp_rw [mul_assoc]
            rw [Finset.mul_sum]
    _ = (1 / 2 : ℚ) * ∑ X : I.Cut, ∑ i : Fin q,
          (if walls i = X then 1 else 0) * f X := by
            congr 1
            exact Finset.sum_congr rfl fun X _ => by rw [Finset.sum_mul]
    _ = (1 / 2 : ℚ) * ∑ i : Fin q, ∑ X : I.Cut,
          (if walls i = X then 1 else 0) * f X := by
            rw [Finset.sum_comm]
    _ = (1 / 2 : ℚ) * ∑ i : Fin q, f (walls i) := by
            congr 1
            exact Finset.sum_congr rfl fun i _ => by simp

private lemma halfLayerWeight_nonneg {q : Nat} (walls : Fin q → I.Cut) (X : I.Cut) :
    0 ≤ halfLayerWeight walls X := by
  classical
  unfold halfLayerWeight
  apply mul_nonneg
  · norm_num
  · exact Finset.sum_nonneg fun i _ => by split <;> norm_num

/-- A positive-alpha exact two-cover, together with the checked half-layer
routing inequalities, is a `DualSqueeze` for the listed wall rows. -/
noncomputable def DualSqueeze.ofHalfLayerTwoCover {q : Nat}
    (d : Dual I) (hd : d.Checked) (walls : Fin q → I.Cut)
    (htwo : ∀ a : I.Atom, 0 < d.alpha a →
      ∑ i : Fin q, I.cov (walls i) a = 2)
    (R : HalfLayerRouted I walls) :
    DualSqueeze I (fun X => ∃ i, walls i = X) d := by
  classical
  refine
    { theta := halfLayerWeight walls
      rho := R.rho
      theta_nonneg := halfLayerWeight_nonneg walls
      theta_allowed := ?_
      rho_nonneg := R.rho_nonneg
      rho_legal := R.rho_legal
      alpha_dominated := ?_
      short_coeff := ?_
      port_coeff_routed := ?_
      sink_coeff := R.sink_capacity }
  · intro X hX
    by_contra hnone
    push_neg at hnone
    have hz : halfLayerWeight walls X = 0 := by
      unfold halfLayerWeight
      rw [Finset.sum_eq_zero (fun i _ => by simp [hnone i])]
      ring
    exact hX hz
  · have halpha : ∀ a : I.Atom,
        d.alpha a = ((1 / 2 : ℚ) * ∑ i : Fin q, I.cov (walls i) a) * d.alpha a := by
      intro a
      by_cases ha : d.alpha a = 0
      · simp [ha]
      · have hapos : 0 < d.alpha a := lt_of_le_of_ne (hd.alpha_nonneg a) (Ne.symm ha)
        rw [htwo a hapos]
        ring
    rw [sum_halfLayerWeight_mul]
    unfold totalAlpha cutAlpha
    calc
      (∑ a : I.Atom, d.alpha a) =
          ∑ a : I.Atom,
            ((1 / 2 : ℚ) * ∑ i : Fin q, I.cov (walls i) a) * d.alpha a := by
              exact Finset.sum_congr rfl fun a _ => halpha a
      _ = (1 / 2 : ℚ) * ∑ i : Fin q,
            ∑ a : I.Atom, I.cov (walls i) a * d.alpha a := by
              simp only [Finset.mul_sum, Finset.sum_mul]
              rw [Finset.sum_comm]
              ring
      _ ≤ (1 / 2 : ℚ) * ∑ i : Fin q,
            ∑ a : I.Atom, I.cov (walls i) a * d.alpha a := le_rfl
  · intro f
    rw [sum_halfLayerWeight_mul]
    exact R.short_half_le f
  · intro p
    rw [sum_halfLayerWeight_mul]
    exact R.port_half_routed p

/-- The half-layer certificate excludes every checked strict dual.  Oddness,
extremality, normalization, and minimum-negative hypotheses are absent. -/
theorem noStrictDual_of_halfLayerTwoCover {q : Nat}
    (d : Dual I) (hd : d.Checked) (walls : Fin q → I.Cut)
    (htwo : ∀ a : I.Atom, 0 < d.alpha a →
      ∑ i : Fin q, I.cov (walls i) a = 2)
    (R : HalfLayerRouted I walls) :
    ¬ d.StrictGap :=
  noStrictDual_of_dualSqueeze hd (DualSqueeze.ofHalfLayerTwoCover d hd walls htwo R)

#print axioms DualSqueeze.ofHalfLayerTwoCover
#print axioms noStrictDual_of_halfLayerTwoCover

end Wall
end Erdos23Delta0
