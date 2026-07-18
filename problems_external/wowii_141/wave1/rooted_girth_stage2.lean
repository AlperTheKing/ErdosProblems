
namespace SimpleGraph

open Classical

variable {α : Type*} [Fintype α] [DecidableEq α]
variable {G : SimpleGraph α}

/-- The parent graph contains a root-to-`x` walk whose length is the original
graph distance. -/
lemma rootedParentGraph_exists_walk_length_dist (hG : G.Connected) (root x : α) :
    ∃ p : (rootedParentGraph hG root).Walk root x, p.length = G.dist root x := by
  induction hn : G.dist root x using Nat.strong_induction_on generalizing x with
  | h n ih =>
      by_cases hx : x = root
      · subst x
        exact ⟨.nil, by simp⟩
      · let y := rootedParent hG root x
        have hyrel : G.dist root y + 1 = G.dist root x :=
          rootedParent_dist_add_one hG root hx
        have hylt : G.dist root y < n := by omega
        obtain ⟨p, hp⟩ := ih (G.dist root y) hylt y rfl
        have hGadj : G.Adj y x := rootedParent_adj hG root hx
        have hTadj : (rootedParentGraph hG root).Adj y x := by
          apply (rootedParentGraph_adj_iff hG root y x).2
          exact ⟨hGadj.ne, Or.inr rfl⟩
        refine ⟨p.concat hTadj, ?_⟩
        simp only [Walk.length_concat]
        omega

lemma rootedParentGraph_connected (hG : G.Connected) (root : α) :
    (rootedParentGraph hG root).Connected := by
  rw [connected_iff_exists_forall_reachable]
  refine ⟨root, fun x => ?_⟩
  obtain ⟨p, -⟩ := rootedParentGraph_exists_walk_length_dist hG root x
  exact p.reachable

lemma rootedParentGraph_dist_eq (hG : G.Connected) (root x : α) :
    (rootedParentGraph hG root).dist root x = G.dist root x := by
  let T := rootedParentGraph hG root
  apply le_antisymm
  · obtain ⟨p, hp⟩ := rootedParentGraph_exists_walk_length_dist hG root x
    rw [← hp]
    exact dist_le p
  · have hr : T.Reachable root x := (rootedParentGraph_connected hG root) root x
    exact hr.dist_anti (rootedParentGraph_le hG root)

lemma rootedParentGraph_isAcyclic (hG : G.Connected) (root : α) :
    (rootedParentGraph hG root).IsAcyclic := by
  let T := rootedParentGraph hG root
  intro z c hc
  have hsne : c.support.toFinset.Nonempty := by
    refine ⟨z, ?_⟩
    simp
  obtain ⟨x, hxmem, hxmax⟩ :=
    Finset.exists_mem_eq_sup c.support.toFinset hsne (G.dist root)
  have hxc : x ∈ c.support := by simpa using hxmem
  let d : T.Walk x x := c.rotate hxc
  have hdc : d.IsCycle := hc.rotate hxc
  have hsndC : d.snd ∈ c.support := by
    apply (c.mem_support_rotate_iff hxc).mp
    simpa only [d] using d.getVert_mem_support 1
  have hpenC : d.penultimate ∈ c.support := by
    apply (c.mem_support_rotate_iff hxc).mp
    simpa only [d] using d.getVert_mem_support (d.length - 1)
  have hsndMax : G.dist root d.snd ≤ G.dist root x := by
    have hle := Finset.le_sup (f := G.dist root) (by simpa using hsndC)
    rwa [hxmax] at hle
  have hpenMax : G.dist root d.penultimate ≤ G.dist root x := by
    have hle := Finset.le_sup (f := G.dist root) (by simpa using hpenC)
    rwa [hxmax] at hle
  have neighbor_eq_parent (y : α) (hxy : T.Adj x y)
      (hymax : G.dist root y ≤ G.dist root x) :
      y = rootedParent hG root x := by
    rw [rootedParentGraph_adj_iff] at hxy
    rcases hxy.2 with hpx | hpy
    · exact hpx.symm
    · exfalso
      by_cases hyroot : y = root
      · subst y
        have hxroot : x = root := by
          exact hpy.symm.trans (rootedParent_eq_root hG root)
        exact hxy.1 hxroot
      · have hyrel := rootedParent_dist_add_one hG root hyroot
        rw [hpy] at hyrel
        omega
  have hsnd : d.snd = rootedParent hG root x :=
    neighbor_eq_parent d.snd (d.adj_snd hdc.not_nil) hsndMax
  have hpen : d.penultimate = rootedParent hG root x :=
    neighbor_eq_parent d.penultimate (d.adj_penultimate hdc.not_nil).symm hpenMax
  exact hdc.snd_ne_penultimate (hsnd.trans hpen.symm)

lemma rootedParentGraph_isTree (hG : G.Connected) (root : α) :
    (rootedParentGraph hG root).IsTree :=
  ⟨rootedParentGraph_connected hG root, rootedParentGraph_isAcyclic hG root⟩

/-- Rooted girth bound: every prescribed root has a vertex at distance large
enough to account for at least half the girth. -/
theorem girth_le_two_mul_dist_sup_add_one (hG : G.Connected)
    (hcyc : ¬ G.IsAcyclic) (root : α) :
    G.girth ≤ 2 * Finset.univ.sup (G.dist root) + 1 := by
  let T := rootedParentGraph hG root
  have hTG : T ≤ G := rootedParentGraph_le hG root
  have hT : T.IsTree := rootedParentGraph_isTree hG root
  have hnle : ¬ G ≤ T := by
    intro hle
    exact hcyc (IsAcyclic.anti hle hT.isAcyclic)
  rw [le_iff_adj] at hnle
  push_neg at hnle
  obtain ⟨a, b, habG, habT⟩ := hnle
  obtain ⟨p, hpPath, hpLen⟩ := hT.isConnected.exists_path_of_dist a b
  let q : G.Walk a b := p.mapLe hTG
  have hqPath : q.IsPath := hpPath.mapLe hTG
  have hclose : s(b, a) ∉ q.edges := by
    intro he
    have heT : s(b, a) ∈ p.edges := by
      dsimp [q] at he
      rwa [p.edges_mapLe_eq_edges hTG] at he
    exact habT (p.adj_of_mem_edges heT)
  let c : G.Walk b b := q.cons habG.symm
  have hc : c.IsCycle := by
    dsimp [c]
    exact (Walk.cons_isCycle_iff q habG.symm).2 ⟨hqPath, hclose⟩
  have hpdist : p.length = T.dist a b := hpLen
  have htri : T.dist a b ≤ T.dist a root + T.dist root b :=
    hT.isConnected.dist_triangle
  have hrootA : T.dist root a = G.dist root a := rootedParentGraph_dist_eq hG root a
  have hrootB : T.dist root b = G.dist root b := rootedParentGraph_dist_eq hG root b
  have haSup : G.dist root a ≤ Finset.univ.sup (G.dist root) :=
    Finset.le_sup (Finset.mem_univ a)
  have hbSup : G.dist root b ≤ Finset.univ.sup (G.dist root) :=
    Finset.le_sup (Finset.mem_univ b)
  have hpBound : p.length ≤ 2 * Finset.univ.sup (G.dist root) := by
    rw [hpdist]
    calc
      T.dist a b ≤ T.dist a root + T.dist root b := htri
      _ = G.dist root a + G.dist root b := by rw [dist_comm, hrootA, hrootB]
      _ ≤ 2 * Finset.univ.sup (G.dist root) := by omega
  have hg := G.girth_le_length hc
  have hclen : c.length = p.length + 1 := by simp [c, q]
  omega

end SimpleGraph
