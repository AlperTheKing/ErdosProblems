import Erdos23Delta0.Gamma.CheckedSinkNeutralAttachmentClass
import Erdos23Delta0.Gamma.CheckedDetourTransportLedger
import Erdos23Delta0.Gamma.R43SupportIncidence

/-!
# Checked balanced-deficiency rotors

This module is the production M3 interface.  It packages a nontrivial cyclic
family of equal-defect live detours inside a checked sink-neutral attachment
class.  Every transition carries the exact R42 transport ledger, and every
rotating owner carries the graph data consumed by the small-window catalogue
and incidence arguments.

The structure is conditional data.  In particular, this file neither builds a
rotor from a Hall failure nor excludes a checked rotor.
-/

namespace Erdos23Delta0
namespace Gamma

open scoped BigOperators
open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open ActiveScopedMinimumExchange
open CollisionDefectGraphAdapter
open CheckedDetourTransportLedger
open R43SupportIncidence

namespace BalancedRotor

abbrev Edge := Nat × Nat

/-- Union of every path edge in the complete shortest-row database. -/
def completeRowSupport (bads : List BadEdgeData) : Finset Edge :=
  (bads.flatMap fun bad => bad.rows.flatMap rowPathEdges).toFinset

/-- Three explicit complete-support edges incident with one rotating owner. -/
structure OwnerSupportTriple (G : GraphData) (bads : List BadEdgeData)
    (owner : Fin G.n) where
  edge0 : Edge
  edge1 : Edge
  edge2 : Edge
  edge0_mem : edge0 ∈ completeRowSupport bads
  edge1_mem : edge1 ∈ completeRowSupport bads
  edge2_mem : edge2 ∈ completeRowSupport bads
  edge0_at_owner : owner.1 = edge0.1 ∨ owner.1 = edge0.2
  edge1_at_owner : owner.1 = edge1.1 ∨ owner.1 = edge1.2
  edge2_at_owner : owner.1 = edge2.1 ∨ owner.1 = edge2.2
  ne01 : edge0 ≠ edge1
  ne02 : edge0 ≠ edge2
  ne12 : edge1 ≠ edge2

namespace OwnerSupportTriple

variable {G : GraphData} {bads : List BadEdgeData} {owner : Fin G.n}

/-- The literal three-edge star exported to the shape-independent consumer. -/
def edges (T : OwnerSupportTriple G bads owner) : Finset Edge :=
  {T.edge0, T.edge1, T.edge2}

def toThreeMembers (T : OwnerSupportTriple G bads owner) :
    ThreeMembers Edge T.edges where
  e0 := T.edge0
  e1 := T.edge1
  e2 := T.edge2
  mem0 := by simp [edges]
  mem1 := by simp [edges]
  mem2 := by simp [edges]
  ne01 := T.ne01
  ne02 := T.ne02
  ne12 := T.ne12

/-- Direct adapter to the existing R43 star interface. -/
def toFullyCoveredLiveStar (T : OwnerSupportTriple G bads owner) :
    FullyCoveredLiveStar Edge where
  support := completeRowSupport bads
  incident := T.edges
  incident_subset := by
    intro e he
    simp only [edges, Finset.mem_insert, Finset.mem_singleton] at he
    rcases he with rfl | rfl | rfl
    · exact T.edge0_mem
    · exact T.edge1_mem
    · exact T.edge2_mem
  witnesses := T.toThreeMembers

end OwnerSupportTriple

/-- One checked length-four blue path from an owner to a bad neighbour.
Both orientations of the database row are accepted, while the four oriented
path edges are exposed directly for downstream incidence constructions. -/
structure CheckedBadNeighbourFourPath
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (owner : Fin G.n) where
  badNeighbour : Fin G.n
  step1 : Fin G.n
  step2 : Fin G.n
  step3 : Fin G.n
  atom : Fin bads.length
  row : Fin (bads.get atom).rows.length
  bad_edge : badb G c owner.1 badNeighbour.1 = true
  row_checked :
    checkRow5 G c (bads.get atom).u (bads.get atom).v
      ((bads.get atom).rows.get row) = true
  row_forward_or_reverse :
    ((bads.get atom).rows.get row).verts =
        [owner.1, step1.1, step2.1, step3.1, badNeighbour.1] ∨
      ((bads.get atom).rows.get row).verts =
        [badNeighbour.1, step3.1, step2.1, step1.1, owner.1]
  vertices_nodup :
    [owner.1, step1.1, step2.1, step3.1, badNeighbour.1].Nodup
  blue01 : blueb G c owner.1 step1.1 = true
  blue12 : blueb G c step1.1 step2.1 = true
  blue23 : blueb G c step2.1 step3.1 = true
  blue34 : blueb G c step3.1 badNeighbour.1 = true
  support01 : normEdge owner.1 step1.1 ∈ completeRowSupport bads
  support12 : normEdge step1.1 step2.1 ∈ completeRowSupport bads
  support23 : normEdge step2.1 step3.1 ∈ completeRowSupport bads
  support34 : normEdge step3.1 badNeighbour.1 ∈ completeRowSupport bads

/-- Three explicit paths to three distinct bad neighbours. -/
structure ThreeBadNeighbourFourPaths
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (owner : Fin G.n) where
  path0 : CheckedBadNeighbourFourPath G c bads owner
  path1 : CheckedBadNeighbourFourPath G c bads owner
  path2 : CheckedBadNeighbourFourPath G c bads owner
  bad01 : path0.badNeighbour ≠ path1.badNeighbour
  bad02 : path0.badNeighbour ≠ path2.badNeighbour
  bad12 : path1.badNeighbour ≠ path2.badNeighbour

/-- Exact production profile at one rotating owner.  `activeNbr` is the
unique active star neighbour in the displayed detour and `supportNbr` is its
displayed supported neighbour.  `otherSupportNbr` makes the R43 witness triple
explicit; the two quantified fields retain the full all-neighbour coverage
semantics needed by the R51 catalogue consumer. -/
structure ActiveFullyCoveredProfileOwner
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (omega : RowChoice bads)
    (owner partner activeNbr supportNbr : Fin G.n) where
  degree : Nat
  three_le_degree : 3 ≤ degree
  owner_active : ActiveOwner G c omega owner
  blue_degree : dB G c [owner.1] = degree
  bad_degree : dM G c [owner.1] = degree
  selected_row_count : pairCount omega owner.1 owner.1 = degree
  active_degree_one : activeDegree G c omega owner = 1
  hit_need_one : hitNeedUnits G c omega owner = 1
  active_edge : normEdge owner.1 activeNbr.1 ∈ activeEdges G c omega
  active_edge_off_support :
    normEdge owner.1 activeNbr.1 ∉ selectedSupport omega
  displayed_support_edge :
    normEdge owner.1 supportNbr.1 ∈ selectedSupport omega
  otherSupportNbr : Fin G.n
  other_support_edge :
    normEdge owner.1 otherSupportNbr.1 ∈ selectedSupport omega
  active_ne_support : activeNbr ≠ supportNbr
  active_ne_other : activeNbr ≠ otherSupportNbr
  support_ne_other : supportNbr ≠ otherSupportNbr
  displayed_pair_covered :
    0 < pairCount omega activeNbr.1 supportNbr.1
  other_pair_covered :
    0 < pairCount omega activeNbr.1 otherSupportNbr.1
  every_other_blue_edge_supported :
    ∀ z : Fin G.n, z ≠ activeNbr →
      blueb G c owner.1 z.1 = true →
        normEdge owner.1 z.1 ∈ selectedSupport omega
  every_active_support_pair_covered :
    ∀ z : Fin G.n, z ≠ activeNbr →
      blueb G c owner.1 z.1 = true →
        0 < pairCount omega activeNbr.1 z.1
  supportWitnesses : OwnerSupportTriple G bads owner
  supportWitness0 :
    supportWitnesses.edge0 = normEdge owner.1 activeNbr.1
  supportWitness1 :
    supportWitnesses.edge1 = normEdge owner.1 supportNbr.1
  supportWitness2 :
    supportWitnesses.edge2 = normEdge owner.1 otherSupportNbr.1
  owner_ne_partner : owner ≠ partner
  same_side : sideb c owner.1 = sideb c partner.1
  owner_common_blue : blueb G c owner.1 activeNbr.1 = true
  partner_common_blue : blueb G c partner.1 activeNbr.1 = true
  badPaths : ThreeBadNeighbourFourPaths G c bads owner

namespace ActiveFullyCoveredProfileOwner

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}
variable {omega : RowChoice bads}
variable {owner partner activeNbr supportNbr : Fin G.n}

def supportStar
    (P : ActiveFullyCoveredProfileOwner G c bads omega
      owner partner activeNbr supportNbr) : FullyCoveredLiveStar Edge :=
  P.supportWitnesses.toFullyCoveredLiveStar

theorem three_le_completeSupport_degree
    (P : ActiveFullyCoveredProfileOwner G c bads omega
      owner partner activeNbr supportNbr) :
    3 ≤ P.supportWitnesses.edges.card :=
  P.supportWitnesses.toThreeMembers.three_le_card

theorem owner_partner_not_blue
    (P : ActiveFullyCoveredProfileOwner G c bads omega
      owner partner activeNbr supportNbr) :
    blueb G c owner.1 partner.1 = false := by
  unfold blueb
  simp [P.same_side]

private theorem adjb_of_blueb {u v : Nat}
    (h : blueb G c u v = true) : adjb G u v = true := by
  unfold blueb at h
  simp only [Bool.and_eq_true] at h
  exact h.1

private theorem adjb_of_badb {u v : Nat}
    (h : badb G c u v = true) : adjb G u v = true := by
  unfold badb at h
  simp only [Bool.and_eq_true] at h
  exact h.1

private theorem ne_of_adjb {u v : Nat}
    (h : adjb G u v = true) : u ≠ v := by
  unfold adjb at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.1

/-- Same side plus a common blue neighbour excludes a bad owner-partner
edge in every triangle-free production graph. -/
theorem owner_partner_not_bad
    (P : ActiveFullyCoveredProfileOwner G c bads omega
      owner partner activeNbr supportNbr)
    (htri : TriangleFree G) :
    badb G c owner.1 partner.1 ≠ true := by
  intro hbad
  have hop := adjb_of_badb hbad
  have hpa := adjb_of_blueb P.partner_common_blue
  have hoa := adjb_of_blueb P.owner_common_blue
  exact htri owner.1 partner.1 activeNbr.1
    owner.isLt partner.isLt activeNbr.isLt
    (fun h => P.owner_ne_partner (Fin.ext h))
    (ne_of_adjb hpa) (ne_of_adjb hoa)
    ⟨hop, hpa, hoa⟩

end ActiveFullyCoveredProfileOwner

theorem two_le_pos {n : Nat} (h : 2 ≤ n) : 0 < n := by
  omega

/-- Canonical successor on a nonempty finite rotor index. -/
def cyclicSucc {n : Nat} (h : 0 < n) (i : Fin n) : Fin n :=
  ⟨(i.1 + 1) % n, Nat.mod_lt _ h⟩

end BalancedRotor

open BalancedRotor

/-- A checked nontrivial balanced rotor in the production collision engine.
All graph semantics and every transport ledger are explicit fields. -/
structure CheckedBalancedDeficiencyRotor
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (relations : NoCommonBlueSourceRelations G c bads) where
  graph_checked : checkGraph G = true
  cut_checked : checkCut G c = true
  triangle_free : TriangleFree G
  max_cut : IsMaxCut G c
  complete_rows : CompleteShortestRowDB G c bads
  sink : CheckedSinkNeutralAttachmentClass G c bads relations
  no_augmentation : ¬ Nonempty sink.Augmentation
  window : Nat
  window_pos : 0 < window
  vertex_window : G.n = 5 * window
  bad_window : bads.length = window * window
  circuit_cardinality :
    (completeRowSupport bads).card + 1 = bads.length
  rotorLength : Nat
  rotorLength_two_le : 2 ≤ rotorLength
  stateIndex : Fin rotorLength → Fin sink.stateCount
  stateIndex_injective : Function.Injective stateIndex
  detour : ∀ i : Fin rotorLength,
    CheckedTwoEdgeDetour
      (sink.state (stateIndex i))
      (sink.state (stateIndex
        (cyclicSucc (two_le_pos rotorLength_two_le) i)))
  edge_marked : ∀ i : Fin rotorLength,
    sink.data.edge (stateIndex i)
      (stateIndex (cyclicSucc (two_le_pos rotorLength_two_le) i)) = true
  ledger : ∀ i : Fin rotorLength,
    CheckedDetourTransportLedger
      (AttachmentDefectData G c bads relations)
      (sink.state (stateIndex i)).omega
      (sink.state (stateIndex
        (cyclicSucc (two_le_pos rotorLength_two_le) i))).omega
  ledger_checked : ∀ i : Fin rotorLength, (ledger i).check = true
  support_balance :
    (∑ i : Fin rotorLength,
      ((selectedSupport
        (sink.state (stateIndex
          (cyclicSucc (two_le_pos rotorLength_two_le) i))).omega).length : Int) -
      ((selectedSupport (sink.state (stateIndex i)).omega).length : Int)) = 0
  profile : ∀ i : Fin rotorLength,
    ActiveFullyCoveredProfileOwner G c bads
      (sink.state (stateIndex i)).omega
      (detour i).v (detour i).m (detour i).x (detour i).y
  profile_degree : ∀ i : Fin rotorLength, (profile i).degree = window

namespace CheckedBalancedDeficiencyRotor

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}
variable {relations : NoCommonBlueSourceRelations G c bads}

variable (R : CheckedBalancedDeficiencyRotor G c bads relations)

theorem rotorLength_pos : 0 < R.rotorLength :=
  two_le_pos R.rotorLength_two_le

/-- Equal state defects and the exact R42 identity force every serialized
rotor ledger to be balanced. -/
theorem ledger_balanced (i : Fin R.rotorLength) :
    (R.ledger i).born.card + (R.ledger i).brokenLive.card =
      (R.ledger i).deadUnmatched.card + (R.ledger i).reoptimizedGain := by
  have hdelta := (R.ledger i).defect_delta_of_check_eq_true
    (R.ledger_checked i)
  have heq := CollisionTraceState.defect_eq
    (R.sink.state (R.stateIndex
      (cyclicSucc R.rotorLength_pos i)))
    (R.sink.state (R.stateIndex i))
  change
    (AttachmentDefectData G c bads relations).collisionDefect
        (R.sink.state (R.stateIndex
          (cyclicSucc R.rotorLength_pos i))).omega =
      (AttachmentDefectData G c bads relations).collisionDefect
        (R.sink.state (R.stateIndex i)).omega at heq
  omega

/-- R51's first consumer step: a nontrivial checked rotor contains an active,
fully covered production profile owner.  This only unpacks checked data. -/
theorem exists_active_fullyCovered_profile_owner :
    ∃ i : Fin R.rotorLength,
      ActiveOwner G c (R.sink.state (R.stateIndex i)).omega (R.detour i).v ∧
        Nonempty (ActiveFullyCoveredProfileOwner G c bads
          (R.sink.state (R.stateIndex i)).omega
          (R.detour i).v (R.detour i).m (R.detour i).x (R.detour i).y) := by
  let i : Fin R.rotorLength := ⟨0, R.rotorLength_pos⟩
  exact ⟨i, (R.profile i).owner_active, ⟨R.profile i⟩⟩

/-- Direct R43 view of one rotating owner's three support witnesses. -/
def ownerSupportStar (i : Fin R.rotorLength) :
    FullyCoveredLiveStar BalancedRotor.Edge :=
  (R.profile i).supportStar

#print axioms ActiveFullyCoveredProfileOwner.owner_partner_not_blue
#print axioms ActiveFullyCoveredProfileOwner.owner_partner_not_bad
#print axioms ledger_balanced
#print axioms exists_active_fullyCovered_profile_owner

end CheckedBalancedDeficiencyRotor
end Gamma
end Erdos23Delta0
