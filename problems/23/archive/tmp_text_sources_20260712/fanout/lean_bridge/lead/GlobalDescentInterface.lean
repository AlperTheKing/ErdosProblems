import Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

namespace Erdos23Delta0
namespace Gamma
namespace ActiveScopedMinimumExchange

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

/-- A failed active-scoped matching admits an arbitrary, not necessarily
Hamming-one, row tuple with strictly smaller scoped obligation score. -/
def HallFailureHasScopedScoreGlobalDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  forall omega : RowChoice bads,
    ¬Nonempty (Matching G c omega) ->
      Exists fun eta : RowChoice bads =>
        scopedObligationScore G c eta < scopedObligationScore G c omega

def RealHallFailureHasScopedScoreGlobalDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G ->
    IsMaxCut G c ->
    BConnected G c ->
    CompleteShortestRowDB G c bads ->
    HallFailureHasScopedScoreGlobalDescent G c bads

/-- Equivalent no-failing-global-minimum formulation. -/
def EveryScopedScoreMinimizerHasMatching
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  forall omega : RowChoice bads,
    (forall eta : RowChoice bads,
      scopedObligationScore G c omega <= scopedObligationScore G c eta) ->
    Nonempty (Matching G c omega)

theorem globalDescent_iff_everyMinimizerHasMatching
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) :
    HallFailureHasScopedScoreGlobalDescent G c bads <->
      EveryScopedScoreMinimizerHasMatching G c bads := by
  constructor
  · intro hdescent omega hminimum
    by_contra hmatching
    obtain ⟨eta, hlt⟩ := hdescent omega hmatching
    exact (Nat.not_lt_of_ge (hminimum eta)) hlt
  · intro hminimum omega hmatching
    by_contra hlower
    have homegaMinimum : forall eta : RowChoice bads,
        scopedObligationScore G c omega <= scopedObligationScore G c eta := by
      intro eta
      apply Nat.le_of_not_gt
      intro hlt
      exact hlower ⟨eta, hlt⟩
    exact hmatching (hminimum omega homegaMinimum)

theorem minimumActiveScopedHall_of_globalDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hrows : RowsNonempty bads)
    (hdescent : HallFailureHasScopedScoreGlobalDescent G c bads) :
    MinimumActiveScopedHall G c bads hrows := by
  unfold MinimumActiveScopedHall
  by_contra hmatching
  let omega := scopedCanonicalChoice G c bads hrows
  obtain ⟨eta, hlt⟩ := hdescent omega hmatching
  have hmin := scopedCanonicalChoice_optimal G c bads hrows eta
  exact (Nat.not_lt_of_ge hmin) hlt

theorem realMinimumActiveScopedHall_of_globalDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (hdescent : RealHallFailureHasScopedScoreGlobalDescent G c bads) :
    MinimumActiveScopedHall G c bads hdb.rowsNonempty := by
  apply minimumActiveScopedHall_of_globalDescent
  exact hdescent htri hmax hconn hdb

end ActiveScopedMinimumExchange
end Gamma
end Erdos23Delta0
