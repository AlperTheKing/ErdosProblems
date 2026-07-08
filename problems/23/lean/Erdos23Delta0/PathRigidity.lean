import Mathlib

/-!
# Path rigidity: a path's edge set determines its endpoint pair (2026-07-08)

Graph-level content behind the `hpair` hypothesis of `Ell5CSReduction.hall_le_five`. For an ell=5 atom (a bad edge
whose blue geodesic has length 4), the shortest-geodesic support is the edge set of a length-4 path; distinct atoms
therefore have distinct supports (their bad edges differ). The heart is:

* an **endpoint** of a path is incident to exactly one edge (Mathlib `IsPath.eq_snd_of_mem_edges`);
* an **internal** vertex is incident to at least two distinct edges (`two_edges_of_internal`, structural induction);

so two paths with the same edge set must share endpoints (`start_mem_endpoints`), and with distinct endpoints they
represent the same unordered bad edge (`edges_determine_badedge`). All theorems axiom-clean
(`{propext, Classical.choice, Quot.sound}`); no `sorry`/`admit`/`native_decide`.
-/

namespace Erdos23Delta0
namespace PathRigidity

open SimpleGraph Finset

variable {V : Type*} {G : SimpleGraph V}

/-- Any edge of a path `p : u ⇝ v` that contains the start vertex `u` equals the first edge `s(u, p.snd)`. -/
theorem incident_start_eq {u v : V} {p : G.Walk u v} (hp : p.IsPath)
    {e : Sym2 V} (he : e ∈ p.edges) (hu : u ∈ e) : e = s(u, p.snd) := by
  induction e using Sym2.ind with
  | _ x y =>
    rw [Sym2.mem_iff] at hu
    rcases hu with rfl | rfl
    · rw [hp.eq_snd_of_mem_edges he]
    · rw [Sym2.eq_swap] at he ⊢
      rw [hp.eq_snd_of_mem_edges he]

/-- Any edge of a path `p : u ⇝ v` that contains the end vertex `v` equals the last edge `s(v, p.penultimate)`. -/
theorem incident_end_eq {u v : V} {p : G.Walk u v} (hp : p.IsPath)
    {e : Sym2 V} (he : e ∈ p.edges) (hv : v ∈ e) : e = s(v, p.penultimate) := by
  induction e using Sym2.ind with
  | _ x y =>
    rw [Sym2.mem_iff] at hv
    rcases hv with rfl | rfl
    · rw [hp.eq_penultimate_of_mem_edges he]
    · rw [Sym2.eq_swap] at he ⊢
      rw [hp.eq_penultimate_of_mem_edges he]

/-- An INTERNAL vertex of a path (in the support, not an endpoint) is incident to (at least) two distinct edges. -/
theorem two_edges_of_internal [DecidableEq V] {u v x : V} {p : G.Walk u v} (hp : p.IsPath)
    (hx : x ∈ p.support) (hxu : x ≠ u) (hxv : x ≠ v) :
    ∃ e1 ∈ p.edges.toFinset, ∃ e2 ∈ p.edges.toFinset, e1 ≠ e2 ∧ x ∈ e1 ∧ x ∈ e2 := by
  induction p with
  | nil =>
    simp only [Walk.support_nil, List.mem_singleton] at hx
    exact absurd hx hxu
  | @cons a w b h q ih =>
    have hpath := (Walk.cons_isPath_iff h q).mp hp
    simp only [Walk.support_cons, List.mem_cons] at hx
    rcases hx with rfl | hxq
    · exact absurd rfl hxu
    · by_cases hxw : x = w
      · subst hxw
        cases q with
        | nil => exact absurd rfl hxv
        | @cons _ m _ h2 q2 =>
          have haw : a ∉ (Walk.cons h2 q2).support := hpath.2
          have ham : a ≠ m := fun hc => haw (by subst hc; simp [Walk.support_cons])
          have haw2 : a ≠ x := fun hc => haw (by subst hc; simp [Walk.support_cons])
          refine ⟨s(a, x), ?_, s(x, m), ?_, ?_, by simp, by simp⟩
          · rw [List.mem_toFinset]; simp [Walk.edges_cons]
          · rw [List.mem_toFinset]; simp [Walk.edges_cons]
          · rw [ne_eq, Sym2.eq_iff]; grind
      · obtain ⟨e1, he1, e2, he2, hne, hx1, hx2⟩ := ih hpath.1 hxq hxw hxv
        rw [List.mem_toFinset] at he1 he2
        exact ⟨e1, by rw [List.mem_toFinset, Walk.edges_cons]; exact List.mem_cons_of_mem _ he1,
               e2, by rw [List.mem_toFinset, Walk.edges_cons]; exact List.mem_cons_of_mem _ he2,
               hne, hx1, hx2⟩

/-- The first edge `s(u, p.snd)` of a nonempty walk belongs to its edge list. -/
theorem start_edge_mem {u v : V} (p : G.Walk u v) (hp : ¬ p.Nil) :
    s(u, p.snd) ∈ p.edges := by
  cases p with
  | nil => simp at hp
  | cons h q => simp [Walk.edges_cons]

/-- **Rigidity, start half.** If two paths `p : u ⇝ v` and `q : u' ⇝ v'` have the same edge set and `p` is nonempty,
    then `p`'s start `u` is an endpoint of `q`. -/
theorem start_mem_endpoints [DecidableEq V] {u v u' v' : V}
    {p : G.Walk u v} {q : G.Walk u' v'} (hp : p.IsPath) (hq : q.IsPath)
    (hpn : ¬ p.Nil) (hE : p.edges.toFinset = q.edges.toFinset) :
    u = u' ∨ u = v' := by
  have hg : s(u, p.snd) ∈ q.edges := by
    rw [← List.mem_toFinset, ← hE, List.mem_toFinset]; exact start_edge_mem p hpn
  have husup : u ∈ q.support := q.fst_mem_support_of_mem_edges hg
  by_contra hcon
  push_neg at hcon
  obtain ⟨e1, he1, e2, he2, hne, hu1, hu2⟩ := two_edges_of_internal hq husup hcon.1 hcon.2
  rw [← hE, List.mem_toFinset] at he1 he2
  have h1 := incident_start_eq hp he1 hu1
  have h2 := incident_start_eq hp he2 hu2
  exact hne (h1.trans h2.symm)

/-- **RIGIDITY.** Two paths with the same edge set and distinct endpoints represent the same unordered endpoint pair:
    `s(u, v) = s(u', v')`. In the ell=5 application, an atom's 4-edge geodesic support determines the bad edge, so
    distinct atoms have distinct supports — the graph content of the `hpair` hypothesis of `hall_le_five`. -/
theorem edges_determine_badedge [DecidableEq V] {u v u' v' : V}
    {p : G.Walk u v} {q : G.Walk u' v'} (hp : p.IsPath) (hq : q.IsPath)
    (hpn : ¬ p.Nil) (huv : u ≠ v) (hE : p.edges.toFinset = q.edges.toFinset) :
    s(u, v) = s(u', v') := by
  have hu : u = u' ∨ u = v' := start_mem_endpoints hp hq hpn hE
  have hrev : p.reverse.edges.toFinset = q.edges.toFinset := by
    rw [Walk.edges_reverse, List.toFinset_reverse]; exact hE
  have hpn' : ¬ p.reverse.Nil := by
    rw [Walk.nil_iff_length_eq, Walk.length_reverse, ← Walk.nil_iff_length_eq]; exact hpn
  have hv : v = u' ∨ v = v' := start_mem_endpoints hp.reverse hq hpn' hrev
  rw [Sym2.eq_iff]
  grind

#print axioms incident_start_eq
#print axioms incident_end_eq
#print axioms two_edges_of_internal
#print axioms start_mem_endpoints
#print axioms edges_determine_badedge

end PathRigidity
end Erdos23Delta0
