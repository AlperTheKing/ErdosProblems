import Erdos23Delta0.Gamma.MinimumDemandRowSelection

/-!
# Collision coverage potential

The repeated-pair term in the canonical row-selection objective is exactly
total ordered-pair incidence minus the number of ordered pairs covered at
least once.  This file records that identity in the literal `GraphData`
model and converts strict score descent, whenever total incidence is fixed,
into a strict covered-pair gain after paying the active-edge change.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CollisionCoveragePotential

open CertGraph
open MinimumDemandRowSelection

/-- Number of in-range ordered vertex pairs covered by at least one selected
row.  Diagonal pairs are included, exactly as in `pairCount`. -/
def coveredPairUnits (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Nat :=
  ((List.range G.n).map fun x =>
    ((List.range G.n).map fun y =>
      if 0 < pairCount omega x y then 1 else 0).sum).sum

/-- Total selected-row incidence on in-range ordered vertex pairs. -/
def totalPairIncidences (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Nat :=
  ((List.range G.n).map fun x =>
    ((List.range G.n).map fun y => pairCount omega x y).sum).sum

private def badIndices (bads : List BadEdgeData) :
    List (Fin bads.length) :=
  List.ofFn fun i => i

private theorem length_filter_decide_eq_sum {α : Type*} (xs : List α)
    (p : α → Prop) [DecidablePred p] :
    (xs.filter fun a => decide (p a)).length =
      (xs.map fun a => if p a then 1 else 0).sum := by
  induction xs with
  | nil => simp
  | cons a xs ih =>
      by_cases hp : p a <;> simp [hp, ih, Nat.add_comm]

/-- Indexed form of the literal filtered-list pair count. -/
theorem pairCount_eq_sum_indicator {bads : List BadEdgeData}
    (omega : RowChoice bads) (x y : Nat) :
    pairCount omega x y =
      (List.ofFn fun i : Fin bads.length =>
        if x ∈ ((bads.get i).rows.get (omega i)).verts ∧
            y ∈ ((bads.get i).rows.get (omega i)).verts
        then 1 else 0).sum := by
  classical
  unfold pairCount
  rw [length_filter_decide_eq_sum]
  unfold selectedRows
  rw [List.map_ofFn]
  apply congrArg List.sum
  apply congrArg List.ofFn
  funext i
  rfl

theorem pairCount_eq_badIndices_sum {bads : List BadEdgeData}
    (omega : RowChoice bads) (x y : Nat) :
    pairCount omega x y =
      ((badIndices bads).map fun i =>
        if x ∈ ((bads.get i).rows.get (omega i)).verts ∧
            y ∈ ((bads.get i).rows.get (omega i)).verts
        then 1 else 0).sum := by
  rw [pairCount_eq_sum_indicator]
  unfold badIndices
  rw [List.map_ofFn]
  apply congrArg List.sum
  apply congrArg List.ofFn
  funext i
  rfl

/-- Every selected row is one of the rows validated by `AllBadsChecked`. -/
theorem selectedRow_checked {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} (hchecked : AllBadsChecked G c bads)
    (omega : RowChoice bads) (i : Fin bads.length) :
    checkRow5 G c (bads.get i).u (bads.get i).v
      ((bads.get i).rows.get (omega i)) = true := by
  have hb := List.all_eq_true.mp hchecked (bads.get i) (List.get_mem bads i)
  unfold checkBadEdge at hb
  simp only [Bool.and_eq_true] at hb
  exact List.all_eq_true.mp hb.2 _
    (List.get_mem (bads.get i).rows (omega i))

theorem selectedRow_length_five {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} (hchecked : AllBadsChecked G c bads)
    (omega : RowChoice bads) (i : Fin bads.length) :
    (((bads.get i).rows.get (omega i)).verts).length = 5 := by
  have hr := selectedRow_checked hchecked omega i
  unfold checkRow5 at hr
  simp only [Bool.and_eq_true] at hr
  have hlen : decide
      ((((bads.get i).rows.get (omega i)).verts).length = 5) = true := by
    aesop
  exact of_decide_eq_true hlen

theorem selectedRow_nodup {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} (hchecked : AllBadsChecked G c bads)
    (omega : RowChoice bads) (i : Fin bads.length) :
    (((bads.get i).rows.get (omega i)).verts).Nodup := by
  have hr := selectedRow_checked hchecked omega i
  unfold checkRow5 at hr
  simp only [Bool.and_eq_true] at hr
  have hnd : decide
      (((bads.get i).rows.get (omega i)).verts).Nodup = true := by
    aesop
  exact of_decide_eq_true hnd

theorem selectedRow_vertex_lt {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} (hchecked : AllBadsChecked G c bads)
    (omega : RowChoice bads) (i : Fin bads.length)
    (x : Nat) (hx : x ∈ ((bads.get i).rows.get (omega i)).verts) :
    x < G.n := by
  have hr := selectedRow_checked hchecked omega i
  unfold checkRow5 at hr
  simp only [Bool.and_eq_true] at hr
  have hall :
      (((bads.get i).rows.get (omega i)).verts).all
        (fun w => decide (w < G.n)) = true := by
    aesop
  have hxtrue := List.all_eq_true.mp hall x hx
  exact of_decide_eq_true hxtrue

private theorem sub_one_add_positiveUnit (n : Nat) :
    (n - 1) + (if 0 < n then 1 else 0) = n := by
  by_cases h : 0 < n
  · simp only [if_pos h]
    omega
  · have hn : n = 0 := Nat.eq_zero_of_not_pos h
    simp [hn]

private theorem sum_add_of_pointwise {α : Type*} (xs : List α)
    (f g h : α → Nat) (hpoint : ∀ x, f x + g x = h x) :
    (xs.map f).sum + (xs.map g).sum = (xs.map h).sum := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      simp only [List.map_cons, List.sum_cons]
      have hx := hpoint x
      omega

private theorem sum_comm_lists {α β : Type*} (xs : List α) (ys : List β)
    (f : α → β → Nat) :
    (xs.map fun x => (ys.map fun y => f x y).sum).sum =
      (ys.map fun y => (xs.map fun x => f x y).sum).sum := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      simp only [List.map_cons, List.sum_cons]
      rw [ih]
      exact sum_add_of_pointwise ys
        (fun y => f x y)
        (fun y => (xs.map fun z => f z y).sum)
        (fun y => f x y + (xs.map fun z => f z y).sum)
        (fun _ => rfl)

private theorem filter_range_card_eq_length (n : Nat) (vs : List Nat)
    (hnd : vs.Nodup) (hlt : ∀ x ∈ vs, x < n) :
    ((List.range n).filter fun x => decide (x ∈ vs)).length = vs.length := by
  have hrnd : (List.range n).Nodup := List.nodup_range
  have hfnd : ((List.range n).filter fun x => decide (x ∈ vs)).Nodup :=
    hrnd.filter _
  rw [← List.toFinset_card_of_nodup hfnd,
    ← List.toFinset_card_of_nodup hnd]
  congr 1
  ext x
  simp only [List.mem_toFinset, List.mem_filter, List.mem_range]
  constructor
  · exact fun h => of_decide_eq_true h.2
  · intro hx
    exact ⟨hlt x hx, by simp [hx]⟩

private theorem sum_mem_indicator_eq_length (n : Nat) (vs : List Nat)
    (hnd : vs.Nodup) (hlt : ∀ x ∈ vs, x < n) :
    ((List.range n).map fun x => if x ∈ vs then 1 else 0).sum = vs.length := by
  rw [← length_filter_decide_eq_sum]
  exact filter_range_card_eq_length n vs hnd hlt

private theorem sum_pair_indicator_eq_mul {α β : Type*}
    (xs : List α) (ys : List β) (p : α → Prop) (q : β → Prop)
    [DecidablePred p] [DecidablePred q] :
    (xs.map fun x =>
      (ys.map fun y => if p x ∧ q y then 1 else 0).sum).sum =
      (xs.map fun x => if p x then 1 else 0).sum *
        (ys.map fun y => if q y then 1 else 0).sum := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      by_cases hp : p x <;> simp [hp, ih, Nat.add_mul]

/-- A checked five-vertex row contributes exactly 25 in-range ordered-pair
incidences. -/
theorem selectedRow_pairIncidences_eq_twentyFive
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (i : Fin bads.length) :
    ((List.range G.n).map fun x =>
      ((List.range G.n).map fun y =>
        if x ∈ ((bads.get i).rows.get (omega i)).verts ∧
            y ∈ ((bads.get i).rows.get (omega i)).verts
        then 1 else 0).sum).sum = 25 := by
  let vs := ((bads.get i).rows.get (omega i)).verts
  have hnd : vs.Nodup := selectedRow_nodup hchecked omega i
  have hlt : ∀ x ∈ vs, x < G.n :=
    fun x hx => selectedRow_vertex_lt hchecked omega i x hx
  have hcount := sum_mem_indicator_eq_length G.n vs hnd hlt
  have hlen : vs.length = 5 := selectedRow_length_five hchecked omega i
  rw [sum_pair_indicator_eq_mul]
  simp only [vs] at hcount hlen ⊢
  rw [hcount, hlen]

/-- Checked five-vertex rows make total ordered-pair incidence independent of
the row choice: each bad edge contributes exactly 25. -/
theorem totalPairIncidences_eq_twentyFive_mul_length
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads) :
    totalPairIncidences G omega = 25 * bads.length := by
  let xs := List.range G.n
  let is := badIndices bads
  let f : Nat → Nat → Fin bads.length → Nat := fun x y i =>
    if x ∈ ((bads.get i).rows.get (omega i)).verts ∧
        y ∈ ((bads.get i).rows.get (omega i)).verts
    then 1 else 0
  unfold totalPairIncidences
  simp_rw [pairCount_eq_badIndices_sum]
  change
    (xs.map fun x => (xs.map fun y => (is.map fun i => f x y i).sum).sum).sum =
      25 * bads.length
  calc
    (xs.map fun x => (xs.map fun y => (is.map fun i => f x y i).sum).sum).sum =
        (xs.map fun x => (is.map fun i => (xs.map fun y => f x y i).sum).sum).sum := by
          apply congrArg List.sum
          apply List.map_congr_left
          intro x _
          exact sum_comm_lists xs is (fun y i => f x y i)
    _ = (is.map fun i =>
          (xs.map fun x => (xs.map fun y => f x y i).sum).sum).sum := by
          exact sum_comm_lists xs is
            (fun x i => (xs.map fun y => f x y i).sum)
    _ = (is.map fun _ => 25).sum := by
          apply congrArg List.sum
          apply List.map_congr_left
          intro i _
          exact selectedRow_pairIncidences_eq_twentyFive hchecked omega i
    _ = 25 * bads.length := by
          simp [is, badIndices, Function.comp_def, Nat.mul_comm]

theorem totalPairIncidences_choice_invariant
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) (omega eta : RowChoice bads) :
    totalPairIncidences G eta = totalPairIncidences G omega := by
  rw [totalPairIncidences_eq_twentyFive_mul_length hchecked eta,
    totalPairIncidences_eq_twentyFive_mul_length hchecked omega]

/-- Collision units plus first-covered units equal total pair incidence. -/
theorem collisionUnits_add_coveredPairUnits
    (G : GraphData) {bads : List BadEdgeData} (omega : RowChoice bads) :
    collisionUnits G omega + coveredPairUnits G omega =
      totalPairIncidences G omega := by
  unfold collisionUnits coveredPairUnits totalPairIncidences
  apply sum_add_of_pointwise
  intro x
  apply sum_add_of_pointwise
  intro y
  exact sub_one_add_positiveUnit (pairCount omega x y)

/-- The exact obligation score after adjoining the covered-pair term. -/
theorem obligationScore_add_twice_coveredPairUnits
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    obligationScore G c omega + 2 * coveredPairUnits G omega =
      2 * totalPairIncidences G omega +
        2 * (activeEdges G c omega).length := by
  have h := collisionUnits_add_coveredPairUnits G omega
  unfold obligationScore
  omega

/-- If every legal choice has the same total ordered-pair incidence (as it
does for checked five-vertex rows), strict obligation-score descent is
equivalent to gaining more covered pairs than the active-edge cost incurred.
-/
theorem obligationScore_lt_iff_coveredPair_gain
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega eta : RowChoice bads)
    (htotal : totalPairIncidences G eta = totalPairIncidences G omega) :
    obligationScore G c eta < obligationScore G c omega ↔
      coveredPairUnits G omega + (activeEdges G c eta).length <
        coveredPairUnits G eta + (activeEdges G c omega).length := by
  have hη := collisionUnits_add_coveredPairUnits G eta
  have hω := collisionUnits_add_coveredPairUnits G omega
  unfold obligationScore
  omega

theorem obligationScore_add_twice_covered_eq_checked_constant
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads) :
    obligationScore G c omega + 2 * coveredPairUnits G omega =
      50 * bads.length + 2 * (activeEdges G c omega).length := by
  rw [obligationScore_add_twice_coveredPairUnits,
    totalPairIncidences_eq_twentyFive_mul_length hchecked]
  omega

theorem obligationScore_lt_iff_coveredPair_gain_of_checked
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) (omega eta : RowChoice bads) :
    obligationScore G c eta < obligationScore G c omega ↔
      coveredPairUnits G omega + (activeEdges G c eta).length <
        coveredPairUnits G eta + (activeEdges G c omega).length :=
  obligationScore_lt_iff_coveredPair_gain G c omega eta
    (totalPairIncidences_choice_invariant hchecked omega eta)

#print axioms collisionUnits_add_coveredPairUnits
#print axioms obligationScore_add_twice_coveredPairUnits
#print axioms obligationScore_lt_iff_coveredPair_gain
#print axioms totalPairIncidences_eq_twentyFive_mul_length
#print axioms obligationScore_add_twice_covered_eq_checked_constant
#print axioms obligationScore_lt_iff_coveredPair_gain_of_checked

end CollisionCoveragePotential
end Gamma
end Erdos23Delta0
