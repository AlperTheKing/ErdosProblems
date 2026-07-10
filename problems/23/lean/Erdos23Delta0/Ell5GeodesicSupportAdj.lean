import Erdos23Delta0.Ell5SupportFinset

/-!
# Adjacent geodesic vertices force a supported edge

In a blue graph, distance from a fixed vertex changes parity across every
edge.  Hence an edge joining two vertices which each lie on a shortest
`a`-`b` geodesic must move exactly one distance layer.  Splicing the edge
between shortest prefix and suffix walks puts it on another shortest
`a`-`b` geodesic.
-/

namespace Erdos23Delta0
namespace Ell5GeodesicSupportAdj

open SimpleGraph
open Ell5SupportFinset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Metric characterization of a vertex lying on a shortest geodesic. -/
def OnGeodesic (H : SimpleGraph V) (a b x : V) : Prop :=
  H.Reachable a x ∧ H.Reachable x b ∧
    H.dist a x + H.dist x b = H.dist a b

private theorem bool_eq_of_left_eq_iff {x y z : Bool}
    (h : (x = y) ↔ (x = z)) : y = z := by
  cases x <;> cases y <;> cases z <;> simp_all

/-- In a blue graph, an edge whose endpoints both lie on shortest `a`-`b`
geodesics belongs to the full shortest-geodesic edge support. -/
theorem blue_adj_mem_geodesicSupport
    (G : SimpleGraph V) (c : Distances.Cut V) {a b u v : V}
    (hadj : (Distances.blueGraph G c).Adj u v)
    (hu : OnGeodesic (Distances.blueGraph G c) a b u)
    (hv : OnGeodesic (Distances.blueGraph G c) a b v) :
    s(u, v) ∈ geodesicSupport (Distances.blueGraph G c) a b := by
  have hdist_ne :
      (Distances.blueGraph G c).dist a u ≠
        (Distances.blueGraph G c).dist a v := by
    intro heq
    obtain ⟨pu, hpu⟩ := hu.1.exists_walk_length_eq_dist
    obtain ⟨pv, hpv⟩ := hv.1.exists_walk_length_eq_dist
    have hparu := Distances.blue_walk_parity G c pu
    have hparv := Distances.blue_walk_parity G c pv
    have hsuv : c.side u = c.side v := by
      rw [hpu, heq] at hparu
      rw [hpv] at hparv
      have hiff : (c.side a = c.side u) ↔ (c.side a = c.side v) :=
        hparu.trans hparv.symm
      exact bool_eq_of_left_eq_iff hiff
    exact hadj.2 hsuv
  rcases hadj.diff_dist_adj (u := a) with hEq | hUp | hDown
  · exact (hdist_ne hEq.symm).elim
  · obtain ⟨pau, hpau⟩ := hu.1.exists_walk_length_eq_dist
    obtain ⟨pvb, hpvb⟩ := hv.2.1.exists_walk_length_eq_dist
    let p : (Distances.blueGraph G c).Walk a b :=
      (pau.concat hadj).append pvb
    have hp : p.length = (Distances.blueGraph G c).dist a b := by
      simp only [p, Walk.length_append, Walk.length_concat]
      rw [hpau, hpvb, ← hUp]
      exact hv.2.2
    apply mem_geodesicSupport.mpr
    refine ⟨p, p.isPath_of_length_eq_dist hp, hp, ?_⟩
    simp [p]
  · have hUp' :
        (Distances.blueGraph G c).dist a u =
          (Distances.blueGraph G c).dist a v + 1 := by
      omega
    obtain ⟨pav, hpav⟩ := hv.1.exists_walk_length_eq_dist
    obtain ⟨pub, hpub⟩ := hu.2.1.exists_walk_length_eq_dist
    let p : (Distances.blueGraph G c).Walk a b :=
      (pav.concat hadj.symm).append pub
    have hp : p.length = (Distances.blueGraph G c).dist a b := by
      simp only [p, Walk.length_append, Walk.length_concat]
      rw [hpav, hpub, ← hUp']
      exact hu.2.2
    apply mem_geodesicSupport.mpr
    refine ⟨p, p.isPath_of_length_eq_dist hp, hp, ?_⟩
    simp [p]

/-- Contrapositive in the form used by the off-support Hall argument: an
off-support blue edge cannot have both endpoints on shortest rows of the same
bad atom. -/
theorem not_both_onGeodesic_of_adj_not_mem
    (G : SimpleGraph V) (c : Distances.Cut V) {a b u v : V}
    (hadj : (Distances.blueGraph G c).Adj u v)
    (hoff : s(u, v) ∉ geodesicSupport (Distances.blueGraph G c) a b) :
    ¬(OnGeodesic (Distances.blueGraph G c) a b u ∧
      OnGeodesic (Distances.blueGraph G c) a b v) := by
  rintro ⟨hu, hv⟩
  exact hoff (blue_adj_mem_geodesicSupport G c hadj hu hv)

end Ell5GeodesicSupportAdj
end Erdos23Delta0
