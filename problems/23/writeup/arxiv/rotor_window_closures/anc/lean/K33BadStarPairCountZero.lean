import Erdos23Delta0.Gamma.ActiveScopedCoordinateTransport
import Erdos23Delta0.Gamma.SelectedRowEndpointAnchoring
import Erdos23Delta0.Gamma.BadStarCoverFreeness

/-!
# K3,3 closed-bad-star adapter

This file lifts the row-local bad-star obstruction to the production
`pairCount` definition.  The hypotheses deliberately name only the database
facts supplied by a one-shore K3,3 bad circuit: every bad edge has both
endpoints on the owner's shore, and every bad edge is covered by the owner's
closed bad star.
-/

namespace Erdos23Delta0
namespace Gamma
namespace K33BadStarPairCountZero

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

private theorem list_eq_five_of_length_eq_five {alpha : Type*}
    (xs : List alpha) (hlen : xs.length = 5) :
    exists a b c d e : alpha, xs = [a, b, c, d, e] := by
  cases xs with
  | nil => simp at hlen
  | cons a xs =>
    cases xs with
    | nil => simp at hlen
    | cons b xs =>
      cases xs with
      | nil => simp at hlen
      | cons c xs =>
        cases xs with
        | nil => simp at hlen
        | cons d xs =>
          cases xs with
          | nil => simp at hlen
          | cons e xs =>
            have htail : xs = [] := by
              exact List.length_eq_zero_iff.mp (by simpa using hlen)
            subst xs
            exact ⟨a, b, c, d, e, rfl⟩

/-- Database-level closed bad-star hypotheses at one owner. -/
structure ClosedBadStarDB
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (v : Fin G.n) : Prop where
  endpointBounds : forall i : Fin bads.length,
    (bads.get i).u < G.n ∧ (bads.get i).v < G.n
  endpointSides : forall i : Fin bads.length,
    sideb c (bads.get i).u = sideb c v.1 ∧
      sideb c (bads.get i).v = sideb c v.1
  closedCover : forall i : Fin bads.length,
    v.1 = (bads.get i).u ∨ v.1 = (bads.get i).v ∨
      badb G c v.1 (bads.get i).u = true ∨
      badb G c v.1 (bads.get i).v = true

private theorem rowPath_mem_selectedSupport
    {bads : List BadEdgeData} (omega : RowChoice bads)
    {row : Row5} (hrow : row ∈ selectedRows omega)
    {e : Nat × Nat} (he : e ∈ rowPathEdges row) :
    e ∈ selectedSupport omega := by
  unfold selectedSupport
  apply List.mem_dedup.mpr
  exact List.mem_flatMap.mpr ⟨row, hrow, he⟩

/-- In a one-shore closed-bad-star database, an active blue edge `vx` and a
second blue neighbour `s` cannot be jointly covered by any selected row.
Consequently their production pair count is zero. -/
theorem pairCount_eq_zero_of_closedBadStar
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hdb : CompleteShortestRowDB G c bads)
    (omega : RowChoice bads)
    (v x s : Fin G.n)
    (htri : TriangleFree G)
    (hstar : ClosedBadStarDB G c bads v)
    (hvx : blueb G c v.1 x.1 = true)
    (hvs : blueb G c v.1 s.1 = true)
    (hxs : x ≠ s)
    (hxOffSupport : normEdge v.1 x.1 ∉ selectedSupport omega) :
    pairCount omega x.1 s.1 = 0 := by
  by_contra hne
  have hpos : 0 < pairCount omega x.1 s.1 := Nat.pos_of_ne_zero hne
  unfold pairCount at hpos
  have hfilter :
      ((selectedRows omega).filter fun row =>
        decide (x.1 ∈ row.verts ∧ s.1 ∈ row.verts)) ≠ [] :=
    List.ne_nil_of_length_pos hpos
  rcases List.exists_mem_of_ne_nil _ hfilter with ⟨row, hrowFilter⟩
  have hrowParts := List.mem_filter.mp hrowFilter
  have hrow : row ∈ selectedRows omega := hrowParts.1
  have hmem : x.1 ∈ row.verts ∧ s.1 ∈ row.verts :=
    of_decide_eq_true hrowParts.2
  rw [ActiveScopedMinimumExchange.mem_selectedRows_iff] at hrow
  rcases hrow with ⟨i, hrowEq⟩
  subst row
  let row := (bads.get i).rows.get (omega i)
  have hcheck : checkRow5 G c (bads.get i).u (bads.get i).v row = true :=
    SelectedRowEndpointAnchoring.selectedRow_checked hdb omega i
  have hshape := list_eq_five_of_length_eq_five row.verts
    (SelectedRowEndpointAnchoring.selectedRow_length_and_nodup hdb omega i).1
  rcases hshape with ⟨u, p, h, q, w, hverts⟩
  have hrange : row.verts.all (fun z => decide (z < G.n)) = true := by
    have hall := hcheck
    unfold checkRow5 at hall
    simp only [Bool.and_eq_true] at hall
    aesop
  rw [hverts] at hrange
  simp only [List.all_cons, List.all_nil, Bool.and_true, Bool.and_eq_true,
    decide_eq_true_eq] at hrange
  rcases hrange with ⟨hu, hp, hh, hq, hw⟩
  let uFin : Fin G.n := ⟨u, hu⟩
  let pFin : Fin G.n := ⟨p, hp⟩
  let hFin : Fin G.n := ⟨h, hh⟩
  let qFin : Fin G.n := ⟨q, hq⟩
  let wFin : Fin G.n := ⟨w, hw⟩
  have hend := SelectedRowEndpointAnchoring.selectedRow_endpoints hdb omega i
  have huEndpoint : u = (bads.get i).u := by
    have hhead : row.verts.head? = some u := by simp [hverts]
    have huSome : some u = some (bads.get i).u := by
      exact hhead.symm.trans hend.1
    exact Option.some.inj huSome
  have hwEndpoint : w = (bads.get i).v := by
    have hlast : row.verts.getLast? = some w := by simp [hverts]
    have hwSome : some w = some (bads.get i).v := by
      exact hlast.symm.trans hend.2
    exact Option.some.inj hwSome
  have hcheck' : checkRow5 G c u w row = true := by
    simpa [huEndpoint, hwEndpoint] using hcheck
  have hside := hstar.endpointSides i
  have hcover := hstar.closedCover i
  have huSide : sideb c u = sideb c v.1 := by simpa [huEndpoint] using hside.1
  have hwSide : sideb c w = sideb c v.1 := by simpa [hwEndpoint] using hside.2
  have hcoverFin : v = uFin ∨ v = wFin ∨
      badb G c v.1 u = true ∨ badb G c v.1 w = true := by
    rcases hcover with h | h | h | h
    · exact Or.inl (Fin.ext (by simpa [uFin, huEndpoint] using h))
    · exact Or.inr <| Or.inl (Fin.ext (by simpa [wFin, hwEndpoint] using h))
    · exact Or.inr <| Or.inr <| Or.inl (by simpa [huEndpoint] using h)
    · exact Or.inr <| Or.inr <| Or.inr (by simpa [hwEndpoint] using h)
  have hxNotRow : normEdge v.1 x.1 ∉ rowPathEdges row := by
    intro he
    exact hxOffSupport <| rowPath_mem_selectedSupport omega
      (by simp [row, selectedRows, List.mem_ofFn]) he
  exact BadStarCoverFreeness.bad_star_cover_row_impossible
    v uFin pFin hFin qFin wFin x s row htri
    (by simpa [uFin, pFin, hFin, qFin, wFin] using hverts)
    hcheck' huSide hwSide hvx hvs hxs
    (by simpa [row] using hmem.1) (by simpa [row] using hmem.2)
    hcoverFin hxNotRow

#print axioms pairCount_eq_zero_of_closedBadStar

end K33BadStarPairCountZero
end Gamma
end Erdos23Delta0

