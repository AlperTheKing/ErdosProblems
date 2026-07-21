import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.VertexDistance

namespace SimpleGraph

open Classical

variable {α : Type*} [Fintype α] [DecidableEq α]
variable {G : SimpleGraph α} {S : Set α} {u v : α}

omit [Fintype α] in
/-- Attaching a new vertex along its unique neighbor in an induced tree gives a larger
induced tree. -/
private lemma IsTree.induce_insert_of_unique_adj_local {G : SimpleGraph α} {s : Finset α} {z a : α}
    (hT : (G.induce (s : Set α)).IsTree)
    (_hz : z ∉ s) (ha : a ∈ s) (hza : G.Adj z a)
    (huniq : ∀ ⦃b : α⦄, b ∈ s → G.Adj z b → b = a) :
    (G.induce ((insert z s : Finset α) : Set α)).IsTree := by
  classical
  constructor
  · have hsconn : (G.induce (s : Set α)).Preconnected := hT.isConnected.preconnected
    have hzconn : (G.induce ({z} : Set α)).Preconnected := .of_subsingleton
    have hconn := connected_induce_union (v := z) (w := a) (s := ({z} : Set α))
      (t := (s : Set α)) hzconn hsconn (by simp) (by simpa using ha) hza
    rw [Finset.coe_insert]
    simpa only [Set.singleton_union] using hconn
  · intro v c hc
    let e : G.induce ((insert z s : Finset α) : Set α) ↪g G :=
      SimpleGraph.Embedding.induce _
    let q : G.Walk (e v) (e v) := c.map e.toHom
    have hq : q.IsCycle := by
      dsimp [q]
      exact (Walk.map_isCycle_iff_of_injective e.injective).2 hc
    have hq_mem (w : α) (hw : w ∈ q.support) : w ∈ insert z s := by
      dsimp [q] at hw
      rw [Walk.support_map] at hw
      obtain ⟨w', hw', rfl⟩ := List.mem_map.mp hw
      change (w' : α) ∈ insert z s
      exact w'.property
    by_cases hzq : z ∈ q.support
    · let r : G.Walk z z := q.rotate hzq
      have hr : r.IsCycle := by
        dsimp [r]
        exact hq.rotate hzq
      have hrsnd : r.snd ∈ q.support := by
        apply (q.mem_support_rotate_iff hzq).mp
        simpa only [r] using r.getVert_mem_support 1
      have hrpenultimate : r.penultimate ∈ q.support := by
        apply (q.mem_support_rotate_iff hzq).mp
        simpa only [r] using r.getVert_mem_support (r.length - 1)
      have hadj_snd : G.Adj z r.snd := r.adj_snd hr.not_nil
      have hadj_penultimate : G.Adj z r.penultimate :=
        (r.adj_penultimate hr.not_nil).symm
      have hsnd : r.snd ∈ s := by
        rcases Finset.mem_insert.mp (hq_mem _ hrsnd) with heq | hmem
        · exact (hadj_snd.ne heq.symm).elim
        · exact hmem
      have hpenultimate : r.penultimate ∈ s := by
        rcases Finset.mem_insert.mp (hq_mem _ hrpenultimate) with heq | hmem
        · exact (hadj_penultimate.ne heq.symm).elim
        · exact hmem
      exact hr.snd_ne_penultimate <|
        (huniq hsnd hadj_snd).trans (huniq hpenultimate hadj_penultimate).symm
    · have hqs : ∀ w ∈ q.support, w ∈ (s : Set α) := by
        intro w hw
        rcases Finset.mem_insert.mp (hq_mem w hw) with heq | hmem
        · subst w
          exact (hzq hw).elim
        · simpa using hmem
      let qi := q.induce (s : Set α) hqs
      have hqi : qi.IsCycle := by
        apply (Walk.map_isCycle_iff_of_injective
          (f := (SimpleGraph.Embedding.induce (G := G) (s : Set α)).toHom)
          (SimpleGraph.Embedding.induce (G := G) (s : Set α)).injective).mp
        rw [show qi.map (SimpleGraph.Embedding.induce (G := G) (s : Set α)).toHom = q by
          dsimp [qi]
          exact Walk.map_induce q hqs]
        exact hq
      exact hT.IsAcyclic qi hqi


omit [Fintype α] in
/-- A shortest walk induces a tree on its support. -/
private lemma Walk.induce_support_isTree_of_length_eq_dist_local {G : SimpleGraph α} {u v : α}
    (p : G.Walk u v) (hp : p.length = G.dist u v) :
    (G.induce (p.support.toFinset : Set α)).IsTree := by
  induction p with
  | @nil u =>
      have hset : (↑(Walk.nil : G.Walk u u).support.toFinset : Set α) = {u} := by
        ext
        simp
      have hsingle : (G.induce ({u} : Set α)).IsTree := by
        letI : Nonempty ↥({u} : Set α) := ⟨⟨u, by simp⟩⟩
        letI : Subsingleton ↥({u} : Set α) := ⟨fun a b => by
          apply Subtype.ext
          have ha : (a : α) = u := by
            simpa only [Set.mem_singleton_iff] using a.property
          have hb : (b : α) = u := by
            simpa only [Set.mem_singleton_iff] using b.property
          exact ha.trans hb.symm⟩
        exact IsTree.of_subsingleton
      rw [hset]
      exact hsingle
  | @cons u v w huv p ih =>
      have hptail : p.length = G.dist v w :=
        length_eq_dist_of_subwalk hp (Walk.isSubwalk_cons p huv)
      have hT := ih hptail
      have hpath : (p.cons huv).IsPath :=
        (p.cons huv).isPath_of_length_eq_dist hp
      have hu_not : u ∉ p.support.toFinset := by
        simpa using (List.nodup_cons.mp hpath.support_nodup).1
      have huniq : ∀ ⦃b : α⦄, b ∈ p.support.toFinset → G.Adj u b → b = v := by
        intro b hb hub
        have hbmem : b ∈ p.support := by simpa using hb
        obtain ⟨i, hi, hib⟩ := List.mem_iff_getElem.mp hbmem
        have hget : p.getVert i = b := by
          rw [← p.support_getElem_eq_getVert hi, hib]
        have hi_le : i ≤ p.length := by
          have hlen := p.length_support
          omega
        have hub' : G.Adj u (p.getVert i) := by simpa [hget] using hub
        let r : G.Walk u w := (p.drop i).cons hub'
        have hdistle : G.dist u w ≤ r.length := G.dist_le r
        have hlen : (p.cons huv).length ≤ r.length := by simpa [hp] using hdistle
        have hi0 : i = 0 := by
          simp only [Walk.length_cons, r, Walk.drop_length] at hlen
          omega
        subst i
        simpa using hget.symm
      have hsupp : (Walk.cons huv p).support.toFinset = insert u p.support.toFinset := by
        simp
      rw [hsupp]
      exact hT.induce_insert_of_unique_adj_local hu_not (by simp) huv huniq


omit [DecidableEq α] in
/-- A member of a finite set bounds the distance to that set. -/
private lemma distToSet_le_dist_of_mem (x : α) {s : α} (hs : s ∈ S) :
    G.distToSet x S ≤ G.dist x s := by
  unfold distToSet
  split_ifs with h
  · exact Finset.min'_le _ _ (Finset.mem_image_of_mem _ (Set.mem_toFinset.mpr hs))
  · exact Nat.zero_le _

/-- A walk which realizes the distance from its first vertex to a set, ending
in that set, is a genuine geodesic to its endpoint.  Consequently it is a
path, its support induces a tree, and no vertex before the endpoint belongs
to the target set.  This is the Lean backbone of the descent construction in
the proof of WOWII Conjecture 142. -/
lemma Walk.nearestSet_descent
    (p : G.Walk u v) (hv : v ∈ S) (hp : p.length = G.distToSet u S) :
    p.length = G.dist u v ∧
      p.IsPath ∧
      (G.induce (p.support.toFinset : Set α)).IsTree ∧
      (∀ i : ℕ, i < p.length → p.getVert i ∉ S) ∧
      ∀ i : ℕ, i + 1 < p.length → ∀ s ∈ S, ¬G.Adj (p.getVert i) s := by
  have hset_le : G.distToSet u S ≤ G.dist u v :=
    distToSet_le_dist_of_mem u hv
  have hdist_le : G.dist u v ≤ p.length := G.dist_le p
  have hgeod : p.length = G.dist u v := by omega
  have hpath : p.IsPath := p.isPath_of_length_eq_dist hgeod
  have htree : (G.induce (p.support.toFinset : Set α)).IsTree :=
    p.induce_support_isTree_of_length_eq_dist_local hgeod
  refine ⟨hgeod, hpath, htree, ?_, ?_⟩
  · intro i hi hiS
    have hto_i : G.distToSet u S ≤ G.dist u (p.getVert i) :=
      distToSet_le_dist_of_mem u hiS
    have hdist_i : G.dist u (p.getVert i) ≤ i := by
      calc
        G.dist u (p.getVert i) ≤ (p.take i).length := G.dist_le (p.take i)
        _ = i := by rw [Walk.take_length, Nat.min_eq_left (Nat.le_of_lt hi)]
    omega
  · intro i hi s hs his
    have hto_s : G.distToSet u S ≤ G.dist u s :=
      distToSet_le_dist_of_mem u hs
    have hdist_s : G.dist u s ≤ i + 1 := by
      calc
        G.dist u s ≤ ((p.take i).concat his).length := G.dist_le ((p.take i).concat his)
        _ = i + 1 := by
          simp only [Walk.length_concat, Walk.take_length]
          rw [Nat.min_eq_left (by omega)]
    omega

end SimpleGraph
