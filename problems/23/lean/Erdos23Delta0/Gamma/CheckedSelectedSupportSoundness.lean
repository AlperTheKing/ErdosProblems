import Erdos23Delta0.Gamma.SelectedSupportActivePartition

/-!
# Checked selected-support soundness

The selected-support partition theorem takes a local soundness hypothesis for
the selected row edges.  This module discharges that hypothesis from the
literal graph checker and the checked bad-edge row database.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CheckedSelectedSupportSoundness

open CertGraph
open MinimumDemandRowSelection
open SelectedSupportActivePartition

theorem blueb_comm (G : GraphData) (c : CutData) (u v : Nat) :
    blueb G c u v = blueb G c v u := by
  unfold blueb
  rw [adjb_comm]
  by_cases h : sideb c u = sideb c v <;> simp [h, Ne.symm]

/-- Every literal graph edge is already in normalized orientation. -/
theorem normEdge_eq_self_of_checkGraph
    {G : GraphData} (hG : checkGraph G = true) {e : Nat × Nat}
    (he : e ∈ G.edges) :
    normEdge e.1 e.2 = e := by
  have hlt := (checkGraph_edge_range G hG e he).1
  simp [normEdge, hlt]

/-- A dependent row choice always selects a row accepted by the literal row
checker when the complete supplied bad-edge database is checked. -/
theorem selectedRow_check_eq_true
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hBads : AllBadsChecked G c bads) (omega : RowChoice bads)
    (i : Fin bads.length) :
    checkRow5 G c (bads.get i).u (bads.get i).v
      ((bads.get i).rows.get (omega i)) = true := by
  unfold AllBadsChecked at hBads
  have hb := List.all_eq_true.mp hBads (bads.get i) (List.get_mem bads i)
  unfold checkBadEdge at hb
  simp only [Bool.and_eq_true] at hb
  exact List.all_eq_true.mp hb.2 _ (List.get_mem (bads.get i).rows (omega i))

theorem mem_selectedVertices_of_mem_selectedRow
    {bads : List BadEdgeData} {omega : RowChoice bads}
    {row : Row5} (hrow : row ∈ selectedRows omega)
    {v : Nat} (hv : v ∈ row.verts) :
    v ∈ selectedVertices omega := by
  unfold selectedVertices
  apply List.mem_dedup.mpr
  exact List.mem_flatMap.mpr ⟨row, hrow, hv⟩

/-- Every selected row-path edge is a literal normalized graph edge whose two
endpoints lie in the selected vertex set and which is blue in the fixed cut. -/
theorem selectedSupport_sound_of_allBadsChecked
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hBads : AllBadsChecked G c bads) (omega : RowChoice bads) :
    ∀ e ∈ selectedSupport omega,
      e ∈ G.edges ∧ internalBlueb G c omega e = true := by
  intro e he
  have heFlat : e ∈ (selectedRows omega).flatMap rowPathEdges := by
    exact List.mem_dedup.mp he
  rcases List.mem_flatMap.mp heFlat with ⟨row, hrow, heRow⟩
  unfold rowPathEdges at heRow
  rcases List.mem_map.mp heRow with ⟨p, hp, rfl⟩
  have hrowRange : row ∈ Set.range
      (fun i : Fin bads.length => (bads.get i).rows.get (omega i)) := by
    simpa [selectedRows, List.mem_ofFn'] using hrow
  rcases hrowRange with ⟨i, rfl⟩
  have hcheck := selectedRow_check_eq_true hBads omega i
  unfold checkRow5 at hcheck
  simp only [Bool.and_eq_true] at hcheck
  have hpathAll :
      (List.zip ((bads.get i).rows.get (omega i)).verts
          ((bads.get i).rows.get (omega i)).verts.tail).all
        (fun q => blueb G c q.1 q.2) = true := hcheck.1.2
  have hblue : blueb G c p.1 p.2 = true :=
    List.all_eq_true.mp hpathAll p hp
  have hblueParts := hblue
  unfold blueb at hblueParts
  simp only [Bool.and_eq_true] at hblueParts
  have hadj : adjb G p.1 p.2 = true := hblueParts.1
  unfold adjb at hadj
  simp only [Bool.and_eq_true] at hadj
  have hmem : normEdge p.1 p.2 ∈ G.edges :=
    of_decide_eq_true hadj.2
  have hpMem := List.of_mem_zip hp
  have hp1 : p.1 ∈ ((bads.get i).rows.get (omega i)).verts := hpMem.1
  have hp2 : p.2 ∈ ((bads.get i).rows.get (omega i)).verts :=
    List.mem_of_mem_tail hpMem.2
  have hs1 : p.1 ∈ selectedVertices omega :=
    mem_selectedVertices_of_mem_selectedRow hrow hp1
  have hs2 : p.2 ∈ selectedVertices omega :=
    mem_selectedVertices_of_mem_selectedRow hrow hp2
  refine ⟨hmem, ?_⟩
  by_cases huv : p.1 < p.2
  · simp [internalBlueb, normEdge, huv, hs1, hs2, hblue]
  · have hblueRev : blueb G c p.2 p.1 = true := by
      rw [← blueb_comm]
      exact hblue
    simp [internalBlueb, normEdge, huv, hs1, hs2, hblueRev]

/-- Fully checked form of the selected-support/active-edge partition. -/
theorem activeEdges_add_selectedSupport_eq_internalBlue_of_checked
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (hG : checkGraph G = true)
    (hBads : AllBadsChecked G c bads) :
    (activeEdges G c omega).length + (selectedSupport omega).length =
      (G.edges.filter (internalBlueb G c omega)).length := by
  apply activeEdges_add_selectedSupport_eq_internalBlue G c omega
  · exact checkGraph_edges_nodup G hG
  · intro e he
    exact normEdge_eq_self_of_checkGraph hG he
  · exact selectedSupport_sound_of_allBadsChecked hBads omega

#print axioms normEdge_eq_self_of_checkGraph
#print axioms selectedRow_check_eq_true
#print axioms selectedSupport_sound_of_allBadsChecked
#print axioms activeEdges_add_selectedSupport_eq_internalBlue_of_checked

end CheckedSelectedSupportSoundness
end Gamma
end Erdos23Delta0
