import Erdos23Delta0.Gamma.CheckedC5BaseTransfer

/-!
# Checked row-companion C5-base transfer terminal

The R20 corridor-overload guardrail shows that same-owner and common-neighbor
base transfers are not complete.  The minimal additional direct terminal is a
permanently-free ordered pair whose two vertices occur on selected rows through
the destination owner.  This module checks that terminal against the literal
graph, cut, bad-edge row database, and canonical row selection.

The source slot and global matching layers remain separate.  In particular,
this checker does not assume a synthetic `TransferData` interface.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CheckedRowCompanionBaseTransfer

open CertGraph

/-- One canonical selected row per bad edge.  The list is in bad-edge order. -/
def checkRowSelection (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (selected : List RowRef) : Bool :=
  decide (selected.map RowRef.badId = List.range bads.length) &&
    selected.all fun ref =>
      match bads[ref.badId]? with
      | none => false
      | some b =>
          match b.rows[ref.rowIdx]? with
          | none => false
          | some row => checkRow5 G c b.u b.v row

/-- A pair is permanently free for the selected row tuple when no selected
row contains both vertices.  Missing referenced rows make the check fail. -/
def pairFree (bads : List BadEdgeData) (selected : List RowRef)
    (x y : Nat) : Bool :=
  selected.all fun ref =>
    match getRow bads ref with
    | none => false
    | some row => decide (¬(x ∈ row.verts ∧ y ∈ row.verts))

/-- A row reference witnesses that `source` is a row companion of `owner`. -/
def RowWitness (bads : List BadEdgeData) (ref : RowRef)
    (owner source : Nat) : Prop :=
  match getRow bads ref with
  | none => False
  | some row => owner ∈ row.verts ∧ source ∈ row.verts

instance rowWitnessDecidable (bads : List BadEdgeData) (ref : RowRef)
    (owner source : Nat) : Decidable (RowWitness bads ref owner source) := by
  unfold RowWitness
  cases h : getRow bads ref with
  | none => exact isFalse (fun hFalse => hFalse)
  | some row => exact inferInstance

/-- Literal row-companion transfer data. -/
structure TerminalData where
  sourceX : Nat
  sourceY : Nat
  owner : Nat
  leftRow : RowRef
  rightRow : RowRef
deriving Repr, DecidableEq

namespace TerminalData

def switch (T : TerminalData) : List Nat := [T.sourceX, T.sourceY]

/-- Decidable proposition checked by the certificate. -/
def RawValid (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (selected : List RowRef) (activeVertices : List Nat)
    (T : TerminalData) : Prop :=
  checkRowSelection G c bads selected = true ∧
    T.sourceX < G.n ∧
    T.sourceY < G.n ∧
    T.owner < G.n ∧
    T.sourceX ≠ T.sourceY ∧
    T.leftRow ∈ selected ∧
    T.rightRow ∈ selected ∧
    RowWitness bads T.leftRow T.owner T.sourceX ∧
    RowWitness bads T.rightRow T.owner T.sourceY ∧
    pairFree bads selected T.sourceX T.sourceY = true ∧
    0 ≤ sigma G c T.switch ∧
    T.owner ∈ activeVertices

instance rawValidDecidable (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (selected : List RowRef)
    (activeVertices : List Nat) (T : TerminalData) :
    Decidable (T.RawValid G c bads selected activeVertices) := by
  unfold RawValid
  infer_instance

/-- Kernel-replayable row-companion terminal checker. -/
def check (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (selected : List RowRef) (activeVertices : List Nat)
    (T : TerminalData) : Bool :=
  decide (T.RawValid G c bads selected activeVertices)

theorem check_eq_true_iff (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (selected : List RowRef)
    (activeVertices : List Nat) (T : TerminalData) :
    T.check G c bads selected activeVertices = true ↔
      T.RawValid G c bads selected activeVertices := by
  simp [check]

/-- Named proof object consumed by transfer-matching soundness. -/
structure CheckedRowCompanionBaseTerminal
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (selected : List RowRef) (activeVertices : List Nat)
    (T : TerminalData) : Prop where
  selection_valid : checkRowSelection G c bads selected = true
  sourceX_lt : T.sourceX < G.n
  sourceY_lt : T.sourceY < G.n
  owner_lt : T.owner < G.n
  source_distinct : T.sourceX ≠ T.sourceY
  left_selected : T.leftRow ∈ selected
  right_selected : T.rightRow ∈ selected
  owner_left : RowWitness bads T.leftRow T.owner T.sourceX
  owner_right : RowWitness bads T.rightRow T.owner T.sourceY
  source_free : pairFree bads selected T.sourceX T.sourceY = true
  loss_nonneg : 0 ≤ sigma G c T.switch
  owner_active : T.owner ∈ activeVertices

/-- A passing Boolean check constructs the named terminal proof object. -/
theorem checked_of_check_eq_true
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {selected : List RowRef} {activeVertices : List Nat} {T : TerminalData}
    (h : T.check G c bads selected activeVertices = true) :
    CheckedRowCompanionBaseTerminal G c bads selected activeVertices T := by
  have hv := (T.check_eq_true_iff G c bads selected activeVertices).mp h
  rcases hv with
    ⟨hselection, hx, hy, ho, hxy, hleft, hright, hwleft, hwright,
      hfree, hloss, hactive⟩
  exact ⟨hselection, hx, hy, ho, hxy, hleft, hright, hwleft, hwright,
    hfree, hloss, hactive⟩

/-- Conversely, the proof object replays through the Boolean checker. -/
theorem check_eq_true_of_checked
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {selected : List RowRef} {activeVertices : List Nat} {T : TerminalData}
    (h : CheckedRowCompanionBaseTerminal G c bads selected activeVertices T) :
    T.check G c bads selected activeVertices = true := by
  apply (T.check_eq_true_iff G c bads selected activeVertices).mpr
  exact ⟨h.selection_valid, h.sourceX_lt, h.sourceY_lt, h.owner_lt,
    h.source_distinct, h.left_selected, h.right_selected, h.owner_left,
    h.owner_right, h.source_free, h.loss_nonneg, h.owner_active⟩

theorem pairFree_not_both_mem
    {bads : List BadEdgeData} {selected : List RowRef} {x y : Nat}
    (hfree : pairFree bads selected x y = true)
    {ref : RowRef} (href : ref ∈ selected) {row : Row5}
    (hrow : getRow bads ref = some row) :
    ¬(x ∈ row.verts ∧ y ∈ row.verts) := by
  unfold pairFree at hfree
  have hitem := List.all_eq_true.mp hfree ref href
  rw [hrow] at hitem
  exact of_decide_eq_true hitem

/-- Freeness forces the two companion witnesses to use distinct selected
rows, matching the geometric interpretation of the R20 terminal. -/
theorem companion_rows_distinct
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {selected : List RowRef} {activeVertices : List Nat} {T : TerminalData}
    (h : CheckedRowCompanionBaseTerminal G c bads selected activeVertices T) :
    T.leftRow ≠ T.rightRow := by
  intro heq
  have hleft := h.owner_left
  have hright := h.owner_right
  unfold RowWitness at hleft hright
  generalize hget : getRow bads T.leftRow = rowOption at hleft
  cases rowOption with
  | none => simp at hleft
  | some row =>
      have hgetRight : getRow bads T.rightRow = some row := by
        simpa [heq] using hget
      rw [hgetRight] at hright
      have hnot := pairFree_not_both_mem h.source_free h.left_selected hget
      exact hnot ⟨hleft.2, hright.2⟩

#print axioms TerminalData.check_eq_true_iff
#print axioms TerminalData.checked_of_check_eq_true
#print axioms TerminalData.check_eq_true_of_checked
#print axioms TerminalData.companion_rows_distinct

end TerminalData

end CheckedRowCompanionBaseTransfer
end Gamma
end Erdos23Delta0
