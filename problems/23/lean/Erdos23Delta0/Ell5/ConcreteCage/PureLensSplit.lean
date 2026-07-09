import Erdos23Delta0.Ell5.ConcreteCage.PureSplit
import Erdos23Delta0.Ell5PureLensCageInterface

/-!
# Concrete ell=5 cage bookkeeping: interface assembly

This module packages the concrete cage bookkeeping into the already compiled
`Ell5PureLensCageInterface.PureLensCageSplit` contract.  The remaining
graph-specific work is supplied as explicit hypotheses: properness of the two
descendants, strong atom split, and vertex disjointness of the two descendants.
-/

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} {c : Distances.Cut V}

private theorem diff_subset_finset (A B : Finset V) : A \ B ⊆ A := by
  intro v hv
  exact (Finset.mem_sdiff.mp hv).1

/-- Concrete pure-lens cage split.  The graph-heavy lens facts enter only as
the properness, strong split, and disjointness hypotheses. -/
theorem concretePureLensCageSplit (F : BankFrame (V := V))
    (C : AmbientCage G c) (U : Finset V)
    (hWProper : ProperRelative C (restrict C U))
    (hCProper : ProperRelative C (restrictCompl C U))
    (hStrong : StrongPureLensAtomSplit C U)
    (hDisj : Disjoint (restrict C U).verts (restrictCompl C U).verts) :
    Ell5PureLensCageInterface.PureLensCageSplit
      (Bank F) AmbientCage.Surplus (Balance F) (ProperRelative C)
      C (restrict C U) (restrictCompl C U) := by
  refine
    { balance_eq := ?_
      wProper := hWProper
      cProper := hCProper
      surplusSplit := ?_
      bankSuper := ?_ }
  · intro D
    exact balance_eq_bank_sub_surplus F D
  · exact surplus_split_of_strongPure C U hStrong
  · apply bank_add_le_of_disjoint_subcages F
    · intro t _ ht
      exact subset_trans ht hWProper.verts_subset
    · intro t _ ht
      exact subset_trans ht (diff_subset_finset C.verts U)
    · exact hDisj

/-- Direct ledger-separation output from the concrete split. -/
theorem ledgerSep_of_concretePureLensCageSplit (F : BankFrame (V := V))
    (C : AmbientCage G c) (U : Finset V)
    (hWProper : ProperRelative C (restrict C U))
    (hCProper : ProperRelative C (restrictCompl C U))
    (hStrong : StrongPureLensAtomSplit C U)
    (hDisj : Disjoint (restrict C U).verts (restrictCompl C U).verts) :
    NeutralLensLedger.LedgerSep
      (Balance F) (ProperRelative C) C (restrict C U) (restrictCompl C U)
      (Balance F C - Balance F (restrictCompl C U) - Balance F (restrict C U)) :=
  Ell5PureLensCageInterface.ledgerSep_of_pureLensCageSplit
    (Bank F) AmbientCage.Surplus (Balance F) (ProperRelative C)
    C (restrict C U) (restrictCompl C U)
    (concretePureLensCageSplit F C U hWProper hCProper hStrong hDisj)

end ConcreteCage
end Ell5
end Erdos23Delta0
