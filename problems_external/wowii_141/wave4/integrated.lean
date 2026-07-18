import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Independence
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


/-
The local ``broom'' certificate for WOWII Conjecture 141.  Path existence is
deliberately not addressed here: the theorem starts with a short simple path
from the centre of an independent neighbourhood star.
-/

namespace SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α] {G : SimpleGraph α}

omit [Fintype α] in
/-- Attaching a new vertex along its unique neighbor in an induced tree gives a larger
induced tree. -/
lemma IsTree.induce_insert_of_unique_adj {G : SimpleGraph α} {s : Finset α} {z a : α}
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


omit [Fintype α] [DecidableEq α] in
lemma Walk.snd_mem_support (p : G.Walk u v) : p.snd ∈ p.support := by
  cases p <;> simp

omit [Fintype α] [DecidableEq α] in
lemma Walk.snd_concat_of_not_nil (p : G.Walk u v) (h : G.Adj v w) (hp : ¬ p.Nil) :
    (p.concat h).snd = p.snd := by
  cases p with
  | nil => exact (hp Walk.nil_nil).elim
  | cons h' q => simp [Walk.concat]

omit [Fintype α] in
/-- A path whose support has fewer vertices than the girth has no ambient
chord, so its support induces a tree. -/
lemma Walk.induce_support_isTree_of_isPath_of_card_lt_girth
    (p : G.Walk u v) (hp : p.IsPath) (hlen : p.length + 1 < G.girth) :
    (G.induce (p.support.toFinset : Set α)).IsTree := by
  constructor
  · have hs : (p.support.toFinset : Set α) = {x : α | x ∈ p.support} := by
      ext x
      simp
    rw [hs]
    exact p.connected_induce_support
  · intro x d hd
    let e : G.induce (p.support.toFinset : Set α) ↪g G :=
      SimpleGraph.Embedding.induce _
    let q : G.Walk (e x) (e x) := d.map e.toHom
    have hq : q.IsCycle := by
      dsimp [q]
      exact (Walk.map_isCycle_iff_of_injective e.injective).2 hd
    have hd_tail_path : d.tail.IsPath := by
      rw [Walk.isPath_def, d.support_tail_of_not_nil hd.not_nil]
      exact hd.support_nodup
    have hd_length_le : d.length ≤ Fintype.card (p.support.toFinset : Set α) := by
      have hlt := hd_tail_path.length_lt
      have hlen' := d.length_tail_add_one hd.not_nil
      omega
    have hq_length : q.length = d.length := by simp [q]
    have hg_le : G.girth ≤ q.length := G.girth_le_length hq
    have hs_type_card :
        Fintype.card (p.support.toFinset : Set α) = p.support.toFinset.card := by
      rw [← Nat.card_eq_fintype_card, Nat.card_coe_set_eq, Set.ncard_coe_finset]
    have hp_card : p.support.toFinset.card = p.length + 1 := by
      rw [List.toFinset_card_of_nodup hp.support_nodup, p.length_support]
    rw [hq_length] at hg_le
    rw [hs_type_card, hp_card] at hd_length_le
    omega

omit [Fintype α] in
/-- On a sufficiently short path, a support vertex adjacent to the initial
vertex must be the first path vertex. -/
lemma Walk.eq_snd_of_mem_support_of_adj_start_of_length_add_two_lt_girth
    (p : G.Walk v z) (hp : p.IsPath) (hshort : p.length + 2 < G.girth)
    {b : α} (hb : b ∈ p.support) (hvb : G.Adj v b) : b = p.snd := by
  by_contra hne
  let q := p.takeUntil b hb
  have hqpath : q.IsPath := hp.takeUntil hb
  have he_not : s(v, b) ∉ q.edges := by
    intro he
    have hbsnd : b = q.snd := hqpath.eq_snd_of_mem_edges he
    have hqsnd : q.snd = p.snd := p.snd_takeUntil hvb.ne' hb
    exact hne (hbsnd.trans hqsnd)
  have hc : (Walk.cons hvb.symm q).IsCycle :=
    (Walk.cons_isCycle_iff q hvb.symm).2 ⟨hqpath, by simpa [Sym2.eq_swap] using he_not⟩
  have hg := G.girth_le_length hc
  have hqle := p.length_takeUntil_le hb
  dsimp [q] at hg
  omega

omit [Fintype α] in
/-- An external neighbour of the path start can see no other support vertex
when the resulting cycle would be shorter than the girth. -/
lemma Walk.eq_start_of_external_adj_mem_support_of_length_add_two_lt_girth
    (p : G.Walk v z) (hp : p.IsPath) (hshort : p.length + 2 < G.girth)
    {w b : α} (hw : w ∉ p.support) (hvw : G.Adj v w)
    (hb : b ∈ p.support) (hwb : G.Adj w b) : b = v := by
  by_contra hbne
  let q₀ := p.takeUntil b hb
  have hq₀path : q₀.IsPath := hp.takeUntil hb
  have hwq₀ : w ∉ q₀.support := fun h => hw (p.support_takeUntil_subset hb h)
  let q := q₀.concat hwb.symm
  have hqpath : q.IsPath := hq₀path.concat hwq₀ hwb.symm
  have hq₀non : ¬ q₀.Nil := Walk.not_nil_of_ne (Ne.symm hbne)
  have he_not : s(w, v) ∉ q.edges := by
    intro he
    have hw_snd : w = q.snd :=
      hqpath.eq_snd_of_mem_edges (by simpa [Sym2.eq_swap] using he)
    have hq_snd : q.snd = q₀.snd := q₀.snd_concat_of_not_nil hwb.symm hq₀non
    have hwq₀mem : w ∈ q₀.support := by
      rw [hw_snd, hq_snd]
      exact q₀.snd_mem_support
    exact hw (p.support_takeUntil_subset hb hwq₀mem)
  have hc : (Walk.cons hvw.symm q).IsCycle :=
    (Walk.cons_isCycle_iff q hvw.symm).2 ⟨hqpath, he_not⟩
  have hg := G.girth_le_length hc
  have hq₀le : q₀.length ≤ p.length := by
    simpa [q₀] using p.length_takeUntil_le hb
  dsimp [q] at hg
  simp only [Walk.length_concat] at hg
  omega

omit [Fintype α] in
/-- Attaching pairwise nonadjacent leaves, each seeing a tree only at `v`,
preserves the induced-tree property. -/
lemma IsTree.induce_union_broom_leaves {s : Finset α} {v : α}
    (hT : (G.induce (s : Set α)).IsTree) (hv : v ∈ s) (W : Finset α)
    (hadj : ∀ w ∈ W, G.Adj v w) (hout : ∀ w ∈ W, w ∉ s)
    (huniq : ∀ w ∈ W, ∀ ⦃b : α⦄, b ∈ s → G.Adj w b → b = v)
    (hind : G.IsIndepSet (W : Set α)) :
    (G.induce ((s ∪ W : Finset α) : Set α)).IsTree := by
  classical
  induction W using Finset.induction_on with
  | empty =>
      rw [Finset.union_empty]
      exact hT
  | @insert w W₀ hw ih =>
      have hT₀ := ih (fun x hx => hadj x (Finset.mem_insert_of_mem hx))
        (fun x hx => hout x (Finset.mem_insert_of_mem hx))
        (fun x hx => huniq x (Finset.mem_insert_of_mem hx))
        (hind.mono (Finset.coe_subset.mpr (Finset.subset_insert w W₀)))
      have hwmem : w ∈ insert w W₀ := Finset.mem_insert_self w W₀
      have hzs : w ∉ s ∪ W₀ := by
        simp only [Finset.mem_union, not_or]
        exact ⟨hout w hwmem, hw⟩
      have hva : v ∈ s ∪ W₀ := Finset.mem_union_left _ hv
      have hza : G.Adj w v := (hadj w hwmem).symm
      have huniq' : ∀ ⦃b : α⦄, b ∈ s ∪ W₀ → G.Adj w b → b = v := by
        intro b hb hwb
        rcases Finset.mem_union.mp hb with hbs | hbW₀
        · exact huniq w hwmem hbs hwb
        · exfalso
          have hwS : w ∈ ((insert w W₀ : Finset α) : Set α) := by simp
          have hbS : b ∈ ((insert w W₀ : Finset α) : Set α) := by
            simp only [Finset.coe_insert, Set.mem_insert_iff, Finset.mem_coe]
            exact Or.inr hbW₀
          have hne : w ≠ b := fun h => hw (h ▸ hbW₀)
          exact hind hwS hbS hne hwb
      have hT' := hT₀.induce_insert_of_unique_adj hzs hva hza huniq'
      have hcomm : (s ∪ insert w W₀ : Finset α) = insert w (s ∪ W₀) := by
        ext x
        simp [Finset.mem_union, Finset.mem_insert]
      rw [hcomm]
      exact hT'

omit [Fintype α] in
/-- A short path rooted at the centre of an independent neighbourhood star,
together with that star, is an induced tree of the required order. -/
theorem broom_induced_tree
    {v z : α} {r : ℕ} (p : G.Walk v z) (hp : p.IsPath) (hlen : p.length = r)
    (hshort : r + 2 < G.girth) (I : Finset α)
    (hadj : ∀ i ∈ I, G.Adj v i) (hind : G.IsIndepSet (I : Set α)) :
    (G.induce ((I ∪ p.support.toFinset : Finset α) : Set α)).IsTree ∧
      I.card + r ≤ (I ∪ p.support.toFinset).card := by
  classical
  let s : Finset α := p.support.toFinset
  let W : Finset α := I.erase p.snd
  have hp_short : p.length + 1 < G.girth := by omega
  have hT : (G.induce (s : Set α)).IsTree := by
    dsimp [s]
    exact p.induce_support_isTree_of_isPath_of_card_lt_girth hp hp_short
  have hv : v ∈ s := by simp [s]
  have hsnd : p.snd ∈ s := by simp [s, p.snd_mem_support]
  have hWadj : ∀ w ∈ W, G.Adj v w := by
    intro w hw
    exact hadj w (Finset.mem_of_mem_erase hw)
  have hWout : ∀ w ∈ W, w ∉ s := by
    intro w hwW hwS
    have hwI : w ∈ I := Finset.mem_of_mem_erase hwW
    have hwsupp : w ∈ p.support := by simpa [s] using hwS
    have heq := p.eq_snd_of_mem_support_of_adj_start_of_length_add_two_lt_girth
      hp (by omega) hwsupp (hadj w hwI)
    exact (Finset.ne_of_mem_erase hwW) heq
  have huniq : ∀ w ∈ W, ∀ ⦃b : α⦄, b ∈ s → G.Adj w b → b = v := by
    intro w hwW b hb hwb
    have hwI : w ∈ I := Finset.mem_of_mem_erase hwW
    have hwout : w ∉ p.support := by simpa [s] using hWout w hwW
    have hbsupp : b ∈ p.support := by simpa [s] using hb
    exact p.eq_start_of_external_adj_mem_support_of_length_add_two_lt_girth
      hp (by omega) hwout (hadj w hwI) hbsupp hwb
  have hWind : G.IsIndepSet (W : Set α) := by
    exact hind.mono (by intro x hx; exact Finset.mem_of_mem_erase (Finset.mem_coe.mp hx))
  have hTreeW : (G.induce ((s ∪ W : Finset α) : Set α)).IsTree :=
    hT.induce_union_broom_leaves hv W hWadj hWout huniq hWind
  have hunion : s ∪ W = I ∪ s := by
    ext x
    constructor
    · intro hx
      rcases Finset.mem_union.mp hx with hxs | hxW
      · exact Finset.mem_union_right _ hxs
      · exact Finset.mem_union_left _ (Finset.mem_of_mem_erase hxW)
    · intro hx
      rcases Finset.mem_union.mp hx with hxI | hxs
      · by_cases hxeq : x = p.snd
        · exact Finset.mem_union_left _ (hxeq ▸ hsnd)
        · exact Finset.mem_union_right _ (Finset.mem_erase.mpr ⟨hxeq, hxI⟩)
      · exact Finset.mem_union_left _ hxs
  have hs_card : s.card = r + 1 := by
    dsimp [s]
    rw [List.toFinset_card_of_nodup hp.support_nodup, p.length_support, hlen]
  have hW_card : I.card ≤ W.card + 1 := by
    by_cases hm : p.snd ∈ I
    · dsimp [W]
      rw [Finset.card_erase_add_one hm]
    · have hWI : W = I := by simp [W, hm]
      rw [hWI]
      omega
  have hdisj : Disjoint s W := Finset.disjoint_left.mpr (by
    intro x hxs hxW
    exact hWout x hxW hxs)
  have hcard : I.card + r ≤ (I ∪ s).card := by
    rw [← hunion, Finset.card_union_of_disjoint hdisj, hs_card]
    omega
  constructor
  · rw [← hunion]
    exact hTreeW
  · simpa [s] using hcard

end SimpleGraph
















namespace WrittenOnTheWallII.GraphConjecture141

open Classical SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α] [Nontrivial α]

omit [DecidableEq α] [Nontrivial α] in
/-- Every concrete induced tree is bounded by `largestInducedTreeSize`. -/
private lemma card_le_largestInducedTreeSize (G : SimpleGraph α) {s : Finset α}
    (hs : (G.induce (s : Set α)).IsTree) :
    s.card ≤ largestInducedTreeSize G := by
  unfold largestInducedTreeSize
  apply le_csSup
  · exact ⟨Fintype.card α, by
      rintro n ⟨t, rfl, -⟩
      exact t.card_le_univ⟩
  · exact ⟨s, rfl, hs⟩

omit [Fintype α] [Nontrivial α] in
/-- An independent subset of a vertex neighbourhood, together with its
centre, induces a star. -/
private lemma star_induced_tree (G : SimpleGraph α) {v : α} (I : Finset α)
    (hadj : ∀ i ∈ I, G.Adj v i) (hind : G.IsIndepSet (I : Set α)) :
    (G.induce ((insert v I : Finset α) : Set α)).IsTree ∧
      (insert v I).card = I.card + 1 := by
  have hvnot : v ∉ I := by
    intro hv
    exact G.irrefl (hadj v hv)
  have hsingleton :
      (G.induce (({v} : Finset α) : Set α)).IsTree := by
    letI : Nonempty (({v} : Finset α) : Set α) := ⟨⟨v, by simp⟩⟩
    letI : Subsingleton (({v} : Finset α) : Set α) := ⟨by
      intro x y
      apply Subtype.ext
      have hx : (x : α) = v := by simpa using x.property
      have hy : (y : α) = v := by simpa using y.property
      exact hx.trans hy.symm⟩
    exact SimpleGraph.IsTree.of_subsingleton
  have hout : ∀ w ∈ I, w ∉ ({v} : Finset α) := by
    intro w hw
    simp only [Finset.mem_singleton]
    intro hwv
    subst w
    exact G.irrefl (hadj v hw)
  have huniq : ∀ w ∈ I, ∀ ⦃b : α⦄,
      b ∈ ({v} : Finset α) → G.Adj w b → b = v := by
    intro w hw b hb hwb
    simpa using hb
  have htree := hsingleton.induce_union_broom_leaves (by simp) I hadj hout huniq hind
  constructor
  · simpa [Finset.singleton_union] using htree
  · rw [Finset.card_insert_of_notMem hvnot]

/-- Integrated scratch proof of WOWII Conjecture 141. -/
theorem conjecture141 (G : SimpleGraph α) [DecidableRel G.Adj] (hconn : G.Connected) :
    (G.girth / 2 : ℤ) - 1 + ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
    (largestInducedTreeSize G : ℤ) := by
  obtain ⟨v, -, hv⟩ := Finset.exists_mem_eq_sup
    (Finset.univ : Finset α) Finset.univ_nonempty (indepNeighborsCard G)
  obtain ⟨J, hJ⟩ :=
    (G.induce (G.neighborSet v)).exists_isNIndepSet_indepNum
  let I : Finset α := J.map ⟨Subtype.val, Subtype.val_injective⟩
  have hIN : G.IsNIndepSet (indepNeighborsCard G v) I := by
    exact (SimpleGraph.isNIndepSet_induce (G := G)).mp
      (by
        rw [← SimpleGraph.induce_eq_coe_induce_top]
        simpa [indepNeighborsCard] using hJ)
  have hIcard : I.card = indepNeighborsCard G v := hIN.card_eq
  have hIind : G.IsIndepSet (I : Set α) := hIN.isIndepSet
  have hIadj : ∀ i ∈ I, G.Adj v i := by
    intro i hi
    simp only [I, Finset.mem_map] at hi
    obtain ⟨j, hj, rfl⟩ := hi
    exact j.property
  obtain ⟨hstar, hstarcard⟩ := star_induced_tree G I hIadj hIind
  have hstarle := card_le_largestInducedTreeSize G hstar
  have hstarbound : I.card + 1 ≤ largestInducedTreeSize G := by omega
  rw [hv]
  by_cases hac : G.IsAcyclic
  · have hg : G.girth = 0 := hac.girth_eq_zero
    rw [hg]
    norm_num
    omega
  · have hg3 : 3 ≤ G.girth := G.three_le_girth hac
    by_cases hg4 : 4 ≤ G.girth
    · let r : ℕ := G.girth / 2 - 1
      have hr : r + 2 ≤ G.girth := by
        dsimp [r]
        omega
      obtain ⟨z, p, hp, hplen⟩ :=
        SimpleGraph.exists_isPath_length_eq_of_add_two_le_girth hconn hac v hr
      have hshort : r + 2 < G.girth := by
        dsimp [r]
        omega
      obtain ⟨hbroom, hbroomcard⟩ :=
        SimpleGraph.broom_induced_tree p hp hplen hshort I hIadj hIind
      have hbroomle := card_le_largestInducedTreeSize G hbroom
      have hbound : I.card + r ≤ largestInducedTreeSize G :=
        hbroomcard.trans hbroomle
      dsimp [r] at hbound
      omega
    · have hg : G.girth = 3 := by omega
      rw [hg]
      norm_num
      omega

end WrittenOnTheWallII.GraphConjecture141
