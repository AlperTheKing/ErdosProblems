import Erdos23Delta0.Gamma.CheckedCollisionDefectTrade
import Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

/-!
# Graph adapter for checked collision defect

This module instantiates `CheckedCollisionDefectTrade.Data` at the literal
row-choice state space.  The obligation carrier is finite and independent of
the state, but its filtered inhabitants retain the complete R34 identity:
owner, other coordinate, producing bad atom, pair-occurrence ordinal, collision
copy, half, and active-component label.

No source-family completeness or collision feasibility is asserted here.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CollisionDefectGraphAdapter

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open ActiveScopedMinimumExchange

attribute [local instance] Classical.propDecidable

/-- Every literal row of a bad atom starts and ends at that atom's ordered
endpoint pair. -/
def RowEndpointAnchoring (bads : List BadEdgeData) : Prop :=
  forall (i : Fin bads.length) (j : Fin (bads.get i).rows.length),
    ((bads.get i).rows.get j).verts.head? = some (bads.get i).u ∧
      ((bads.get i).rows.get j).verts.getLast? = some (bads.get i).v

/-- Distinct database atoms have distinct normalized endpoint pairs. -/
def BadEndpointPairsDistinct (bads : List BadEdgeData) : Prop :=
  (bads.map badEdgeKey).Nodup

/-- The real row-geometry facts used by occurrence-level arguments. -/
structure RealRowGeometry (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) : Prop where
  rowEndpointAnchoring : RowEndpointAnchoring bads
  badEndpointPairsDistinct : BadEndpointPairsDistinct bads

theorem rowEndpointAnchoring_of_allBadsChecked
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) :
    RowEndpointAnchoring bads := by
  intro i j
  have hb := List.all_eq_true.mp hchecked (bads.get i) (List.get_mem bads i)
  unfold checkBadEdge at hb
  simp only [Bool.and_eq_true] at hb
  have hr := List.all_eq_true.mp hb.2 _ (List.get_mem (bads.get i).rows j)
  unfold checkRow5 at hr
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hr
  exact ⟨hr.1.1.1.2, hr.1.1.2⟩

theorem RealRowGeometry.of_completeShortestRowDB
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hdb : CompleteShortestRowDB G c bads) :
    RealRowGeometry G c bads where
  rowEndpointAnchoring :=
    rowEndpointAnchoring_of_allBadsChecked hdb.checked
  badEndpointPairsDistinct := hdb.badKeys_nodup

/-- The actual selected-row endpoints, compiled from the checked database. -/
theorem selectedRow_endpoints
    {bads : List BadEdgeData} (hanchor : RowEndpointAnchoring bads)
    (omega : RowChoice bads) (i : Fin bads.length) :
    ((bads.get i).rows.get (omega i)).verts.head? = some (bads.get i).u ∧
      ((bads.get i).rows.get (omega i)).verts.getLast? = some (bads.get i).v :=
  hanchor i (omega i)

theorem badEdgeKey_get_injective
    {bads : List BadEdgeData} (hdistinct : BadEndpointPairsDistinct bads) :
    Function.Injective fun i : Fin bads.length => badEdgeKey (bads.get i) := by
  intro i j hij
  let i' : Fin (bads.map badEdgeKey).length :=
    ⟨i.1, by rw [List.length_map]; exact i.2⟩
  let j' : Fin (bads.map badEdgeKey).length :=
    ⟨j.1, by rw [List.length_map]; exact j.2⟩
  have hget : (bads.map badEdgeKey).get i' =
      (bads.map badEdgeKey).get j' := by
    simpa [i', j'] using hij
  have hindex : i' = j' :=
    (List.Nodup.get_inj_iff hdistinct).mp hget
  have hval : i'.val = j'.val := congrArg
    (fun k : Fin (bads.map badEdgeKey).length => k.val) hindex
  exact Fin.ext (by simpa [i', j'] using hval)

/-- Endpoint anchoring plus distinct bad-edge endpoint pairs rules out the R34
parallel-atom degeneracy: two selected rows are equal only for the same atom. -/
theorem selectedRow_injective
    {bads : List BadEdgeData} (hanchor : RowEndpointAnchoring bads)
    (hdistinct : BadEndpointPairsDistinct bads) (omega : RowChoice bads) :
    Function.Injective fun i : Fin bads.length =>
      (bads.get i).rows.get (omega i) := by
  intro i j hrow
  change (bads.get i).rows.get (omega i) =
    (bads.get j).rows.get (omega j) at hrow
  have hi := selectedRow_endpoints hanchor omega i
  have hj := selectedRow_endpoints hanchor omega j
  have hu : (bads.get i).u = (bads.get j).u := by
    apply Option.some.inj
    calc
      some (bads.get i).u =
          ((bads.get i).rows.get (omega i)).verts.head? := hi.1.symm
      _ = ((bads.get j).rows.get (omega j)).verts.head? :=
        congrArg (fun row : Row5 => row.verts.head?) hrow
      _ = some (bads.get j).u := hj.1
  have hv : (bads.get i).v = (bads.get j).v := by
    apply Option.some.inj
    calc
      some (bads.get i).v =
          ((bads.get i).rows.get (omega i)).verts.getLast? := hi.2.symm
      _ = ((bads.get j).rows.get (omega j)).verts.getLast? :=
        congrArg (fun row : Row5 => row.verts.getLast?) hrow
      _ = some (bads.get j).v := hj.2
  apply badEdgeKey_get_injective hdistinct
  change normEdge (bads.get i).u (bads.get i).v =
    normEdge (bads.get j).u (bads.get j).v
  rw [hu, hv]

/-- The real active selected component, represented by its full reachable
vertex set in the selected off-support graph. -/
noncomputable def activeSelectedComponent (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) (v : Fin G.n) :
    Finset (Fin G.n) :=
  Finset.univ.filter fun w => (activeGraph G c omega).Reachable v w

/-- Canonical finite identity of the real active selected component. -/
noncomputable def activeComponentLabel (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) (v : Fin G.n) :
    Fin G.n :=
  (activeSelectedComponent G c omega v).min' (by
    exact ⟨v, by simp [activeSelectedComponent]⟩)

@[simp] theorem mem_activeSelectedComponent_iff
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (v w : Fin G.n) :
    w ∈ activeSelectedComponent G c omega v ↔
      (activeGraph G c omega).Reachable v w := by
  simp [activeSelectedComponent]

theorem activeComponentLabel_mem
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (v : Fin G.n) :
    activeComponentLabel G c omega v ∈
      activeSelectedComponent G c omega v := by
  exact Finset.min'_mem _ _

/-- The canonical label identifies exactly the connected component in the
actual selected active graph. -/
theorem activeComponentLabel_eq_iff_reachable
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (v w : Fin G.n) :
    activeComponentLabel G c omega v = activeComponentLabel G c omega w ↔
      (activeGraph G c omega).Reachable v w := by
  constructor
  · intro hlabel
    have hv := (mem_activeSelectedComponent_iff G c omega v _).mp
      (activeComponentLabel_mem G c omega v)
    have hw := (mem_activeSelectedComponent_iff G c omega w _).mp
      (activeComponentLabel_mem G c omega w)
    exact hv.trans (hlabel ▸ hw.symm)
  · intro hvw
    have hcomponents :
        activeSelectedComponent G c omega v =
          activeSelectedComponent G c omega w := by
      ext x
      simp only [mem_activeSelectedComponent_iff]
      constructor
      · exact fun hvx => hvw.symm.trans hvx
      · exact fun hwx => hvw.trans hwx
    unfold activeComponentLabel
    apply le_antisymm
    · apply Finset.min'_le
      rw [hcomponents]
      exact Finset.min'_mem _ _
    · apply Finset.min'_le
      rw [← hcomponents]
      exact Finset.min'_mem _ _

/-- Fixed finite R34 collision-obligation carrier.  State dependence appears
only in the validity filter below. -/
structure CollisionObligation (G : GraphData) (bads : List BadEdgeData) where
  owner : Fin G.n
  other : Fin G.n
  producerAtom : Fin bads.length
  occurrence : Fin bads.length
  copy : Fin bads.length
  half : Fin 2
  component : Fin G.n
deriving DecidableEq

private abbrev CollisionObligationCode
    (G : GraphData) (bads : List BadEdgeData) :=
  (Fin G.n × Fin G.n) ×
    (Fin bads.length × Fin bads.length × Fin bads.length) ×
      (Fin 2 × Fin G.n)

private def collisionObligationEquivCode
    (G : GraphData) (bads : List BadEdgeData) :
    CollisionObligation G bads ≃ CollisionObligationCode G bads where
  toFun d := ((d.owner, d.other),
    (d.producerAtom, d.occurrence, d.copy), (d.half, d.component))
  invFun d :=
    { owner := d.1.1
      other := d.1.2
      producerAtom := d.2.1.1
      occurrence := d.2.1.2.1
      copy := d.2.1.2.2
      half := d.2.2.1
      component := d.2.2.2 }
  left_inv d := by cases d; rfl
  right_inv d := by
    rcases d with ⟨⟨owner, other⟩, ⟨producer, occurrence, copy⟩,
      ⟨half, component⟩⟩
    rfl

noncomputable instance collisionObligationFintype
    (G : GraphData) (bads : List BadEdgeData) :
    Fintype (CollisionObligation G bads) :=
  Fintype.ofEquiv (CollisionObligationCode G bads)
    (collisionObligationEquivCode G bads).symm

/-- Selected bad atoms whose chosen rows contain both ordered coordinates, in
database order. -/
def pairOccurrenceAtoms {bads : List BadEdgeData} (omega : RowChoice bads)
    (owner other : Nat) : List (Fin bads.length) :=
  (List.finRange bads.length).filter fun i =>
    decide (owner ∈ ((bads.get i).rows.get (omega i)).verts ∧
      other ∈ ((bads.get i).rows.get (omega i)).verts)

private theorem length_filter_map {alpha beta : Type*}
    (f : alpha → beta) (p : beta → Bool) (l : List alpha) :
    ((l.map f).filter p).length =
      (l.filter fun x => p (f x)).length := by
  induction l with
  | nil => simp
  | cons x xs ih =>
      cases h : p (f x) <;> simp [h, ih]

theorem pairOccurrenceAtoms_length
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (owner other : Nat) :
    (pairOccurrenceAtoms omega owner other).length =
      pairCount omega owner other := by
  unfold pairOccurrenceAtoms pairCount selectedRows
  rw [List.ofFn_eq_map, length_filter_map]

theorem pairCount_le_bads_length
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (owner other : Nat) :
    pairCount omega owner other ≤ bads.length := by
  unfold pairCount
  calc
    ((selectedRows omega).filter fun row =>
      decide (owner ∈ row.verts ∧ other ∈ row.verts)).length ≤
        (selectedRows omega).length := List.length_filter_le _ _
    _ = bads.length := selectedRows_length omega

/-- Exact state-dependent validity predicate for the fixed ambient carrier.
The positive occurrence ordinal skips occurrence zero, so its predecessor is
the dependent `CollisionHalf.copy`. -/
structure IsActiveObligation (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (d : CollisionObligation G bads) : Prop where
  copy_lt : d.copy.1 < pairCount omega d.owner.1 d.other.1 - 1
  occurrence_eq : d.occurrence.1 = d.copy.1 + 1
  producerAtom_eq :
    (pairOccurrenceAtoms omega d.owner.1 d.other.1)[d.occurrence.1]? =
      some d.producerAtom
  active_owner : ActiveOwner G c omega d.owner
  component_eq :
    d.component = activeComponentLabel G c omega d.owner

/-- The state's concrete collision obligations, obtained by filtering the
fixed ambient R34 carrier. -/
noncomputable def obligations (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) :
    Finset (CollisionObligation G bads) :=
  Finset.univ.filter (IsActiveObligation G c omega)

@[simp] theorem mem_obligations_iff
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (d : CollisionObligation G bads) :
    d ∈ obligations G c omega ↔ IsActiveObligation G c omega d := by
  simp [obligations]

private theorem copy_lt_bads_length
    {G : GraphData} {bads : List BadEdgeData} (omega : RowChoice bads)
    (d : CollisionHalf G omega) : d.copy.1 < bads.length := by
  have hcount := pairCount_le_bads_length omega d.owner.1 d.other.1
  omega

private theorem successor_copy_lt_bads_length
    {G : GraphData} {bads : List BadEdgeData} (omega : RowChoice bads)
    (d : CollisionHalf G omega) : d.copy.1 + 1 < bads.length := by
  have hcount := pairCount_le_bads_length omega d.owner.1 d.other.1
  omega

private theorem successor_copy_lt_occurrence_length
    {G : GraphData} {bads : List BadEdgeData} (omega : RowChoice bads)
    (d : CollisionHalf G omega) :
    d.copy.1 + 1 <
      (pairOccurrenceAtoms omega d.owner.1 d.other.1).length := by
  rw [pairOccurrenceAtoms_length]
  omega

private def ambientCopy {G : GraphData} {bads : List BadEdgeData}
    (omega : RowChoice bads) (d : CollisionHalf G omega) : Fin bads.length :=
  ⟨d.copy.1, copy_lt_bads_length omega d⟩

private def repeatedOccurrence {G : GraphData} {bads : List BadEdgeData}
    (omega : RowChoice bads) (d : CollisionHalf G omega) : Fin bads.length :=
  ⟨d.copy.1 + 1, successor_copy_lt_bads_length omega d⟩

private def repeatedProducerAtom {G : GraphData} {bads : List BadEdgeData}
    (omega : RowChoice bads) (d : CollisionHalf G omega) : Fin bads.length :=
  (pairOccurrenceAtoms omega d.owner.1 d.other.1).get
    ⟨d.copy.1 + 1, successor_copy_lt_occurrence_length omega d⟩

/-- Enrich a real dependent collision debit with its canonical positive
occurrence, producing atom, and real active-component label. -/
noncomputable def ofReal
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (d : ActiveCollisionHalf G c omega) :
    CollisionObligation G bads where
  owner := d.1.owner
  other := d.1.other
  producerAtom := repeatedProducerAtom omega d.1
  occurrence := repeatedOccurrence omega d.1
  copy := ambientCopy omega d.1
  half := d.1.half
  component := activeComponentLabel G c omega d.1.owner

theorem ofReal_isActive
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (d : ActiveCollisionHalf G c omega) :
    IsActiveObligation G c omega (ofReal G c omega d) := by
  refine
    { copy_lt := d.1.copy.isLt
      occurrence_eq := rfl
      producerAtom_eq := ?_
      active_owner := d.2
      component_eq := rfl }
  change
    (pairOccurrenceAtoms omega d.1.owner.1 d.1.other.1)[d.1.copy.1 + 1]? =
      some (repeatedProducerAtom omega d.1)
  unfold repeatedProducerAtom
  rw [List.getElem?_eq_getElem
    (successor_copy_lt_occurrence_length omega d.1)]
  rw [List.get_eq_getElem]

/-- Forget the ambient bounds and recover the actual dependent collision
debit. -/
def toReal
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (d : CollisionObligation G bads)
    (hd : IsActiveObligation G c omega d) :
    ActiveCollisionHalf G c omega :=
  ⟨{
    owner := d.owner
    other := d.other
    copy := ⟨d.copy.1, hd.copy_lt⟩
    half := d.half
  }, hd.active_owner⟩

private theorem repeatedProducerAtom_toReal
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (d : CollisionObligation G bads)
    (hd : IsActiveObligation G c omega d) :
    repeatedProducerAtom omega (toReal G c omega d hd).1 =
      d.producerAtom := by
  have hproducer := hd.producerAtom_eq
  have hcopy := hd.copy_lt
  have hlt : d.copy.1 + 1 <
      (pairOccurrenceAtoms omega d.owner.1 d.other.1).length := by
    rw [pairOccurrenceAtoms_length]
    omega
  rw [hd.occurrence_eq, List.getElem?_eq_getElem hlt] at hproducer
  exact Option.some.inj hproducer

@[ext] theorem CollisionObligation.ext
    {G : GraphData} {bads : List BadEdgeData}
    {d e : CollisionObligation G bads}
    (howner : d.owner = e.owner) (hother : d.other = e.other)
    (hproducer : d.producerAtom = e.producerAtom)
    (hoccurrence : d.occurrence = e.occurrence)
    (hcopy : d.copy = e.copy) (hhalf : d.half = e.half)
    (hcomponent : d.component = e.component) : d = e := by
  cases d
  cases e
  simp_all

theorem ofReal_toReal
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (d : CollisionObligation G bads)
    (hd : IsActiveObligation G c omega d) :
    ofReal G c omega (toReal G c omega d hd) = d := by
  apply CollisionObligation.ext
  · rfl
  · rfl
  · exact repeatedProducerAtom_toReal G c omega d hd
  · exact Fin.ext hd.occurrence_eq.symm
  · rfl
  · rfl
  · exact hd.component_eq.symm

theorem toReal_ofReal
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (d : ActiveCollisionHalf G c omega) :
    toReal G c omega (ofReal G c omega d) (ofReal_isActive G c omega d) = d := by
  cases d with
  | mk d hd =>
      cases d
      rfl

/-- Exact equivalence between filtered ambient obligations and the real
state-dependent active collision debit halves. -/
noncomputable def obligationEquivReal
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    {d // d ∈ obligations G c omega} ≃ ActiveCollisionHalf G c omega where
  toFun d := toReal G c omega d.1 (mem_obligations_iff G c omega d.1 |>.mp d.2)
  invFun d := ⟨ofReal G c omega d,
    mem_obligations_iff G c omega _ |>.mpr (ofReal_isActive G c omega d)⟩
  left_inv d := by
    apply Subtype.ext
    exact ofReal_toReal G c omega d.1
      (mem_obligations_iff G c omega d.1 |>.mp d.2)
  right_inv d := toReal_ofReal G c omega d

theorem obligations_card_eq_realCollisionHalf_card
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    (obligations G c omega).card =
      Fintype.card (ActiveCollisionHalf G c omega) := by
  classical
  rw [← Fintype.card_coe]
  exact Fintype.card_congr (obligationEquivReal G c omega)

/-- Fixed source base; state-dependent freeness is retained in the witness
inside `sourceRealized`. -/
structure SourceBase (G : GraphData) where
  sourceX : Fin G.n
  sourceY : Fin G.n
deriving DecidableEq, Fintype

/-- Caller-supplied graph relations for the exact no-common-blue source union.
Each field is a proposition on a real active debit and a real free source. -/
structure NoCommonBlueSourceRelations (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) where
  p1 : forall (omega : RowChoice bads),
    ActiveCollisionHalf G c omega → FreeHalf G omega → Prop
  p3 : forall (omega : RowChoice bads),
    ActiveCollisionHalf G c omega → FreeHalf G omega → Prop
  strictP4 : forall (omega : RowChoice bads),
    ActiveCollisionHalf G c omega → FreeHalf G omega → Prop
  p5 : forall (omega : RowChoice bads),
    ActiveCollisionHalf G c omega → FreeHalf G omega → Prop

/-- The exact four-family union.  Common-blue is intentionally absent. -/
def NoCommonBlueSourceRelations.Realized
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (R : NoCommonBlueSourceRelations G c bads)
    (omega : RowChoice bads) (d : ActiveCollisionHalf G c omega)
    (s : FreeHalf G omega) : Prop :=
  ¬ScopedReserved G c omega s ∧
    (R.p1 omega d s ∨ R.p3 omega d s ∨
      R.strictP4 omega d s ∨ R.p5 omega d s)

def sourceKey {G : GraphData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (s : FreeHalf G omega) : SourceBase G × Fin 2 :=
  (⟨s.sourceX, s.sourceY⟩, s.half)

/-- Exact graph-facing realization predicate used by the abstract defect data.
It exposes a real `FreeHalf` witness and the P1/P3/strict-P4/P5 disjunction. -/
def sourceRealized
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (R : NoCommonBlueSourceRelations G c bads)
    (omega : RowChoice bads) (d : CollisionObligation G bads)
    (key : SourceBase G × Fin 2) : Prop :=
  ∃ hd : d ∈ obligations G c omega,
    ∃ s : FreeHalf G omega,
      sourceKey s = key ∧
        R.Realized omega ((obligationEquivReal G c omega) ⟨d, hd⟩) s

/-- Concrete `CheckedCollisionDefectTrade` data over the real row-choice state
space. -/
noncomputable def defectData
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads) :
    CheckedCollisionDefectTrade.Data
      (RowChoice bads) (CollisionObligation G bads)
      (SourceBase G) (Fin G.n) where
  obligations := obligations G c
  component := fun _ d => d.component
  sourceRealized := sourceRealized G c R

/-- A genuinely total assignment on the filtered ambient obligations. -/
structure TotalCoherentAssignment
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (R : NoCommonBlueSourceRelations G c bads)
    (omega : RowChoice bads) where
  assign : {d // d ∈ obligations G c omega} ↪ (SourceBase G × Fin 2)
  source_realized : forall d,
    sourceRealized G c R omega d.1 (assign d)
  base_component_coherent :
    Pattern5StaticOwnership.BaseKeyComponentCoherent assign
      (fun d => d.1.component)

private noncomputable def TotalCoherentAssignment.toPartial
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads} {omega : RowChoice bads}
    (A : TotalCoherentAssignment G c R omega) :
    CheckedCollisionDefectTrade.CoherentPartialMatching
      (defectData G c bads R) omega where
  matched := obligations G c omega
  matched_subset := Finset.Subset.rfl
  assign := A.assign
  source_realized := A.source_realized
  base_component_coherent := A.base_component_coherent

private noncomputable def TotalCoherentAssignment.ofPartialTotal
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads} {omega : RowChoice bads}
    (M : CheckedCollisionDefectTrade.CoherentPartialMatching
      (defectData G c bads R) omega)
    (htotal : M.matched = obligations G c omega) :
    TotalCoherentAssignment G c R omega where
  assign :=
    { toFun := fun d => M.assign ⟨d.1, by rw [htotal]; exact d.2⟩
      inj' := by
        intro d e h
        have hsub :
            (⟨d.1, by rw [htotal]; exact d.2⟩ : {x // x ∈ M.matched}) =
              ⟨e.1, by rw [htotal]; exact e.2⟩ := M.assign.injective h
        have hval : d.1 = e.1 := congrArg
          (fun z : {x // x ∈ M.matched} => z.1) hsub
        exact Subtype.ext hval }
  source_realized := by
    intro d
    exact M.source_realized ⟨d.1, by rw [htotal]; exact d.2⟩
  base_component_coherent := by
    intro d e hbase
    exact M.base_component_coherent
      ⟨d.1, by rw [htotal]; exact d.2⟩
      ⟨e.1, by rw [htotal]; exact e.2⟩ hbase

/-- Zero checked collision defect is exactly a total coherent assignment for
the concrete filtered graph obligations. -/
theorem collisionDefect_eq_zero_iff_total
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (R : NoCommonBlueSourceRelations G c bads)
    (omega : RowChoice bads) :
    (defectData G c bads R).collisionDefect omega = 0 ↔
      Nonempty (TotalCoherentAssignment G c R omega) := by
  rw [CheckedCollisionDefectTrade.Data.collisionDefect_eq_zero_iff_exists_total]
  constructor
  · rintro ⟨M, htotal⟩
    exact ⟨TotalCoherentAssignment.ofPartialTotal M htotal⟩
  · rintro ⟨A⟩
    exact ⟨A.toPartial, rfl⟩

/-- Named graph frontier left after this adapter: under the real graph and
complete-row hypotheses, choose a row state with a total coherent assignment
for the explicit no-common-blue union. -/
def NoCommonBlueCollisionFeasibility
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads) : Prop :=
  TriangleFree G → IsMaxCut G c → BConnected G c →
    CompleteShortestRowDB G c bads →
      ∃ omega : RowChoice bads,
        Nonempty (TotalCoherentAssignment G c R omega)

theorem exists_zero_collisionDefect_of_feasibility
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads)
    (hfeasible : NoCommonBlueCollisionFeasibility G c bads R)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconnected : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads) :
    ∃ omega : RowChoice bads,
      (defectData G c bads R).collisionDefect omega = 0 := by
  obtain ⟨omega, htotal⟩ := hfeasible htri hmax hconnected hdb
  exact ⟨omega,
    (collisionDefect_eq_zero_iff_total G c R omega).mpr htotal⟩

theorem exists_zero_collisionDefect_iff_exists_total
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads) :
    (∃ omega : RowChoice bads,
      (defectData G c bads R).collisionDefect omega = 0) ↔
    (∃ omega : RowChoice bads,
      Nonempty (TotalCoherentAssignment G c R omega)) := by
  constructor <;> rintro ⟨omega, homega⟩
  · exact ⟨omega, (collisionDefect_eq_zero_iff_total G c R omega).mp homega⟩
  · exact ⟨omega, (collisionDefect_eq_zero_iff_total G c R omega).mpr homega⟩

#print axioms rowEndpointAnchoring_of_allBadsChecked
#print axioms obligationEquivReal
#print axioms obligations_card_eq_realCollisionHalf_card
#print axioms collisionDefect_eq_zero_iff_total
#print axioms exists_zero_collisionDefect_of_feasibility
#print axioms exists_zero_collisionDefect_iff_exists_total

end CollisionDefectGraphAdapter
end Gamma
end Erdos23Delta0
