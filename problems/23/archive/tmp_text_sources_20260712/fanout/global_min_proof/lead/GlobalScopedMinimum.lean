import Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

/-!
The exact finite-minimum wrapper surviving the R29 Hamming-one falsifier.
The only open input is an unbounded simultaneous scoped-score descent.
-/

namespace Erdos23Delta0
namespace Gamma
namespace ActiveScopedMinimumExchange

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

/-- A Hall-failing row tuple has some lower-scoring row tuple.  There is no
bound on the number of changed coordinates. -/
def HallFailureHasGlobalScopedScoreDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  forall omega : RowChoice bads,
    Not (Nonempty (Matching G c omega)) ->
      exists eta : RowChoice bads,
        scopedObligationScore G c eta < scopedObligationScore G c omega

def RealHallFailureHasGlobalScopedScoreDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G ->
    IsMaxCut G c ->
    BConnected G c ->
    CompleteShortestRowDB G c bads ->
    HallFailureHasGlobalScopedScoreDescent G c bads

/-- Every row tuple that globally minimizes the active-scoped demand
cardinality has a scoped matching. -/
def AllGlobalScopedMinimaHall
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  forall omega : RowChoice bads,
    (forall eta : RowChoice bads,
      scopedObligationScore G c omega <= scopedObligationScore G c eta) ->
    Nonempty (Matching G c omega)

/-- On the finite row-choice space, the unbounded descent form is exactly the
statement that no scoped Hall failure is a global scoped-score minimizer. -/
theorem hallFailureHasGlobalScopedScoreDescent_iff_allGlobalScopedMinimaHall
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) :
    HallFailureHasGlobalScopedScoreDescent G c bads <->
      AllGlobalScopedMinimaHall G c bads := by
  constructor
  · intro hdescent omega hmin
    by_contra hmatching
    obtain ⟨eta, hlt⟩ := hdescent omega hmatching
    exact (Nat.not_lt_of_ge (hmin eta)) hlt
  · intro hhall omega hmatching
    by_contra hnoLower
    have hmin : forall eta : RowChoice bads,
        scopedObligationScore G c omega <=
          scopedObligationScore G c eta := by
      intro eta
      apply Nat.le_of_not_gt
      intro hlt
      exact hnoLower ⟨eta, hlt⟩
    exact hmatching (hhall omega hmin)

/-- The canonical global scoped-score minimizer satisfies scoped Hall as soon
as every scoped Hall failure has an unbounded simultaneous descent. -/
theorem minimumActiveScopedHall_of_globalScopedScoreDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hrows : RowsNonempty bads)
    (hdescent : HallFailureHasGlobalScopedScoreDescent G c bads) :
    MinimumActiveScopedHall G c bads hrows := by
  unfold MinimumActiveScopedHall
  by_contra hmatching
  let omega := scopedCanonicalChoice G c bads hrows
  obtain ⟨eta, hlt⟩ := hdescent omega hmatching
  have hmin := scopedCanonicalChoice_optimal G c bads hrows eta
  exact (Nat.not_lt_of_ge hmin) hlt

theorem realMinimumActiveScopedHall_of_globalScopedScoreDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (hdescent : RealHallFailureHasGlobalScopedScoreDescent G c bads) :
    MinimumActiveScopedHall G c bads hdb.rowsNonempty := by
  apply minimumActiveScopedHall_of_globalScopedScoreDescent
  exact hdescent htri hmax hconn hdb

#print axioms minimumActiveScopedHall_of_globalScopedScoreDescent
#print axioms realMinimumActiveScopedHall_of_globalScopedScoreDescent
#print axioms hallFailureHasGlobalScopedScoreDescent_iff_allGlobalScopedMinimaHall

end ActiveScopedMinimumExchange
end Gamma
end Erdos23Delta0
