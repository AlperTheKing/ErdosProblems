import Erdos23Delta0.Gamma.CollisionOwnerLoadReduction
import Erdos23Delta0.Gamma.SoftEdgeCapGraphAdapter

/-!
# Same-first owner-shore overload identity

The P1 same-first source capacity has one exact obstruction. Raw zero-pair
bases pay collision halves owner by owner; grouping the two orientations of
an internal active edge under capacity two removes exactly one ordered-base
unit. Hence P1 deficiency is equivalent to selected-load overload plus the
number of internal active locks.
-/

namespace Erdos23Delta0
namespace Gamma
namespace SoftCapOwnerShoreOverload

open scoped BigOperators
open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

def ownerCollisionBaseUnits (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (v : Fin G.n) : Nat :=
  ∑ y : Fin G.n, (pairCount omega v.1 y.1 - 1)

def ownerCoveredBaseUnits (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (v : Fin G.n) : Nat :=
  ∑ y : Fin G.n, if 0 < pairCount omega v.1 y.1 then 1 else 0

def ownerZeroBaseUnits (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (v : Fin G.n) : Nat :=
  ∑ y : Fin G.n, if pairCount omega v.1 y.1 = 0 then 1 else 0

def ownerPairUnits (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (v : Fin G.n) : Nat :=
  ∑ y : Fin G.n, pairCount omega v.1 y.1

theorem ownerCollision_add_covered
    (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (v : Fin G.n) :
    ownerCollisionBaseUnits G omega v + ownerCoveredBaseUnits G omega v =
      ownerPairUnits G omega v := by
  unfold ownerCollisionBaseUnits ownerCoveredBaseUnits ownerPairUnits
  calc
    (∑ y : Fin G.n, (pairCount omega v.1 y.1 - 1)) +
        (∑ y : Fin G.n,
          if 0 < pairCount omega v.1 y.1 then 1 else 0) =
        ∑ y : Fin G.n,
          ((pairCount omega v.1 y.1 - 1) +
            if 0 < pairCount omega v.1 y.1 then 1 else 0) := by


      exact (@Finset.sum_add_distrib (Fin G.n) Nat Finset.univ
        (inferInstance : AddCommMonoid Nat)
        (fun y => pairCount omega v.1 y.1 - 1)
        (fun y => if 0 < pairCount omega v.1 y.1 then 1 else 0)).symm
    _ = ∑ y : Fin G.n, pairCount omega v.1 y.1 := by
      apply Finset.sum_congr rfl
      intro y _
      by_cases hzero : pairCount omega v.1 y.1 = 0
      · simp [hzero]
      · have hpos : 0 < pairCount omega v.1 y.1 :=
          Nat.pos_of_ne_zero hzero
        simp [hpos]
        omega

theorem ownerCovered_add_zero
    (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (v : Fin G.n) :
    ownerCoveredBaseUnits G omega v + ownerZeroBaseUnits G omega v = G.n := by
  unfold ownerCoveredBaseUnits ownerZeroBaseUnits
  calc
    (∑ y : Fin G.n,
        if 0 < pairCount omega v.1 y.1 then 1 else 0) +
        (∑ y : Fin G.n,
          if pairCount omega v.1 y.1 = 0 then 1 else 0) =
        ∑ y : Fin G.n,
          ((if 0 < pairCount omega v.1 y.1 then 1 else 0) +
            if pairCount omega v.1 y.1 = 0 then 1 else 0) := by


      exact (@Finset.sum_add_distrib (Fin G.n) Nat Finset.univ
        (inferInstance : AddCommMonoid Nat)
        (fun y => if 0 < pairCount omega v.1 y.1 then 1 else 0)
        (fun y => if pairCount omega v.1 y.1 = 0 then 1 else 0)).symm
    _ = ∑ _y : Fin G.n, 1 := by
      apply Finset.sum_congr rfl
      intro y _
      by_cases hzero : pairCount omega v.1 y.1 = 0
      · simp [hzero]
      · have hpos : 0 < pairCount omega v.1 y.1 :=
          Nat.pos_of_ne_zero hzero
        simp [hzero, hpos]
    _ = G.n := by simp

theorem ownerPairUnits_eq_five_mul_diagonal
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (v : Fin G.n) :
    ownerPairUnits G omega v = 5 * pairCount omega v.1 v.1 := by
  unfold ownerPairUnits
  rw [SoftEdgeCapGraphAdapter.fin_sum_eq_list_range_sum]
  exact CanonicalCollisionHall.pairCount_rowSum_eq_five_mul_diagonal
    hchecked omega v

theorem ownerCollision_add_order_eq_load_add_zero
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (v : Fin G.n) :
    ownerCollisionBaseUnits G omega v + G.n =
      5 * pairCount omega v.1 v.1 + ownerZeroBaseUnits G omega v := by
  have hcollision := ownerCollision_add_covered G omega v
  have hpartition := ownerCovered_add_zero G omega v
  have hpairs := ownerPairUnits_eq_five_mul_diagonal hchecked omega v
  omega

def shoreCollisionBaseUnits (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) : Nat :=
  ∑ v ∈ A, ownerCollisionBaseUnits G omega v

def shoreZeroBaseUnits (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) : Nat :=
  ∑ v ∈ A, ownerZeroBaseUnits G omega v

def shoreSelectedLoad (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) : Nat :=
  ∑ v ∈ A, 5 * pairCount omega v.1 v.1

theorem shoreCollision_add_order_eq_load_add_zero
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (A : Finset (Fin G.n)) :
    shoreCollisionBaseUnits G omega A + G.n * A.card =
      shoreSelectedLoad G omega A + shoreZeroBaseUnits G omega A := by
  have hsum :
      (∑ v ∈ A, (ownerCollisionBaseUnits G omega v + G.n)) =
        ∑ v ∈ A,
          (5 * pairCount omega v.1 v.1 + ownerZeroBaseUnits G omega v) := by
    apply Finset.sum_congr rfl
    intro v hv
    exact ownerCollision_add_order_eq_load_add_zero hchecked omega v
  simpa [shoreCollisionBaseUnits, shoreSelectedLoad, shoreZeroBaseUnits,
    Finset.sum_add_distrib, Finset.mul_sum, Nat.mul_comm] using hsum

def p1GroupedCapacity (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n))
    (internalActive : Nat) : Nat :=
  2 * (shoreZeroBaseUnits G omega A - internalActive)

theorem p1Grouped_deficient_iff_overload_or_lock
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (A : Finset (Fin G.n)) (internalActive : Nat)
    (hactive : internalActive ≤ shoreZeroBaseUnits G omega A) :
    2 * shoreCollisionBaseUnits G omega A >
        p1GroupedCapacity G omega A internalActive ↔
      G.n * A.card < shoreSelectedLoad G omega A + internalActive := by
  have hid :=
    shoreCollision_add_order_eq_load_add_zero hchecked omega A
  unfold p1GroupedCapacity
  omega


def activeLeft
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) {omega : RowChoice bads}
    (e : SoftEdgeCapGraphAdapter.ActiveEdge G c omega) : Fin G.n :=
  ⟨e.1.1, (SoftEdgeCapGraphAdapter.activeEdge_endpoint_lt hG e).1⟩

def activeRight
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) {omega : RowChoice bads}
    (e : SoftEdgeCapGraphAdapter.ActiveEdge G c omega) : Fin G.n :=
  ⟨e.1.2, (SoftEdgeCapGraphAdapter.activeEdge_endpoint_lt hG e).2⟩

abbrev InternalActiveEdge
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (omega : RowChoice bads)
    (A : Finset (Fin G.n)) :=
  {e : SoftEdgeCapGraphAdapter.ActiveEdge G c omega //
    activeLeft hG e ∈ A ∧ activeRight hG e ∈ A}

abbrev ShoreZeroBase
    (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) :=
  {p : Fin G.n × Fin G.n //
    p.1 ∈ A ∧ pairCount omega p.1.1 p.2.1 = 0}

def internalActiveUnits
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (omega : RowChoice bads)
    (A : Finset (Fin G.n)) : Nat :=
  Fintype.card (InternalActiveEdge (c := c) hG omega A)

def shoreZeroBaseEquiv
    (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) :
    ShoreZeroBase G omega A ≃
      Σ v : {v : Fin G.n // v ∈ A},
        {y : Fin G.n // pairCount omega v.1.1 y.1 = 0} where
  toFun p := ⟨⟨p.1.1, p.2.1⟩, ⟨p.1.2, p.2.2⟩⟩
  invFun p := ⟨(p.1.1, p.2.1), p.1.2, p.2.2⟩
  left_inv p := by cases p; rfl
  right_inv p := by rcases p with ⟨⟨v, hv⟩, ⟨y, hy⟩⟩; rfl

theorem shoreZeroBase_card
    (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) :
    Fintype.card (ShoreZeroBase G omega A) =
      shoreZeroBaseUnits G omega A := by
  rw [Fintype.card_congr (shoreZeroBaseEquiv G omega A)]
  rw [Fintype.card_sigma]
  have hfiber (v : Fin G.n) :
      Fintype.card {y : Fin G.n // pairCount omega v.1 y.1 = 0} =
        ∑ y : Fin G.n, if pairCount omega v.1 y.1 = 0 then 1 else 0 := by
    rw [Fintype.card_subtype]
    rw [Finset.card_eq_sum_ones, Finset.sum_filter]
  calc
    (∑ v : {v : Fin G.n // v ∈ A},
        Fintype.card {y : Fin G.n //
          pairCount omega v.1.1 y.1 = 0}) =
        ∑ v : {v : Fin G.n // v ∈ A},
          ∑ y : Fin G.n,
            if pairCount omega v.1.1 y.1 = 0 then 1 else 0 := by
      apply Finset.sum_congr rfl
      intro v _
      exact hfiber v.1
    _ = ∑ v ∈ A,
          ∑ y : Fin G.n,
            if pairCount omega v.1 y.1 = 0 then 1 else 0 :=
      Finset.sum_coe_sort A fun v : Fin G.n =>
        ∑ y : Fin G.n, if pairCount omega v.1 y.1 = 0 then 1 else 0
    _ = shoreZeroBaseUnits G omega A := by
      rfl

def internalActiveToShoreZero
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (A : Finset (Fin G.n)) :
    InternalActiveEdge (c := c) hG omega A ↪ ShoreZeroBase G omega A where
  toFun e :=
    ⟨(activeLeft hG e.1, activeRight hG e.1),
      e.2.1,
      SoftEdgeCapGraphAdapter.activeEdge_pairCount_eq_zero
        htri hchecked omega e.1⟩
  inj' := by
    intro e f hef
    apply Subtype.ext
    apply Subtype.ext
    have hpair := congrArg
      (fun p : ShoreZeroBase G omega A =>
        (p.1.1.1, p.1.2.1)) hef
    exact hpair

theorem internalActiveUnits_le_shoreZeroBaseUnits
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (A : Finset (Fin G.n)) :
    internalActiveUnits (c := c) hG omega A ≤ shoreZeroBaseUnits G omega A := by
  rw [← shoreZeroBase_card G omega A]
  exact Fintype.card_le_of_injective
    (internalActiveToShoreZero hG htri hchecked omega A)
    (internalActiveToShoreZero hG htri hchecked omega A).injective

theorem p1Grouped_real_deficient_iff_overload_or_lock
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (A : Finset (Fin G.n)) :
    2 * shoreCollisionBaseUnits G omega A >
        p1GroupedCapacity G omega A (internalActiveUnits (c := c) hG omega A) ↔
      G.n * A.card <
        shoreSelectedLoad G omega A + internalActiveUnits (c := c) hG omega A := by
  exact p1Grouped_deficient_iff_overload_or_lock hchecked omega A
    (internalActiveUnits (c := c) hG omega A)
    (internalActiveUnits_le_shoreZeroBaseUnits
      hG htri hchecked omega A)

#print axioms ownerCollision_add_order_eq_load_add_zero
#print axioms shoreCollision_add_order_eq_load_add_zero
#print axioms p1Grouped_deficient_iff_overload_or_lock
#print axioms internalActiveUnits_le_shoreZeroBaseUnits
#print axioms p1Grouped_real_deficient_iff_overload_or_lock

end SoftCapOwnerShoreOverload
end Gamma
end Erdos23Delta0
