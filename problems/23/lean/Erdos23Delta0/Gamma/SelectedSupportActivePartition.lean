import Erdos23Delta0.Gamma.MinimumDemandRowSelection

/-!
# Selected support / active-edge partition

For a normalized literal graph, the selected row support and the active
off-support blue edges partition all blue edges internal to the selected vertex
set.  This is the exact active-edge bookkeeping used by rectangle exchanges.
-/

namespace Erdos23Delta0
namespace Gamma
namespace SelectedSupportActivePartition

open CertGraph
open MinimumDemandRowSelection

def internalBlueb (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (e : Nat × Nat) : Bool :=
  decide (e.1 ∈ selectedVertices omega) &&
    decide (e.2 ∈ selectedVertices omega) &&
    blueb G c e.1 e.2

/-- Exact finite partition.  `hnorm` is essential: `activeEdges` normalizes its
support lookup, while `G.edges` itself is the list being filtered. -/
theorem activeEdges_add_selectedSupport_eq_internalBlue
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (hnd : G.edges.Nodup)
    (hnorm : ∀ e ∈ G.edges, normEdge e.1 e.2 = e)
    (hsupport : ∀ e ∈ selectedSupport omega,
      e ∈ G.edges ∧ internalBlueb G c omega e = true) :
    (activeEdges G c omega).length + (selectedSupport omega).length =
      (G.edges.filter (internalBlueb G c omega)).length := by
  classical
  let S := (selectedSupport omega).toFinset
  let I := (G.edges.filter (internalBlueb G c omega)).toFinset
  have hS : S ⊆ I := by
    intro e he
    have he' : e ∈ selectedSupport omega := by
      simpa [S] using he
    simpa [I, List.mem_filter] using hsupport e he'
  have hA : (activeEdges G c omega).toFinset = I \ S := by
    ext e
    by_cases he : e ∈ G.edges
    · have hne := hnorm e he
      simp [activeEdges, I, S, internalBlueb, he, hne, Bool.and_assoc,
        and_assoc]
    · simp [activeEdges, I, S, internalBlueb, he]
  have hA_nd : (activeEdges G c omega).Nodup := by
    unfold activeEdges
    exact hnd.filter _
  have hS_nd : (selectedSupport omega).Nodup := by
    unfold selectedSupport
    exact List.nodup_dedup _
  have hI_nd :
      (G.edges.filter (internalBlueb G c omega)).Nodup :=
    hnd.filter _
  rw [← List.toFinset_card_of_nodup hA_nd, hA,
    ← List.toFinset_card_of_nodup hS_nd,
    ← List.toFinset_card_of_nodup hI_nd]
  exact Finset.card_sdiff_add_card_eq_card hS

#print axioms activeEdges_add_selectedSupport_eq_internalBlue

end SelectedSupportActivePartition
end Gamma
end Erdos23Delta0
