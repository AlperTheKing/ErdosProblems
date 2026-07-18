import FormalConjecturesUtil

/-!
Rooted girth bound needed for WOWII Conjecture 141.

The intended theorem is that, in a finite connected cyclic graph, the girth is
at most twice the largest distance from any prescribed root, plus one.  We
construct a shortest-path parent graph and use a non-tree edge to obtain the
short cycle.
-/

namespace SimpleGraph

open Classical

variable {α : Type*} [Fintype α] [DecidableEq α]
variable {G : SimpleGraph α}

/-- A chosen shortest path from `root` to `x`. -/
noncomputable def rootedShortestPath (hG : G.Connected) (root x : α) : G.Walk root x :=
  Classical.choose (hG.exists_path_of_dist root x)

lemma rootedShortestPath_isPath (hG : G.Connected) (root x : α) :
    (rootedShortestPath hG root x).IsPath :=
  (Classical.choose_spec (hG.exists_path_of_dist root x)).1

lemma rootedShortestPath_length (hG : G.Connected) (root x : α) :
    (rootedShortestPath hG root x).length = G.dist root x :=
  (Classical.choose_spec (hG.exists_path_of_dist root x)).2

/-- The predecessor of `x` on a chosen shortest path from `root`.  At the root
itself this is the root. -/
noncomputable def rootedParent (hG : G.Connected) (root x : α) : α :=
  (rootedShortestPath hG root x).penultimate

lemma rootedParent_eq_root (hG : G.Connected) (root : α) :
    rootedParent hG root root = root := by
  have hp0 : (rootedShortestPath hG root root).length = 0 := by
    rw [rootedShortestPath_length, dist_self]
  simp [rootedParent, Walk.penultimate, hp0]

lemma rootedParent_adj (hG : G.Connected) (root : α) {x : α} (hx : x ≠ root) :
    G.Adj (rootedParent hG root x) x := by
  let p := rootedShortestPath hG root x
  have hpne : ¬ p.Nil := by
    rw [Walk.nil_iff_length_eq, rootedShortestPath_length]
    exact (hG.dist_eq_zero_iff.not.mpr hx.symm)
  exact p.adj_penultimate hpne

lemma rootedParent_dist_add_one (hG : G.Connected) (root : α) {x : α} (hx : x ≠ root) :
    G.dist root (rootedParent hG root x) + 1 = G.dist root x := by
  let p := rootedShortestPath hG root x
  have hpne : ¬ p.Nil := by
    rw [Walk.nil_iff_length_eq, rootedShortestPath_length]
    exact (hG.dist_eq_zero_iff.not.mpr hx.symm)
  have hdrop : p.dropLast.length = G.dist root p.penultimate :=
    length_eq_dist_of_subwalk (rootedShortestPath_length hG root x)
      (Walk.isSubwalk_take p (p.length - 1))
  have hplen : p.length = G.dist root x := rootedShortestPath_length hG root x
  have hpos : 0 < p.length := by
    rw [hplen]
    exact hG.pos_dist_of_ne hx.symm
  have hdropLen : p.dropLast.length + 1 = p.length := by
    dsimp [Walk.dropLast]
    rw [Walk.take_length, Nat.min_eq_left (Nat.sub_le _ _)]
    omega
  change G.dist root p.penultimate + 1 = G.dist root x
  rw [← hdrop, hdropLen, hplen]

/-- The undirected graph consisting of the chosen parent edges. -/
noncomputable def rootedParentGraph (hG : G.Connected) (root : α) : SimpleGraph α :=
  SimpleGraph.fromRel (fun x y => rootedParent hG root x = y)

lemma rootedParentGraph_adj_iff (hG : G.Connected) (root x y : α) :
    (rootedParentGraph hG root).Adj x y ↔
      x ≠ y ∧ (rootedParent hG root x = y ∨ rootedParent hG root y = x) := by
  simp [rootedParentGraph, SimpleGraph.fromRel_adj]

lemma rootedParentGraph_le (hG : G.Connected) (root : α) :
    rootedParentGraph hG root ≤ G := by
  intro x y hxy
  rw [rootedParentGraph_adj_iff] at hxy
  rcases hxy.2 with hpx | hpy
  · have hxroot : x ≠ root := by
      intro hx
      subst x
      apply hxy.1
      exact (rootedParent_eq_root hG root).symm.trans hpx
    subst y
    exact (rootedParent_adj hG root hxroot).symm
  · have hyroot : y ≠ root := by
      intro hy
      subst y
      apply hxy.1
      exact hpy.symm.trans (rootedParent_eq_root hG root)
    subst x
    exact rootedParent_adj hG root hyroot

end SimpleGraph
