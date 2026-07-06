/-
Finite mask-symmetry layer for the A1-proper six-cone reduction (graph-independent).
The 30 nonempty proper masks of Z/5 form 6 rotation-orbits; each maps to a canonical
mask (bit-codes 1,3,5,7,11,15) by a rotation. Table cross-verified 30/30 (Claude) and
matches GPT-Pro MAIN's design. All finite; honest kernel `decide` only.
-/
import Mathlib

namespace Erdos23Delta0
namespace A1MaskSymmetry

/-- Bit code of a mask over `Fin 5`. -/
def maskCode (A : Finset (Fin 5)) : Nat := ∑ i ∈ A, 2 ^ i.val

/-- The mask with the given bit code. -/
def maskOfCode (code : Nat) : Finset (Fin 5) :=
  Finset.univ.filter (fun i : Fin 5 => (code / 2 ^ i.val) % 2 = 1)

/-- Bit code of the canonical representative of orbit `j`. -/
def canonicalMaskCode : Fin 6 → Nat
  | 0 => 1 | 1 => 3 | 2 => 5 | 3 => 7 | 4 => 11 | 5 => 15

/-- Canonical mask of orbit `j`: M0={0}, M1={0,1}, M2={0,2}, M3={0,1,2}, M4={0,1,3}, M5={0,1,2,3}. -/
def canonicalMask (j : Fin 6) : Finset (Fin 5) := maskOfCode (canonicalMaskCode j)

/-- Orbit id of a mask, by bit code (verified table). -/
def canonicalMaskIdOfCode : Nat → Fin 6
  | 1 => 0 | 2 => 0 | 3 => 1 | 4 => 0 | 5 => 2 | 6 => 1 | 7 => 3 | 8 => 0 | 9 => 2 | 10 => 2
  | 11 => 4 | 12 => 1 | 13 => 4 | 14 => 3 | 15 => 5 | 16 => 0 | 17 => 1 | 18 => 2 | 19 => 3 | 20 => 2
  | 21 => 4 | 22 => 4 | 23 => 5 | 24 => 1 | 25 => 3 | 26 => 4 | 27 => 5 | 28 => 3 | 29 => 5 | 30 => 5
  | _ => 0

/-- Rotation taking a mask to its canonical representative, by bit code (verified table). -/
def canonicalRotOfCode : Nat → Fin 5
  | 1 => 0 | 2 => 4 | 3 => 0 | 4 => 3 | 5 => 0 | 6 => 4 | 7 => 0 | 8 => 2 | 9 => 2 | 10 => 4
  | 11 => 0 | 12 => 3 | 13 => 3 | 14 => 4 | 15 => 0 | 16 => 1 | 17 => 1 | 18 => 1 | 19 => 1 | 20 => 3
  | 21 => 1 | 22 => 4 | 23 => 1 | 24 => 2 | 25 => 2 | 26 => 2 | 27 => 2 | 28 => 3 | 29 => 3 | 30 => 4
  | _ => 0

/-- Inverse rotation: `rotBack r` sends index `i` to `i - r (mod 5)`. -/
def rotBack (r i : Fin 5) : Fin 5 := ⟨(i.val + 5 - r.val) % 5, Nat.mod_lt _ (by omega)⟩

theorem rotBack_injective (r : Fin 5) : Function.Injective (rotBack r) := by
  intro a b h
  have : (a.val + 5 - r.val) % 5 = (b.val + 5 - r.val) % 5 := congrArg Fin.val h
  have ha := a.isLt
  have hb := b.isLt
  have hr := r.isLt
  omega

/-- Symmetry data reducing a proper mask to a canonical one via a rotation. -/
structure MaskSymmetryData (A : Finset (Fin 5)) where
  id : Fin 6
  rot : Fin 5
  mask_eq : A = (canonicalMask id).image (rotBack rot)

/-- The finite classifier is correct on every nonempty proper mask (decidable, 32-case). -/
theorem maskSymmetryData_valid :
    ∀ A : Finset (Fin 5), A.Nonempty → A ≠ Finset.univ →
      A = (canonicalMask (canonicalMaskIdOfCode (maskCode A))).image
            (rotBack (canonicalRotOfCode (maskCode A))) := by
  decide

/-- Total classifier: every nonempty proper mask carries its symmetry data. -/
def maskSymmetryData_of_proper (A : Finset (Fin 5))
    (hAne : A.Nonempty) (hAproper : A ≠ Finset.univ) : MaskSymmetryData A :=
  ⟨canonicalMaskIdOfCode (maskCode A), canonicalRotOfCode (maskCode A),
    maskSymmetryData_valid A hAne hAproper⟩

end A1MaskSymmetry
end Erdos23Delta0
