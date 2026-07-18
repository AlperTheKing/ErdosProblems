import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Independence
import Mathlib.Combinatorics.SimpleGraph.Girth

/-!
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
















