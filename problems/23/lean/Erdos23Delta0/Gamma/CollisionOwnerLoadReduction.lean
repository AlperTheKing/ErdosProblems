import Erdos23Delta0.Gamma.CollisionOwnerHallReduction
import Erdos23Delta0.Gamma.CollisionCoveragePotential

/-!
# Collision owner-source load reduction

The owner-saturated source neighborhood splits according to whether the first
source coordinate lies in the owner shore.  Outside the shore, same-owner
cancellation is impossible, so every available source is witnessed by a row
companion.  This gives an exact scalar owner-Hall inequality with separate
same-owner and companion-only loads.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CanonicalCollisionHall

open CertGraph
open MinimumDemandRowSelection

/-- The part of the actual owner-source neighborhood whose first coordinate
lies in the owner shore. -/
def sameOwnerSourceSet (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (A : Finset (Fin G.n)) : Finset (FreeHalf G omega) :=
  (ownerSourceSet G c (omega := omega) A).filter fun s => s.sourceX ∈ A

/-- The part of the actual owner-source neighborhood whose first coordinate
lies outside the owner shore. -/
def companionOnlySourceSet (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (A : Finset (Fin G.n)) : Finset (FreeHalf G omega) :=
  (ownerSourceSet G c (omega := omega) A).filter fun s => s.sourceX ∉ A

@[simp] theorem mem_sameOwnerSourceSet_iff
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {A : Finset (Fin G.n)}
    {s : FreeHalf G omega} :
    s ∈ sameOwnerSourceSet G c (omega := omega) A ↔
      s ∈ ownerSourceSet G c (omega := omega) A ∧ s.sourceX ∈ A := by
  simp [sameOwnerSourceSet]

/-- Every source in the same-owner side of the partition is unreserved. -/
theorem sameOwnerSource_unreserved
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {A : Finset (Fin G.n)}
    {s : FreeHalf G omega}
    (hs : s ∈ sameOwnerSourceSet G c (omega := omega) A) :
    ¬Reserved G c omega s := by
  have hsource := (mem_sameOwnerSourceSet_iff.mp hs).1
  simp only [ownerSourceSet, Finset.mem_filter, Finset.mem_univ,
    true_and] at hsource
  rcases hsource with ⟨d, _hd, havailable⟩
  exact havailable.2

/-- Outside the owner shore, availability is exactly unreserved
row-companion availability to a collision demand owned in the shore. -/
theorem mem_companionOnlySourceSet_iff
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {A : Finset (Fin G.n)}
    {s : FreeHalf G omega} :
    s ∈ companionOnlySourceSet G c (omega := omega) A ↔
      s.sourceX ∉ A ∧
      ¬Reserved G c omega s ∧
      ∃ d ∈ ownerDemandSet (G := G) (omega := omega) A,
        RowCompanion G c d s := by
  constructor
  · intro hs
    have hparts :
        s ∈ ownerSourceSet G c (omega := omega) A ∧ s.sourceX ∉ A := by
      simpa [companionOnlySourceSet] using hs
    have hsource := hparts.1
    simp only [ownerSourceSet, Finset.mem_filter, Finset.mem_univ,
      true_and] at hsource
    rcases hsource with ⟨d, hd, havailable⟩
    have hunreserved : ¬Reserved G c omega s := havailable.2
    have heligible := havailable.1
    unfold Eligible at heligible
    have hcompanion : RowCompanion G c d s := by
      rcases heligible with hsame | hcompanion
      · have howner : d.owner ∈ A := by
          simpa only [ownerDemandSet, Finset.mem_filter, Finset.mem_univ,
            true_and] using hd
        unfold SameOwner at hsame
        exact False.elim (hparts.2 (by simpa [hsame] using howner))
      · exact hcompanion
    exact ⟨hparts.2, hunreserved, d, hd, hcompanion⟩
  · rintro ⟨houtside, hunreserved, d, hd, hcompanion⟩
    simp only [companionOnlySourceSet, Finset.mem_filter]
    refine ⟨?_, houtside⟩
    simp only [ownerSourceSet, Finset.mem_filter, Finset.mem_univ,
      true_and]
    exact ⟨d, hd, ⟨Or.inr hcompanion, hunreserved⟩⟩

/-- The two source buckets are disjoint. -/
theorem sameOwnerSourceSet_disjoint_companionOnlySourceSet
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} (A : Finset (Fin G.n)) :
    Disjoint (sameOwnerSourceSet G c (omega := omega) A)
      (companionOnlySourceSet G c (omega := omega) A) := by
  rw [Finset.disjoint_left]
  intro s hsame hcompanion
  exact (mem_companionOnlySourceSet_iff.mp hcompanion).1
    (mem_sameOwnerSourceSet_iff.mp hsame).2

/-- The two source buckets exhaust the owner-source neighborhood. -/
theorem sameOwnerSourceSet_union_companionOnlySourceSet
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} (A : Finset (Fin G.n)) :
    sameOwnerSourceSet G c (omega := omega) A ∪
        companionOnlySourceSet G c (omega := omega) A =
      ownerSourceSet G c (omega := omega) A := by
  ext s
  by_cases hs : s.sourceX ∈ A <;>
    simp [sameOwnerSourceSet, companionOnlySourceSet, hs]

/-- Cardinal form of the exact source partition. -/
theorem ownerSourceSet_card_eq_sameOwner_add_companionOnly
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} (A : Finset (Fin G.n)) :
    (ownerSourceSet G c (omega := omega) A).card =
      (sameOwnerSourceSet G c (omega := omega) A).card +
        (companionOnlySourceSet G c (omega := omega) A).card := by
  calc
    (ownerSourceSet G c (omega := omega) A).card =
        (sameOwnerSourceSet G c (omega := omega) A ∪
          companionOnlySourceSet G c (omega := omega) A).card :=
      congrArg Finset.card
        (sameOwnerSourceSet_union_companionOnlySourceSet G c A).symm
    _ = (sameOwnerSourceSet G c (omega := omega) A).card +
        (companionOnlySourceSet G c (omega := omega) A).card :=
      Finset.card_union_of_disjoint
        (sameOwnerSourceSet_disjoint_companionOnlySourceSet G c A)

/-- Scalar same-owner-side source load. -/
def sameOwnerUnits (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (A : Finset (Fin G.n)) : Nat :=
  (sameOwnerSourceSet G c (omega := omega) A).card

/-- Scalar companion-only source load. -/
def companionOnlyUnits (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (A : Finset (Fin G.n)) : Nat :=
  (companionOnlySourceSet G c (omega := omega) A).card

theorem ownerSourceUnits_eq_sameOwnerUnits_add_companionOnlyUnits
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} (A : Finset (Fin G.n)) :
    ownerSourceUnits G c (omega := omega) A =
      sameOwnerUnits G c (omega := omega) A +
        companionOnlyUnits G c (omega := omega) A := by
  exact ownerSourceSet_card_eq_sameOwner_add_companionOnly G c A

/-- Owner Hall is exactly demand load bounded by the two disjoint source
loads for every owner shore. -/
theorem ownerHallCondition_iff_ownerLoadUnits
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} :
    OwnerHallCondition G c omega ↔
      ∀ A : Finset (Fin G.n),
        ownerDemandUnits (G := G) omega A ≤
          sameOwnerUnits G c (omega := omega) A +
            companionOnlyUnits G c (omega := omega) A := by
  rw [ownerHallCondition_iff_ownerUnits]
  constructor
  · intro h A
    rw [← ownerSourceUnits_eq_sameOwnerUnits_add_companionOnlyUnits]
    exact h A
  · intro h A
    rw [ownerSourceUnits_eq_sameOwnerUnits_add_companionOnlyUnits]
    exact h A

private theorem owner_sum_add_of_pointwise {α : Type*} (xs : List α)
    (f g h : α → Nat) (hpoint : ∀ x, f x + g x = h x) :
    (xs.map f).sum + (xs.map g).sum = (xs.map h).sum := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      simp only [List.map_cons, List.sum_cons]
      have hx := hpoint x
      omega

private theorem owner_sum_comm_lists {α β : Type*} (xs : List α) (ys : List β)
    (f : α → β → Nat) :
    (xs.map fun x => (ys.map fun y => f x y).sum).sum =
      (ys.map fun y => (xs.map fun x => f x y).sum).sum := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      simp only [List.map_cons, List.sum_cons]
      rw [ih]
      exact owner_sum_add_of_pointwise ys
        (fun y => f x y)
        (fun y => (xs.map fun z => f z y).sum)
        (fun y => f x y + (xs.map fun z => f z y).sum)
        (fun _ => rfl)

private theorem owner_length_filter_decide_eq_sum {α : Type*} (xs : List α)
    (p : α → Prop) [DecidablePred p] :
    (xs.filter fun a => decide (p a)).length =
      (xs.map fun a => if p a then 1 else 0).sum := by
  induction xs with
  | nil => simp
  | cons a xs ih =>
      by_cases hp : p a <;> simp [hp, ih, Nat.add_comm]

private theorem owner_sum_mem_indicator_eq_length (n : Nat) (vs : List Nat)
    (hnd : vs.Nodup) (hlt : ∀ x ∈ vs, x < n) :
    ((List.range n).map fun x => if x ∈ vs then 1 else 0).sum = vs.length := by
  rw [← owner_length_filter_decide_eq_sum]
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

private theorem owner_sum_five_indicator {α : Type*} (xs : List α)
    (p : α → Prop) [DecidablePred p] :
    (xs.map fun x => if p x then 5 else 0).sum =
      5 * (xs.map fun x => if p x then 1 else 0).sum := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      by_cases hx : p x <;> simp [hx, ih, Nat.mul_add]

/-- A checked selected five-row contributes five pair incidences to each
vertex it contains.  Summing over rows gives the exact per-owner load
identity used by the FullBank overload formula. -/
theorem pairCount_rowSum_eq_five_mul_diagonal
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (v : Fin G.n) :
    ((List.range G.n).map fun y => pairCount omega v.1 y).sum =
      5 * pairCount omega v.1 v.1 := by
  let ys := List.range G.n
  let is : List (Fin bads.length) := List.ofFn fun i => i
  let row : Fin bads.length → List Nat := fun i =>
    ((bads.get i).rows.get (omega i)).verts
  let f : Nat → Fin bads.length → Nat := fun y i =>
    if v.1 ∈ row i ∧ y ∈ row i then 1 else 0
  have hmain : (ys.map fun y => (is.map fun i => f y i).sum).sum =
      5 * (is.map fun i => f v.1 i).sum := by
    calc
    (ys.map fun y => (is.map fun i => f y i).sum).sum =
        (is.map fun i => (ys.map fun y => f y i).sum).sum :=
      owner_sum_comm_lists ys is f
    _ = (is.map fun i => if v.1 ∈ row i then 5 else 0).sum := by
      apply congrArg List.sum
      apply List.map_congr_left
      intro i _
      by_cases hv : v.1 ∈ row i
      · have hnd : (row i).Nodup :=
          CollisionCoveragePotential.selectedRow_nodup hchecked omega i
        have hlt : ∀ x ∈ row i, x < G.n := fun x hx =>
          CollisionCoveragePotential.selectedRow_vertex_lt
            hchecked omega i x hx
        have hcount := owner_sum_mem_indicator_eq_length G.n (row i) hnd hlt
        have hlen : (row i).length = 5 :=
          CollisionCoveragePotential.selectedRow_length_five hchecked omega i
        simp only [f, hv, true_and, if_pos]
        simpa [ys, hlen] using hcount
      · simp [f, hv]
    _ = 5 * (is.map fun i => if v.1 ∈ row i then 1 else 0).sum :=
      owner_sum_five_indicator is (fun i => v.1 ∈ row i)
    _ = 5 * (is.map fun i => f v.1 i).sum := by
      congr 1
      apply congrArg List.sum
      apply List.map_congr_left
      intro i _
      by_cases hv : v.1 ∈ row i <;> simp [f, hv]
  simp_rw [CollisionCoveragePotential.pairCount_eq_sum_indicator]
  simpa [ys, is, row, f, List.map_ofFn, Function.comp_def] using hmain

#print axioms mem_companionOnlySourceSet_iff
#print axioms sameOwnerSourceSet_union_companionOnlySourceSet
#print axioms ownerSourceSet_card_eq_sameOwner_add_companionOnly
#print axioms ownerHallCondition_iff_ownerLoadUnits
#print axioms pairCount_rowSum_eq_five_mul_diagonal

end CanonicalCollisionHall
end Gamma
end Erdos23Delta0
