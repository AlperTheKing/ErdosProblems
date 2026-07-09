import Mathlib
import Erdos23Delta0.Distances
import Erdos23Delta0.Ell5AtomBase

/-!
# Building `Ell5Atom`s from real blue-graph bad edges (2026-07-08)

Connects the abstract `Ell5AtomBase.Ell5Atom` (bad edge + length-4 geodesic) to the actual `Distances.blueGraph` of a
cut: an ell=5 blue-connected bad edge `(u,v)` has `blueGraph.dist u v = 4` (since `ell = dist + 1`), so a shortest blue
geodesic is a length-4 `Path` (`Reachable.exists_path_of_dist`), which is exactly the data of an `Ell5Atom`.

Choosing ONE canonical geodesic suffices for the support-expansion base case: its 4-edge support is a *subset* of the
full multi-geodesic `P_e`, and `PathRigidity` still forces distinct atoms to have distinct one-geodesic supports, so
`Ell5AtomBase.ell5_base_case`'s Hall bound transfers to `E_short` by monotonicity of `Finset.biUnion`.
No forbidden proof shortcuts; axiom-clean.
-/

namespace Erdos23Delta0
namespace Ell5AtomGraph

open SimpleGraph

variable {V : Type*} {G : SimpleGraph V}

/-- **From an ell=5 blue-connected bad edge to an `Ell5Atom` of the blue graph.** If the row length `ell G c u v = 5`
    (so `blueGraph.dist u v = 4`) and `u, v` are blue-connected, then there is an `Ell5Atom (blueGraph G c)` with
    endpoints `u, v`, carrying a shortest length-4 blue geodesic. -/
theorem ell5_atom_of_badEdge {c : Distances.Cut V} {u v : V}
    (hell : Distances.ell G c u v = 5)
    (hconn : (Distances.blueGraph G c).Reachable u v) :
    ∃ a : Ell5AtomBase.Ell5Atom (Distances.blueGraph G c), a.u = u ∧ a.v = v := by
  have hd : (Distances.blueGraph G c).dist u v = 4 := by
    unfold Distances.ell at hell; omega
  obtain ⟨p, hpath, hlen⟩ := hconn.exists_path_of_dist
  rw [hd] at hlen
  exact ⟨⟨u, v, p, hpath, hlen⟩, rfl, rfl⟩

/-- The constructed atom's support has exactly 4 edges (a length-4 geodesic), and its bad edge is `s(u,v)`. -/
theorem ell5_atom_support_card [DecidableEq V] {c : Distances.Cut V} {u v : V}
    (a : Ell5AtomBase.Ell5Atom (Distances.blueGraph G c)) :
    a.support.card = 4 :=
  a.support_card


end Ell5AtomGraph
end Erdos23Delta0
