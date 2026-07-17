import Erdos23Delta0.Gamma.ActiveScopedCoordinateTransport

/-!
# Support persistence excludes multiplicity-saturated rotors

A checked length-five row in a triangle-free graph is induced: two of its
vertices joined by a blue edge must be consecutive.  Consequently, if a
selected row containing a blue edge is replaced while its endpoint-pair has
multiplicity at least two, another selected row keeps that edge in support.

The persistence contradiction at either directed middle swap rules out the
strict R38 multiplicity-saturated inverse rotor.
-/

namespace Erdos23Delta0
namespace Gamma
namespace SaturatedRotorSupportPersistence

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open TwoRowRectangleExchange
open ActiveScopedMinimumExchange

attribute [local instance] Classical.propDecidable

private theorem adjb_of_blueb {G : GraphData} {c : CutData} {x y : Nat}
    (h : blueb G c x y = true) : adjb G x y = true := by
  unfold blueb at h
  simp only [Bool.and_eq_true] at h
  exact h.1

private theorem adjb_of_badb {G : GraphData} {c : CutData} {x y : Nat}
    (h : badb G c x y = true) : adjb G x y = true := by
  unfold badb at h
  simp only [Bool.and_eq_true] at h
  exact h.1

private theorem blueb_comm (G : GraphData) (c : CutData) (x y : Nat) :
    blueb G c x y = blueb G c y x := by
  unfold blueb
  rw [adjb_comm]
  simp only [ne_eq, ne_comm]

private theorem blueb_badb_false
    {G : GraphData} {c : CutData} {x y : Nat}
    (hblue : blueb G c x y = true) (hbad : badb G c x y = true) : False := by
  unfold blueb at hblue
  unfold badb at hbad
  simp only [Bool.and_eq_true] at hblue hbad
  exact (of_decide_eq_true hblue.2) (of_decide_eq_true hbad.2)

private theorem blueb_irrefl_false
    {G : GraphData} {c : CutData} {x : Nat}
    (hblue : blueb G c x x = true) : False := by
  simp [blueb, adjb] at hblue

private theorem vertex_lt_of_checkedRow
    {G : GraphData} {c : CutData} {u v : Nat} {row : Row5}
    (hcheck : checkRow5 G c u v row = true) {x : Nat}
    (hx : x ∈ row.verts) : x < G.n := by
  unfold checkRow5 at hcheck
  simp only [Bool.and_eq_true] at hcheck
  have hall : row.verts.all (fun w => decide (w < G.n)) = true := by
    aesop
  exact of_decide_eq_true (List.all_eq_true.mp hall x hx)

private theorem selectedRow_checked
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hchecked : AllBadsChecked G c bads) (omega : RowChoice bads)
    (i : Fin bads.length) :
    checkRow5 G c (bads.get i).u (bads.get i).v
      ((bads.get i).rows.get (omega i)) = true := by
  have hb := List.all_eq_true.mp hchecked (bads.get i) (List.get_mem bads i)
  unfold checkBadEdge at hb
  simp only [Bool.and_eq_true] at hb
  exact List.all_eq_true.mp hb.2 _
    (List.get_mem (bads.get i).rows (omega i))

private theorem list_eq_five_of_length {xs : List Nat}
    (h : xs.length = 5) :
    ∃ a b d e f, xs = [a, b, d, e, f] := by
  rcases xs with _ | ⟨a, xs⟩
  · simp at h
  rcases xs with _ | ⟨b, xs⟩
  · simp at h
  rcases xs with _ | ⟨d, xs⟩
  · simp at h
  rcases xs with _ | ⟨e, xs⟩
  · simp at h
  rcases xs with _ | ⟨f, xs⟩
  · simp at h
  rcases xs with _ | ⟨g, xs⟩
  · exact ⟨a, b, d, e, f, rfl⟩
  · simp at h

private theorem literal_five_row_induced
    {G : GraphData} {c : CutData} {a b d e f x y : Nat}
    (htri : TriangleFree G)
    (hall : a < G.n ∧ b < G.n ∧ d < G.n ∧ e < G.n ∧ f < G.n)
    (hnd : [a, b, d, e, f].Nodup)
    (hab : blueb G c a b = true) (hbd : blueb G c b d = true)
    (hde : blueb G c d e = true) (hef : blueb G c e f = true)
    (haf : badb G c a f = true)
    (hx : x ∈ [a, b, d, e, f]) (hy : y ∈ [a, b, d, e, f])
    (hblue : blueb G c x y = true) :
    normEdge x y ∈ rowPathEdges { badId := 0, verts := [a, b, d, e, f] } := by
  rcases hall with ⟨halt, hblt, hdlt, helt, hflt⟩
  simp at hnd
  rcases hnd with
    ⟨⟨hneab, hnead, hneae, hneaf⟩,
      ⟨hnebd, hnebe, hnebf⟩, ⟨hnede, hnedf⟩, hneef⟩
  have hab' := adjb_of_blueb hab
  have hbd' := adjb_of_blueb hbd
  have hde' := adjb_of_blueb hde
  have hef' := adjb_of_blueb hef
  have haf' := adjb_of_badb haf
  have hba' : adjb G b a = true := by rw [← adjb_comm]; exact hab'
  have hnoAD : blueb G c a d ≠ true := by
    intro h
    exact htri a b d halt hblt hdlt hneab hnebd hnead
      ⟨hab', hbd', adjb_of_blueb h⟩
  have hnoDA : blueb G c d a ≠ true := by
    intro h; apply hnoAD; rw [blueb_comm]; exact h
  have hnoAE : blueb G c a e ≠ true := by
    intro h
    exact htri a e f halt helt hflt hneae hneef hneaf
      ⟨adjb_of_blueb h, hef', haf'⟩
  have hnoEA : blueb G c e a ≠ true := by
    intro h; apply hnoAE; rw [blueb_comm]; exact h
  have hnoAF : blueb G c a f ≠ true := by
    exact fun h => blueb_badb_false h haf
  have hnoFA : blueb G c f a ≠ true := by
    intro h; apply hnoAF; rw [blueb_comm]; exact h
  have hnoBE : blueb G c b e ≠ true := by
    intro h
    exact htri b d e hblt hdlt helt hnebd hnede hnebe
      ⟨hbd', hde', adjb_of_blueb h⟩
  have hnoEB : blueb G c e b ≠ true := by
    intro h; apply hnoBE; rw [blueb_comm]; exact h
  have hnoBF : blueb G c b f ≠ true := by
    intro h
    exact htri b a f hblt halt hflt (Ne.symm hneab) hneaf hnebf
      ⟨hba', haf', adjb_of_blueb h⟩
  have hnoFB : blueb G c f b ≠ true := by
    intro h; apply hnoBF; rw [blueb_comm]; exact h
  have hnoDF : blueb G c d f ≠ true := by
    intro h
    exact htri d e f hdlt helt hflt hnede hneef hnedf
      ⟨hde', hef', adjb_of_blueb h⟩
  have hnoFD : blueb G c f d ≠ true := by
    intro h; apply hnoDF; rw [blueb_comm]; exact h
  let q : Fin 5 → Nat := ![a, b, d, e, f]
  have hxq : ∃ ix : Fin 5, q ix = x := by
    simp at hx
    rcases hx with h | h | h | h | h
    · exact ⟨0, by simpa [q] using h.symm⟩
    · exact ⟨1, by simpa [q] using h.symm⟩
    · exact ⟨2, by simpa [q] using h.symm⟩
    · exact ⟨3, by simpa [q] using h.symm⟩
    · exact ⟨4, by simpa [q] using h.symm⟩
  have hyq : ∃ iy : Fin 5, q iy = y := by
    simp at hy
    rcases hy with h | h | h | h | h
    · exact ⟨0, by simpa [q] using h.symm⟩
    · exact ⟨1, by simpa [q] using h.symm⟩
    · exact ⟨2, by simpa [q] using h.symm⟩
    · exact ⟨3, by simpa [q] using h.symm⟩
    · exact ⟨4, by simpa [q] using h.symm⟩
  rcases hxq with ⟨ix, hix⟩
  rcases hyq with ⟨iy, hiy⟩
  fin_cases ix <;> simp [q] at hix
  all_goals subst x
  all_goals fin_cases iy <;> simp [q] at hiy
  all_goals subst y
  all_goals simp [rowPathEdges, normEdge_comm] at ⊢
  all_goals exfalso
  all_goals first
    | exact blueb_irrefl_false hblue
    | exact hnoAD hblue
    | exact hnoDA hblue
    | exact hnoAE hblue
    | exact hnoEA hblue
    | exact hnoAF hblue
    | exact hnoFA hblue
    | exact hnoBE hblue
    | exact hnoEB hblue
    | exact hnoBF hblue
    | exact hnoFB hblue
    | exact hnoDF hblue
    | exact hnoFD hblue

/-- Triangle-freeness makes every checked length-five row induced with respect
to blue edges.  This is the literal `Row5` version of shortest-row inducedness.
-/
theorem checkedRow_blue_cooccur_implies_pathEdge
    {G : GraphData} {c : CutData} {u v : Nat} {row : Row5}
    (htri : TriangleFree G)
    (hcheck : checkRow5 G c u v row = true)
    {x y : Nat} (hx : x ∈ row.verts) (hy : y ∈ row.verts)
    (hblue : blueb G c x y = true) :
    normEdge x y ∈ rowPathEdges row := by
  have hparts := hcheck
  unfold checkRow5 at hparts
  simp only [Bool.and_eq_true] at hparts
  have hlen : row.verts.length = 5 := of_decide_eq_true (by aesop)
  rcases list_eq_five_of_length hlen with ⟨a, b, d, e, f, hverts⟩
  have hall : a < G.n ∧ b < G.n ∧ d < G.n ∧ e < G.n ∧ f < G.n := by
    have h := hparts
    rw [hverts] at h
    simp at h
    aesop
  have hnd : [a, b, d, e, f].Nodup := by
    have : decide row.verts.Nodup = true := by aesop
    simpa [hverts] using of_decide_eq_true this
  have hhead : a = u := by
    have : decide (row.verts.head? = some u) = true := by aesop
    simpa [hverts] using of_decide_eq_true this
  have hlast : f = v := by
    have : decide (row.verts.getLast? = some v) = true := by aesop
    simpa [hverts] using of_decide_eq_true this
  have hpath : blueb G c a b = true ∧ blueb G c b d = true ∧
      blueb G c d e = true ∧ blueb G c e f = true := by
    have : (List.zip row.verts row.verts.tail).all
        (fun p => blueb G c p.1 p.2) = true := by aesop
    simpa [hverts] using this
  have hbad : badb G c a f = true := by
    have : badb G c u v = true := by aesop
    simpa [hhead, hlast] using this
  have h := literal_five_row_induced htri hall hnd hpath.1 hpath.2.1
    hpath.2.2.1 hpath.2.2.2 hbad (by simpa [hverts] using hx)
    (by simpa [hverts] using hy) hblue
  simpa [rowPathEdges, hverts] using h

/-- Pair multiplicity at least two leaves a different selected row containing
the pair when one distinguished row is removed. -/
theorem exists_other_selectedRow_of_pairCount_ge_two
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (i : Fin bads.length) {x y : Nat}
    (hxi : x ∈ ((bads.get i).rows.get (omega i)).verts)
    (hyi : y ∈ ((bads.get i).rows.get (omega i)).verts)
    (hmul : 2 ≤ pairCount omega x y) :
    ∃ j : Fin bads.length, j ≠ i ∧
      x ∈ ((bads.get j).rows.get (omega j)).verts ∧
      y ∈ ((bads.get j).rows.get (omega j)).verts := by
  let S := Finset.univ.filter fun j : Fin bads.length =>
    x ∈ ((bads.get j).rows.get (omega j)).verts ∧
      y ∈ ((bads.get j).rows.get (omega j)).verts
  have hcard : 2 ≤ S.card := by
    simpa [S, pairCount_eq_card_filter] using hmul
  have hi : i ∈ S := by
    exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, hxi, hyi⟩
  by_contra h
  push_neg at h
  have hsub : S ⊆ {i} := by
    intro j hj
    simp only [Finset.mem_singleton]
    by_contra hji
    have hs := (Finset.mem_filter.mp hj).2
    exact h j hji hs.1 hs.2
  have hle := Finset.card_le_card hsub
  simp at hle
  omega

/-- General support-persistence theorem.  Replacing a selected row by one
omitting `m` cannot activate a blue edge `m-x` of multiplicity at least two:
another checked selected row contains the pair, inducedness makes it a path
edge there, and hence it remains in selected support. -/
theorem support_persists_after_replacing_row_omitting_endpoint
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (htri : TriangleFree G) (hdb : CompleteShortestRowDB G c bads)
    (omega : RowChoice bads) (i : Fin bads.length)
    (replacement : Fin (bads.get i).rows.length) {m x : Nat}
    (hmOld : m ∈ ((bads.get i).rows.get (omega i)).verts)
    (hxOld : x ∈ ((bads.get i).rows.get (omega i)).verts)
    (hmNew : m ∉ ((bads.get i).rows.get replacement).verts)
    (hblue : blueb G c m x = true)
    (hmul : 2 ≤ pairCount omega m x) :
    normEdge m x ∈ selectedSupport (replaceOne omega i replacement) ∧
      normEdge m x ∉ activeEdges G c (replaceOne omega i replacement) := by
  have hmOmitted := hmNew
  clear hmOmitted
  rcases exists_other_selectedRow_of_pairCount_ge_two omega i hmOld hxOld hmul with
    ⟨j, hji, hmj, hxj⟩
  have hcheck := selectedRow_checked hdb.checked omega j
  have hedge := checkedRow_blue_cooccur_implies_pathEdge
    htri hcheck hmj hxj hblue
  have hrow : (bads.get j).rows.get (omega j) ∈
      selectedRows (replaceOne omega i replacement) := by
    rw [mem_selectedRows_replaceOne_iff]
    exact Or.inr ⟨j, hji, rfl⟩
  have hsupport : normEdge m x ∈
      selectedSupport (replaceOne omega i replacement) := by
    simp only [selectedSupport, List.mem_dedup, List.mem_flatMap]
    exact ⟨(bads.get j).rows.get (omega j), hrow, hedge⟩
  refine ⟨hsupport, ?_⟩
  have hnorm :
      normEdge (normEdge m x).1 (normEdge m x).2 = normEdge m x := by
    by_cases hmx : m < x
    · simp [normEdge, hmx]
    · by_cases hxm : x < m
      · simp [normEdge, hmx, hxm]
      · have : m = x := by omega
        subst x
        simp [normEdge]
  simp [activeEdges, hnorm, hsupport]

/-- A strict multiplicity-saturated transition asks an edge to become active
even though the old selected pair occurs at least twice. -/
structure StrictMultiplicitySaturatedTransition
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Type where
  index : Fin bads.length
  replacement : Fin (bads.get index).rows.length
  oldMiddle : Nat
  retained : Nat
  oldMiddle_mem :
    oldMiddle ∈ ((bads.get index).rows.get (omega index)).verts
  retained_mem : retained ∈ ((bads.get index).rows.get (omega index)).verts
  oldMiddle_omitted :
    oldMiddle ∉ ((bads.get index).rows.get replacement).verts
  blue : blueb G c oldMiddle retained = true
  saturated : 2 ≤ pairCount omega oldMiddle retained
  becomes_active : normEdge oldMiddle retained ∈
    activeEdges G c (replaceOne omega index replacement)

/-- The strict R38 multiplicity-saturated inverse rotor is impossible already
at either directed transition. -/
theorem strictMultiplicitySaturatedTransition_empty
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (htri : TriangleFree G) (hdb : CompleteShortestRowDB G c bads)
    (omega : RowChoice bads) :
    IsEmpty (StrictMultiplicitySaturatedTransition G c omega) := by
  refine ⟨fun T => ?_⟩
  exact (support_persists_after_replacing_row_omitting_endpoint
    htri hdb omega T.index T.replacement T.oldMiddle_mem T.retained_mem
    T.oldMiddle_omitted T.blue T.saturated).2 T.becomes_active

#print axioms checkedRow_blue_cooccur_implies_pathEdge
#print axioms exists_other_selectedRow_of_pairCount_ge_two
#print axioms support_persists_after_replacing_row_omitting_endpoint
#print axioms strictMultiplicitySaturatedTransition_empty

end SaturatedRotorSupportPersistence
end Gamma
end Erdos23Delta0
