import Erdos23Delta0.Gamma.MinimumDemandCollisionHall

/-!
# Endpoint anchoring of selected shortest rows

The corrected R34 trace state must retain the producing bad edge and row
occurrence.  The abstract sterile-cycle countermodel allowed several atoms to
share one row.  `CompleteShortestRowDB` excludes that situation: every listed
row is checked from its own bad-edge endpoints, and bad endpoint keys are
pairwise distinct.
-/

namespace Erdos23Delta0
namespace Gamma
namespace SelectedRowEndpointAnchoring

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}

/-- The row selected at one bad-edge index passes the literal endpoint/path
checker for that bad edge. -/
theorem selectedRow_checked
    (hdb : CompleteShortestRowDB G c bads)
    (omega : RowChoice bads) (i : Fin bads.length) :
    checkRow5 G c (bads.get i).u (bads.get i).v
      ((bads.get i).rows.get (omega i)) = true := by
  have hbad := List.all_eq_true.mp hdb.checked
    (bads.get i) (List.get_mem bads i)
  unfold checkBadEdge at hbad
  simp only [Bool.and_eq_true] at hbad
  exact List.all_eq_true.mp hbad.2
    ((bads.get i).rows.get (omega i))
    (List.get_mem (bads.get i).rows (omega i))

/-- The selected row starts and ends at the ordered endpoints stored by its
producing bad-edge record. -/
theorem selectedRow_endpoints
    (hdb : CompleteShortestRowDB G c bads)
    (omega : RowChoice bads) (i : Fin bads.length) :
    (((bads.get i).rows.get (omega i)).verts.head? =
        some (bads.get i).u) ∧
      (((bads.get i).rows.get (omega i)).verts.getLast? =
        some (bads.get i).v) := by
  have hcheck := selectedRow_checked hdb omega i
  unfold checkRow5 at hcheck
  simp only [Bool.and_eq_true] at hcheck
  rcases hcheck with
    ⟨⟨⟨⟨⟨⟨_hlen, _hrange⟩, _hnodup⟩, hhead⟩, hlast⟩,
      _hsteps⟩, _hbad⟩
  exact ⟨of_decide_eq_true hhead, of_decide_eq_true hlast⟩

/-- A selected row is a five-vertex simple path. -/
theorem selectedRow_length_and_nodup
    (hdb : CompleteShortestRowDB G c bads)
    (omega : RowChoice bads) (i : Fin bads.length) :
    ((bads.get i).rows.get (omega i)).verts.length = 5 ∧
      ((bads.get i).rows.get (omega i)).verts.Nodup := by
  have hcheck := selectedRow_checked hdb omega i
  unfold checkRow5 at hcheck
  simp only [Bool.and_eq_true] at hcheck
  rcases hcheck with
    ⟨⟨⟨⟨⟨⟨hlen, _hrange⟩, hnodup⟩, _hhead⟩, _hlast⟩,
      _hsteps⟩, _hbad⟩
  exact ⟨of_decide_eq_true hlen, of_decide_eq_true hnodup⟩

/-- Distinct bad-edge indices cannot select the same ordered row vertex list.
This is the exact production fact missing from R34's sterile abstract cycle. -/
theorem selectedRow_verts_injective
    (hdb : CompleteShortestRowDB G c bads)
    (omega : RowChoice bads) :
    Function.Injective
      (fun i : Fin bads.length =>
        ((bads.get i).rows.get (omega i)).verts) := by
  intro i j hrows
  have hi := selectedRow_endpoints hdb omega i
  have hj := selectedRow_endpoints hdb omega j
  have hu : (bads.get i).u = (bads.get j).u := by
    have hheads := congrArg List.head? hrows
    have : some (bads.get i).u = some (bads.get j).u := by
      exact hi.1.symm.trans (hheads.trans hj.1)
    exact Option.some.inj this
  have hv : (bads.get i).v = (bads.get j).v := by
    have hlasts := congrArg List.getLast? hrows
    have : some (bads.get i).v = some (bads.get j).v := by
      exact hi.2.symm.trans (hlasts.trans hj.2)
    exact Option.some.inj this
  let i' : Fin (bads.map badEdgeKey).length :=
    ⟨i.1, by simp⟩
  let j' : Fin (bads.map badEdgeKey).length :=
    ⟨j.1, by simp⟩
  have hkey : badEdgeKey (bads.get i) = badEdgeKey (bads.get j) := by
    unfold badEdgeKey
    rw [hu, hv]
  have hget : (bads.map badEdgeKey).get i' =
      (bads.map badEdgeKey).get j' := by
    simpa [i', j'] using hkey
  have hij : i' = j' := hdb.badKeys_nodup.get_inj_iff.mp hget
  apply Fin.ext
  simpa [i', j'] using congrArg Fin.val hij

#print axioms selectedRow_checked
#print axioms selectedRow_endpoints
#print axioms selectedRow_verts_injective

end SelectedRowEndpointAnchoring
end Gamma
end Erdos23Delta0
