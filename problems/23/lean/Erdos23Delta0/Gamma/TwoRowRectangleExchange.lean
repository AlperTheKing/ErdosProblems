import Erdos23Delta0.Gamma.MinimumDemandCollisionHall

/-!
# Two-row rectangle exchanges

The exact N<=10 gate shows that every matching failure without a one-row
descent is repaired by changing two rows while preserving, at each of the five
path positions, the unordered pair of vertices across those rows.  This module
isolates the dependent row-update bookkeeping and reduces such a checked
rectangle to `HasTwoRowImprovement`.
-/

namespace Erdos23Delta0
namespace Gamma
namespace TwoRowRectangleExchange

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

/-- Replace at most two coordinates of a dependent shortest-row tuple. -/
def replaceTwo {bads : List BadEdgeData} (omega : RowChoice bads)
    (left right : Fin bads.length)
    (newLeft : Fin (bads.get left).rows.length)
    (newRight : Fin (bads.get right).rows.length) : RowChoice bads :=
  fun i =>
    if hleft : i = left then
      hleft ▸ newLeft
    else if hright : i = right then
      hright ▸ newRight
    else
      omega i

theorem replaceTwo_eq_of_ne
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (left right i : Fin bads.length)
    (newLeft : Fin (bads.get left).rows.length)
    (newRight : Fin (bads.get right).rows.length)
    (hil : i ≠ left) (hir : i ≠ right) :
    replaceTwo omega left right newLeft newRight i = omega i := by
  simp [replaceTwo, hil, hir]

/-- A two-coordinate replacement has Hamming distance at most two. -/
theorem disagreementCount_replaceTwo_le_two
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (left right : Fin bads.length)
    (newLeft : Fin (bads.get left).rows.length)
    (newRight : Fin (bads.get right).rows.length) :
    disagreementCount omega
      (replaceTwo omega left right newLeft newRight) ≤ 2 := by
  unfold disagreementCount
  have hsubset :
      (Finset.univ.filter fun i : Fin bads.length =>
        omega i ≠ replaceTwo omega left right newLeft newRight i) ⊆
        {left, right} := by
    intro i hi
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hi
    simp only [Finset.mem_insert, Finset.mem_singleton]
    by_contra hnot
    push_neg at hnot
    exact hi (replaceTwo_eq_of_ne omega left right i newLeft newRight
      hnot.1 hnot.2).symm
  calc
    (Finset.univ.filter fun i : Fin bads.length =>
      omega i ≠ replaceTwo omega left right newLeft newRight i).card
        ≤ ({left, right} : Finset (Fin bads.length)).card :=
          Finset.card_le_card hsubset
    _ ≤ 2 := Finset.card_le_two

/-- Equality of unordered two-element columns, allowing either no swap or a
swap between the two rows. -/
def PairPreserved (a b c d : Nat) : Prop :=
  (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/-- Every path-position column is preserved as an unordered pair. -/
def ColumnsPreserved (oldLeft oldRight newLeft newRight : Row5) : Prop :=
  ∀ k : Fin 5,
    PairPreserved
      (oldLeft.verts.getD k.1 0) (oldRight.verts.getD k.1 0)
      (newLeft.verts.getD k.1 0) (newRight.verts.getD k.1 0)

/-- The score arithmetic used by every observed rectangle atom. -/
theorem obligationScore_lt_of_collision_noninc_active_lt
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega eta : RowChoice bads}
    (hcollision : collisionUnits G eta ≤ collisionUnits G omega)
    (hactive : (activeEdges G c eta).length < (activeEdges G c omega).length) :
    obligationScore G c eta < obligationScore G c omega := by
  unfold obligationScore
  omega

/-- Strong rectangle atom isolated by the exact gate: column pairs are
preserved, collision load does not increase, and at least one active blue edge
disappears. -/
structure MonotoneRectangleDescent (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type where
  left : Fin bads.length
  right : Fin bads.length
  left_ne_right : left ≠ right
  newLeft : Fin (bads.get left).rows.length
  newRight : Fin (bads.get right).rows.length
  columns : ColumnsPreserved
    ((bads.get left).rows.get (omega left))
    ((bads.get right).rows.get (omega right))
    ((bads.get left).rows.get newLeft)
    ((bads.get right).rows.get newRight)
  collision_noninc :
    collisionUnits G (replaceTwo omega left right newLeft newRight) ≤
      collisionUnits G omega
  active_drop :
    (activeEdges G c (replaceTwo omega left right newLeft newRight)).length <
      (activeEdges G c omega).length

/-- A literal two-row rectangle replacement in the complete row database. -/
structure RectangleImprovement (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type where
  left : Fin bads.length
  right : Fin bads.length
  left_ne_right : left ≠ right
  newLeft : Fin (bads.get left).rows.length
  newRight : Fin (bads.get right).rows.length
  columns : ColumnsPreserved
    ((bads.get left).rows.get (omega left))
    ((bads.get right).rows.get (omega right))
    ((bads.get left).rows.get newLeft)
    ((bads.get right).rows.get newRight)
  score_drop :
    obligationScore G c (replaceTwo omega left right newLeft newRight) <
      obligationScore G c omega

def MonotoneRectangleDescent.toImprovement
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads}
    (R : MonotoneRectangleDescent G c omega) :
    RectangleImprovement G c omega where
  left := R.left
  right := R.right
  left_ne_right := R.left_ne_right
  newLeft := R.newLeft
  newRight := R.newRight
  columns := R.columns
  score_drop := obligationScore_lt_of_collision_noninc_active_lt
    R.collision_noninc R.active_drop

/-- Once the graph argument supplies a strict rectangle, all dependent-update
and Hamming-distance obligations are automatic. -/
theorem hasTwoRowImprovement_of_rectangle
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads}
    (R : RectangleImprovement G c omega) :
    HasTwoRowImprovement G c omega := by
  refine ⟨replaceTwo omega R.left R.right R.newLeft R.newRight, ?_, R.score_drop⟩
  exact disagreementCount_replaceTwo_le_two
    omega R.left R.right R.newLeft R.newRight

theorem hasTwoRowImprovement_of_monotoneRectangle
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads}
    (R : MonotoneRectangleDescent G c omega) :
    HasTwoRowImprovement G c omega :=
  hasTwoRowImprovement_of_rectangle R.toImprovement

/-- A direct strict descent changing one selected row. -/
structure OneRowImprovement (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type where
  index : Fin bads.length
  replacement : Fin (bads.get index).rows.length
  score_drop :
    obligationScore G c
        (replaceTwo omega index index replacement replacement) <
      obligationScore G c omega

/-- The exact descent alternatives surviving the complete N<=10 gate. -/
inductive DescentCertificate (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type
  | one (R : OneRowImprovement G c omega)
  | rectangle (R : MonotoneRectangleDescent G c omega)

theorem hasTwoRowImprovement_of_descentCertificate
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads}
    (D : DescentCertificate G c omega) :
    HasTwoRowImprovement G c omega := by
  cases D with
  | one R =>
      refine ⟨replaceTwo omega R.index R.index R.replacement R.replacement,
        ?_, R.score_drop⟩
      exact disagreementCount_replaceTwo_le_two
        omega R.index R.index R.replacement R.replacement
  | rectangle R =>
      exact hasTwoRowImprovement_of_monotoneRectangle R

/-- Sharp remaining exchange statement: every failed collision matching emits
either a direct one-row descent or the monotone rectangle atom. -/
def HallFailureHasDescent (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) : Prop :=
  ∀ omega : RowChoice bads,
    ¬Nonempty (CollisionMatching G c omega) →
      Nonempty (DescentCertificate G c omega)

/-- Real semantic form of the sole exchange lemma. -/
def RealHallFailureHasDescent (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    HallFailureHasDescent G c bads

theorem twoRowExchangeComplete_of_hallFailureHasDescent
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (h : HallFailureHasDescent G c bads) :
    TwoRowExchangeComplete G c bads := by
  intro omega hmatching
  obtain ⟨D⟩ := h omega hmatching
  exact hasTwoRowImprovement_of_descentCertificate D

/-- Final finite-choice/Hall reduction from the sharp real descent lemma. -/
theorem realMinimumDemandCollisionHall_of_descent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (hdescent : RealHallFailureHasDescent G c bads) :
    MinimumDemandCollisionHall G c bads hdb.rowsNonempty := by
  apply minimumDemandCollisionHall_of_twoRowExchange
  apply twoRowExchangeComplete_of_hallFailureHasDescent
  exact hdescent htri hmax hconn hdb

#print axioms disagreementCount_replaceTwo_le_two
#print axioms hasTwoRowImprovement_of_rectangle
#print axioms obligationScore_lt_of_collision_noninc_active_lt
#print axioms hasTwoRowImprovement_of_monotoneRectangle
#print axioms hasTwoRowImprovement_of_descentCertificate
#print axioms twoRowExchangeComplete_of_hallFailureHasDescent
#print axioms realMinimumDemandCollisionHall_of_descent

end TwoRowRectangleExchange
end Gamma
end Erdos23Delta0
