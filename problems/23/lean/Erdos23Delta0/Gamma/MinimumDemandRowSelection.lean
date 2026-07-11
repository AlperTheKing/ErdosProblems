import Erdos23Delta0.Gamma.CheckedRowCompanionBaseTransfer

/-!
# Canonical minimum-demand shortest-row selection

For every bad edge, choose one of its checked shortest rows.  The exact R20
exchange potential is twice the repeated ordered-pair count plus twice the
number of blue edges internal to the selected vertex support but absent from
the selected row-edge support.  This is precisely the number of collision
halves plus endpoint hit-needs used by the transfer matcher.

The finite argmin below supplies a canonical extremal row tuple and its global
optimality theorem.  Hall completeness of that tuple is the remaining
graph-exchange lemma; it is not assumed here.
-/

namespace Erdos23Delta0
namespace Gamma
namespace MinimumDemandRowSelection

open CertGraph

/-- One row index for each bad edge. -/
abbrev RowChoice (bads : List BadEdgeData) :=
  (i : Fin bads.length) -> Fin (bads.get i).rows.length

/-- Every bad edge has at least one row, so the dependent product is nonempty. -/
def RowsNonempty (bads : List BadEdgeData) : Prop :=
  forall i : Fin bads.length, 0 < (bads.get i).rows.length

/-- Literal validation of the complete bad-edge row database. -/
def AllBadsChecked (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) : Prop :=
  bads.all (checkBadEdge G c) = true

/-- The existing bad-edge checker supplies the nonemptiness needed by the
dependent finite row-choice product. -/
theorem rowsNonempty_of_allBadsChecked {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} (h : AllBadsChecked G c bads) :
    RowsNonempty bads := by
  intro i
  have hb := List.all_eq_true.mp h (bads.get i) (List.get_mem bads i)
  unfold checkBadEdge at hb
  simp only [Bool.and_eq_true] at hb
  have hne : (bads.get i).rows ≠ [] := of_decide_eq_true hb.1.2
  exact List.length_pos_of_ne_nil hne

def defaultChoice {bads : List BadEdgeData} (h : RowsNonempty bads) :
    RowChoice bads :=
  fun i => ⟨0, h i⟩

/-- Canonical bad-edge-ordered row references of one choice tuple. -/
def selectedRefs {bads : List BadEdgeData} (omega : RowChoice bads) :
    List RowRef :=
  List.ofFn fun i : Fin bads.length =>
    { badId := i.1, rowIdx := (omega i).1 }

/-- Literal selected rows.  Every reference constructed above is in range. -/
def selectedRows {bads : List BadEdgeData} (omega : RowChoice bads) :
    List Row5 :=
  List.ofFn fun i : Fin bads.length => (bads.get i).rows.get (omega i)

/-- Vertices occurring on at least one selected row. -/
def selectedVertices {bads : List BadEdgeData} (omega : RowChoice bads) :
    List Nat :=
  ((selectedRows omega).flatMap Row5.verts).dedup

/-- The four path edges of a selected length-five row (or all consecutive
edges if the input row is malformed; row validity is checked upstream). -/
def rowPathEdges (row : Row5) : List (Nat × Nat) :=
  (List.zip row.verts row.verts.tail).map fun e => normEdge e.1 e.2

/-- Union of selected row-path edges. -/
def selectedSupport {bads : List BadEdgeData} (omega : RowChoice bads) :
    List (Nat × Nat) :=
  ((selectedRows omega).flatMap rowPathEdges).dedup

/-- Number of selected rows containing both ordered-pair coordinates. -/
def pairCount {bads : List BadEdgeData} (omega : RowChoice bads)
    (x y : Nat) : Nat :=
  ((selectedRows omega).filter fun row =>
    decide (x ∈ row.verts ∧ y ∈ row.verts)).length

/-- Repeated ordered-pair units.  Multiplication by two produces the two
collision halves in the transfer matcher. -/
def collisionUnits (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Nat :=
  ((List.range G.n).map fun x =>
    ((List.range G.n).map fun y => pairCount omega x y - 1).sum).sum

/-- Blue edges internal to the selected vertex support but absent from the
selected row-edge support. -/
def activeEdges (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : List (Nat × Nat) :=
  let vertices := selectedVertices omega
  let support := selectedSupport omega
  G.edges.filter fun e =>
    decide (e.1 ∈ vertices) &&
      decide (e.2 ∈ vertices) &&
      blueb G c e.1 e.2 &&
      !(decide (normEdge e.1 e.2 ∈ support))

/-- Exact number of collision-half and active-endpoint obligations. -/
def obligationScore (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Nat :=
  2 * collisionUnits G omega + 2 * (activeEdges G c omega).length

/-- The canonical row tuple minimizing the exact transfer-obligation count. -/
noncomputable def minDemandChoice (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (h : RowsNonempty bads) :
    {omega : RowChoice bads // forall eta : RowChoice bads,
      obligationScore G c omega <= obligationScore G c eta} := by
  letI : Nonempty (RowChoice bads) := ⟨defaultChoice h⟩
  exact chooseFiniteMinimizer (obligationScore G c)

theorem minDemandChoice_optimal (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (h : RowsNonempty bads)
    (eta : RowChoice bads) :
    obligationScore G c (minDemandChoice G c bads h).1 <=
      obligationScore G c eta :=
  (minDemandChoice G c bads h).2 eta

/-- The selected reference list has exactly one entry per bad edge. -/
theorem selectedRefs_length {bads : List BadEdgeData} (omega : RowChoice bads) :
    (selectedRefs omega).length = bads.length := by
  simp [selectedRefs]

/-- The selected row list has exactly one row per bad edge. -/
theorem selectedRows_length {bads : List BadEdgeData} (omega : RowChoice bads) :
    (selectedRows omega).length = bads.length := by
  simp [selectedRows]

#print axioms minDemandChoice_optimal
#print axioms rowsNonempty_of_allBadsChecked
#print axioms selectedRefs_length
#print axioms selectedRows_length

end MinimumDemandRowSelection
end Gamma
end Erdos23Delta0
