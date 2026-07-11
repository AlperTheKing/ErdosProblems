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
    Fintype (OneRowAlternative omega) := by
  unfold OneRowAlternative
  infer_instance

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

/-- Collision and endpoint-hit cardinalities before they are combined into
the active-scoped obligation score. -/
noncomputable def scopedCollisionScore
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Nat :=
  Fintype.card (ActiveCollisionHalf G c omega)

noncomputable def scopedHitNeedScore
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Nat :=
  Fintype.card (ActiveHitNeed G c omega)

theorem scopedObligationScore_eq_parts
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    scopedObligationScore G c omega =
      scopedCollisionScore G c omega + scopedHitNeedScore G c omega := by
  simp [scopedObligationScore, scopedCollisionScore, scopedHitNeedScore,
    Demand]

noncomputable def oneRowCollisionDelta
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (a : OneRowAlternative omega) : Int :=
  (scopedCollisionScore G c (choiceAfterAlternative omega a) : Int) -
    (scopedCollisionScore G c omega : Int)

noncomputable def oneRowHitNeedDelta
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (a : OneRowAlternative omega) : Int :=
  (scopedHitNeedScore G c (choiceAfterAlternative omega a) : Int) -
    (scopedHitNeedScore G c omega : Int)

noncomputable def oneRowCollisionVariation
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Int :=
  ∑ a : OneRowAlternative omega, oneRowCollisionDelta G c omega a

noncomputable def oneRowHitNeedVariation
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Int :=
  ∑ a : OneRowAlternative omega, oneRowHitNeedDelta G c omega a

theorem oneRowDelta_eq_collision_add_hitNeed
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (a : OneRowAlternative omega) :
    oneRowDelta G c omega a =
      oneRowCollisionDelta G c omega a +
        oneRowHitNeedDelta G c omega a := by
  unfold oneRowDelta oneRowCollisionDelta oneRowHitNeedDelta
  rw [scopedObligationScore_eq_parts, scopedObligationScore_eq_parts]
  push_cast
  ring

theorem oneRowVariation_eq_collision_add_hitNeed
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    oneRowVariation G c omega =
      oneRowCollisionVariation G c omega +
        oneRowHitNeedVariation G c omega := by
  classical
  unfold oneRowVariation oneRowCollisionVariation oneRowHitNeedVariation
  calc
    (∑ a : OneRowAlternative omega, oneRowDelta G c omega a) =
        ∑ a : OneRowAlternative omega,
          (oneRowCollisionDelta G c omega a +
            oneRowHitNeedDelta G c omega a) := by
      apply Finset.sum_congr rfl
      intro a _ha
      exact oneRowDelta_eq_collision_add_hitNeed G c omega a
    _ = _ := Finset.sum_add_distrib

/-- Alternatives for one fixed bad-edge coordinate. -/
abbrev OneCoordinateAlternative {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length) : Type :=
  {replacement : Fin (bads.get i).rows.length // replacement ≠ omega i}

noncomputable def oneCoordinateCollisionVariation
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length) : Int :=
  ∑ q : OneCoordinateAlternative omega i,
    oneRowCollisionDelta G c omega ⟨i, q⟩

noncomputable def oneCoordinateHitNeedVariation
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length) : Int :=
  ∑ q : OneCoordinateAlternative omega i,
    oneRowHitNeedDelta G c omega ⟨i, q⟩

theorem oneRowCollisionVariation_eq_sum_coordinates
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    oneRowCollisionVariation G c omega =
      ∑ i : Fin bads.length, oneCoordinateCollisionVariation G c omega i := by
  classical
  unfold oneRowCollisionVariation oneCoordinateCollisionVariation
  simpa only [OneRowAlternative, OneCoordinateAlternative] using
    (Fintype.sum_sigma
      (fun a : OneRowAlternative omega => oneRowCollisionDelta G c omega a))

theorem oneRowHitNeedVariation_eq_sum_coordinates
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    oneRowHitNeedVariation G c omega =
      ∑ i : Fin bads.length, oneCoordinateHitNeedVariation G c omega i := by
  classical
  unfold oneRowHitNeedVariation oneCoordinateHitNeedVariation
  simpa only [OneRowAlternative, OneCoordinateAlternative] using
    (Fintype.sum_sigma
      (fun a : OneRowAlternative omega => oneRowHitNeedDelta G c omega a))

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

/-- Split form suggested by the exact census.  Collision variation pays the
Hall defect; aggregate endpoint-hit variation is nonpositive. -/
noncomputable def DeficientOwnerShoreCollisionVariationBound
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ (omega : RowChoice bads) (A : Finset (Fin G.n)),
    (scopedOwnerSourceSet G c omega A).card <
        (scopedOwnerDemandSet
          (G := G) (c := c) (omega := omega) A).card →
      oneRowCollisionVariation G c omega ≤
        ((scopedOwnerSourceSet G c omega A).card : Int) -
          ((scopedOwnerDemandSet
            (G := G) (c := c) (omega := omega) A).card : Int)

noncomputable def DeficientOwnerShoreHitNeedVariationNonpositive
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ (omega : RowChoice bads) (A : Finset (Fin G.n)),
    (scopedOwnerSourceSet G c omega A).card <
        (scopedOwnerDemandSet
          (G := G) (c := c) (omega := omega) A).card →
      oneRowHitNeedVariation G c omega ≤ 0

/-- Stronger one-coordinate form seen by the exact gates. -/
noncomputable def DeficientOwnerShoreCoordinateCollisionVariationBound
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ (omega : RowChoice bads) (A : Finset (Fin G.n)),
    (scopedOwnerSourceSet G c omega A).card <
        (scopedOwnerDemandSet
          (G := G) (c := c) (omega := omega) A).card →
      ∀ i : Fin bads.length,
        oneCoordinateCollisionVariation G c omega i ≤
          (Fintype.card (OneCoordinateAlternative omega i) : Int) *
            (((scopedOwnerSourceSet G c omega A).card : Int) -
              ((scopedOwnerDemandSet
                (G := G) (c := c) (omega := omega) A).card : Int))

noncomputable def DeficientOwnerShoreCoordinateHitNeedVariationNonpositive
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ (omega : RowChoice bads) (A : Finset (Fin G.n)),
    (scopedOwnerSourceSet G c omega A).card <
        (scopedOwnerDemandSet
          (G := G) (c := c) (omega := omega) A).card →
      ∀ i : Fin bads.length,
        oneCoordinateHitNeedVariation G c omega i ≤ 0

noncomputable def DeficientOwnerShoreHasNontrivialCoordinate
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ (omega : RowChoice bads) (A : Finset (Fin G.n)),
    (scopedOwnerSourceSet G c omega A).card <
        (scopedOwnerDemandSet
          (G := G) (c := c) (omega := omega) A).card →
      0 < ∑ i : Fin bads.length,
        Fintype.card (OneCoordinateAlternative omega i)

theorem deficientOwnerShoreCollisionVariationBound_of_coordinates
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hcoordinate :
      DeficientOwnerShoreCoordinateCollisionVariationBound G c bads)
    (hnontrivial : DeficientOwnerShoreHasNontrivialCoordinate G c bads) :
    DeficientOwnerShoreCollisionVariationBound G c bads := by
  intro omega A hdefect
  rw [oneRowCollisionVariation_eq_sum_coordinates]
  calc
    (∑ i : Fin bads.length, oneCoordinateCollisionVariation G c omega i) ≤
        ∑ i : Fin bads.length,
          (Fintype.card (OneCoordinateAlternative omega i) : Int) *
            (((scopedOwnerSourceSet G c omega A).card : Int) -
              ((scopedOwnerDemandSet
                (G := G) (c := c) (omega := omega) A).card : Int)) := by
      exact Finset.sum_le_sum fun i _hi => hcoordinate omega A hdefect i
    _ = (∑ i : Fin bads.length,
          (Fintype.card (OneCoordinateAlternative omega i) : Int)) *
            (((scopedOwnerSourceSet G c omega A).card : Int) -
              ((scopedOwnerDemandSet
                (G := G) (c := c) (omega := omega) A).card : Int)) := by
      rw [Finset.sum_mul]
    _ ≤ ((scopedOwnerSourceSet G c omega A).card : Int) -
          ((scopedOwnerDemandSet
            (G := G) (c := c) (omega := omega) A).card : Int) := by
      have hfactor :
          (1 : Int) ≤ ∑ i : Fin bads.length,
            (Fintype.card (OneCoordinateAlternative omega i) : Int) := by
        exact_mod_cast hnontrivial omega A hdefect
      have hrhs :
          ((scopedOwnerSourceSet G c omega A).card : Int) -
              ((scopedOwnerDemandSet
                (G := G) (c := c) (omega := omega) A).card : Int) < 0 := by
        exact sub_neg.mpr (by exact_mod_cast hdefect)
      nlinarith

theorem deficientOwnerShoreHitNeedVariationNonpositive_of_coordinates
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hcoordinate :
      DeficientOwnerShoreCoordinateHitNeedVariationNonpositive G c bads) :
    DeficientOwnerShoreHitNeedVariationNonpositive G c bads := by
  intro omega A hdefect
  rw [oneRowHitNeedVariation_eq_sum_coordinates]
  exact Finset.sum_nonpos fun i _hi => hcoordinate omega A hdefect i

theorem deficientOwnerShoreVariationBound_of_coordinates
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hcollision :
      DeficientOwnerShoreCoordinateCollisionVariationBound G c bads)
    (hhitNeed :
      DeficientOwnerShoreCoordinateHitNeedVariationNonpositive G c bads)
    (hnontrivial : DeficientOwnerShoreHasNontrivialCoordinate G c bads) :
    DeficientOwnerShoreVariationBound G c bads := by
  intro omega A hdefect
  rw [oneRowVariation_eq_collision_add_hitNeed]
  have hcollision' :=
    deficientOwnerShoreCollisionVariationBound_of_coordinates
      G c bads hcollision hnontrivial omega A hdefect
  have hhitNeed' :=
    deficientOwnerShoreHitNeedVariationNonpositive_of_coordinates
      G c bads hhitNeed omega A hdefect
  have hsum := add_le_add hcollision' hhitNeed'
  simpa using hsum

theorem deficientOwnerShoreVariationBound_of_split
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hcollision : DeficientOwnerShoreCollisionVariationBound G c bads)
    (hhitNeed : DeficientOwnerShoreHitNeedVariationNonpositive G c bads) :
    DeficientOwnerShoreVariationBound G c bads := by
  intro omega A hdefect
  rw [oneRowVariation_eq_collision_add_hitNeed]
  have hsum := add_le_add (hcollision omega A hdefect)
    (hhitNeed omega A hdefect)
  simpa using hsum

def RealDeficientOwnerShoreCollisionVariationBound
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    DeficientOwnerShoreCollisionVariationBound G c bads

def RealDeficientOwnerShoreHitNeedVariationNonpositive
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    DeficientOwnerShoreHitNeedVariationNonpositive G c bads

theorem realDeficientOwnerShoreVariationBound_of_split
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hcollision : RealDeficientOwnerShoreCollisionVariationBound G c bads)
    (hhitNeed : RealDeficientOwnerShoreHitNeedVariationNonpositive G c bads) :
    RealDeficientOwnerShoreVariationBound G c bads := by
  intro htri hmax hconn hdb
  exact deficientOwnerShoreVariationBound_of_split G c bads
    (hcollision htri hmax hconn hdb)
    (hhitNeed htri hmax hconn hdb)

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
