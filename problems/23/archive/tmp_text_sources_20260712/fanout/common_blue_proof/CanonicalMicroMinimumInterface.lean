import Erdos23Delta0.Gamma.CommonBlueExtendedMatching

namespace Erdos23Delta0
namespace Gamma
namespace CommonBlueExtendedMatching

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

/-- Exact bank-scale demand cardinality used by the canonical selector. -/
noncomputable def microObligationScore
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Nat :=
  Fintype.card (MicroDemand G c omega)

def IsMicroScoreMinimizer
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Prop :=
  forall eta : RowChoice bads,
    microObligationScore G c omega <= microObligationScore G c eta

/-- A finite global minimizer of the exact bank-scale demand count. -/
noncomputable def minMicroChoice
    (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (hrows : RowsNonempty bads) :
    {omega : RowChoice bads // IsMicroScoreMinimizer G c omega} := by
  letI : Nonempty (RowChoice bads) := ⟨defaultChoice hrows⟩
  exact chooseFiniteMinimizer (microObligationScore G c)

noncomputable def microCanonicalChoice
    (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (hrows : RowsNonempty bads) :
    RowChoice bads :=
  (minMicroChoice G c bads hrows).1

theorem microCanonicalChoice_optimal
    (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (hrows : RowsNonempty bads) :
    IsMicroScoreMinimizer G c (microCanonicalChoice G c bads hrows) :=
  (minMicroChoice G c bads hrows).2

/-- Named mathematical frontier. It is an interface, not an asserted graph
theorem: every exact score minimizer must satisfy the literal micro-Hall
inequalities. -/
def MinimumMicroCommonBlueHall
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  forall omega : RowChoice bads,
    IsMicroScoreMinimizer G c omega -> MicroHallCondition G c omega

/-- Real graph-facing form of the named frontier. -/
def RealMinimumMicroCommonBlueHall
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  checkGraph G = true ->
    TriangleFree G ->
    IsMaxCut G c ->
    BConnected G c ->
    GammaMinimalConnected G c ->
    CompleteShortestRowDB G c bads ->
    MinimumMicroCommonBlueHall G c bads

theorem canonicalMicroHall_of_minimumMicroCommonBlueHall
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hrows : RowsNonempty bads)
    (hminHall : MinimumMicroCommonBlueHall G c bads) :
    MicroHallCondition G c (microCanonicalChoice G c bads hrows) :=
  hminHall (microCanonicalChoice G c bads hrows)
    (microCanonicalChoice_optimal G c bads hrows)

theorem canonicalMicroMatching_of_minimumMicroCommonBlueHall
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hrows : RowsNonempty bads)
    (hminHall : MinimumMicroCommonBlueHall G c bads) :
    Nonempty (MicroMatching G c (microCanonicalChoice G c bads hrows)) := by
  apply (microMatching_nonempty_iff_hall G c
    (microCanonicalChoice G c bads hrows)).2
  exact canonicalMicroHall_of_minimumMicroCommonBlueHall
    G c bads hrows hminHall

theorem realCanonicalMicroMatching_of_minimumMicroCommonBlueHall
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hgraph : checkGraph G = true)
    (htri : TriangleFree G)
    (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hgamma : GammaMinimalConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (hminHall : RealMinimumMicroCommonBlueHall G c bads) :
    Nonempty (MicroMatching G c
      (microCanonicalChoice G c bads hdb.rowsNonempty)) := by
  apply canonicalMicroMatching_of_minimumMicroCommonBlueHall
  exact hminHall hgraph htri hmax hconn hgamma hdb

/-- A zero score is a kernel-side sufficient condition: the domain is empty. -/
theorem microMatching_of_score_zero
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (hzero : microObligationScore G c omega = 0) :
    Nonempty (MicroMatching G c omega) := by
  classical
  haveI : IsEmpty (MicroDemand G c omega) :=
    Fintype.card_eq_zero_iff.mp hzero
  exact ⟨{
    assign := fun d => isEmptyElim d
    injective := fun d => isEmptyElim d
    available := fun d => isEmptyElim d
  }⟩

#print axioms microCanonicalChoice_optimal
#print axioms canonicalMicroMatching_of_minimumMicroCommonBlueHall
#print axioms realCanonicalMicroMatching_of_minimumMicroCommonBlueHall
#print axioms microMatching_of_score_zero

end CommonBlueExtendedMatching
end Gamma
end Erdos23Delta0
