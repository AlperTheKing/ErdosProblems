import Erdos23Delta0.Ell5SupportFinset

/-!
# A shortest row has no off-row chord

The R18 transfer construction needs the following scope-corrected graph fact:
if two vertices co-occur on one shortest blue row and are joined by a blue
edge, that edge is already a row edge.  The result is true for shortest walks
of arbitrary length.

The proof uses positions rather than a length-four case split.  Every prefix
of a shortest walk is a shortest subwalk, so the distance from the initial
vertex to position `i` is exactly `i`.  Adjacent vertices have distance levels
differing by at most one; looplessness rules out equality.  Their positions
are therefore consecutive.
-/

namespace Erdos23Delta0

open SimpleGraph

variable {V : Type*} {H : SimpleGraph V}

private theorem edge_getVert_succ_mem_edges {u v : V} (P : H.Walk u v)
    {i : ℕ} (hi : i < P.length) :
    s(P.getVert i, P.getVert (i + 1)) ∈ P.edges := by
  have hidarts : i < P.darts.length := by simpa using hi
  have hdmem : P.darts[i] ∈ P.darts := List.getElem_mem hidarts
  have hemem : P.darts[i].edge ∈ P.edges := by
    exact List.mem_map.mpr ⟨P.darts[i], hdmem, rfl⟩
  rw [P.darts_getElem_eq_getVert i hidarts] at hemem
  exact hemem

/-- Two adjacent vertices on a shortest row occur consecutively on that row. -/
theorem internalOffSupport_cooccur_implies_rowEdge
    {u v x y : V} (P : H.Walk u v)
    (hshort : P.length = H.dist u v)
    (hx : x ∈ P.support) (hy : y ∈ P.support)
    (hxy : H.Adj x y) :
    s(x, y) ∈ P.edges := by
  obtain ⟨i, hi, hiLe⟩ := Walk.mem_support_iff_exists_getVert.mp hx
  obtain ⟨j, hj, hjLe⟩ := Walk.mem_support_iff_exists_getVert.mp hy
  subst x
  subst y
  have hdistI : i = H.dist u (P.getVert i) := by
    have h := length_eq_dist_of_subwalk hshort (P.isSubwalk_take i)
    simpa [Nat.min_eq_left hiLe] using h
  have hdistJ : j = H.dist u (P.getVert j) := by
    have h := length_eq_dist_of_subwalk hshort (P.isSubwalk_take j)
    simpa [Nat.min_eq_left hjLe] using h
  rcases hxy.diff_dist_adj (u := u) with hEq | hUp | hDown
  · rw [← hdistI, ← hdistJ] at hEq
    have hij : i = j := by omega
    subst j
    exact False.elim (H.loopless _ hxy)
  · rw [← hdistI, ← hdistJ] at hUp
    have hij : j = i + 1 := by omega
    subst j
    exact edge_getVert_succ_mem_edges P (by omega)
  · rw [← hdistI, ← hdistJ] at hDown
    have hij : i = j + 1 := by
      have hne : i ≠ j := by
        intro hij
        exact hxy.ne (congrArg P.getVert hij)
      omega
    subst i
    rw [Sym2.eq_swap]
    exact edge_getVert_succ_mem_edges P (by omega)

/-- An edge outside one row cannot have both endpoints on that row.  This is
the form consumed after restricting the family support to the selected atom
family. -/
theorem internalOffSupport_not_cooccur_in_familyRow
    {u v x y : V} (P : H.Walk u v)
    (hshort : P.length = H.dist u v)
    (hOff : s(x, y) ∉ P.edges) (hxy : H.Adj x y) :
    ¬(x ∈ P.support ∧ y ∈ P.support) := by
  rintro ⟨hx, hy⟩
  exact hOff (internalOffSupport_cooccur_implies_rowEdge P hshort hx hy hxy)

/-- Real selected-family form.  If `A` is the chosen atom family and `F` is
its full multi-geodesic support `Eshort H A`, then an edge outside `F` cannot
have both endpoints on any shortest row of an atom in `A`.

This scope restriction is essential: rows belonging to atoms outside `A` may
legitimately use an edge outside `Eshort H A`. -/
theorem selectedFamily_internalOffSupport_not_cooccur
    [Fintype V] [DecidableEq V]
    (A : Finset (Ell5AtomBase.Ell5Atom H))
    {a : Ell5AtomBase.Ell5Atom H} (ha : a ∈ A)
    (P : H.Walk a.u a.v) (hshort : P.length = H.dist a.u a.v)
    {x y : V} (hxy : H.Adj x y)
    (hOff : s(x, y) ∉ Ell5SupportFinset.Eshort H A) :
    ¬(x ∈ P.support ∧ y ∈ P.support) := by
  rintro ⟨hx, hy⟩
  have hrow : s(x, y) ∈ P.edges :=
    internalOffSupport_cooccur_implies_rowEdge P hshort hx hy hxy
  have hgeo : s(x, y) ∈
      Ell5SupportFinset.geodesicSupport H a.u a.v :=
    Ell5SupportFinset.mem_geodesicSupport.mpr
      ⟨P, P.isPath_of_length_eq_dist hshort, hshort, hrow⟩
  exact hOff (Finset.mem_biUnion.mpr ⟨a, ha, hgeo⟩)

#print axioms internalOffSupport_cooccur_implies_rowEdge
#print axioms internalOffSupport_not_cooccur_in_familyRow
#print axioms selectedFamily_internalOffSupport_not_cooccur

end Erdos23Delta0
