import Erdos23Delta0.Ell5.ConcreteCage.Bank

/-!
# Concrete ell=5 cage bookkeeping: proper ambient subcages

Properness is relative to an ambient cage.  It is deliberately not an induced
max-cut assertion; it records the vertex-set strictness and the blue
connectivity obligations that the lens certificate supplies later.
-/

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} {c : Distances.Cut V}

/-- A proper prunable descendant of an ambient cage. -/
structure AmbientProperSubcage (C D : AmbientCage G c) : Prop where
  verts_subset : D.verts ⊆ C.verts
  verts_ne : D.verts ≠ C.verts
  insideBlueConnected :
    ((Distances.blueGraph G c).induce ((D.verts : Set V))).Connected
  complementBlueConnected :
    ((Distances.blueGraph G c).induce (((C.verts \ D.verts : Finset V) : Set V))).Connected

/-- The unary `Proper` predicate consumed by the abstract pure-lens interface,
relative to a fixed ambient cage. -/
def ProperRelative (C : AmbientCage G c) (D : AmbientCage G c) : Prop :=
  AmbientProperSubcage C D

theorem proper_verts_subset {C D : AmbientCage G c}
    (h : ProperRelative C D) :
    D.verts ⊆ C.verts :=
  h.verts_subset

theorem proper_verts_ne {C D : AmbientCage G c}
    (h : ProperRelative C D) :
    D.verts ≠ C.verts :=
  h.verts_ne

#print axioms proper_verts_subset
#print axioms proper_verts_ne

end ConcreteCage
end Ell5
end Erdos23Delta0
