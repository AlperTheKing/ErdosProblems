import Erdos23Delta0.Gamma.GlobalSoftCapTrace

/-!
# Same-atom exclusive forks in the global soft-cap trace

This is the graph-facing part of the R55 saturated-fork interface.  It does
not assume the retired active-scoped coherent trace.  A fork records two
checked shortest rows of one bad edge, their first divergent vertices, and
the common blue predecessor.  Triangle-freeness makes the divergent ordered
pair a non-active free base.  Saturating its two physical halves therefore
uses two distinct obligations of the exact optimal grouped-cap partial flow.
-/

namespace Erdos23Delta0
namespace Gamma
namespace GlobalSoftCapExclusiveFork

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open SoftEdgeCapGraphAdapter
open GlobalSoftCapTrace

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}

/-- The literal graph payload of one same-bad-edge first-divergence fork. -/
structure CheckedSameAtomExclusiveFork
    (omega : RowChoice bads) where
  atom : Fin bads.length
  leftRow : Row5
  rightRow : Row5
  left_mem : leftRow ∈ (bads.get atom).rows
  right_mem : rightRow ∈ (bads.get atom).rows
  rows_distinct : leftRow ≠ rightRow
  position : Nat
  position_pos : 0 < position
  position_lt_five : position < 5
  commonPredecessor : Fin G.n
  leftVertex : Fin G.n
  rightVertex : Fin G.n
  common_prefix :
    leftRow.verts.take position = rightRow.verts.take position
  left_predecessor :
    leftRow.verts[position - 1]? = some commonPredecessor.1
  right_predecessor :
    rightRow.verts[position - 1]? = some commonPredecessor.1
  left_at_divergence :
    leftRow.verts[position]? = some leftVertex.1
  right_at_divergence :
    rightRow.verts[position]? = some rightVertex.1
  first_divergence : leftVertex ≠ rightVertex
  common_left_blue :
    blueb G c commonPredecessor.1 leftVertex.1 = true
  common_right_blue :
    blueb G c commonPredecessor.1 rightVertex.1 = true

namespace CheckedSameAtomExclusiveFork

variable {omega : RowChoice bads}
variable (F : CheckedSameAtomExclusiveFork (G := G) (c := c) omega)

theorem left_checked (hchecked : AllBadsChecked G c bads) :
    checkRow5 G c (bads.get F.atom).u (bads.get F.atom).v F.leftRow = true := by
  have hb := List.all_eq_true.mp hchecked
    (bads.get F.atom) (List.get_mem bads F.atom)
  unfold checkBadEdge at hb
  simp only [Bool.and_eq_true] at hb
  exact List.all_eq_true.mp hb.2 F.leftRow F.left_mem

theorem right_checked (hchecked : AllBadsChecked G c bads) :
    checkRow5 G c (bads.get F.atom).u (bads.get F.atom).v F.rightRow = true := by
  have hb := List.all_eq_true.mp hchecked
    (bads.get F.atom) (List.get_mem bads F.atom)
  unfold checkBadEdge at hb
  simp only [Bool.and_eq_true] at hb
  exact List.all_eq_true.mp hb.2 F.rightRow F.right_mem

private theorem adjb_of_blueb {u v : Nat}
    (h : blueb G c u v = true) : adjb G u v = true := by
  unfold blueb at h
  simp only [Bool.and_eq_true] at h
  exact h.1

private theorem ne_of_adjb {u v : Nat}
    (h : adjb G u v = true) : u ≠ v := by
  unfold adjb at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.1

/-- The two divergent vertices cannot themselves be adjacent: together with
their common blue predecessor they would span a triangle. -/
theorem divergent_not_adjacent (htri : TriangleFree G) :
    adjb G F.leftVertex.1 F.rightVertex.1 ≠ true := by
  intro huv
  have hcu := adjb_of_blueb F.common_left_blue
  have hcw := adjb_of_blueb F.common_right_blue
  exact htri F.commonPredecessor.1 F.leftVertex.1 F.rightVertex.1
    F.commonPredecessor.isLt F.leftVertex.isLt F.rightVertex.isLt
    (ne_of_adjb hcu) (by
      intro h
      apply F.first_divergence
      exact Fin.ext h) (ne_of_adjb hcw)
    ⟨hcu, huv, hcw⟩

/-- The proof-carrying free ordered base exposed by first divergence. -/
def divergenceBase
    (hfree : pairCount omega F.leftVertex.1 F.rightVertex.1 = 0) :
    FreeBase G omega :=
  { sourceX := F.leftVertex
    sourceY := F.rightVertex
    distinct := F.first_divergence
    free := hfree }

def divergenceHalf
    (hfree : pairCount omega F.leftVertex.1 F.rightVertex.1 = 0)
    (half : Fin 2) : FreeHalf G omega :=
  { sourceX := F.leftVertex
    sourceY := F.rightVertex
    half := half
    distinct := F.first_divergence
    free := hfree }

/-- The divergent free base lies in the direct part of the exact active/direct
partition, not in an active-edge four-key block. -/
theorem divergenceBase_not_active
    (htri : TriangleFree G)
    (hfree : pairCount omega F.leftVertex.1 F.rightVertex.1 = 0) :
    ¬ IsActiveFreeBase G c omega (F.divergenceBase hfree) := by
  intro hactive
  unfold IsActiveFreeBase at hactive
  unfold activeEdges at hactive
  have hedge : normEdge F.leftVertex.1 F.rightVertex.1 ∈ G.edges :=
    (List.mem_filter.mp hactive).1
  have hne : F.leftVertex.1 ≠ F.rightVertex.1 := by
    intro h
    apply F.first_divergence
    exact Fin.ext h
  have hadj : adjb G F.leftVertex.1 F.rightVertex.1 = true := by
    simp [adjb, hne, hedge]
  exact F.divergent_not_adjacent htri hadj

def divergenceDirectBase
    (htri : TriangleFree G)
    (hfree : pairCount omega F.leftVertex.1 F.rightVertex.1 = 0) :
    DirectBase G c omega :=
  ⟨F.divergenceBase hfree, F.divergenceBase_not_active htri hfree⟩

end CheckedSameAtomExclusiveFork

namespace Payload

variable {hG : checkGraph G = true} {htri : TriangleFree G}
variable {hchecked : AllBadsChecked G c bads}
variable {Eligible : ∀ omega : RowChoice bads,
  CollisionHalf G omega → FreeHalf G omega → Prop}

variable (P : GlobalSoftCapTrace.Payload hG htri hchecked Eligible)

/-- If both physical halves of the first-divergence base are occupied, the
exact optimal partial flow contains two distinct matched obligations using
those two literal keys. -/
theorem exists_distinct_matched_of_fork_bothHalvesUsed
    (F : CheckedSameAtomExclusiveFork (G := G) (c := c) P.omega)
    (hfree : pairCount P.omega F.leftVertex.1 F.rightVertex.1 = 0)
    (hused : P.BothHalvesUsed (F.divergenceBase hfree)) :
    ∃ d0 d1 : {d // d ∈ P.flow.matched},
      d0 ≠ d1 ∧
      P.flow.assign d0 =
        (edgeCappedKeyEquivFreeHalf hG htri hchecked P.omega).symm
          (F.divergenceHalf hfree 0) ∧
      P.flow.assign d1 =
        (edgeCappedKeyEquivFreeHalf hG htri hchecked P.omega).symm
          (F.divergenceHalf hfree 1) := by
  change ∀ half : Fin 2,
    P.UsesFreeHalf (F.divergenceHalf hfree half) at hused
  obtain ⟨d0, hd0⟩ := hused 0
  obtain ⟨d1, hd1⟩ := hused 1
  refine ⟨d0, d1, ?_, hd0, hd1⟩
  intro heq
  subst d1
  have hkey := hd0.symm.trans hd1
  have hhalf := congrArg
    (fun s : FreeHalf G P.omega => s.half)
    ((edgeCappedKeyEquivFreeHalf hG htri hchecked P.omega).symm.injective hkey)
  simp [CheckedSameAtomExclusiveFork.divergenceHalf] at hhalf

end Payload

#print axioms CheckedSameAtomExclusiveFork.divergent_not_adjacent
#print axioms CheckedSameAtomExclusiveFork.divergenceBase_not_active
#print axioms Payload.exists_distinct_matched_of_fork_bothHalvesUsed

end GlobalSoftCapExclusiveFork
end Gamma
end Erdos23Delta0
