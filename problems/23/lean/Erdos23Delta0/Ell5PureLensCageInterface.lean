import Erdos23Delta0.Ell5LensStatement
import Erdos23Delta0.Ell5GapLemmas

/-!
# Pure-lens cage split interface

This module turns the pure balanced-neutral lens proof sketch into a compiled
contract. It does not define the eventual graph/rowDB cage model. Instead, it
records the exact algebraic fields that such a model must supply, and proves
that those fields imply `Ell5LensStatement.PureLensLedgerSeparation`.
-/

namespace Erdos23Delta0
namespace Ell5PureLensCageInterface

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The exact cage-model split obligations needed by the pure lens branch.

The future concrete cage model must provide `W` and `C'` as proper ambient
prunable descendants, define `Balance = Bank - Surplus`, prove surplus splits
across the pure lens pruning, and prove bank superadditivity. -/
structure PureLensCageSplit {γ : Type*} (Bank Surplus Balance : γ -> ℚ)
    (Proper : γ -> Prop) (C W C' : γ) : Prop where
  balance_eq : ∀ D, Balance D = Bank D - Surplus D
  wProper : Proper W
  cProper : Proper C'
  surplusSplit : Surplus C = Surplus W + Surplus C'
  bankSuper : Bank W + Bank C' <= Bank C

/-- A `PureLensCageSplit` produces the abstract ledger separation used by the
minimal-negative cage lever. -/
theorem ledgerSep_of_pureLensCageSplit {γ : Type*}
    (Bank Surplus Balance : γ -> ℚ) (Proper : γ -> Prop) (C W C' : γ)
    (hSplit : PureLensCageSplit Bank Surplus Balance Proper C W C') :
    NeutralLensLedger.LedgerSep Balance Proper C W C'
      (Balance C - Balance C' - Balance W) :=
  Ell5GapLemmas.pure_lens_ledgerSep Bank Surplus Balance Proper C W C'
    hSplit.balance_eq hSplit.wProper hSplit.cProper hSplit.surplusSplit hSplit.bankSuper

/-- The same split is a `LensReducible` witness in the statement module's
dichotomy vocabulary. -/
theorem lensReducible_of_pureLensCageSplit {γ : Type*}
    (Bank Surplus Balance : γ -> ℚ) (Proper : γ -> Prop) (C W C' : γ)
    (hSplit : PureLensCageSplit Bank Surplus Balance Proper C W C') :
    Ell5LensStatement.LensReducible Balance Proper C := by
  refine ⟨W, C', Balance C - Balance C' - Balance W, ?_⟩
  exact ledgerSep_of_pureLensCageSplit Bank Surplus Balance Proper C W C' hSplit

/-- T8 interface theorem: once a concrete pure-lens cage split provider exists,
the open pure-case Prop in `Ell5LensStatement` follows. -/
theorem pureLensLedgerSeparation_of_splitProvider {γ : Type*}
    (Bank Surplus Balance : γ -> ℚ) (Proper : γ -> Prop) (C : γ)
    (G : SimpleGraph V) [Fintype G.edgeSet] (c : Distances.Cut V)
    (S : Finset (Ell5AtomBase.Ell5Atom (Distances.blueGraph G c)))
    (pair : Ell5LensStatement.SharedSupportPair (Distances.blueGraph G c))
    (lens : Ell5LensStatement.BalancedNeutralLens G c pair)
    (provide :
      Ell5LensStatement.IsPureLens G c S pair lens ->
        ∃ W C', PureLensCageSplit Bank Surplus Balance Proper C W C') :
    Ell5LensStatement.PureLensLedgerSeparation Balance Proper C G c S pair lens := by
  intro hpure
  rcases provide hpure with ⟨W, C', hSplit⟩
  exact lensReducible_of_pureLensCageSplit Bank Surplus Balance Proper C W C' hSplit

/-- Direct consumption form for the pure branch in a minimal-negative cage. -/
theorem no_pure_lens_of_splitProvider_in_minNeg {γ : Type*}
    (Bank Surplus Balance : γ -> ℚ) (Proper : γ -> Prop) (C : γ)
    (G : SimpleGraph V) [Fintype G.edgeSet] (c : Distances.Cut V)
    (S : Finset (Ell5AtomBase.Ell5Atom (Distances.blueGraph G c)))
    (pair : Ell5LensStatement.SharedSupportPair (Distances.blueGraph G c))
    (lens : Ell5LensStatement.BalancedNeutralLens G c pair)
    (hCneg : Balance C < 0)
    (hMin : ∀ D, Proper D -> 0 <= Balance D)
    (provide :
      Ell5LensStatement.IsPureLens G c S pair lens ->
        ∃ W C', PureLensCageSplit Bank Surplus Balance Proper C W C')
    (hpure : Ell5LensStatement.IsPureLens G c S pair lens) :
    False := by
  have hSep :
      Ell5LensStatement.PureLensLedgerSeparation Balance Proper C G c S pair lens :=
    pureLensLedgerSeparation_of_splitProvider Bank Surplus Balance Proper C G c S pair lens provide
  exact Ell5LensStatement.pure_lens_impossible_in_minNeg Balance Proper C G c S pair lens hCneg hMin hpure hSep

end Ell5PureLensCageInterface
end Erdos23Delta0
