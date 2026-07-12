import Erdos23Delta0.Gamma.CollisionDefectGraphAdapter

/-!
# Checked `t = 5` catalogue kernel

This module is the data-facing R51 interface.  It deliberately separates
three statements which must not be conflated:

* a rooted `25/24` circuit is semantic graph data;
* a finite catalogue is complete only after a parent-relation checker has
  accepted an explicit certificate;
* an intrinsic obstruction marked `preprocessingOnly` is not a production
  obstruction until every ambient split has a checked extension refutation.

The weighted switch-capacity checker below is proved in-kernel.  LRAT/PB is
exposed only through a backend whose checker soundness must itself be proved
in Lean.  This file defines no catalogue payload, proves no catalogue is
complete, and contains no `no_t5` theorem.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CheckedT5CatalogueKernel

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

abbrev Edge := Nat × Nat

/-! ## Rooted intrinsic circuits -/

noncomputable def supportVertices (support : Finset Edge) : Finset Nat :=
  (support.toList.flatMap fun e => [e.1, e.2]).toFinset

def supportConsecutiveEdges : List Nat → List Edge
  | [] => []
  | [_] => []
  | u :: v :: rest => normEdge u v :: supportConsecutiveEdges (v :: rest)

def SupportPath (support : Finset Edge) (u v : Nat) (path : List Nat) : Prop :=
  path ≠ [] ∧ path.head? = some u ∧ path.getLast? = some v ∧
    ∀ e ∈ supportConsecutiveEdges path, e ∈ support

noncomputable def SupportConnected (support : Finset Edge) (root : Nat) : Prop :=
  ∀ v ∈ supportVertices support, ∃ path, SupportPath support root v path

noncomputable def SupportBipartite (support : Finset Edge)
    (leftShore rightShore : Finset Nat) : Prop :=
  Disjoint leftShore rightShore ∧
    leftShore ∪ rightShore = supportVertices support ∧
    ∀ e ∈ support,
      (e.1 ∈ leftShore ∧ e.2 ∈ rightShore) ∨
        (e.2 ∈ leftShore ∧ e.1 ∈ rightShore)

def supportDegree (support : Finset Edge) (v : Nat) : Nat :=
  (support.filter fun e => e.1 = v ∨ e.2 = v).card

def BadAtomUsesEdge (bads : List BadEdgeData)
    (atom : Fin bads.length) (edge : Edge) : Prop :=
  ∃ row ∈ (bads.get atom).rows, edge ∈ rowPathEdges row

def DeletionTransversal (bads : List BadEdgeData)
    (support : Finset Edge) (deleted : Fin bads.length) : Prop :=
  ∃ assign : {atom : Fin bads.length // atom ≠ deleted} → Edge,
    Function.Injective assign ∧
      ∀ atom, assign atom ∈ support ∧
        BadAtomUsesEdge bads atom.1 (assign atom)

def InclusionMinimalCircuit (bads : List BadEdgeData)
    (support : Finset Edge) : Prop :=
  ∀ deleted : Fin bads.length, DeletionTransversal bads support deleted

/-- Semantic rooted `t = 5` circuit.  Every field is either literal data or
an explicit proof obligation.  In particular, `database` is the production
complete-shortest-row contract; it is not replaced by a Boolean flag. -/
structure RootedT5Circuit where
  graph : GraphData
  cut : CutData
  bads : List BadEdgeData
  graph_checked : checkGraph graph = true
  cut_checked : checkCut graph cut = true
  database : CompleteShortestRowDB graph cut bads
  support : Finset Edge
  leftShore : Finset Nat
  rightShore : Finset Nat
  owner : Fin graph.n
  activeNbr : Fin graph.n
  atom_card : bads.length = 25
  support_card : support.card = 24
  support_normalized : ∀ e ∈ support, e.1 < e.2 ∧ e.2 < graph.n
  support_blue : ∀ e ∈ support, blueb graph cut e.1 e.2 = true
  support_bipartite : SupportBipartite support leftShore rightShore
  support_connected : SupportConnected support owner.1
  inclusion_minimal : InclusionMinimalCircuit bads support
  owner_support_degree : supportDegree support owner.1 = 5
  active_edge_blue : blueb graph cut owner.1 activeNbr.1 = true
  active_edge_off_support : normEdge owner.1 activeNbr.1 ∉ support


/-! ### Rooted shore range projections -/

/-- A bad-atom neighbor of the rooted owner whose blue distance is exactly
four in the only direction used below: every blue owner-to-neighbor path has
at least five vertices.  Existence of the corresponding length-four row is
already supplied by the circuit's complete row database. -/
def OwnerDistanceFourBadNeighbor (circuit : RootedT5Circuit)
    (neighbor : Fin circuit.graph.n) : Prop :=
  neighbor ≠ circuit.owner ∧
    (∃ atom : Fin circuit.bads.length,
      badEdgeKey (circuit.bads.get atom) =
        normEdge circuit.owner.1 neighbor.1) ∧
    ∀ path : List Nat,
      BluePath circuit.graph circuit.cut circuit.owner.1 neighbor.1 path →
        5 ≤ path.length

theorem blueEdge_symm {graph : GraphData} {cut : CutData} {u v : Nat}
    (h : BlueEdge graph cut u v) : BlueEdge graph cut v u := by
  exact ⟨by simpa only [adjb_comm] using h.1, h.2.symm⟩

theorem bluePath_three_of_common_blue
    {graph : GraphData} {cut : CutData}
    (u pivot v : Fin graph.n)
    (hup : BlueEdge graph cut u.1 pivot.1)
    (hvp : BlueEdge graph cut v.1 pivot.1) :
    BluePath graph cut u.1 v.1 [u.1, pivot.1, v.1] := by
  refine ⟨by simp, by simp, by simp, ?_, ?_⟩
  · intro z hz
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hz
    rcases hz with rfl | rfl | rfl
    · exact u.isLt
    · exact pivot.isLt
    · exact v.isLt
  · exact ⟨hup, blueEdge_symm hvp, trivial⟩

theorem OwnerDistanceFourBadNeighbor.no_common_blue
    {circuit : RootedT5Circuit} {neighbor pivot : Fin circuit.graph.n}
    (hneighbor : OwnerDistanceFourBadNeighbor circuit neighbor)
    (howner : BlueEdge circuit.graph circuit.cut
      circuit.owner.1 pivot.1)
    (hneighborPivot : BlueEdge circuit.graph circuit.cut
      neighbor.1 pivot.1) : False := by
  have hpath := bluePath_three_of_common_blue
    circuit.owner pivot neighbor howner hneighborPivot
  have hlength := hneighbor.2.2 _ hpath
  norm_num at hlength

/-- Minimal projection from the live rooted profile into the catalogue
carrier.  The production/rooting adapter must construct this object; none is
manufactured in this module.

ownerNeighbors is a five-vertex blue neighborhood supplied by the rooted
projection.  distance_support_neighbor records positive support degree for each
of the five distance-four neighbors in the form needed by the opposite-shore
argument. -/
structure RootedT5OwnerShoreData (circuit : RootedT5Circuit) where
  middle : Fin circuit.graph.n
  endpointA : Fin circuit.graph.n
  endpointB : Fin circuit.graph.n
  commonX : Fin circuit.graph.n
  commonY : Fin circuit.graph.n
  ownerShore : Finset Nat
  oppositeShore : Finset Nat
  shores_match :
    (ownerShore = circuit.leftShore ∧ oppositeShore = circuit.rightShore) ∨
      (ownerShore = circuit.rightShore ∧ oppositeShore = circuit.leftShore)
  root_vertices_nodup :
    [circuit.owner.1, middle.1, endpointA.1, endpointB.1].Nodup
  owner_mem_shore : circuit.owner.1 ∈ ownerShore
  middle_mem_shore : middle.1 ∈ ownerShore
  endpointA_mem_shore : endpointA.1 ∈ ownerShore
  endpointB_mem_shore : endpointB.1 ∈ ownerShore
  owner_commonX_blue :
    BlueEdge circuit.graph circuit.cut circuit.owner.1 commonX.1
  middle_commonX_blue :
    BlueEdge circuit.graph circuit.cut middle.1 commonX.1
  endpointA_commonX_blue :
    BlueEdge circuit.graph circuit.cut endpointA.1 commonX.1
  owner_commonY_blue :
    BlueEdge circuit.graph circuit.cut circuit.owner.1 commonY.1
  middle_commonY_blue :
    BlueEdge circuit.graph circuit.cut middle.1 commonY.1
  endpointB_commonY_blue :
    BlueEdge circuit.graph circuit.cut endpointB.1 commonY.1
  distanceFourNeighbors : Finset (Fin circuit.graph.n)
  distance_four_card : 5 ≤ distanceFourNeighbors.card
  distance_four_sound : ∀ neighbor ∈ distanceFourNeighbors,
    OwnerDistanceFourBadNeighbor circuit neighbor
  distance_four_mem_owner_shore : ∀ neighbor ∈ distanceFourNeighbors,
    neighbor.1 ∈ ownerShore
  ownerNeighbors : Finset Nat
  owner_neighbors_card : ownerNeighbors.card = 5
  owner_neighbors_subset_opposite : ownerNeighbors ⊆ oppositeShore
  owner_neighbors_blue : ∀ neighbor ∈ ownerNeighbors,
    BlueEdge circuit.graph circuit.cut circuit.owner.1 neighbor
  distance_support_neighbor : ∀ neighbor ∈ distanceFourNeighbors,
    ∃ across : Fin circuit.graph.n, across.1 ∈ oppositeShore ∧
      BlueEdge circuit.graph circuit.cut neighbor.1 across.1

namespace RootedT5OwnerShoreData

variable {circuit : RootedT5Circuit}

def rootVertices (data : RootedT5OwnerShoreData circuit) : Finset Nat :=
  [circuit.owner.1, data.middle.1,
    data.endpointA.1, data.endpointB.1].toFinset

def distanceVertices (data : RootedT5OwnerShoreData circuit) : Finset Nat :=
  data.distanceFourNeighbors.image fun neighbor => neighbor.1

theorem distance_neighbor_ne_middle
    (data : RootedT5OwnerShoreData circuit)
    {neighbor : Fin circuit.graph.n}
    (hneighbor : neighbor ∈ data.distanceFourNeighbors) :
    neighbor ≠ data.middle := by
  intro heq
  subst neighbor
  exact (data.distance_four_sound data.middle hneighbor).no_common_blue
    data.owner_commonX_blue data.middle_commonX_blue

theorem distance_neighbor_ne_endpointA
    (data : RootedT5OwnerShoreData circuit)
    {neighbor : Fin circuit.graph.n}
    (hneighbor : neighbor ∈ data.distanceFourNeighbors) :
    neighbor ≠ data.endpointA := by
  intro heq
  subst neighbor
  exact (data.distance_four_sound data.endpointA hneighbor).no_common_blue
    data.owner_commonX_blue data.endpointA_commonX_blue

theorem distance_neighbor_ne_endpointB
    (data : RootedT5OwnerShoreData circuit)
    {neighbor : Fin circuit.graph.n}
    (hneighbor : neighbor ∈ data.distanceFourNeighbors) :
    neighbor ≠ data.endpointB := by
  intro heq
  subst neighbor
  exact (data.distance_four_sound data.endpointB hneighbor).no_common_blue
    data.owner_commonY_blue data.endpointB_commonY_blue

theorem rootVertices_card (data : RootedT5OwnerShoreData circuit) :
    data.rootVertices.card = 4 := by
  unfold rootVertices
  rw [List.toFinset_card_of_nodup data.root_vertices_nodup]
  rfl

theorem distanceVertices_card (data : RootedT5OwnerShoreData circuit) :
    data.distanceVertices.card = data.distanceFourNeighbors.card := by
  unfold distanceVertices
  apply Finset.card_image_of_injOn
  intro first _ second _ heq
  exact Fin.ext heq

theorem rootVertices_disjoint_distanceVertices
    (data : RootedT5OwnerShoreData circuit) :
    Disjoint data.rootVertices data.distanceVertices := by
  rw [Finset.disjoint_left]
  intro vertex hroot hdistance
  rcases Finset.mem_image.mp hdistance with ⟨neighbor, hneighbor, hval⟩
  subst vertex
  have howner := (data.distance_four_sound neighbor hneighbor).1
  have hmiddle := data.distance_neighbor_ne_middle hneighbor
  have hendpointA := data.distance_neighbor_ne_endpointA hneighbor
  have hendpointB := data.distance_neighbor_ne_endpointB hneighbor
  simp [rootVertices] at hroot
  rcases hroot with h | h | h | h
  · exact howner (Fin.ext h)
  · exact hmiddle (Fin.ext h)
  · exact hendpointA (Fin.ext h)
  · exact hendpointB (Fin.ext h)

theorem rootVertices_union_distanceVertices_subset
    (data : RootedT5OwnerShoreData circuit) :
    data.rootVertices ∪ data.distanceVertices ⊆ data.ownerShore := by
  intro vertex hvertex
  rcases Finset.mem_union.mp hvertex with hroot | hdistance
  · simp [rootVertices] at hroot
    rcases hroot with h | h | h | h
    · simpa [h] using data.owner_mem_shore
    · simpa [h] using data.middle_mem_shore
    · simpa [h] using data.endpointA_mem_shore
    · simpa [h] using data.endpointB_mem_shore
  · rcases Finset.mem_image.mp hdistance with ⟨neighbor, hneighbor, hval⟩
    simpa [← hval] using data.distance_four_mem_owner_shore neighbor hneighbor

/-- The owner shore contains the four distinct rooted vertices and five
additional distance-four bad-atom neighbors. -/
theorem ownerShore_card_ge_nine
    (data : RootedT5OwnerShoreData circuit) :
    9 ≤ data.ownerShore.card := by
  have hunion := Finset.card_le_card
    (data.rootVertices_union_distanceVertices_subset)
  rw [Finset.card_union_of_disjoint
    data.rootVertices_disjoint_distanceVertices,
    data.rootVertices_card, data.distanceVertices_card] at hunion
  have hdistance : 5 ≤ data.distanceFourNeighbors.card :=
    data.distance_four_card
  omega

/-- The opposite shore has at least six vertices.  Otherwise the owner's
five support neighbors exhaust it.  A positive-degree distance-four neighbor
then shares one of those blue neighbors with the owner, producing a forbidden
two-step blue path. -/
theorem oppositeShore_card_ge_six
    (data : RootedT5OwnerShoreData circuit) :
    6 ≤ data.oppositeShore.card := by
  by_contra hsmall
  have hopposite_le : data.oppositeShore.card ≤ 5 := by omega
  have hneighbors_eq : data.ownerNeighbors = data.oppositeShore := by
    apply Finset.eq_of_subset_of_card_le data.owner_neighbors_subset_opposite
    rw [data.owner_neighbors_card]
    exact hopposite_le
  have hdistance_nonempty : data.distanceFourNeighbors.Nonempty := by
    apply Finset.card_pos.mp
    have hdistance : 5 ≤ data.distanceFourNeighbors.card :=
      data.distance_four_card
    omega
  rcases hdistance_nonempty with ⟨neighbor, hneighbor⟩
  rcases data.distance_support_neighbor neighbor hneighbor with
    ⟨across, hacross, hneighborAcross⟩
  have hacrossOwner : across.1 ∈ data.ownerNeighbors := by
    rw [hneighbors_eq]
    exact hacross
  exact (data.distance_four_sound neighbor hneighbor).no_common_blue
    (data.owner_neighbors_blue across.1 hacrossOwner) hneighborAcross

theorem rooted_shore_range
    (data : RootedT5OwnerShoreData circuit) :
    9 ≤ data.ownerShore.card ∧ 6 ≤ data.oppositeShore.card :=
  ⟨data.ownerShore_card_ge_nine, data.oppositeShore_card_ge_six⟩

end RootedT5OwnerShoreData

/-! ### Rooted support-order projection -/

/-- Literal support edges not incident with the rooted owner. -/
noncomputable def supportWithoutOwnerEdges
    (circuit : RootedT5Circuit) : Finset Edge :=
  circuit.support.filter fun edge =>
    ¬ (edge.1 = circuit.owner.1 ∨ edge.2 = circuit.owner.1)

/-- Support vertices other than the rooted owner. -/
abbrev SupportNonOwner (circuit : RootedT5Circuit) :=
  {vertex : Fin circuit.graph.n // vertex ≠ circuit.owner}

/-- Exact simple graph induced by the literal support away from the owner. -/
noncomputable def supportWithoutOwnerGraph
    (circuit : RootedT5Circuit) : SimpleGraph (SupportNonOwner circuit) where
  Adj first second :=
    normEdge first.1.1 second.1.1 ∈ circuit.support
  symm := by
    intro first second h
    simpa only [normEdge_comm] using h
  loopless := by
    intro vertex h
    have hnormalized := circuit.support_normalized _ h
    exact (Nat.lt_irrefl vertex.1.1) (by
      simpa [normEdge] using hnormalized.1)

theorem supportWithoutOwnerEdges_card
    (circuit : RootedT5Circuit) :
    (supportWithoutOwnerEdges circuit).card = 19 := by
  classical
  have hpartition := Finset.card_filter_add_card_filter_not
    (s := circuit.support)
    (fun edge : Edge =>
      edge.1 = circuit.owner.1 ∨ edge.2 = circuit.owner.1)
  change supportDegree circuit.support circuit.owner.1 +
      (supportWithoutOwnerEdges circuit).card = circuit.support.card at hpartition
  rw [circuit.owner_support_degree, circuit.support_card] at hpartition
  omega

/-- Minimal production/profile bridge for the upper-order argument.

neighbor_connected packages the four owner-avoiding paths from neighbor
zero to the other four neighbors (the zero case is reflexive).
reaches_neighbor is the standard consequence of connectedness: after the
owner is removed, every remaining vertex reaches some owner neighbor.
The final cardinal field only identifies the literal filtered support with
the edge set of the exact SimpleGraph representation. -/
structure RootedT5SupportOrderData (circuit : RootedT5Circuit) where
  support_spanning :
    supportVertices circuit.support = Finset.range circuit.graph.n
  neighbors : Fin 5 → Fin circuit.graph.n
  neighbors_injective : Function.Injective neighbors
  neighbor_ne_owner : ∀ i, neighbors i ≠ circuit.owner
  neighbor_support_edge : ∀ i,
    normEdge circuit.owner.1 (neighbors i).1 ∈ circuit.support
  neighbor_connected : ∀ i,
    (supportWithoutOwnerGraph circuit).Reachable
      ⟨neighbors 0, neighbor_ne_owner 0⟩
      ⟨neighbors i, neighbor_ne_owner i⟩
  reaches_neighbor : ∀ vertex : SupportNonOwner circuit,
    ∃ i,
      (supportWithoutOwnerGraph circuit).Reachable vertex
        ⟨neighbors i, neighbor_ne_owner i⟩
  reduced_edge_card :
    Nat.card (supportWithoutOwnerGraph circuit).edgeSet =
      (supportWithoutOwnerEdges circuit).card

theorem RootedT5SupportOrderData.deletedSupport_connected
    {circuit : RootedT5Circuit}
    (data : RootedT5SupportOrderData circuit) :
    (supportWithoutOwnerGraph circuit).Connected := by
  let anchor : SupportNonOwner circuit :=
    ⟨data.neighbors 0, data.neighbor_ne_owner 0⟩
  refine ⟨?_, ⟨anchor⟩⟩
  intro first second
  rcases data.reaches_neighbor first with ⟨i, hfirst⟩
  rcases data.reaches_neighbor second with ⟨j, hsecond⟩
  exact hfirst.trans <|
    (data.neighbor_connected i).symm.trans <|
      (data.neighbor_connected j).trans hsecond.symm

/-- Removing the degree-five owner leaves a connected graph with 19 edges,
so it has at most 20 vertices and the original support order is at most 21. -/
theorem supportOrder_le_twentyOne {circuit : RootedT5Circuit}
    (data : RootedT5SupportOrderData circuit) :
    circuit.graph.n ≤ 21 := by
  have hcard := data.deletedSupport_connected.card_vert_le_card_edgeSet_add_one
  have hedge : Nat.card (supportWithoutOwnerGraph circuit).edgeSet = 19 := by
    calc
      Nat.card (supportWithoutOwnerGraph circuit).edgeSet =
          (supportWithoutOwnerEdges circuit).card := data.reduced_edge_card
      _ = 19 := supportWithoutOwnerEdges_card circuit
  have hvertices : Nat.card (SupportNonOwner circuit) =
      circuit.graph.n - 1 := by
    rw [Nat.card_eq_fintype_card]
    simpa [SupportNonOwner] using (Set.card_ne_eq circuit.owner)
  rw [hvertices, hedge] at hcard
  have howner_lt := circuit.owner.isLt
  omega

/-! ### Small-order distance-four pair-cover gates -/

/-- A proof-carrying cover of all 25 literal bad-atom endpoint pairs.  The
database supplies injectivity of those pairs; a rooted structural adapter
supplies the finite cover.  This record does not assert that such a cover
exists. -/
structure RootedT5AtomPairCover (circuit : RootedT5Circuit) where
  pairs : Finset Edge
  atom_mem : ∀ atom : Fin circuit.bads.length,
    badEdgeKey (circuit.bads.get atom) ∈ pairs

namespace RootedT5AtomPairCover

variable {circuit : RootedT5Circuit}

/-- Distinct database atoms inject into any certified endpoint-pair cover. -/
theorem atom_card_le (cover : RootedT5AtomPairCover circuit) :
    circuit.bads.length ≤ cover.pairs.card := by
  let embed : Fin circuit.bads.length → {pair // pair ∈ cover.pairs} :=
    fun atom => ⟨badEdgeKey (circuit.bads.get atom), cover.atom_mem atom⟩
  have hinjective : Function.Injective embed := by
    intro first second heq
    apply CollisionDefectGraphAdapter.badEdgeKey_get_injective
      circuit.database.badKeys_nodup
    exact congrArg Subtype.val heq
  simpa [embed] using Fintype.card_le_of_injective embed hinjective

end RootedT5AtomPairCover

/-- Exact order-15 projection expected from the rooted structural argument.
The 21-pair field is deliberately explicit: the current owner-shore carrier
does not yet expose the second owner's degree/distance-four neighborhood or a
classification of every database atom. -/
structure RootedT5Order15PairProjection (circuit : RootedT5Circuit) where
  shore : RootedT5OwnerShoreData circuit
  graph_order : circuit.graph.n = 15
  owner_shore_card : shore.ownerShore.card = 9
  opposite_shore_card : shore.oppositeShore.card = 6
  cover : RootedT5AtomPairCover circuit
  cover_card_le : cover.pairs.card ≤ 21

/-- Kernel endpoint for the order-15 structural proof.  It is conditional on
the explicit pair projection; no catalogue completeness is asserted here. -/
theorem no_order15_rootedT5 {circuit : RootedT5Circuit}
    (projection : RootedT5Order15PairProjection circuit) : False := by
  have hlower := projection.cover.atom_card_le
  rw [circuit.atom_card] at hlower
  have hupper := projection.cover_card_le
  omega

/-- Exact order-16 projection shared by the (10,6) and (9,7) arguments.
The split disjunction records which structural derivation produced the
24-pair cover. -/
structure RootedT5Order16PairProjection (circuit : RootedT5Circuit) where
  shore : RootedT5OwnerShoreData circuit
  graph_order : circuit.graph.n = 16
  rooted_split :
    (shore.ownerShore.card = 10 ∧ shore.oppositeShore.card = 6) ∨
      (shore.ownerShore.card = 9 ∧ shore.oppositeShore.card = 7)
  cover : RootedT5AtomPairCover circuit
  cover_card_le : cover.pairs.card ≤ 24

/-- Kernel endpoint for either order-16 structural pair-cover argument. -/
theorem no_order16_rootedT5 {circuit : RootedT5Circuit}
    (projection : RootedT5Order16PairProjection circuit) : False := by
  have hlower := projection.cover.atom_card_le
  rw [circuit.atom_card] at hlower
  have hupper := projection.cover_card_le
  omega

def mapVertex {n m : Nat} (equiv : Fin n ≃ Fin m) (v : Nat) : Nat :=
  if h : v < n then (equiv ⟨v, h⟩).1 else m

/-- Rooted isomorphisms preserve the literal graph/cut, the complete atom-row
database, the support shores, and both distinguished vertices. -/
structure RootedT5Iso (first second : RootedT5Circuit) : Type where
  vertexEquiv : Fin first.graph.n ≃ Fin second.graph.n
  atomEquiv : Fin first.bads.length ≃ Fin second.bads.length
  rowEquiv : ∀ atom : Fin first.bads.length,
    Fin (first.bads.get atom).rows.length ≃
      Fin (second.bads.get (atomEquiv atom)).rows.length
  adjacency : ∀ u v : Fin first.graph.n,
    adjb first.graph u.1 v.1 =
      adjb second.graph (vertexEquiv u).1 (vertexEquiv v).1
  side : ∀ v : Fin first.graph.n,
    sideb first.cut v.1 = sideb second.cut (vertexEquiv v).1
  support : ∀ u v : Fin first.graph.n,
    normEdge u.1 v.1 ∈ first.support ↔
      normEdge (vertexEquiv u).1 (vertexEquiv v).1 ∈ second.support
  atom_endpoints : ∀ atom : Fin first.bads.length,
    normEdge
        (mapVertex vertexEquiv (first.bads.get atom).u)
        (mapVertex vertexEquiv (first.bads.get atom).v) =
      badEdgeKey (second.bads.get (atomEquiv atom))
  row_vertices : ∀ atom : Fin first.bads.length,
    ∀ row : Fin (first.bads.get atom).rows.length,
      ((second.bads.get (atomEquiv atom)).rows.get (rowEquiv atom row)).verts =
        ((first.bads.get atom).rows.get row).verts.map
          (mapVertex vertexEquiv)
  left_shore : ∀ v : Fin first.graph.n,
    v.1 ∈ first.leftShore ↔ (vertexEquiv v).1 ∈ second.leftShore
  right_shore : ∀ v : Fin first.graph.n,
    v.1 ∈ first.rightShore ↔ (vertexEquiv v).1 ∈ second.rightShore
  owner : vertexEquiv first.owner = second.owner
  active_nbr : vertexEquiv first.activeNbr = second.activeNbr

def RootedT5CatalogueComplete (entries : List RootedT5Circuit) : Prop :=
  ∀ circuit : RootedT5Circuit,
    ∃ entry ∈ entries, Nonempty (RootedT5Iso circuit entry)

/-! ## Checked parent-relation catalogue interface -/

/-- A concrete catalogue generator instantiates this backend with its node
type and proof payload.  `check_sound` is a theorem about that executable
checker, not a field of any emitted catalogue entry. -/
structure RootedT5ParentRelationKernel (Node ParentCert : Type*) where
  nodes : ParentCert → List Node
  parentEdges : ParentCert → List (Nat × Nat)
  parentRelation : Node → Node → Prop
  represents : Node → RootedT5Circuit → Prop
  check : List RootedT5Circuit → ParentCert → Bool
  checked_edges_sound : ∀ entries cert,
    check entries cert = true →
      ∀ edge ∈ parentEdges cert,
        ∃ parent child,
          (nodes cert)[edge.1]? = some parent ∧
            (nodes cert)[edge.2]? = some child ∧
            parentRelation parent child
  check_sound : ∀ entries cert,
    check entries cert = true → RootedT5CatalogueComplete entries

/-- Emitted catalogue plus a passing parent-relation certificate. -/
structure CheckedRootedT5Catalogue
    {Node ParentCert : Type*}
    (kernel : RootedT5ParentRelationKernel Node ParentCert) where
  entries : List RootedT5Circuit
  certificate : ParentCert
  checked : kernel.check entries certificate = true

theorem checkedRootedT5Catalogue_complete
    {Node ParentCert : Type*}
    {kernel : RootedT5ParentRelationKernel Node ParentCert}
    (catalogue : CheckedRootedT5Catalogue kernel) :
    RootedT5CatalogueComplete catalogue.entries :=
  kernel.check_sound catalogue.entries catalogue.certificate catalogue.checked

/-! ## Profile keys and checked profile lists -/

/-- Serializable key for one rooted selected-row profile.  The checker owns
the interpretation of `rowChoice`, classifier coordinates, coverage choices,
and the endpoint type word. -/
structure T5ProfileKey where
  owner : Nat
  activeNbr : Nat
  rowChoice : List Nat
  classifier : List Nat
  coverageChoice : List Nat
  typeWord : List Nat
deriving Repr, DecidableEq

/-- Executable profile enumerator and its once-for-all completeness theorem. -/
structure T5ProfileListKernel where
  ProfileRealized : RootedT5Circuit → T5ProfileKey → Prop
  checkKey : RootedT5Circuit → T5ProfileKey → Bool
  checkKey_sound : ∀ circuit key,
    checkKey circuit key = true → ProfileRealized circuit key
  enumerate : RootedT5Circuit → List T5ProfileKey
  enumerate_checked : ∀ circuit key,
    key ∈ enumerate circuit → checkKey circuit key = true
  enumerate_complete : ∀ circuit key,
    ProfileRealized circuit key → key ∈ enumerate circuit

structure CheckedT5ProfileList
    (kernel : T5ProfileListKernel) (circuit : RootedT5Circuit) where
  keys : List T5ProfileKey
  nodup : keys.Nodup

namespace CheckedT5ProfileList

def check {kernel : T5ProfileListKernel} {circuit : RootedT5Circuit}
    (profiles : CheckedT5ProfileList kernel circuit) : Bool :=
  decide (profiles.keys = kernel.enumerate circuit)

theorem check_eq_true_iff
    {kernel : T5ProfileListKernel} {circuit : RootedT5Circuit}
    (profiles : CheckedT5ProfileList kernel circuit) :
    profiles.check = true ↔ profiles.keys = kernel.enumerate circuit := by
  simp [check]

theorem complete
    {kernel : T5ProfileListKernel} {circuit : RootedT5Circuit}
    (profiles : CheckedT5ProfileList kernel circuit)
    (hcheck : profiles.check = true) {key : T5ProfileKey}
    (hkey : kernel.ProfileRealized circuit key) :
    key ∈ profiles.keys := by
  rw [(check_eq_true_iff profiles).mp hcheck]
  exact kernel.enumerate_complete circuit key hkey

end CheckedT5ProfileList

/-! ## Intrinsic certificates: final rejection versus preprocessing only -/

inductive T5IntrinsicScope
  | profileImpossible
  | preprocessingOnly
deriving Repr, DecidableEq

inductive T5IntrinsicKind
  | classifierNonzero
  | noProfileTuple
  | forcedTailSeparator
  | captureUnsat
deriving Repr, DecidableEq

structure T5IntrinsicKernel
    (profileKernel : T5ProfileListKernel) (Payload : Type*) where
  scope : Payload → T5IntrinsicScope
  kind : Payload → T5IntrinsicKind
  PreprocessingFact : RootedT5Circuit → T5ProfileKey → Prop
  check : RootedT5Circuit → T5ProfileKey → Payload → Bool
  check_sound : ∀ circuit key payload,
    check circuit key payload = true →
      match scope payload with
      | .profileImpossible => ¬ profileKernel.ProfileRealized circuit key
      | .preprocessingOnly => PreprocessingFact circuit key

structure CheckedT5IntrinsicCert
    {Payload : Type*} {profileKernel : T5ProfileListKernel}
    (kernel : T5IntrinsicKernel profileKernel Payload)
    (circuit : RootedT5Circuit) (key : T5ProfileKey) where
  payload : Payload
  checked : kernel.check circuit key payload = true

theorem CheckedT5IntrinsicCert.sound
    {Payload : Type*} {profileKernel : T5ProfileListKernel}
    {kernel : T5IntrinsicKernel profileKernel Payload}
    {circuit : RootedT5Circuit} {key : T5ProfileKey}
    (cert : CheckedT5IntrinsicCert kernel circuit key) :
    match kernel.scope cert.payload with
    | .profileImpossible => ¬ profileKernel.ProfileRealized circuit key
    | .preprocessingOnly => kernel.PreprocessingFact circuit key :=
  kernel.check_sound circuit key cert.payload cert.checked

/-! ## Ambient splits and semantic production extensions -/

structure T5AmbientSplit where
  ambientOrder : Nat
  newLeft : Nat
  newRight : Nat
deriving Repr, DecidableEq

def T5AmbientSplit.ValidFor
    (split : T5AmbientSplit) (circuit : RootedT5Circuit) : Prop :=
  split.ambientOrder = 25 ∧
    circuit.graph.n + split.newLeft + split.newRight = split.ambientOrder

def T5AmbientSplit.checkFor
    (split : T5AmbientSplit) (circuit : RootedT5Circuit) : Bool :=
  decide (split.ambientOrder = 25) &&
    decide (circuit.graph.n + split.newLeft + split.newRight = split.ambientOrder)

theorem T5AmbientSplit.checkFor_eq_true_iff
    (split : T5AmbientSplit) (circuit : RootedT5Circuit) :
    split.checkFor circuit = true ↔ split.ValidFor circuit := by
  simp [T5AmbientSplit.checkFor, T5AmbientSplit.ValidFor]

structure T5AmbientSplitKernel where
  enumerate : RootedT5Circuit → T5ProfileKey → List T5AmbientSplit
  enumerate_valid : ∀ circuit key split,
    split ∈ enumerate circuit key → split.ValidFor circuit
  enumerate_complete : ∀ circuit key split,
    split.ValidFor circuit → split ∈ enumerate circuit key

/-- Semantic ambient extension.  The intrinsic circuit is the prefix on
vertices `< circuit.graph.n`; additional old-old and new edges are permitted.
Every old row remains valid and no genuinely new length-four row for an old
bad atom is introduced. -/
structure T5ProductionExtension
    (profileKernel : T5ProfileListKernel)
    (circuit : RootedT5Circuit) (key : T5ProfileKey)
    (split : T5AmbientSplit) where
  ambientGraph : GraphData
  ambientCut : CutData
  graph_checked : checkGraph ambientGraph = true
  cut_checked : checkCut ambientGraph ambientCut = true
  ambient_order : ambientGraph.n = split.ambientOrder
  split_valid : split.ValidFor circuit
  triangle_free : TriangleFree ambientGraph
  max_cut : IsMaxCut ambientGraph ambientCut
  core_side : ∀ v : Fin circuit.graph.n,
    sideb ambientCut v.1 = sideb circuit.cut v.1
  core_edge_monotone : ∀ u v : Fin circuit.graph.n,
    adjb circuit.graph u.1 v.1 = true →
      adjb ambientGraph u.1 v.1 = true
  old_rows_preserved : ∀ atom : Fin circuit.bads.length,
    ∀ row ∈ (circuit.bads.get atom).rows,
      checkRow5 ambientGraph ambientCut
        (circuit.bads.get atom).u (circuit.bads.get atom).v row = true
  no_new_old_rows : ∀ atom : Fin circuit.bads.length,
    ∀ verts : List Nat,
      checkRow5 ambientGraph ambientCut
        (circuit.bads.get atom).u (circuit.bads.get atom).v
        { badId := atom.1, verts := verts } = true →
      ∃ row ∈ (circuit.bads.get atom).rows, row.verts = verts
  profile_realized : profileKernel.ProfileRealized circuit key

/-! ## Exact switch-capacity problem and checker -/

/-- Finite Boolean production-extension relaxation.  A selected variable is
an added row-safe edge.  Every switch must receive at least `kappa` selected
crossings. -/
structure T5ExtensionProblem where
  variableCount : Nat
  switchCount : Nat
  rowSafe : Fin variableCount → Bool
  crosses : Fin switchCount → Fin variableCount → Bool
  kappa : Fin switchCount → Nat

namespace T5ExtensionProblem

def selectedCrossCount (problem : T5ExtensionProblem)
    (selected : Fin problem.variableCount → Bool)
    (switch : Fin problem.switchCount) : Nat :=
  ∑ edge, if selected edge && problem.crosses switch edge then 1 else 0

def Satisfies (problem : T5ExtensionProblem)
    (selected : Fin problem.variableCount → Bool) : Prop :=
  (∀ edge, selected edge = true → problem.rowSafe edge = true) ∧
    ∀ switch, problem.kappa switch ≤
      problem.selectedCrossCount selected switch

instance satisfiesDecidable (problem : T5ExtensionProblem)
    (selected : Fin problem.variableCount → Bool) :
    Decidable (problem.Satisfies selected) := by
  unfold Satisfies
  infer_instance

def checkAssignment (problem : T5ExtensionProblem)
    (selected : Fin problem.variableCount → Bool) : Bool :=
  decide (problem.Satisfies selected)

theorem checkAssignment_eq_true_iff (problem : T5ExtensionProblem)
    (selected : Fin problem.variableCount → Bool) :
    problem.checkAssignment selected = true ↔ problem.Satisfies selected := by
  simp [checkAssignment]

def weightedDemand (problem : T5ExtensionProblem)
    (weight : Fin problem.switchCount → Nat) : Nat :=
  ∑ switch, weight switch * problem.kappa switch

def edgeWeight (problem : T5ExtensionProblem)
    (weight : Fin problem.switchCount → Nat)
    (edge : Fin problem.variableCount) : Nat :=
  ∑ switch, if problem.crosses switch edge then weight switch else 0

def safeUpper (problem : T5ExtensionProblem)
    (weight : Fin problem.switchCount → Nat) : Nat :=
  ∑ edge, if problem.rowSafe edge then problem.edgeWeight weight edge else 0


private theorem weightedSelected_eq_edgeSum (problem : T5ExtensionProblem)
    (selected : Fin problem.variableCount → Bool)
    (weight : Fin problem.switchCount → Nat) :
    (∑ switch, weight switch * problem.selectedCrossCount selected switch) =
      ∑ edge,
        problem.edgeWeight weight edge * (if selected edge then 1 else 0) := by
  classical
  simp only [selectedCrossCount, edgeWeight, Finset.mul_sum]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro edge _
  by_cases hs : selected edge = true
  · simp [hs, Bool.true_and]
  · have hs' : selected edge = false := Bool.eq_false_of_not_eq_true hs
    simp [hs']

private theorem weightedDemand_le_weightedSelected
    (problem : T5ExtensionProblem)
    (selected : Fin problem.variableCount → Bool)
    (weight : Fin problem.switchCount → Nat)
    (hsat : problem.Satisfies selected) :
    problem.weightedDemand weight ≤
      ∑ switch, weight switch * problem.selectedCrossCount selected switch := by
  unfold weightedDemand
  apply Finset.sum_le_sum
  intro switch _
  exact Nat.mul_le_mul_left _ (hsat.2 switch)

private theorem weightedSelected_le_safeUpper
    (problem : T5ExtensionProblem)
    (selected : Fin problem.variableCount → Bool)
    (weight : Fin problem.switchCount → Nat)
    (hsat : problem.Satisfies selected) :
    (∑ switch, weight switch * problem.selectedCrossCount selected switch) ≤
      problem.safeUpper weight := by
  rw [weightedSelected_eq_edgeSum]
  unfold safeUpper
  apply Finset.sum_le_sum
  intro edge _
  by_cases hs : selected edge = true
  · have hsafe := hsat.1 edge hs
    simp [hs, hsafe]
  · have hs' : selected edge = false := Bool.eq_false_of_not_eq_true hs
    simp [hs']

end T5ExtensionProblem

/-- Cleared nonnegative Farkas multipliers for switch inequalities.  Rational
multipliers are represented after multiplication by a common denominator. -/
structure CheckedWeightedSwitchCapacity (problem : T5ExtensionProblem) where
  weight : Fin problem.switchCount → Nat

namespace CheckedWeightedSwitchCapacity

def check {problem : T5ExtensionProblem}
    (cert : CheckedWeightedSwitchCapacity problem) : Bool :=
  decide (problem.safeUpper cert.weight < problem.weightedDemand cert.weight)

theorem check_eq_true_iff {problem : T5ExtensionProblem}
    (cert : CheckedWeightedSwitchCapacity problem) :
    cert.check = true ↔
      problem.safeUpper cert.weight < problem.weightedDemand cert.weight := by
  simp [check]

theorem sound {problem : T5ExtensionProblem}
    (cert : CheckedWeightedSwitchCapacity problem)
    (hcheck : cert.check = true) :
    ¬ ∃ selected, problem.Satisfies selected := by
  intro hexists
  rcases hexists with ⟨selected, hsat⟩
  have hdemand := problem.weightedDemand_le_weightedSelected
    selected cert.weight hsat
  have hupper := problem.weightedSelected_le_safeUpper
    selected cert.weight hsat
  have hstrict := (check_eq_true_iff cert).mp hcheck
  omega

end CheckedWeightedSwitchCapacity

/-! ## LRAT/PB fallback and extension-unsat bridge -/

/-- Interface to an in-kernel LRAT or pseudo-Boolean proof checker.  A future
backend may use any proof format, but its `sound` theorem is mandatory. -/
structure LRATPBBackend (ProofPayload : Type*) where
  check : T5ExtensionProblem → ProofPayload → Bool
  sound : ∀ problem proof,
    check problem proof = true → ¬ ∃ selected, problem.Satisfies selected

universe uPayload uProof

inductive CheckedT5ExtensionUnsat
    {ProofPayload : Type uProof} (backend : LRATPBBackend ProofPayload)
    (problem : T5ExtensionProblem) : Type uProof
  | weighted (cert : CheckedWeightedSwitchCapacity problem)
      (checked : cert.check = true)
  | lratPB (proof : ProofPayload)
      (checked : backend.check problem proof = true)

theorem checkedT5ExtensionUnsat_sound
    {ProofPayload : Type*} {backend : LRATPBBackend ProofPayload}
    {problem : T5ExtensionProblem}
    (cert : CheckedT5ExtensionUnsat backend problem) :
    ¬ ∃ selected, problem.Satisfies selected := by
  cases cert with
  | weighted cert checked => exact cert.sound checked
  | lratPB proof checked => exact backend.sound problem proof checked

/-- Graph-to-PB encoder.  This is the explicit production bridge future
catalogue data must instantiate for every entry/profile/split. -/
structure T5ExtensionEncoding
    (profileKernel : T5ProfileListKernel)
    (circuit : RootedT5Circuit) (key : T5ProfileKey)
    (split : T5AmbientSplit) where
  problem : T5ExtensionProblem
  encode : T5ProductionExtension profileKernel circuit key split →
    Fin problem.variableCount → Bool
  encode_sound : ∀ extension,
    problem.Satisfies (encode extension)

theorem no_production_extension_of_checked_unsat
    {ProofPayload : Type*} {backend : LRATPBBackend ProofPayload}
    {profileKernel : T5ProfileListKernel}
    {circuit : RootedT5Circuit} {key : T5ProfileKey}
    {split : T5AmbientSplit}
    (encoding : T5ExtensionEncoding profileKernel circuit key split)
    (cert : CheckedT5ExtensionUnsat backend encoding.problem) :
    ¬ Nonempty (T5ProductionExtension profileKernel circuit key split) := by
  intro hextension
  rcases hextension with ⟨extension⟩
  exact checkedT5ExtensionUnsat_sound cert
    ⟨encoding.encode extension, encoding.encode_sound extension⟩

/-! ## Profile, entry, and catalogue bundles -/

structure T5ExtensionKernel (profileKernel : T5ProfileListKernel) where
  encoding : ∀ circuit key split,
    T5ExtensionEncoding profileKernel circuit key split

def T5ProfileClosure
    {Payload : Type uPayload} {ProofPayload : Type uProof}
    {profileKernel : T5ProfileListKernel}
    (intrinsicKernel : T5IntrinsicKernel profileKernel Payload)
    (splitKernel : T5AmbientSplitKernel)
    (extensionKernel : T5ExtensionKernel profileKernel)
    (backend : LRATPBBackend ProofPayload)
    (circuit : RootedT5Circuit) (key : T5ProfileKey)
    (intrinsic : CheckedT5IntrinsicCert intrinsicKernel circuit key) : Type uProof :=
  match intrinsicKernel.scope intrinsic.payload with
  | .profileImpossible => PUnit
  | .preprocessingOnly =>
      ∀ split, split ∈ splitKernel.enumerate circuit key →
        CheckedT5ExtensionUnsat backend
          (extensionKernel.encoding circuit key split).problem

structure CheckedT5ProfileBundle
    {Payload : Type uPayload} {ProofPayload : Type uProof}
    {profileKernel : T5ProfileListKernel}
    (intrinsicKernel : T5IntrinsicKernel profileKernel Payload)
    (splitKernel : T5AmbientSplitKernel)
    (extensionKernel : T5ExtensionKernel profileKernel)
    (backend : LRATPBBackend ProofPayload)
    (circuit : RootedT5Circuit) (key : T5ProfileKey) where
  intrinsic : CheckedT5IntrinsicCert intrinsicKernel circuit key
  closure : T5ProfileClosure intrinsicKernel splitKernel extensionKernel
    backend circuit key intrinsic

theorem CheckedT5ProfileBundle.noProductionExtension
    {Payload ProofPayload : Type*}
    {profileKernel : T5ProfileListKernel}
    {intrinsicKernel : T5IntrinsicKernel profileKernel Payload}
    {splitKernel : T5AmbientSplitKernel}
    {extensionKernel : T5ExtensionKernel profileKernel}
    {backend : LRATPBBackend ProofPayload}
    {circuit : RootedT5Circuit} {key : T5ProfileKey}
    (bundle : CheckedT5ProfileBundle intrinsicKernel splitKernel
      extensionKernel backend circuit key)
    (split : T5AmbientSplit) :
    ¬ Nonempty (T5ProductionExtension profileKernel circuit key split) := by
  intro hextension
  rcases hextension with ⟨extension⟩
  cases hscope : intrinsicKernel.scope bundle.intrinsic.payload with
  | profileImpossible =>
      have himpossible :
          ¬ profileKernel.ProfileRealized circuit key := by
        simpa [hscope] using bundle.intrinsic.sound
      exact himpossible extension.profile_realized
  | preprocessingOnly =>
      have hmem := splitKernel.enumerate_complete circuit key split
        extension.split_valid
      have hclosure :
          ∀ split, split ∈ splitKernel.enumerate circuit key →
            CheckedT5ExtensionUnsat backend
              (extensionKernel.encoding circuit key split).problem := by
        simpa [T5ProfileClosure, hscope] using bundle.closure
      have hcert := hclosure split hmem
      exact no_production_extension_of_checked_unsat
        (extensionKernel.encoding circuit key split) hcert ⟨extension⟩

structure CheckedT5EntryBundle
    {Payload ProofPayload : Type*}
    (profileKernel : T5ProfileListKernel)
    (intrinsicKernel : T5IntrinsicKernel profileKernel Payload)
    (splitKernel : T5AmbientSplitKernel)
    (extensionKernel : T5ExtensionKernel profileKernel)
    (backend : LRATPBBackend ProofPayload)
    (circuit : RootedT5Circuit) where
  profiles : CheckedT5ProfileList profileKernel circuit
  profiles_checked : profiles.check = true
  profileBundle : ∀ key, key ∈ profiles.keys →
    CheckedT5ProfileBundle intrinsicKernel splitKernel extensionKernel
      backend circuit key

theorem CheckedT5EntryBundle.noProductionExtension
    {Payload ProofPayload : Type*}
    {profileKernel : T5ProfileListKernel}
    {intrinsicKernel : T5IntrinsicKernel profileKernel Payload}
    {splitKernel : T5AmbientSplitKernel}
    {extensionKernel : T5ExtensionKernel profileKernel}
    {backend : LRATPBBackend ProofPayload}
    {circuit : RootedT5Circuit}
    (bundle : CheckedT5EntryBundle profileKernel intrinsicKernel splitKernel
      extensionKernel backend circuit)
    (key : T5ProfileKey) (split : T5AmbientSplit)
    (hkey : profileKernel.ProfileRealized circuit key) :
    ¬ Nonempty (T5ProductionExtension profileKernel circuit key split) := by
  have hmem := bundle.profiles.complete bundle.profiles_checked hkey
  exact (bundle.profileBundle key hmem).noProductionExtension split

structure CheckedT5CatalogueBundle
    {Node ParentCert Payload ProofPayload : Type*}
    (parentKernel : RootedT5ParentRelationKernel Node ParentCert)
    (profileKernel : T5ProfileListKernel)
    (intrinsicKernel : T5IntrinsicKernel profileKernel Payload)
    (splitKernel : T5AmbientSplitKernel)
    (extensionKernel : T5ExtensionKernel profileKernel)
    (backend : LRATPBBackend ProofPayload) where
  catalogue : CheckedRootedT5Catalogue parentKernel
  entryBundle : ∀ entry, entry ∈ catalogue.entries →
    CheckedT5EntryBundle profileKernel intrinsicKernel splitKernel
      extensionKernel backend entry

/-- A checked catalogue bundle gives an isomorphic entry and its checked
profile/extension bundle for every rooted circuit.  Transporting a production
extension across that isomorphism belongs to the later consumer module. -/
theorem CheckedT5CatalogueBundle.lookup
    {Node ParentCert Payload ProofPayload : Type*}
    {parentKernel : RootedT5ParentRelationKernel Node ParentCert}
    {profileKernel : T5ProfileListKernel}
    {intrinsicKernel : T5IntrinsicKernel profileKernel Payload}
    {splitKernel : T5AmbientSplitKernel}
    {extensionKernel : T5ExtensionKernel profileKernel}
    {backend : LRATPBBackend ProofPayload}
    (bundle : CheckedT5CatalogueBundle parentKernel profileKernel
      intrinsicKernel splitKernel extensionKernel backend)
    (circuit : RootedT5Circuit) :
    ∃ entry ∈ bundle.catalogue.entries,
      Nonempty (RootedT5Iso circuit entry) ∧
        Nonempty (CheckedT5EntryBundle profileKernel intrinsicKernel
          splitKernel extensionKernel backend entry) := by
  rcases checkedRootedT5Catalogue_complete bundle.catalogue circuit with
    ⟨entry, hentry, hiso⟩
  exact ⟨entry, hentry, hiso, ⟨bundle.entryBundle entry hentry⟩⟩

#print axioms checkedRootedT5Catalogue_complete
#print axioms CheckedT5ProfileList.complete
#print axioms CheckedT5IntrinsicCert.sound
#print axioms CheckedWeightedSwitchCapacity.sound
#print axioms checkedT5ExtensionUnsat_sound
#print axioms no_production_extension_of_checked_unsat
#print axioms CheckedT5ProfileBundle.noProductionExtension
#print axioms CheckedT5EntryBundle.noProductionExtension
#print axioms CheckedT5CatalogueBundle.lookup
#print axioms RootedT5OwnerShoreData.ownerShore_card_ge_nine
#print axioms RootedT5OwnerShoreData.oppositeShore_card_ge_six
#print axioms RootedT5OwnerShoreData.rooted_shore_range
#print axioms RootedT5AtomPairCover.atom_card_le
#print axioms no_order15_rootedT5
#print axioms no_order16_rootedT5
#print axioms supportWithoutOwnerEdges_card
#print axioms RootedT5SupportOrderData.deletedSupport_connected
#print axioms supportOrder_le_twentyOne

end CheckedT5CatalogueKernel
end Gamma
end Erdos23Delta0




