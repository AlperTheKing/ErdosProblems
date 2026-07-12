import Erdos23Delta0.Gamma.CheckedSoftCollisionTwoCover
import Erdos23Delta0.Gamma.SaturatedRotorSupportPersistence

/-!
# Typed graph adapter for adaptive active-edge caps

This module identifies the abstract shores in `CheckedSoftCollisionTwoCover`
with the production `CollisionHalf` and proof-carrying `FreeHalf` types.
It proves only cardinality, freeness, and partition facts. In particular, it
does not assert that a supported flow exists.
-/

namespace Erdos23Delta0
namespace Gamma
namespace SoftEdgeCapGraphAdapter

open scoped BigOperators
open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

/-! ## Global collision shore -/

def collisionHalfEquiv (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    CollisionHalf G omega ≃
      Sigma fun x : Fin G.n =>
        Sigma fun y : Fin G.n =>
          Fin (pairCount omega x.1 y.1 - 1) × Fin 2 where
  toFun d := ⟨d.owner, d.other, d.copy, d.half⟩
  invFun d :=
    { owner := d.1
      other := d.2.1
      copy := d.2.2.1
      half := d.2.2.2 }
  left_inv d := by cases d; rfl
  right_inv d := by rcases d with ⟨x, y, copy, half⟩; rfl

theorem fin_sum_eq_list_range_sum {n : Nat} (f : Nat → Nat) :
    (∑ i : Fin n, f i.1) = ((List.range n).map f).sum := by
  rw [Finset.sum_fin_eq_sum_range]
  rw [← List.sum_toFinset f List.nodup_range]
  simp only [List.toFinset_range]
  apply Finset.sum_congr rfl
  intro i hi
  simp only [Finset.mem_range] at hi
  simp [hi]

theorem collisionUnits_eq_fin_sum
    (G : GraphData) {bads : List BadEdgeData} (omega : RowChoice bads) :
    collisionUnits G omega =
      ∑ x : Fin G.n, ∑ y : Fin G.n,
        (pairCount omega x.1 y.1 - 1) := by
  symm
  exact calc
    (∑ x : Fin G.n, ∑ y : Fin G.n,
        (pairCount omega x.1 y.1 - 1)) =
        ∑ x : Fin G.n,
          ((List.range G.n).map fun y =>
            pairCount omega x.1 y - 1).sum := by
      apply Finset.sum_congr rfl
      intro x _
      exact fin_sum_eq_list_range_sum (n := G.n)
        (fun y => pairCount omega x.1 y - 1)
    _ = ((List.range G.n).map fun x =>
          ((List.range G.n).map fun y =>
            pairCount omega x y - 1).sum).sum := by
      exact fin_sum_eq_list_range_sum (n := G.n)
        (fun x => ((List.range G.n).map fun y =>
          pairCount omega x y - 1).sum)
    _ = collisionUnits G omega := rfl

theorem collisionHalf_card_eq_two_mul_collisionUnits
    (G : GraphData) {bads : List BadEdgeData} (omega : RowChoice bads) :
    Fintype.card (CollisionHalf G omega) = 2 * collisionUnits G omega := by
  calc
    Fintype.card (CollisionHalf G omega) =
        ∑ x : Fin G.n, ∑ y : Fin G.n,
          2 * (pairCount omega x.1 y.1 - 1) := by
      rw [Fintype.card_congr (collisionHalfEquiv G omega)]
      simp [Fintype.card_sigma, Fintype.card_prod, Nat.mul_comm]
    _ = 2 * (∑ x : Fin G.n, ∑ y : Fin G.n,
          (pairCount omega x.1 y.1 - 1)) := by
      simp only [Finset.mul_sum]
    _ = 2 * collisionUnits G omega := by
      rw [← collisionUnits_eq_fin_sum]

theorem collisionMass_pairCount_eq_collisionUnits
    (G : GraphData) {bads : List BadEdgeData} (omega : RowChoice bads) :
    CollisionResidualIdentity.collisionMass
        (fun x y : Fin G.n => pairCount omega x.1 y.1) =
      (collisionUnits G omega : Int) := by
  unfold CollisionResidualIdentity.collisionMass
  have h := collisionUnits_eq_fin_sum G omega
  exact_mod_cast h.symm

theorem collisionHalf_card_eq_two_mul_collisionMass
    (G : GraphData) {bads : List BadEdgeData} (omega : RowChoice bads) :
    (Fintype.card (CollisionHalf G omega) : Int) =
      2 * CollisionResidualIdentity.collisionMass
        (fun x y : Fin G.n => pairCount omega x.1 y.1) := by
  rw [collisionMass_pairCount_eq_collisionUnits]
  exact_mod_cast collisionHalf_card_eq_two_mul_collisionUnits G omega

/-! ## Active edges are free in both orientations -/

abbrev ActiveEdge (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) :=
  ↥(activeEdges G c omega).toFinset

theorem activeEdge_mem_activeEdges
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (e : ActiveEdge G c omega) :
    e.1 ∈ activeEdges G c omega := by
  have he : e.1 ∈ (activeEdges G c omega).toFinset := e.2
  exact List.mem_toFinset.mp he

theorem activeEdge_facts
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (e : ActiveEdge G c omega) :
    e.1 ∈ G.edges ∧
      e.1.1 ∈ selectedVertices omega ∧
      e.1.2 ∈ selectedVertices omega ∧
      blueb G c e.1.1 e.1.2 = true ∧
      normEdge e.1.1 e.1.2 ∉ selectedSupport omega := by
  have he := activeEdge_mem_activeEdges e
  unfold activeEdges at he
  have he' := List.mem_filter.mp he
  rcases he' with ⟨hgraph, hpred⟩
  simp only [Bool.and_eq_true] at hpred
  have hv1b := hpred.1.1.1
  have hv2b := hpred.1.1.2
  have hblue := hpred.1.2
  have hoffb := hpred.2
  have hv1 := of_decide_eq_true hv1b
  have hv2 := of_decide_eq_true hv2b
  have hfalse :
      decide (normEdge e.1.1 e.1.2 ∈ selectedSupport omega) = false := by
    cases hdec : decide (normEdge e.1.1 e.1.2 ∈ selectedSupport omega) with
    | false => rfl
    | true => simp [hdec] at hoffb
  have hoff := of_decide_eq_false hfalse
  exact ⟨hgraph, hv1, hv2, hblue, hoff⟩

theorem activeEdges_nodup
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (hG : checkGraph G = true) :
    (activeEdges G c omega).Nodup := by
  unfold activeEdges
  exact (checkGraph_edges_nodup G hG).filter _

theorem activeEdge_card_eq_activeEdges_length
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (hG : checkGraph G = true) :
    Fintype.card (ActiveEdge G c omega) = (activeEdges G c omega).length := by
  calc
    Fintype.card (ActiveEdge G c omega) =
        (activeEdges G c omega).toFinset.card := Fintype.card_coe _
    _ = (activeEdges G c omega).length :=
      List.toFinset_card_of_nodup
        (activeEdges_nodup (c := c) (omega := omega) hG)

theorem pairCount_comm {bads : List BadEdgeData}
    (omega : RowChoice bads) (x y : Nat) :
    pairCount omega x y = pairCount omega y x := by
  unfold pairCount
  congr 2
  funext row
  simp only [and_comm]

/-- A selected-row co-occurrence would force this active blue edge into the
selected path support, contradicting the definition of `activeEdges`. -/
theorem activeEdge_pairCount_eq_zero
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (htri : TriangleFree G) (hchecked : AllBadsChecked G c bads)
    (omega : RowChoice bads) (e : ActiveEdge G c omega) :
    pairCount omega e.1.1 e.1.2 = 0 := by
  by_contra hne
  have hpos : 0 < pairCount omega e.1.1 e.1.2 := Nat.pos_of_ne_zero hne
  rw [ActiveScopedMinimumExchange.pairCount_eq_card_filter] at hpos
  rcases Finset.card_pos.mp hpos with ⟨i, hi⟩
  have hi' := (Finset.mem_filter.mp hi).2
  have hb := List.all_eq_true.mp hchecked
    (bads.get i) (List.get_mem bads i)
  unfold checkBadEdge at hb
  simp only [Bool.and_eq_true] at hb
  have hcheck : checkRow5 G c (bads.get i).u (bads.get i).v
      ((bads.get i).rows.get (omega i)) = true :=
    List.all_eq_true.mp hb.2 _
      (List.get_mem (bads.get i).rows (omega i))
  have hpath :=
    SaturatedRotorSupportPersistence.checkedRow_blue_cooccur_implies_pathEdge
      htri hcheck hi'.1 hi'.2 (activeEdge_facts e).2.2.2.1
  have hrow : (bads.get i).rows.get (omega i) ∈ selectedRows omega := by
    simp [selectedRows]
  have hsupport : normEdge e.1.1 e.1.2 ∈ selectedSupport omega := by
    unfold selectedSupport
    rw [List.mem_dedup]
    exact List.mem_flatMap.mpr ⟨_, hrow, hpath⟩
  exact (activeEdge_facts e).2.2.2.2 hsupport

theorem activeEdge_reverse_pairCount_eq_zero
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (htri : TriangleFree G) (hchecked : AllBadsChecked G c bads)
    (omega : RowChoice bads) (e : ActiveEdge G c omega) :
    pairCount omega e.1.2 e.1.1 = 0 := by
  rw [pairCount_comm]
  exact activeEdge_pairCount_eq_zero htri hchecked omega e

/-! ## Proof-carrying free bases -/

structure FreeBase (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) where
  sourceX : Fin G.n
  sourceY : Fin G.n
  distinct : sourceX ≠ sourceY
  free : pairCount omega sourceX.1 sourceY.1 = 0
deriving DecidableEq, Fintype

@[ext] theorem FreeBase.ext
    {G : GraphData} {bads : List BadEdgeData} {omega : RowChoice bads}
    {a b : FreeBase G omega}
    (hx : a.sourceX = b.sourceX) (hy : a.sourceY = b.sourceY) : a = b := by
  cases a
  cases b
  simp_all

def freeHalfEquivBaseHalf (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    FreeHalf G omega ≃ FreeBase G omega × Fin 2 where
  toFun s :=
    ({ sourceX := s.sourceX
       sourceY := s.sourceY
       distinct := s.distinct
       free := s.free }, s.half)
  invFun s :=
    { sourceX := s.1.sourceX
      sourceY := s.1.sourceY
      half := s.2
      distinct := s.1.distinct
      free := s.1.free }
  left_inv s := by cases s; rfl
  right_inv s := by rcases s with ⟨b, half⟩; cases b; rfl

abbrev FreeOrderedBase (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :=
  {p : Fin G.n × Fin G.n // pairCount omega p.1.1 p.2.1 = 0}

def freeBaseEmbedding (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    FreeBase G omega ↪ FreeOrderedBase G omega where
  toFun b := ⟨(b.sourceX, b.sourceY), b.free⟩
  inj' := by
    intro a b hab
    apply FreeBase.ext
    · exact congrArg (fun p => p.1.1) hab
    · exact congrArg (fun p => p.1.2) hab

theorem freeOrderedBase_card_eq_freeMass
    (G : GraphData) {bads : List BadEdgeData} (omega : RowChoice bads) :
    (Fintype.card (FreeOrderedBase G omega) : Int) =
      CollisionResidualIdentity.freeMass
        (fun x y : Fin G.n => pairCount omega x.1 y.1) := by
  unfold CollisionResidualIdentity.freeMass
  have hnat : Fintype.card (FreeOrderedBase G omega) =
      ∑ x : Fin G.n, ∑ y : Fin G.n,
        if pairCount omega x.1 y.1 = 0 then 1 else 0 := by
    rw [Fintype.card_subtype]
    rw [Finset.card_eq_sum_ones, Finset.sum_filter]
    simp only [Fintype.sum_prod_type]
  exact_mod_cast hnat

theorem freeBase_card_le_freeMass
    (G : GraphData) {bads : List BadEdgeData} (omega : RowChoice bads) :
    (Fintype.card (FreeBase G omega) : Int) ≤
      CollisionResidualIdentity.freeMass
        (fun x y : Fin G.n => pairCount omega x.1 y.1) := by
  rw [← freeOrderedBase_card_eq_freeMass]
  have hnat := Fintype.card_le_of_injective (freeBaseEmbedding G omega)
    (freeBaseEmbedding G omega).injective
  exact_mod_cast hnat

theorem activeEdge_endpoint_lt
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (hG : checkGraph G = true)
    (e : ActiveEdge G c omega) :
    e.1.1 < G.n ∧ e.1.2 < G.n := by
  have hrange := checkGraph_edge_range G hG e.1 (activeEdge_facts e).1
  exact ⟨lt_trans hrange.1 hrange.2, hrange.2⟩

theorem activeEdge_normalized
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (hG : checkGraph G = true)
    (e : ActiveEdge G c omega) :
    normEdge e.1.1 e.1.2 = e.1 := by
  have hrange := checkGraph_edge_range G hG e.1 (activeEdge_facts e).1
  simp [normEdge, hrange.1]

def activeFreeBase
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (e : ActiveEdge G c omega) (orientation : Fin 2) : FreeBase G omega :=
  let u : Fin G.n := ⟨e.1.1, (activeEdge_endpoint_lt hG e).1⟩
  let v : Fin G.n := ⟨e.1.2, (activeEdge_endpoint_lt hG e).2⟩
  if orientation = 0 then
    { sourceX := u
      sourceY := v
      distinct := by
        intro huv
        have := congrArg Fin.val huv
        have hlt := (checkGraph_edge_range G hG e.1 (activeEdge_facts e).1).1
        simp [u, v] at this
        omega
      free := activeEdge_pairCount_eq_zero htri hchecked omega e }
  else
    { sourceX := v
      sourceY := u
      distinct := by
        intro hvu
        have := congrArg Fin.val hvu
        have hlt := (checkGraph_edge_range G hG e.1 (activeEdge_facts e).1).1
        simp [u, v] at this
        omega
      free := activeEdge_reverse_pairCount_eq_zero htri hchecked omega e }

theorem activeFreeBase_normEdge
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (e : ActiveEdge G c omega) (orientation : Fin 2) :
    normEdge (activeFreeBase hG htri hchecked omega e orientation).sourceX.1
        (activeFreeBase hG htri hchecked omega e orientation).sourceY.1 = e.1 := by
  by_cases horientation : orientation = 0
  · simpa [activeFreeBase, horientation] using activeEdge_normalized hG e
  · simpa [activeFreeBase, horientation, normEdge_comm] using
      activeEdge_normalized hG e

def IsActiveFreeBase
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (b : FreeBase G omega) : Prop :=
  normEdge b.sourceX.1 b.sourceY.1 ∈ activeEdges G c omega

instance isActiveFreeBaseDecidable
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    DecidablePred (IsActiveFreeBase G c omega) := by
  intro b
  unfold IsActiveFreeBase
  infer_instance

abbrev DirectBase
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :=
  {b : FreeBase G omega // ¬IsActiveFreeBase G c omega b}

def activeBaseEquiv
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads) :
    ActiveEdge G c omega × Fin 2 ≃
      {b : FreeBase G omega // IsActiveFreeBase G c omega b} where
  toFun p :=
    ⟨activeFreeBase hG htri hchecked omega p.1 p.2, by
      unfold IsActiveFreeBase
      rw [activeFreeBase_normEdge]
      exact activeEdge_mem_activeEdges p.1⟩
  invFun b :=
    (⟨normEdge b.1.sourceX.1 b.1.sourceY.1,
        List.mem_toFinset.mpr b.2⟩,
      if b.1.sourceX.1 < b.1.sourceY.1 then 0 else 1)
  left_inv p := by
    rcases p with ⟨e, orientation⟩
    apply Prod.ext
    · apply Subtype.ext
      exact activeFreeBase_normEdge hG htri hchecked omega e orientation
    · have hlt := (checkGraph_edge_range G hG e.1
        (activeEdge_facts e).1).1
      fin_cases orientation <;> simp [activeFreeBase, hlt] <;> omega
  right_inv b := by
    apply Subtype.ext
    apply FreeBase.ext
    · by_cases hxy : b.1.sourceX.1 < b.1.sourceY.1
      · simp [activeFreeBase, hxy, normEdge]
      · simp [activeFreeBase, hxy, normEdge]
    · by_cases hxy : b.1.sourceX.1 < b.1.sourceY.1
      · simp [activeFreeBase, hxy, normEdge]
      · simp [activeFreeBase, hxy, normEdge]

/-- Active oriented bases and direct complementary bases partition all
proof-carrying free ordered-pair bases. -/
def freeBasePartitionEquiv
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads) :
    (ActiveEdge G c omega × Fin 2) ⊕ DirectBase G c omega ≃
      FreeBase G omega :=
  (Equiv.sumCongr (activeBaseEquiv hG htri hchecked omega) (Equiv.refl _)).trans
    (Equiv.sumCompl (IsActiveFreeBase G c omega))

/-! ## Four-key blocks in the actual `FreeHalf` shore -/

def activeFreeHalf
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (e : ActiveEdge G c omega) (orientation half : Fin 2) : FreeHalf G omega :=
  let b := activeFreeBase hG htri hchecked omega e orientation
  { sourceX := b.sourceX
    sourceY := b.sourceY
    half := half
    distinct := b.distinct
    free := b.free }

theorem freeHalf_eq
    {G : GraphData} {bads : List BadEdgeData} {omega : RowChoice bads}
    {s t : FreeHalf G omega}
    (hx : s.sourceX = t.sourceX) (hy : s.sourceY = t.sourceY)
    (hh : s.half = t.half) : s = t := by
  cases s
  cases t
  simp_all

theorem activeFreeHalf_normEdge
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (e : ActiveEdge G c omega) (orientation half : Fin 2) :
    normEdge (activeFreeHalf hG htri hchecked omega e orientation half).sourceX.1
        (activeFreeHalf hG htri hchecked omega e orientation half).sourceY.1 = e.1 := by
  exact activeFreeBase_normEdge hG htri hchecked omega e orientation

theorem activeFreeHalf_injective
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (e : ActiveEdge G c omega) :
    Function.Injective (fun p : Fin 2 × Fin 2 =>
      activeFreeHalf hG htri hchecked omega e p.1 p.2) := by
  intro p q hpq
  apply Prod.ext
  · have hbase : activeFreeBase hG htri hchecked omega e p.1 =
        activeFreeBase hG htri hchecked omega e q.1 := by
      apply FreeBase.ext
      · exact congrArg FreeHalf.sourceX hpq
      · exact congrArg FreeHalf.sourceY hpq
    have hactive : (e, p.1) = (e, q.1) := by
      apply (activeBaseEquiv hG htri hchecked omega).injective
      apply Subtype.ext
      exact hbase
    exact congrArg Prod.snd hactive
  · exact congrArg FreeHalf.half hpq

def activeEdgeFreeHalfBlock
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (e : ActiveEdge G c omega) : Finset (FreeHalf G omega) :=
  Finset.univ.image fun p : Fin 2 × Fin 2 =>
    activeFreeHalf hG htri hchecked omega e p.1 p.2

theorem activeEdgeFreeHalfBlock_card
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (e : ActiveEdge G c omega) :
    (activeEdgeFreeHalfBlock hG htri hchecked omega e).card = 4 := by
  unfold activeEdgeFreeHalfBlock
  rw [Finset.card_image_iff.mpr
    (activeFreeHalf_injective hG htri hchecked omega e).injOn]
  simp

theorem mem_activeEdgeFreeHalfBlock_iff
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (e : ActiveEdge G c omega) (s : FreeHalf G omega) :
    s ∈ activeEdgeFreeHalfBlock hG htri hchecked omega e ↔
      normEdge s.sourceX.1 s.sourceY.1 = e.1 := by
  constructor
  · intro hs
    rcases Finset.mem_image.mp hs with ⟨p, _, rfl⟩
    exact activeFreeHalf_normEdge hG htri hchecked omega e p.1 p.2
  · intro hs
    unfold activeEdgeFreeHalfBlock
    by_cases hxy : s.sourceX.1 < s.sourceY.1
    · refine Finset.mem_image.mpr ⟨(0, s.half), Finset.mem_univ _, ?_⟩
      apply freeHalf_eq
      · apply Fin.ext
        have hx := congrArg Prod.fst hs
        simpa [activeFreeHalf, activeFreeBase, normEdge, hxy] using hx.symm
      · apply Fin.ext
        have hy := congrArg Prod.snd hs
        simpa [activeFreeHalf, activeFreeBase, normEdge, hxy] using hy.symm
      · rfl
    · refine Finset.mem_image.mpr ⟨(1, s.half), Finset.mem_univ _, ?_⟩
      apply freeHalf_eq
      · apply Fin.ext
        have hx := congrArg Prod.snd hs
        simpa [activeFreeHalf, activeFreeBase, normEdge, hxy] using hx.symm
      · apply Fin.ext
        have hy := congrArg Prod.fst hs
        simpa [activeFreeHalf, activeFreeBase, normEdge, hxy] using hy.symm
      · rfl

/-- The four actual `FreeHalf` keys over one checked active undirected edge. -/
theorem activeEdgeFreeHalfKeys_card
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (e : ActiveEdge G c omega) :
    (Finset.univ.filter fun s : FreeHalf G omega =>
      normEdge s.sourceX.1 s.sourceY.1 = e.1).card = 4 := by
  have heq : (Finset.univ.filter fun s : FreeHalf G omega =>
      normEdge s.sourceX.1 s.sourceY.1 = e.1) =
      activeEdgeFreeHalfBlock hG htri hchecked omega e := by
    ext s
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    exact (mem_activeEdgeFreeHalfBlock_iff hG htri hchecked omega e s).symm
  rw [heq]
  exact activeEdgeFreeHalfBlock_card hG htri hchecked omega e

theorem activeEdgeFreeHalfBlocks_disjoint
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    {e f : ActiveEdge G c omega} (hef : e ≠ f) :
    Disjoint (activeEdgeFreeHalfBlock hG htri hchecked omega e)
      (activeEdgeFreeHalfBlock hG htri hchecked omega f) := by
  rw [Finset.disjoint_left]
  intro s hse hsf
  apply hef
  apply Subtype.ext
  exact (mem_activeEdgeFreeHalfBlock_iff hG htri hchecked omega e s).mp hse
    |>.symm.trans
      ((mem_activeEdgeFreeHalfBlock_iff hG htri hchecked omega f s).mp hsf)

/-! ## Exact typed partition and eligibility transport -/

def edgeCappedKeyEquivFreeHalf
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads) :
    CheckedSoftCollisionTwoCover.EdgeCappedPhysicalKey
        (ActiveEdge G c omega) (DirectBase G c omega) ≃ FreeHalf G omega :=
  (Equiv.prodCongr (freeBasePartitionEquiv hG htri hchecked omega)
      (Equiv.refl (Fin 2))).trans
    (freeHalfEquivBaseHalf G omega).symm

@[simp] theorem edgeCappedKeyEquivFreeHalf_active
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (e : ActiveEdge G c omega) (orientation half : Fin 2) :
    edgeCappedKeyEquivFreeHalf hG htri hchecked omega
        ((Sum.inl (e, orientation)), half) =
      activeFreeHalf hG htri hchecked omega e orientation half := by
  rfl

def directFreeHalf
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (omega : RowChoice bads) (b : DirectBase G c omega)
    (half : Fin 2) : FreeHalf G omega :=
  { sourceX := b.1.sourceX
    sourceY := b.1.sourceY
    half := half
    distinct := b.1.distinct
    free := b.1.free }

@[simp] theorem edgeCappedKeyEquivFreeHalf_direct
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (b : DirectBase G c omega) (half : Fin 2) :
    edgeCappedKeyEquivFreeHalf hG htri hchecked omega
        ((Sum.inr b), half) = directFreeHalf omega b half := by
  rfl

theorem freeBase_card_eq_active_add_direct
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads) :
    Fintype.card (FreeBase G omega) =
      2 * Fintype.card (ActiveEdge G c omega) +
        Fintype.card (DirectBase G c omega) := by
  have hcard := Fintype.card_congr
    (freeBasePartitionEquiv hG htri hchecked omega)
  simpa [Fintype.card_sum, Fintype.card_prod, Nat.mul_comm] using hcard.symm

theorem freeHalf_card_eq_four_active_add_two_direct
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads) :
    Fintype.card (FreeHalf G omega) =
      4 * Fintype.card (ActiveEdge G c omega) +
        2 * Fintype.card (DirectBase G c omega) := by
  have hhalf := Fintype.card_congr (freeHalfEquivBaseHalf G omega)
  simp only [Fintype.card_prod, Fintype.card_fin] at hhalf
  have hbase := freeBase_card_eq_active_add_direct hG htri hchecked omega
  omega

theorem active_direct_card_le_freeMass
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads) :
    2 * (Fintype.card (ActiveEdge G c omega) : Int) +
        (Fintype.card (DirectBase G c omega) : Int) ≤
      CollisionResidualIdentity.freeMass
        (fun x y : Fin G.n => pairCount omega x.1 y.1) := by
  have hpartition := freeBase_card_eq_active_add_direct hG htri hchecked omega
  have hpartitionInt : (Fintype.card (FreeBase G omega) : Int) =
      2 * (Fintype.card (ActiveEdge G c omega) : Int) +
        (Fintype.card (DirectBase G c omega) : Int) := by
    exact_mod_cast hpartition
  rw [← hpartitionInt]
  exact freeBase_card_le_freeMass G omega

/-- Pull any production eligibility relation, including a union of six
relations, back along the exact proof-carrying key equivalence. -/
def transportEligible
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (Eligible : CollisionHalf G omega → FreeHalf G omega → Prop) :
    CollisionHalf G omega →
      CheckedSoftCollisionTwoCover.EdgeCappedPhysicalKey
        (ActiveEdge G c omega) (DirectBase G c omega) → Prop :=
  fun d key => Eligible d (edgeCappedKeyEquivFreeHalf hG htri hchecked omega key)

abbrev GlobalFractionalCollisionFlowWithEdgeCaps
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (Eligible : CollisionHalf G omega → FreeHalf G omega → Prop) :=
  CheckedSoftCollisionTwoCover.FractionalCollisionFlowWithEdgeCaps
    (transportEligible hG htri hchecked omega Eligible)

/-- Conditional counting consumer for the corrected global typed flow. This
does not provide a flow; it only discharges the two cardinal adapters. -/
theorem collision_add_active_le_free_of_globalFlow
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    {Eligible : CollisionHalf G omega → FreeHalf G omega → Prop}
    (F : GlobalFractionalCollisionFlowWithEdgeCaps
      hG htri hchecked omega Eligible) :
    CollisionResidualIdentity.collisionMass
        (fun x y : Fin G.n => pairCount omega x.1 y.1) +
        (Fintype.card (ActiveEdge G c omega) : Int) ≤
      CollisionResidualIdentity.freeMass
        (fun x y : Fin G.n => pairCount omega x.1 y.1) := by
  exact CheckedSoftCollisionTwoCover.collision_add_active_le_free
    (fun x y : Fin G.n => pairCount omega x.1 y.1) F
    (collisionHalf_card_eq_two_mul_collisionMass G omega)
    (active_direct_card_le_freeMass hG htri hchecked omega)

#print axioms collisionHalf_card_eq_two_mul_collisionUnits
#print axioms collisionHalf_card_eq_two_mul_collisionMass
#print axioms activeEdge_pairCount_eq_zero
#print axioms activeEdgeFreeHalfKeys_card
#print axioms activeEdgeFreeHalfBlocks_disjoint
#print axioms freeBasePartitionEquiv
#print axioms edgeCappedKeyEquivFreeHalf
#print axioms collision_add_active_le_free_of_globalFlow

end SoftEdgeCapGraphAdapter
end Gamma
end Erdos23Delta0
