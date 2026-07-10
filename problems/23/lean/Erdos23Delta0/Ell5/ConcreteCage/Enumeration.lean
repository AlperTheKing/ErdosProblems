import Erdos23Delta0.Ell5.ConcreteCage.PureLensSplit

/-!
# Concrete pure-lens cut enumeration interface

This module separates finite enumeration from graph reflection.  A provider
supplies `candidateB` together with a proof that it recognizes concrete cuts
on subsets of the ambient cage.  The checker below only enumerates those
subsets; it does not decide connectivity, geodesic support, or a BFS result.

Constructing such a `candidateB` from executable graph data remains open.  In
particular, this module neither implements nor assumes a BFS/support
reflection theorem.
-/

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} {c : Distances.Cut V}

/-- The three concrete obligations recognized by a pure-lens cut candidate. -/
def ConcretePureLensCut (C : AmbientCage G c) (U : Finset V) : Prop :=
  ProperRelative C (restrict C U) ∧
    ProperRelative C (restrictCompl C U) ∧
      StrongPureLensAtomSplit C U

/-- A concrete cut is necessarily contained in its ambient cage. -/
theorem concretePureLensCut_verts_subset {C : AmbientCage G c} {U : Finset V}
    (h : ConcretePureLensCut C U) :
    U ⊆ C.verts :=
  h.1.verts_subset

/-- Restriction to `U` and restriction to its ambient complement have
disjoint vertex sets by definition. -/
theorem restrict_disjoint_restrictCompl (C : AmbientCage G c) (U : Finset V) :
    Disjoint (restrict C U).verts (restrictCompl C U).verts := by
  change Disjoint U (C.verts \ U)
  rw [Finset.disjoint_left]
  intro v hvU hvCompl
  exact (Finset.mem_sdiff.mp hvCompl).2 hvU

/-- A complete Boolean classifier for the bounded family of candidate cuts.

This is a provider interface, not a construction: supplying `candidateB` and
proving `candidateB_iff` from executable graph data is the remaining open
reflection obligation. -/
structure ConcretePureLensEnumerationComplete (C : AmbientCage G c) where
  candidateB : Finset V → Bool
  candidateB_iff :
    ∀ U, U ⊆ C.verts →
      (candidateB U = true ↔ ConcretePureLensCut C U)

/-- Check the provider's Boolean classifier on every subset of `C.verts`.

The decided proposition mentions only finite membership and Boolean equality;
it does not claim a decision procedure for the graph predicates inside
`ConcretePureLensCut`. -/
def checkConcretePureLensExists (C : AmbientCage G c)
    (enumeration : ConcretePureLensEnumerationComplete C) : Bool :=
  decide (∃ U ∈ C.verts.powerset, enumeration.candidateB U = true)

/-- Bounded correctness of the positive checker result. -/
theorem checkConcretePureLensExists_eq_true_iff_bounded
    (C : AmbientCage G c)
    (enumeration : ConcretePureLensEnumerationComplete C) :
    checkConcretePureLensExists C enumeration = true ↔
      ∃ U, U ⊆ C.verts ∧ ConcretePureLensCut C U := by
  rw [checkConcretePureLensExists, decide_eq_true_iff]
  constructor
  · rintro ⟨U, hU, hcandidate⟩
    have hsub : U ⊆ C.verts := Finset.mem_powerset.mp hU
    exact
      ⟨U, hsub,
        (ConcretePureLensEnumerationComplete.candidateB_iff enumeration U hsub).mp
          hcandidate⟩
  · rintro ⟨U, hsub, hcut⟩
    exact
      ⟨U, Finset.mem_powerset.mpr hsub,
        (ConcretePureLensEnumerationComplete.candidateB_iff enumeration U hsub).mpr
          hcut⟩

/-- Bounded correctness of the negative checker result. -/
theorem checkConcretePureLensExists_eq_false_iff_bounded
    (C : AmbientCage G c)
    (enumeration : ConcretePureLensEnumerationComplete C) :
    checkConcretePureLensExists C enumeration = false ↔
      ∀ U, U ⊆ C.verts → ¬ ConcretePureLensCut C U := by
  constructor
  · intro hfalse U hsub hcut
    have htrue : checkConcretePureLensExists C enumeration = true :=
      (checkConcretePureLensExists_eq_true_iff_bounded C enumeration).2
        ⟨U, hsub, hcut⟩
    rw [hfalse] at htrue
    cases htrue
  · intro hnone
    cases hcheck : checkConcretePureLensExists C enumeration with
    | false => rfl
    | true =>
        obtain ⟨U, hsub, hcut⟩ :=
          (checkConcretePureLensExists_eq_true_iff_bounded C enumeration).1 hcheck
        exact (hnone U hsub hcut).elim

/-- Completeness for an arbitrary concrete cut.  Properness automatically
places its vertex set inside the bounded powerset searched by the checker. -/
theorem checkConcretePureLensExists_complete
    (C : AmbientCage G c)
    (enumeration : ConcretePureLensEnumerationComplete C)
    {U : Finset V} (hcut : ConcretePureLensCut C U) :
    checkConcretePureLensExists C enumeration = true :=
  (checkConcretePureLensExists_eq_true_iff_bounded C enumeration).2
    ⟨U, concretePureLensCut_verts_subset hcut, hcut⟩

/-- Unbounded positive correctness: every concrete cut is already in the
ambient powerset by `concretePureLensCut_verts_subset`. -/
theorem checkConcretePureLensExists_eq_true_iff
    (C : AmbientCage G c)
    (enumeration : ConcretePureLensEnumerationComplete C) :
    checkConcretePureLensExists C enumeration = true ↔
      ∃ U, ConcretePureLensCut C U := by
  constructor
  · rintro hcheck
    obtain ⟨U, _, hcut⟩ :=
      (checkConcretePureLensExists_eq_true_iff_bounded C enumeration).1 hcheck
    exact ⟨U, hcut⟩
  · rintro ⟨U, hcut⟩
    exact checkConcretePureLensExists_complete C enumeration hcut

/-- Unbounded negative correctness, suitable for an exhaustive no-split
certificate. -/
theorem checkConcretePureLensExists_eq_false_iff
    (C : AmbientCage G c)
    (enumeration : ConcretePureLensEnumerationComplete C) :
    checkConcretePureLensExists C enumeration = false ↔
      ∀ U, ¬ ConcretePureLensCut C U := by
  constructor
  · intro hfalse U hcut
    exact
      (checkConcretePureLensExists_eq_false_iff_bounded C enumeration).1
        hfalse U (concretePureLensCut_verts_subset hcut) hcut
  · intro hnone
    exact
      (checkConcretePureLensExists_eq_false_iff_bounded C enumeration).2
        (fun U _ hcut => hnone U hcut)

/-- A positive enumeration result supplies the current abstract pure-lens
cage-split interface.  Shore disjointness is derived from the restriction
definitions rather than carried by the Boolean provider. -/
theorem pureLensCageSplit_of_checkConcretePureLensExists
    (F : BankFrame (V := V))
    (C : AmbientCage G c)
    (enumeration : ConcretePureLensEnumerationComplete C)
    (hcheck : checkConcretePureLensExists C enumeration = true) :
    ∃ U, U ⊆ C.verts ∧
      Ell5PureLensCageInterface.PureLensCageSplit
        (Bank F) AmbientCage.Surplus (Balance F) (ProperRelative C)
        C (restrict C U) (restrictCompl C U) := by
  obtain ⟨U, hsub, hcut⟩ :=
    (checkConcretePureLensExists_eq_true_iff_bounded C enumeration).1 hcheck
  exact
    ⟨U, hsub,
      concretePureLensCageSplit F C U hcut.1 hcut.2.1 hcut.2.2
        (restrict_disjoint_restrictCompl C U)⟩

end ConcreteCage
end Ell5
end Erdos23Delta0
