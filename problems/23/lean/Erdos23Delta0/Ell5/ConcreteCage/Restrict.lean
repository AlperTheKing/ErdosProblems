import Erdos23Delta0.Ell5.ConcreteCage.Proper

/-!
# Concrete ell=5 cage bookkeeping: vertex restrictions

Restriction keeps exactly the atoms whose full multi-geodesic supports are
contained in the chosen vertex set.
-/

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} {c : Distances.Cut V}

/-- Restrict an ambient cage to atoms supported on `U`. -/
noncomputable def restrict (C : AmbientCage G c) (U : Finset V) : AmbientCage G c :=
  by
    classical
    refine
      { verts := U
        atoms := C.atoms.filter fun a => atomSupportedOn a U
        atom_support_subset := ?_ }
    intro a ha
    rw [Finset.mem_filter] at ha
    exact ha.2

/-- Restrict to the complement of a vertex set inside the ambient cage. -/
noncomputable def restrictCompl (C : AmbientCage G c) (U : Finset V) : AmbientCage G c :=
  restrict C (C.verts \ U)

theorem mem_restrict_atoms {C : AmbientCage G c} {U : Finset V}
    {a : Atom (Distances.blueGraph G c)} :
    a ∈ (restrict C U).atoms ↔ a ∈ C.atoms ∧ atomSupportedOn a U := by
  classical
  simp [restrict]

theorem restrict_atoms_subset {C : AmbientCage G c} {U : Finset V} :
    (restrict C U).atoms ⊆ C.atoms := by
  intro a ha
  exact (mem_restrict_atoms.mp ha).1

theorem mem_restrictCompl_atoms {C : AmbientCage G c} {U : Finset V}
    {a : Atom (Distances.blueGraph G c)} :
    a ∈ (restrictCompl C U).atoms ↔
      a ∈ C.atoms ∧ atomSupportedOn a (C.verts \ U) := by
  simp [restrictCompl, mem_restrict_atoms]

end ConcreteCage
end Ell5
end Erdos23Delta0
