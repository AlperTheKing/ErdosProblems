import Mathlib.Combinatorics.SimpleGraph.Girth

/-!
# A prescribed-length path from a vertex to a shortest cycle

This file isolates the path-existence frontier used by the direct R1 route
for WOWII / Graffiti.pc Conjecture 141.  In a connected cyclic graph, a
shortest path from `v` to the nearest vertex of a shortest cycle, followed by
the cycle with its closing edge removed, is a path starting at `v`.  Taking a
prefix produces every length at most two below the girth.
-/

namespace SimpleGraph

namespace Walk

variable {V : Type*} {G : SimpleGraph V}

/-- Rotating a closed walk preserves its length. -/
private lemma length_rotate [DecidableEq V] {u v : V} (c : G.Walk v v)
    (h : u ∈ c.support) : (c.rotate h).length = c.length := by
  obtain ⟨n, hn⟩ := c.rotate_edges h
  have hlen := congrArg List.length hn
  simpa only [Walk.length_edges, List.length_rotate] using hlen

/-- The initial arc of a cycle ending at its penultimate vertex has all but
one of the cycle's edges. -/
private lemma length_takeUntil_penultimate [DecidableEq V] {v : V}
    {c : G.Walk v v} (hc : c.IsCycle)
    (hpen : c.penultimate ∈ c.support) :
    (c.takeUntil c.penultimate hpen).length = c.length - 1 := by
  let q := c.takeUntil c.penultimate hpen
  have hne : c.penultimate ≠ v := (c.adj_penultimate hc.not_nil).ne
  have hlt : q.length < c.length := c.length_takeUntil_lt hpen hne
  have hqle : q.length ≤ c.length - 1 := by omega
  have hend : c.getVert q.length = c.penultimate :=
    c.getVert_length_takeUntil hpen
  have hlast : c.getVert (c.length - 1) = c.penultimate := rfl
  exact hc.getVert_injOn' hqle (by simp) (hend.trans hlast.symm)

end Walk

variable {V : Type*} [DecidableEq V] {G : SimpleGraph V}

/-- If `G` is connected and cyclic and `r + 2 ≤ G.girth`, then every
vertex starts a simple path of length exactly `r`.

The construction avoids a breadth-first spanning tree.  It joins the chosen
vertex to a nearest vertex of a shortest cycle by a geodesic, traverses the
cycle up to (but not including) its closing edge, and takes the length-`r`
prefix of the resulting path. -/
theorem exists_isPath_length_eq_of_add_two_le_girth
    (hconn : G.Connected) (hcyc : ¬ G.IsAcyclic) (v : V) {r : ℕ}
    (hr : r + 2 ≤ G.girth) :
    ∃ w : V, ∃ p : G.Walk v w, p.IsPath ∧ p.length = r := by
  obtain ⟨a, c, hc, hcg⟩ := G.exists_girth_eq_length.mpr hcyc

  have hcs : c.support.toFinset.Nonempty := by
    exact ⟨a, by simp⟩
  obtain ⟨y, hy, hymin⟩ :=
    c.support.toFinset.exists_min_image (G.dist v) hcs
  have hyc : y ∈ c.support := by simpa using hy

  obtain ⟨p, hp, hplen⟩ := hconn.exists_path_of_dist v y

  have hp_meets_cycle_only_at_end :
      ∀ x : V, x ∈ p.support → x ∈ c.support → x = y := by
    intro x hxp hxc
    by_contra hxy
    have hmin : G.dist v y ≤ G.dist v x :=
      hymin x (by simpa using hxc)
    have hdist : G.dist v x ≤ (p.takeUntil x hxp).length := G.dist_le _
    have hlt : (p.takeUntil x hxp).length < p.length :=
      p.length_takeUntil_lt hxp hxy
    omega

  let c' : G.Walk y y := c.rotate hyc
  have hc' : c'.IsCycle := hc.rotate hyc
  have hc'len : c'.length = c.length := Walk.length_rotate c hyc
  have hpen : c'.penultimate ∈ c'.support := c'.getVert_mem_support _
  let q : G.Walk y c'.penultimate := c'.takeUntil c'.penultimate hpen
  have hq : q.IsPath := hc'.isPath_takeUntil hpen
  have hqlen : q.length = c'.length - 1 :=
    Walk.length_takeUntil_penultimate hc' hpen

  have hp_meets_rotated_cycle_only_at_end :
      ∀ x : V, x ∈ p.support → x ∈ c'.support → x = y := by
    intro x hxp hxc'
    exact hp_meets_cycle_only_at_end x hxp
      ((c.mem_support_rotate_iff hyc).mp hxc')

  have hpq : (p.append q).IsPath := by
    rw [Walk.isPath_def, Walk.support_append]
    have hdisj : p.support.Disjoint q.support.tail := by
      rw [List.disjoint_left]
      intro x hxp hxq
      have hxq' : x ∈ q.support := List.mem_of_mem_tail hxq
      have hxc' : x ∈ c'.support := c'.support_takeUntil_subset hpen hxq'
      have hxy : x = y := hp_meets_rotated_cycle_only_at_end x hxp hxc'
      subst x
      have hynot : y ∉ q.support.tail := by
        have hnodup := hq.support_nodup
        rw [q.support_eq_cons] at hnodup
        exact (List.nodup_cons.mp hnodup).1
      exact hynot hxq
    exact List.Nodup.append hp.support_nodup hq.support_nodup.tail hdisj

  have hpqlen : r ≤ (p.append q).length := by
    rw [Walk.length_append, hqlen, hc'len, ← hcg]
    omega

  let result := (p.append q).take r
  refine ⟨(p.append q).getVert r, result, ?_, ?_⟩
  · exact Walk.isPath_of_isSubwalk (Walk.isSubwalk_take _ _) hpq
  · dsimp [result]
    rw [Walk.take_length, Nat.min_eq_left hpqlen]

end SimpleGraph
