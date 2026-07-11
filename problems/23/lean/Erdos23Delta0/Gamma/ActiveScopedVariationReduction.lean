import Erdos23Delta0.Gamma.ActiveScopedOwnerHallReduction

/-!
# Active-scoped one-row variation reduction

The sum of all Hamming-one score changes is an integer.  If that sum is
negative, at least one row replacement strictly lowers the scoped obligation
score.  Thus the real graph frontier can be stated as one scalar averaged
inequality, with no distinguished geometric replacement pattern.
-/

namespace Erdos23Delta0
namespace Gamma
namespace ActiveScopedMinimumExchange

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

attribute [local instance] Classical.propDecidable

abbrev OneRowAlternative {bads : List BadEdgeData}
    (omega : RowChoice bads) : Type :=
  Σ i : Fin bads.length,
    {replacement : Fin (bads.get i).rows.length // replacement ≠ omega i}

noncomputable instance oneRowAlternativeFintype
    {bads : List BadEdgeData} (omega : RowChoice bads) :
    Fintype (OneRowAlternative omega) :=
  Fintype.ofFinite _

def choiceAfterAlternative {bads : List BadEdgeData}
    (omega : RowChoice bads) (a : OneRowAlternative omega) :
    RowChoice bads :=
  replaceOne omega a.1 a.2.1

noncomputable def oneRowDelta
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (a : OneRowAlternative omega) : Int :=
  (scopedObligationScore G c (choiceAfterAlternative omega a) : Int) -
    (scopedObligationScore G c omega : Int)

noncomputable def oneRowVariation
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Int :=
  ∑ a : OneRowAlternative omega, oneRowDelta G c omega a

theorem scopedScoreOneRowDescent_of_variation_neg
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (hnegative : oneRowVariation G c omega < 0) :
    Nonempty (ScopedScoreOneRowDescent G c omega) := by
  classical
  by_contra hnone
  have hdelta : ∀ a : OneRowAlternative omega,
      0 ≤ oneRowDelta G c omega a := by
    intro a
    by_cases hlt :
        scopedObligationScore G c (choiceAfterAlternative omega a) <
          scopedObligationScore G c omega
    · exact False.elim (hnone ⟨{
        index := a.1
        replacement := a.2.1
        changed := a.2.2
        score_drop := hlt
      }⟩)
    · have hle : scopedObligationScore G c omega ≤
          scopedObligationScore G c (choiceAfterAlternative omega a) :=
        Nat.le_of_not_gt hlt
      unfold oneRowDelta
      exact Int.sub_nonneg.mpr (by exact_mod_cast hle)
  have hnonnegative : 0 ≤ oneRowVariation G c omega := by
    unfold oneRowVariation
    exact Finset.sum_nonneg fun a _ha => hdelta a
  exact (not_lt_of_ge hnonnegative) hnegative

def HallFailureHasNegativeOneRowVariation
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ omega : RowChoice bads,
    ¬Nonempty (Matching G c omega) → oneRowVariation G c omega < 0

def RealHallFailureHasNegativeOneRowVariation
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    HallFailureHasNegativeOneRowVariation G c bads

/-- Quantitative owner-shore target.  Every Hall-deficient owner shore pays
its entire cardinal defect in negative total one-row variation. -/
noncomputable def DeficientOwnerShoreVariationBound
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ (omega : RowChoice bads) (A : Finset (Fin G.n)),
    (scopedOwnerSourceSet G c omega A).card <
        (scopedOwnerDemandSet
          (G := G) (c := c) (omega := omega) A).card →
      oneRowVariation G c omega ≤
        ((scopedOwnerSourceSet G c omega A).card : Int) -
          ((scopedOwnerDemandSet
            (G := G) (c := c) (omega := omega) A).card : Int)

noncomputable def RealDeficientOwnerShoreVariationBound
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    DeficientOwnerShoreVariationBound G c bads

theorem hallFailureHasNegativeVariation_of_ownerShoreBound
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hbound : DeficientOwnerShoreVariationBound G c bads) :
    HallFailureHasNegativeOneRowVariation G c bads := by
  intro omega hfailure
  rcases (matching_failure_iff_exists_scopedOwner_defect G c omega).mp
      hfailure with ⟨A, hdefect⟩
  have hvariation := hbound omega A hdefect
  have hrhs :
      ((scopedOwnerSourceSet G c omega A).card : Int) -
          ((scopedOwnerDemandSet
            (G := G) (c := c) (omega := omega) A).card : Int) < 0 := by
    exact sub_neg.mpr (by exact_mod_cast hdefect)
  exact lt_of_le_of_lt hvariation hrhs

theorem realHallFailureHasNegativeVariation_of_ownerShoreBound
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hbound : RealDeficientOwnerShoreVariationBound G c bads) :
    RealHallFailureHasNegativeOneRowVariation G c bads := by
  intro htri hmax hconn hdb
  exact hallFailureHasNegativeVariation_of_ownerShoreBound G c bads
    (hbound htri hmax hconn hdb)

theorem hallFailureHasScopedScoreDescent_of_negativeVariation
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hvariation : HallFailureHasNegativeOneRowVariation G c bads) :
    HallFailureHasScopedScoreOneRowDescent G c bads := by
  intro omega hfailure
  exact scopedScoreOneRowDescent_of_variation_neg G c omega
    (hvariation omega hfailure)

theorem realHallFailureHasScopedScoreDescent_of_negativeVariation
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hvariation : RealHallFailureHasNegativeOneRowVariation G c bads) :
    RealHallFailureHasScopedScoreOneRowDescent G c bads := by
  intro htri hmax hconn hdb
  exact hallFailureHasScopedScoreDescent_of_negativeVariation G c bads
    (hvariation htri hmax hconn hdb)

theorem realMinimumActiveScopedHall_of_negativeVariation
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (hvariation : RealHallFailureHasNegativeOneRowVariation G c bads) :
    MinimumActiveScopedHall G c bads hdb.rowsNonempty := by
  apply realMinimumActiveScopedHall_of_scopedScoreDescent
    G c bads htri hmax hconn hdb
  exact realHallFailureHasScopedScoreDescent_of_negativeVariation
    G c bads hvariation

theorem realMinimumActiveScopedHall_of_ownerShoreVariationBound
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (hbound : RealDeficientOwnerShoreVariationBound G c bads) :
    MinimumActiveScopedHall G c bads hdb.rowsNonempty := by
  apply realMinimumActiveScopedHall_of_negativeVariation
    G c bads htri hmax hconn hdb
  exact realHallFailureHasNegativeVariation_of_ownerShoreBound
    G c bads hbound

end ActiveScopedMinimumExchange
end Gamma
end Erdos23Delta0
