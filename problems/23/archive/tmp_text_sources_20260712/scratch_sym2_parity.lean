import Mathlib

namespace Erdos23Delta0
namespace ScratchSym2Parity

open SimpleGraph

variable {V : Type*} [DecidableEq V]

 theorem sym2_eq_of_even_two_nonloop {a b c d : V}
    (hab : a ≠ b) (hcd : c ≠ d)
    (hpar : ∀ x : V,
      Even ((if x ∈ s(a,b) then 1 else 0) + (if x ∈ s(c,d) then 1 else 0))) :
    s(a,b) = s(c,d) := by
  have ha : a ∈ s(c,d) := by
    by_contra ha
    have h := hpar a
    simp [Sym2.mem_iff, hab, ha] at h
  have hb : b ∈ s(c,d) := by
    by_contra hb
    have h := hpar b
    simp [Sym2.mem_iff, hab.symm, hb] at h
  rw [Sym2.eq_iff]
  rw [Sym2.mem_iff] at ha hb
  grind

#print axioms sym2_eq_of_even_two_nonloop

end ScratchSym2Parity
end Erdos23Delta0
