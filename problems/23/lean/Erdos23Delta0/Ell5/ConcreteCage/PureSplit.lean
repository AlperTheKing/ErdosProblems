import Erdos23Delta0.Ell5.ConcreteCage.Restrict

/-!
# Concrete ell=5 cage bookkeeping: pure surplus split

The graph-heavy statement is isolated as `StrongPureLensAtomSplit`: each atom
of the ambient cage is supported on the lens shore, supported on the complement,
or has zero surplus, and no atom is counted on both sides.  From that, the
surplus split is finite-sum bookkeeping.
-/

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} {c : Distances.Cut V}

private theorem sum_split_filter_aux {α : Type*} [DecidableEq α]
    (s : Finset α) (w : α → ℚ) (p q : α → Prop)
    [DecidablePred p] [DecidablePred q]
    (hno : ∀ a ∈ s, ¬ (p a ∧ q a))
    (hcover : ∀ a ∈ s, p a ∨ q a ∨ w a = 0) :
    s.sum w = (s.filter p).sum w + (s.filter q).sum w := by
  classical
  revert hno hcover
  refine Finset.induction_on s ?empty ?insert
  · intro _ _
    simp
  · intro a s ha ih hno hcover
    have hno_s : ∀ b ∈ s, ¬ (p b ∧ q b) := by
      intro b hb
      exact hno b (Finset.mem_insert_of_mem hb)
    have hcover_s : ∀ b ∈ s, p b ∨ q b ∨ w b = 0 := by
      intro b hb
      exact hcover b (Finset.mem_insert_of_mem hb)
    have ihs := ih hno_s hcover_s
    have hno_a : ¬ (p a ∧ q a) := hno a (Finset.mem_insert_self a s)
    have hcover_a : p a ∨ q a ∨ w a = 0 := hcover a (Finset.mem_insert_self a s)
    by_cases hp : p a
    · by_cases hq : q a
      · exact (hno_a ⟨hp, hq⟩).elim
      · rw [Finset.filter_insert, Finset.filter_insert]
        simp [ha, hp, hq, ihs]
        ring_nf
    · by_cases hq : q a
      · rw [Finset.filter_insert, Finset.filter_insert]
        simp [ha, hp, hq, ihs]
        ring_nf
      · have hw : w a = 0 := by
          rcases hcover_a with hp' | hq' | hz
          · exact (hp hp').elim
          · exact (hq hq').elim
          · exact hz
        rw [Finset.filter_insert, Finset.filter_insert]
        simp [ha, hp, hq, hw, ihs]

/-- Strong pure split at a vertex cut `U`: all nonzero-surplus atoms are fully
owned by exactly one side. -/
structure StrongPureLensAtomSplit (C : AmbientCage G c) (U : Finset V) : Prop where
  noDouble :
    ∀ a ∈ C.atoms,
      ¬ (atomSupportedOn a U ∧ atomSupportedOn a (C.verts \ U))
  coverOrZero :
    ∀ a ∈ C.atoms,
      atomSupportedOn a U ∨ atomSupportedOn a (C.verts \ U) ∨ atomSurplus G c a = 0

/-- Strong purity gives the concrete surplus split across `U` and its ambient
complement. -/
theorem surplus_split_of_strongPure (C : AmbientCage G c) (U : Finset V)
    (h : StrongPureLensAtomSplit C U) :
    C.Surplus = (restrict C U).Surplus + (restrictCompl C U).Surplus := by
  classical
  change C.atoms.sum (fun a => atomSurplus G c a) =
    (C.atoms.filter fun a => atomSupportedOn a U).sum (fun a => atomSurplus G c a) +
      (C.atoms.filter fun a => atomSupportedOn a (C.verts \ U)).sum
        (fun a => atomSurplus G c a)
  exact sum_split_filter_aux C.atoms (fun a => atomSurplus G c a)
    (fun a => atomSupportedOn a U)
    (fun a => atomSupportedOn a (C.verts \ U))
    h.noDouble h.coverOrZero

end ConcreteCage
end Ell5
end Erdos23Delta0
