import Erdos23Delta0.Ell5LensStatement

/-!
# Concrete ell=5 cage bookkeeping: basic vocabulary

This module starts the T8 concrete cage model against the existing compiled
surface.  The design note used a speculative `vertexSupport`; here the support
predicate is defined from the real multi-geodesic edge support
`Ell5SupportFinset.geodesicSupport` and the standard `Finset.sym2` vertex
closure.
-/

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Concrete ell=5 atoms are the existing geodesic-carrying atoms. -/
abbrev Atom (H : SimpleGraph V) := Ell5AtomBase.Ell5Atom H

/-- The bad edge associated to an atom. -/
def atomBadEdge {H : SimpleGraph V} (a : Atom H) : Sym2 V :=
  s(a.u, a.v)

/-- The full multi-geodesic edge support of an atom. -/
noncomputable def atomEdgeSupport {H : SimpleGraph V} (a : Atom H) : Finset (Sym2 V) :=
  Ell5SupportFinset.geodesicSupport H a.u a.v

/-- An atom is supported on a vertex set when every edge in its full support has
both endpoints in that vertex set. -/
def atomSupportedOn {H : SimpleGraph V} (a : Atom H) (U : Finset V) : Prop :=
  atomEdgeSupport a ⊆ U.sym2

/-- The ambient row length of an atom's bad edge. -/
noncomputable def atomEll (G : SimpleGraph V) (c : Distances.Cut V)
    (a : Atom (Distances.blueGraph G c)) : ℚ :=
  (Distances.ell G c a.u a.v : ℚ)

/-- Local surplus contribution of an atom, normalized to vanish at length 5. -/
noncomputable def atomSurplus (G : SimpleGraph V) (c : Distances.Cut V)
    (a : Atom (Distances.blueGraph G c)) : ℚ :=
  atomEll G c a ^ 2 - 25

/-- Length-five atoms have zero surplus. -/
theorem atom_surplus_eq_zero_of_ell5 (G : SimpleGraph V) (c : Distances.Cut V)
    (a : Atom (Distances.blueGraph G c))
    (hell : Distances.ell G c a.u a.v = 5) :
    atomSurplus G c a = 0 := by
  simp [atomSurplus, atomEll, hell]
  norm_num

/-- Full edge support is nonempty once the carried geodesic is known to be
distance-tight. -/
theorem atomEdgeSupport_nonempty_of_dist4 {H : SimpleGraph V} (a : Atom H)
    (hd : H.dist a.u a.v = 4) :
    (atomEdgeSupport a).Nonempty := by
  have hsub : a.support ⊆ atomEdgeSupport a :=
    Ell5SupportFinset.atom_support_subset_geodesicSupport a hd
  have hpos : 0 < a.support.card := by
    rw [a.support_card]
    norm_num
  obtain ⟨e, he⟩ := Finset.card_pos.mp hpos
  exact ⟨e, hsub he⟩

/-- A concrete ambient cage: a vertex set plus the atoms whose full supports it
owns. -/
structure AmbientCage (G : SimpleGraph V) (c : Distances.Cut V) where
  verts : Finset V
  atoms : Finset (Atom (Distances.blueGraph G c))
  atom_support_subset : ∀ a, a ∈ atoms → atomSupportedOn a verts

namespace AmbientCage

variable {G : SimpleGraph V} {c : Distances.Cut V}

/-- Sum of squared row lengths in a cage. -/
noncomputable def gammaOf (C : AmbientCage G c) : ℚ :=
  C.atoms.sum fun a => atomEll G c a ^ 2

/-- Sum of normalized surplus contributions in a cage. -/
noncomputable def Surplus (C : AmbientCage G c) : ℚ :=
  C.atoms.sum fun a => atomSurplus G c a

/-- The surplus sum is just gamma minus the length-five baseline. -/
theorem Surplus_eq_gamma_sub_25_card (C : AmbientCage G c) :
    C.Surplus = C.gammaOf - 25 * (C.atoms.card : ℚ) := by
  simp [Surplus, gammaOf, atomSurplus]
  ring

end AmbientCage

end ConcreteCage
end Ell5
end Erdos23Delta0
