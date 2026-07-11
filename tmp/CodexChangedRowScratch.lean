import Erdos23Delta0.Gamma.ActiveScopedCoordinateTransport

namespace Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

open CertGraph
open MinimumDemandRowSelection
open TwoRowRectangleExchange

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

end Erdos23Delta0.Gamma.ActiveScopedMinimumExchange
