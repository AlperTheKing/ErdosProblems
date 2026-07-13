import Erdos23Delta0.Gamma.MinimumDemandRowSelection

/-!
# A nonendpoint row occurrence uses two owner-star edges

This is the graph adapter for the external atom forced by dual strict Hall.
In a checked five-vertex row, any occurring vertex that is not a bad endpoint
is internal and therefore has two distinct path neighbours.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CheckedRowInternalOwner

open CertGraph
open MinimumDemandRowSelection

/-- Pure five-row incidence form. -/
theorem internal_vertex_has_two_path_edges
    (row : Row5) (u p h q w v : Nat)
    (hverts : row.verts = [u, p, h, q, w])
    (hnodup : row.verts.Nodup)
    (hvmem : v ∈ row.verts)
    (hvneU : v ≠ u) (hvneW : v ≠ w) :
    exists z0 z1,
      z0 ≠ z1 ∧
      normEdge v z0 ∈ rowPathEdges row ∧
      normEdge v z1 ∈ rowPathEdges row := by
  have hcases : v = p ∨ v = h ∨ v = q := by
    simp [hverts] at hvmem
    rcases hvmem with hvu | hvp | hvh | hvq | hvw
    · exact False.elim (hvneU hvu)
    · exact Or.inl hvp
    · exact Or.inr (Or.inl hvh)
    · exact Or.inr (Or.inr hvq)
    · exact False.elim (hvneW hvw)
  have hdistinct : List.Nodup [u, p, h, q, w] := by
    simpa [hverts] using hnodup
  rcases hcases with rfl | rfl | rfl
  · refine ⟨u, h, ?_, ?_, ?_⟩
    · intro heq
      subst h
      simp at hdistinct
    · simp [rowPathEdges, hverts, normEdge_comm]
    · simp [rowPathEdges, hverts]
  · refine ⟨p, q, ?_, ?_, ?_⟩
    · intro heq
      subst q
      simp at hdistinct
    · simp [rowPathEdges, hverts, normEdge_comm]
    · simp [rowPathEdges, hverts]
  · refine ⟨h, w, ?_, ?_, ?_⟩
    · intro heq
      subst w
      simp at hdistinct
    · simp [rowPathEdges, hverts, normEdge_comm]
    · simp [rowPathEdges, hverts]

#print axioms internal_vertex_has_two_path_edges

end CheckedRowInternalOwner
end Gamma
end Erdos23Delta0
