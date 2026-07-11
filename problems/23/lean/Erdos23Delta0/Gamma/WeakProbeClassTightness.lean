import Erdos23Delta0.CertGraph

/-!
# Arithmetic core of the weak-probe reduction

For two nonempty attachment classes, nonnegative integral singleton switch
surpluses whose cross sums are all below two force one whole class to be
cut-tight.  The graph bridge uses triangle-freeness to identify each cross
pair surplus with this sum.
-/

namespace Erdos23Delta0
namespace Gamma
namespace WeakProbeClassTightness

/-- If every cross-pair sum of nonnegative integral surpluses is below two,
one side is identically zero. -/
theorem one_class_zero_of_pair_sum_lt_two
    {X Y : Type*} (a : X → Int) (b : Y → Int)
    (ha : ∀ x, 0 ≤ a x) (hb : ∀ y, 0 ≤ b y)
    (hpair : ∀ x y, a x + b y < 2) :
    (∀ x, a x = 0) ∨ (∀ y, b y = 0) := by
  classical
  by_cases hzero : ∀ x, a x = 0
  · exact Or.inl hzero
  · right
    push_neg at hzero
    obtain ⟨x, hx⟩ := hzero
    have hax := ha x
    have hapos : 1 ≤ a x := by omega
    intro y
    have hp := hpair x y
    have hby_le : b y ≤ 0 := by omega
    exact le_antisymm hby_le (hb y)

/-- Contrapositive form used to locate a production-strength probe. -/
theorem exists_pair_sum_two_of_both_classes_positive
    {X Y : Type*} (a : X → Int) (b : Y → Int)
    (hx : ∃ x, 0 < a x) (hy : ∃ y, 0 < b y) :
    ∃ x y, 2 ≤ a x + b y := by
  obtain ⟨x, hx⟩ := hx
  obtain ⟨y, hy⟩ := hy
  exact ⟨x, y, by omega⟩

#print axioms one_class_zero_of_pair_sum_lt_two
#print axioms exists_pair_sum_two_of_both_classes_positive

end WeakProbeClassTightness
end Gamma
end Erdos23Delta0
