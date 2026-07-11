import Erdos23Delta0.Gamma.ActiveScopedVariationReduction

/-!
# One-coordinate transport target

For one fixed bad-edge row family, bundle every demand produced by an
alternative row.  A transport sends that dependent bundle injectively into
copies of the old demands outside a deficient owner shore together with
copies of the old free-half neighborhood of that shore.  Pure finite
cardinality then gives the one-coordinate variation inequality.
-/

namespace Erdos23Delta0
namespace Gamma
namespace ActiveScopedMinimumExchange

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open TwoRowRectangleExchange

attribute [local instance] Classical.propDecidable

abbrev CoordinateNewDemandBundle
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length) : Type :=
  Σ q : OneCoordinateAlternative omega i,
    Demand G c (choiceAfterAlternative omega ⟨i, q⟩)

abbrev ShoreDemand
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) : Type :=
  {d : Demand G c omega // demandOwner d ∈ A}

abbrev OutsideShoreDemand
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) : Type :=
  {d : Demand G c omega // demandOwner d ∉ A}

abbrev ShoreSource
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) : Type :=
  {s : FreeHalf G omega // s ∈ scopedOwnerSourceSet G c omega A}

abbrev CoordinateTransportTarget
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n))
    (i : Fin bads.length) : Type :=
  (OneCoordinateAlternative omega i × OutsideShoreDemand G c omega A) ⊕
    (OneCoordinateAlternative omega i × ShoreSource G c omega A)

structure CoordinateReplacementInjection
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n))
    (i : Fin bads.length) : Type where
  assign : CoordinateNewDemandBundle G c omega i →
    CoordinateTransportTarget G c omega A i
  injective : Function.Injective assign

def NewComponentTouchesChangedRows
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length)
    (q : OneCoordinateAlternative omega i) (owner : Fin G.n) : Prop :=
  ∃ x : Fin G.n,
    (x.1 ∈ ((bads.get i).rows.get (omega i)).verts ∨
      x.1 ∈ ((bads.get i).rows.get q.1).verts) ∧
      (activeGraph G c (choiceAfterAlternative omega ⟨i, q⟩)).Reachable owner x

def CoordinateComponentInherited
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length)
    (q : OneCoordinateAlternative omega i)
    (newOwner oldOwner : Fin G.n) : Prop :=
  ∃ x : Fin G.n,
      (activeGraph G c (choiceAfterAlternative omega ⟨i, q⟩)).Reachable
        newOwner x ∧
      (activeGraph G c omega).Reachable oldOwner x

/-- Exact graph-derived source relation used by the component transport gate.
A newly active demand may inherit an old shore source through intersecting
active components or from a new component touched by either changed row. -/
def ComponentTransportSourceEligible
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n))
    (i : Fin bads.length)
    (z : CoordinateNewDemandBundle G c omega i)
    (s : ShoreSource G c omega A) : Prop :=
  NewComponentTouchesChangedRows G c omega i z.1 (demandOwner z.2) ∨
    ∃ d : Demand G c omega,
      demandOwner d ∈ A ∧
      Available G c d s.1 ∧
      CoordinateComponentInherited G c omega i z.1
        (demandOwner z.2) (demandOwner d)

theorem replaceOne_apply_self
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (i : Fin bads.length)
    (replacement : Fin (bads.get i).rows.length) :
    replaceOne omega i replacement i = replacement := by
  simp [replaceOne, replaceTwo]

theorem replaceOne_apply_of_ne
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (i j : Fin bads.length)
    (replacement : Fin (bads.get i).rows.length)
    (hji : j ≠ i) :
    replaceOne omega i replacement j = omega j := by
  exact replaceTwo_eq_of_ne omega i i j replacement replacement hji hji

theorem mem_selectedRows_replaceOne_iff
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (i : Fin bads.length)
    (replacement : Fin (bads.get i).rows.length)
    (row : Row5) :
    row ∈ selectedRows (replaceOne omega i replacement) ↔
      row = (bads.get i).rows.get replacement ∨
        ∃ j : Fin bads.length, j ≠ i ∧
          row = (bads.get j).rows.get (omega j) := by
  simp only [selectedRows, List.mem_ofFn]
  constructor
  · rintro ⟨j, rfl⟩
    by_cases hji : j = i
    · subst j
      left
      rw [replaceOne_apply_self]
    · right
      exact ⟨j, hji, by rw [replaceOne_apply_of_ne omega i j replacement hji]⟩
  · rintro (h | ⟨j, hji, hrow⟩)
    · refine ⟨i, ?_⟩
      rw [replaceOne_apply_self]
      exact h.symm
    · refine ⟨j, ?_⟩
      rw [replaceOne_apply_of_ne omega i j replacement hji]
      exact hrow.symm

theorem mem_selectedRows_iff
    {bads : List BadEdgeData} (omega : RowChoice bads) (row : Row5) :
    row ∈ selectedRows omega ↔
      ∃ j : Fin bads.length,
        row = (bads.get j).rows.get (omega j) := by
  simp [selectedRows, eq_comm]

theorem mem_selectedVertices_replaceOne_iff_of_not_mem_changed
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (i : Fin bads.length)
    (replacement : Fin (bads.get i).rows.length)
    (x : Nat)
    (hxold : x ∉ ((bads.get i).rows.get (omega i)).verts)
    (hxnew : x ∉ ((bads.get i).rows.get replacement).verts) :
    x ∈ selectedVertices (replaceOne omega i replacement) ↔
      x ∈ selectedVertices omega := by
  simp only [selectedVertices, List.mem_dedup, List.mem_flatMap]
  constructor
  · rintro ⟨row, hrow, hxrow⟩
    rw [mem_selectedRows_replaceOne_iff] at hrow
    rcases hrow with hnew | ⟨j, hji, hrow⟩
    · subst row
      exact False.elim (hxnew hxrow)
    · refine ⟨row, ?_, hxrow⟩
      rw [mem_selectedRows_iff]
      exact ⟨j, hrow⟩
  · rintro ⟨row, hrow, hxrow⟩
    rw [mem_selectedRows_iff] at hrow
    rcases hrow with ⟨j, hrow⟩
    by_cases hji : j = i
    · subst j
      subst row
      exact False.elim (hxold hxrow)
    · refine ⟨row, ?_, hxrow⟩
      rw [mem_selectedRows_replaceOne_iff]
      exact Or.inr ⟨j, hji, hrow⟩

theorem mem_selectedSupport_replaceOne_iff_of_not_mem_changed
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (i : Fin bads.length)
    (replacement : Fin (bads.get i).rows.length)
    (e : Nat × Nat)
    (heold : e ∉ rowPathEdges ((bads.get i).rows.get (omega i)))
    (henew : e ∉ rowPathEdges ((bads.get i).rows.get replacement)) :
    e ∈ selectedSupport (replaceOne omega i replacement) ↔
      e ∈ selectedSupport omega := by
  simp only [selectedSupport, List.mem_dedup, List.mem_flatMap]
  constructor
  · rintro ⟨row, hrow, herow⟩
    rw [mem_selectedRows_replaceOne_iff] at hrow
    rcases hrow with hnew | ⟨j, hji, hrow⟩
    · subst row
      exact False.elim (henew herow)
    · refine ⟨row, ?_, herow⟩
      rw [mem_selectedRows_iff]
      exact ⟨j, hrow⟩
  · rintro ⟨row, hrow, herow⟩
    rw [mem_selectedRows_iff] at hrow
    rcases hrow with ⟨j, hrow⟩
    by_cases hji : j = i
    · subst j
      subst row
      exact False.elim (heold herow)
    · refine ⟨row, ?_, herow⟩
      rw [mem_selectedRows_replaceOne_iff]
      exact Or.inr ⟨j, hji, hrow⟩

theorem rowPathEdge_endpoints_mem
    {row : Row5} {e : Nat × Nat} (he : e ∈ rowPathEdges row) :
    e.1 ∈ row.verts ∧ e.2 ∈ row.verts := by
  unfold rowPathEdges at he
  rcases List.mem_map.mp he with ⟨p, hp, rfl⟩
  have hpMem := List.of_mem_zip hp
  have hp1 : p.1 ∈ row.verts := hpMem.1
  have hp2 : p.2 ∈ row.verts := List.mem_of_mem_tail hpMem.2
  by_cases h : p.1 < p.2 <;> simp [normEdge, h, hp1, hp2]

theorem normEdge_not_mem_rowPathEdges_of_not_mem
    {row : Row5} {x y : Nat} (hx : x ∉ row.verts) :
    normEdge x y ∉ rowPathEdges row := by
  intro he
  have hmem := rowPathEdge_endpoints_mem he
  by_cases h : x < y
  · exact hx (by simpa [normEdge, h] using hmem.1)
  · exact hx (by simpa [normEdge, h] using hmem.2)

theorem mem_activeEdges_replaceOne_iff_of_not_mem_changed
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length)
    (replacement : Fin (bads.get i).rows.length)
    (e : Nat × Nat)
    (hxold : e.1 ∉ ((bads.get i).rows.get (omega i)).verts)
    (hxnew : e.1 ∉ ((bads.get i).rows.get replacement).verts)
    (hyold : e.2 ∉ ((bads.get i).rows.get (omega i)).verts)
    (hynew : e.2 ∉ ((bads.get i).rows.get replacement).verts) :
    e ∈ activeEdges G c (replaceOne omega i replacement) ↔
      e ∈ activeEdges G c omega := by
  have hxv := mem_selectedVertices_replaceOne_iff_of_not_mem_changed
    omega i replacement e.1 hxold hxnew
  have hyv := mem_selectedVertices_replaceOne_iff_of_not_mem_changed
    omega i replacement e.2 hyold hynew
  have hs := mem_selectedSupport_replaceOne_iff_of_not_mem_changed
    omega i replacement (normEdge e.1 e.2)
      (normEdge_not_mem_rowPathEdges_of_not_mem hxold)
      (normEdge_not_mem_rowPathEdges_of_not_mem hxnew)
  unfold activeEdges
  simp [hxv, hyv, hs]

theorem activeGraph_adj_replaceOne_iff_of_not_mem_changed
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length)
    (replacement : Fin (bads.get i).rows.length)
    (x y : Fin G.n)
    (hxold : x.1 ∉ ((bads.get i).rows.get (omega i)).verts)
    (hxnew : x.1 ∉ ((bads.get i).rows.get replacement).verts)
    (hyold : y.1 ∉ ((bads.get i).rows.get (omega i)).verts)
    (hynew : y.1 ∉ ((bads.get i).rows.get replacement).verts) :
    (activeGraph G c (replaceOne omega i replacement)).Adj x y ↔
      (activeGraph G c omega).Adj x y := by
  change (x ≠ y ∧
      normEdge x.1 y.1 ∈ activeEdges G c (replaceOne omega i replacement)) ↔
    (x ≠ y ∧ normEdge x.1 y.1 ∈ activeEdges G c omega)
  apply and_congr Iff.rfl
  by_cases hxy : x.1 < y.1
  · simpa [normEdge, hxy] using
      (mem_activeEdges_replaceOne_iff_of_not_mem_changed
        G c omega i replacement (x.1, y.1) hxold hxnew hyold hynew)
  · simpa [normEdge, hxy] using
      (mem_activeEdges_replaceOne_iff_of_not_mem_changed
        G c omega i replacement (y.1, x.1) hyold hynew hxold hxnew)

theorem activeGraph_reachable_replaceOne_of_component_avoids_changed
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length)
    (replacement : Fin (bads.get i).rows.length)
    (owner y : Fin G.n)
    (havoid : ∀ z : Fin G.n,
      (activeGraph G c (replaceOne omega i replacement)).Reachable owner z →
        z.1 ∉ ((bads.get i).rows.get (omega i)).verts ∧
        z.1 ∉ ((bads.get i).rows.get replacement).verts)
    (hreach :
      (activeGraph G c (replaceOne omega i replacement)).Reachable owner y) :
    (activeGraph G c omega).Reachable owner y := by
  let newGraph := activeGraph G c (replaceOne omega i replacement)
  let oldGraph := activeGraph G c omega
  let rec copyWalk {a b : Fin G.n} (p : newGraph.Walk a b)
      (ha : newGraph.Reachable owner a) : oldGraph.Walk a b := by
    cases p with
    | nil => exact .nil
    | cons hadj tail =>
        have hb : newGraph.Reachable owner _ := ha.trans hadj.reachable
        have hna := havoid a ha
        have hnb := havoid _ hb
        have holdAdj : oldGraph.Adj a _ :=
          (activeGraph_adj_replaceOne_iff_of_not_mem_changed
            G c omega i replacement a _ hna.1 hna.2 hnb.1 hnb.2).mp hadj
        exact .cons holdAdj (copyWalk tail hb)
  rcases hreach with ⟨p⟩
  exact ⟨copyWalk p .rfl⟩

/-- A new active component that never meets either changed row is contained
in its old active component. -/
theorem newComponent_reachable_old_of_not_touchesChangedRows
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length)
    (q : OneCoordinateAlternative omega i)
    (owner y : Fin G.n)
    (hnot : ¬NewComponentTouchesChangedRows G c omega i q owner)
    (hreach :
      (activeGraph G c (choiceAfterAlternative omega ⟨i, q⟩)).Reachable
        owner y) :
    (activeGraph G c omega).Reachable owner y := by
  apply activeGraph_reachable_replaceOne_of_component_avoids_changed
    G c omega i q.1 owner y
  · intro z hz
    constructor
    · intro hzold
      apply hnot
      exact ⟨z, Or.inl hzold, by simpa [choiceAfterAlternative] using hz⟩
    · intro hznew
      apply hnot
      exact ⟨z, Or.inr hznew, by simpa [choiceAfterAlternative] using hz⟩
  · simpa [choiceAfterAlternative] using hreach

structure ComponentAwareCoordinateReplacementInjection
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n))
    (i : Fin bads.length) : Type where
  assign : CoordinateNewDemandBundle G c omega i →
    CoordinateTransportTarget G c omega A i
  injective : Function.Injective assign
  legal : ∀ z,
    match assign z with
    | Sum.inl _ => True
    | Sum.inr target =>
        ComponentTransportSourceEligible G c omega A i z target.2

def ComponentAwareCoordinateReplacementInjection.toReplacementInjection
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {A : Finset (Fin G.n)}
    {i : Fin bads.length}
    (T : ComponentAwareCoordinateReplacementInjection G c omega A i) :
    CoordinateReplacementInjection G c omega A i where
  assign := T.assign
  injective := T.injective

theorem card_coordinateNewDemandBundle
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length) :
    Fintype.card (CoordinateNewDemandBundle G c omega i) =
      ∑ q : OneCoordinateAlternative omega i,
        scopedObligationScore G c (choiceAfterAlternative omega ⟨i, q⟩) := by
  simp [CoordinateNewDemandBundle, scopedObligationScore]

theorem card_shoreDemand
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) :
    Fintype.card (ShoreDemand G c omega A) =
      (scopedOwnerDemandSet
        (G := G) (c := c) (omega := omega) A).card := by
  classical
  rw [Fintype.card_subtype]
  simp [scopedOwnerDemandSet]

theorem card_outsideShoreDemand
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) :
    Fintype.card (OutsideShoreDemand G c omega A) =
      scopedObligationScore G c omega -
        (scopedOwnerDemandSet
          (G := G) (c := c) (omega := omega) A).card := by
  classical
  rw [Fintype.card_subtype_compl]
  rw [card_shoreDemand]
  rfl

theorem card_shoreSource
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n)) :
    Fintype.card (ShoreSource G c omega A) =
      (scopedOwnerSourceSet G c omega A).card := by
  classical
  rw [Fintype.card_subtype]
  simp

theorem card_coordinateTransportTarget
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n))
    (i : Fin bads.length) :
    Fintype.card (CoordinateTransportTarget G c omega A i) =
      Fintype.card (OneCoordinateAlternative omega i) *
        (scopedObligationScore G c omega -
          (scopedOwnerDemandSet
            (G := G) (c := c) (omega := omega) A).card +
          (scopedOwnerSourceSet G c omega A).card) := by
  unfold CoordinateTransportTarget
  rw [Fintype.card_sum, Fintype.card_prod, Fintype.card_prod]
  rw [card_outsideShoreDemand, card_shoreSource, Nat.mul_add]

noncomputable def oneCoordinateVariation
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length) : Int :=
  ∑ q : OneCoordinateAlternative omega i,
    oneRowDelta G c omega ⟨i, q⟩

theorem oneCoordinateVariation_eq_collision_add_hitNeed
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (i : Fin bads.length) :
    oneCoordinateVariation G c omega i =
      oneCoordinateCollisionVariation G c omega i +
        oneCoordinateHitNeedVariation G c omega i := by
  classical
  unfold oneCoordinateVariation oneCoordinateCollisionVariation
    oneCoordinateHitNeedVariation
  calc
    (∑ q : OneCoordinateAlternative omega i,
        oneRowDelta G c omega ⟨i, q⟩) =
      ∑ q : OneCoordinateAlternative omega i,
        (oneRowCollisionDelta G c omega ⟨i, q⟩ +
          oneRowHitNeedDelta G c omega ⟨i, q⟩) := by
      apply Finset.sum_congr rfl
      intro q _hq
      exact oneRowDelta_eq_collision_add_hitNeed G c omega ⟨i, q⟩
    _ = _ := Finset.sum_add_distrib

/-- Finite cardinal bridge: a concrete coordinate transport pays the full
owner-shore defect in the coordinate's total score variation. -/
theorem oneCoordinateVariation_le_of_replacementInjection
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (A : Finset (Fin G.n))
    (i : Fin bads.length)
    (T : CoordinateReplacementInjection G c omega A i) :
    oneCoordinateVariation G c omega i ≤
      (Fintype.card (OneCoordinateAlternative omega i) : Int) *
        (((scopedOwnerSourceSet G c omega A).card : Int) -
          ((scopedOwnerDemandSet
            (G := G) (c := c) (omega := omega) A).card : Int)) := by
  classical
  have hcard := Fintype.card_le_of_injective T.assign T.injective
  rw [card_coordinateNewDemandBundle, card_coordinateTransportTarget] at hcard
  have hdemand_le :
      (scopedOwnerDemandSet
        (G := G) (c := c) (omega := omega) A).card ≤
          scopedObligationScore G c omega := by
    exact Finset.card_le_univ _
  have hcardInt0 :
      ((∑ q : OneCoordinateAlternative omega i,
          scopedObligationScore G c
            (choiceAfterAlternative omega ⟨i, q⟩) : Nat) : Int) ≤
        (Fintype.card (OneCoordinateAlternative omega i) *
          (scopedObligationScore G c omega -
            (scopedOwnerDemandSet
              (G := G) (c := c) (omega := omega) A).card +
            (scopedOwnerSourceSet G c omega A).card) : Nat) := by
    exact_mod_cast hcard
  push_cast [hdemand_le] at hcardInt0
  have hcardInt :
      (∑ q : OneCoordinateAlternative omega i,
          (scopedObligationScore G c
            (choiceAfterAlternative omega ⟨i, q⟩) : Int)) ≤
        (Fintype.card (OneCoordinateAlternative omega i) : Int) *
          ((scopedObligationScore G c omega : Int) -
            ((scopedOwnerDemandSet
              (G := G) (c := c) (omega := omega) A).card : Int) +
            ((scopedOwnerSourceSet G c omega A).card : Int)) := by
    exact hcardInt0
  unfold oneCoordinateVariation oneRowDelta
  rw [Finset.sum_sub_distrib]
  simp only [Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
  nlinarith [hcardInt]

theorem oneRowVariation_eq_sum_coordinateVariations
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    oneRowVariation G c omega =
      ∑ i : Fin bads.length, oneCoordinateVariation G c omega i := by
  classical
  unfold oneRowVariation oneCoordinateVariation
  simpa only [OneRowAlternative, OneCoordinateAlternative] using
    (Fintype.sum_sigma
      (fun a : OneRowAlternative omega => oneRowDelta G c omega a))

noncomputable def DeficientOwnerShoreCoordinateTransport
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ (omega : RowChoice bads) (A : Finset (Fin G.n)),
    (scopedOwnerSourceSet G c omega A).card <
        (scopedOwnerDemandSet
          (G := G) (c := c) (omega := omega) A).card →
      ∀ i : Fin bads.length,
        Nonempty (CoordinateReplacementInjection G c omega A i)

noncomputable def DeficientOwnerShoreComponentAwareCoordinateTransport
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ (omega : RowChoice bads) (A : Finset (Fin G.n)),
    (scopedOwnerSourceSet G c omega A).card <
        (scopedOwnerDemandSet
          (G := G) (c := c) (omega := omega) A).card →
      ∀ i : Fin bads.length,
        Nonempty
          (ComponentAwareCoordinateReplacementInjection G c omega A i)

theorem deficientOwnerShoreCoordinateTransport_of_componentAware
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htransport :
      DeficientOwnerShoreComponentAwareCoordinateTransport G c bads) :
    DeficientOwnerShoreCoordinateTransport G c bads := by
  intro omega A hdefect i
  obtain ⟨T⟩ := htransport omega A hdefect i
  exact ⟨T.toReplacementInjection⟩

theorem deficientOwnerShoreVariationBound_of_coordinateTransport
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htransport : DeficientOwnerShoreCoordinateTransport G c bads)
    (hnontrivial : DeficientOwnerShoreHasNontrivialCoordinate G c bads) :
    DeficientOwnerShoreVariationBound G c bads := by
  intro omega A hdefect
  rw [oneRowVariation_eq_sum_coordinateVariations]
  calc
    (∑ i : Fin bads.length, oneCoordinateVariation G c omega i) ≤
        ∑ i : Fin bads.length,
          (Fintype.card (OneCoordinateAlternative omega i) : Int) *
            (((scopedOwnerSourceSet G c omega A).card : Int) -
              ((scopedOwnerDemandSet
                (G := G) (c := c) (omega := omega) A).card : Int)) := by
      apply Finset.sum_le_sum
      intro i _hi
      obtain ⟨T⟩ := htransport omega A hdefect i
      exact oneCoordinateVariation_le_of_replacementInjection
        G c omega A i T
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

def RealDeficientOwnerShoreCoordinateTransport
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    DeficientOwnerShoreCoordinateTransport G c bads

def RealDeficientOwnerShoreComponentAwareCoordinateTransport
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    DeficientOwnerShoreComponentAwareCoordinateTransport G c bads

def RealDeficientOwnerShoreHasNontrivialCoordinate
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    DeficientOwnerShoreHasNontrivialCoordinate G c bads

theorem realMinimumActiveScopedHall_of_coordinateTransport
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (htransport : RealDeficientOwnerShoreCoordinateTransport G c bads)
    (hnontrivial : RealDeficientOwnerShoreHasNontrivialCoordinate G c bads) :
    MinimumActiveScopedHall G c bads hdb.rowsNonempty := by
  apply realMinimumActiveScopedHall_of_ownerShoreVariationBound
    G c bads htri hmax hconn hdb
  intro _htri _hmax _hconn _hdb
  exact deficientOwnerShoreVariationBound_of_coordinateTransport
    G c bads
    (htransport htri hmax hconn hdb)
    (hnontrivial htri hmax hconn hdb)

theorem realMinimumActiveScopedHall_of_componentAwareCoordinateTransport
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (htransport :
      RealDeficientOwnerShoreComponentAwareCoordinateTransport G c bads)
    (hnontrivial : RealDeficientOwnerShoreHasNontrivialCoordinate G c bads) :
    MinimumActiveScopedHall G c bads hdb.rowsNonempty := by
  apply realMinimumActiveScopedHall_of_coordinateTransport
    G c bads htri hmax hconn hdb
  · intro _htri _hmax _hconn _hdb
    exact deficientOwnerShoreCoordinateTransport_of_componentAware
      G c bads (htransport htri hmax hconn hdb)
  · exact hnontrivial

/-- Exact existential form aligned with the max-flow gate: one matching
failure supplies one deficient owner shore, a nontrivial row coordinate, and
component-aware transports for every coordinate. -/
noncomputable def HallFailureHasComponentAwareCoordinateTransport
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ omega : RowChoice bads,
    ¬Nonempty (Matching G c omega) →
      ∃ A : Finset (Fin G.n),
        (scopedOwnerSourceSet G c omega A).card <
          (scopedOwnerDemandSet
            (G := G) (c := c) (omega := omega) A).card ∧
        0 < ∑ i : Fin bads.length,
          Fintype.card (OneCoordinateAlternative omega i) ∧
        ∀ i : Fin bads.length,
          Nonempty
            (ComponentAwareCoordinateReplacementInjection G c omega A i)

def RealHallFailureHasComponentAwareCoordinateTransport
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    HallFailureHasComponentAwareCoordinateTransport G c bads

theorem hallFailureHasNegativeVariation_of_componentAwareTransport
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htransport : HallFailureHasComponentAwareCoordinateTransport G c bads) :
    HallFailureHasNegativeOneRowVariation G c bads := by
  intro omega hfailure
  obtain ⟨A, hdefect, hnontrivial, hcoordinate⟩ :=
    htransport omega hfailure
  rw [oneRowVariation_eq_sum_coordinateVariations]
  calc
    (∑ i : Fin bads.length, oneCoordinateVariation G c omega i) ≤
        ∑ i : Fin bads.length,
          (Fintype.card (OneCoordinateAlternative omega i) : Int) *
            (((scopedOwnerSourceSet G c omega A).card : Int) -
              ((scopedOwnerDemandSet
                (G := G) (c := c) (omega := omega) A).card : Int)) := by
      apply Finset.sum_le_sum
      intro i _hi
      obtain ⟨T⟩ := hcoordinate i
      exact oneCoordinateVariation_le_of_replacementInjection
        G c omega A i T.toReplacementInjection
    _ = (∑ i : Fin bads.length,
          (Fintype.card (OneCoordinateAlternative omega i) : Int)) *
            (((scopedOwnerSourceSet G c omega A).card : Int) -
              ((scopedOwnerDemandSet
                (G := G) (c := c) (omega := omega) A).card : Int)) := by
      rw [Finset.sum_mul]
    _ < 0 := by
      have hfactor :
          (0 : Int) < ∑ i : Fin bads.length,
            (Fintype.card (OneCoordinateAlternative omega i) : Int) := by
        exact_mod_cast hnontrivial
      have hrhs :
          ((scopedOwnerSourceSet G c omega A).card : Int) -
              ((scopedOwnerDemandSet
                (G := G) (c := c) (omega := omega) A).card : Int) < 0 := by
        exact sub_neg.mpr (by exact_mod_cast hdefect)
      nlinarith

theorem realMinimumActiveScopedHall_of_failureComponentAwareTransport
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (htransport :
      RealHallFailureHasComponentAwareCoordinateTransport G c bads) :
    MinimumActiveScopedHall G c bads hdb.rowsNonempty := by
  apply realMinimumActiveScopedHall_of_negativeVariation
    G c bads htri hmax hconn hdb
  intro _htri _hmax _hconn _hdb
  exact hallFailureHasNegativeVariation_of_componentAwareTransport
    G c bads (htransport htri hmax hconn hdb)

end ActiveScopedMinimumExchange
end Gamma
end Erdos23Delta0
