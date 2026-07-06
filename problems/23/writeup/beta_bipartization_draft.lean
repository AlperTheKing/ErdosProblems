/-! ### FC bridge: `beta_bipartization` — betaSimple ≤ K yields a bipartite
subgraph deleting ≤ K edges (the sole Mathlib lemma the official erdos_23
shape reduces to). Grafted here (not a separate file) because it uses the
private `mem_orderedEdgeFinset_iff`. -/

namespace SimpleGraphBridge

noncomputable section

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Monochromatic edge set as a set of `Sym2 V`. -/
def monoEdgeSet (Gs : SimpleGraph V) (f : V → Bool) : Set (Sym2 V) :=
  {e | ∃ u v : V, e = s(u, v) ∧ Gs.Adj u v ∧ f u = f v}

/-- The monochromatic-edge graph. -/
def monoGraph (Gs : SimpleGraph V) (f : V → Bool) : SimpleGraph V :=
  SimpleGraph.fromEdgeSet (monoEdgeSet Gs f)

/-- The bichromatic subgraph obtained by deleting the monochromatic graph. -/
def bichromSubgraph (Gs : SimpleGraph V) (f : V → Bool) : SimpleGraph V :=
  Gs \ monoGraph Gs f

private lemma monoGraph_le (Gs : SimpleGraph V) (f : V → Bool) :
    monoGraph Gs f ≤ Gs := by
  intro u v h
  rw [monoGraph, SimpleGraph.fromEdgeSet_adj] at h
  rcases h with ⟨hmem, huv_ne⟩
  rcases hmem with ⟨a, b, hsym, hadj, hsame⟩
  have hs : s(u, v) = s(a, b) := by simpa using hsym.symm
  rcases (Sym2.mk_eq_mk_iff.mp hs) with hcase | hcase
  · rcases hcase with ⟨rfl, rfl⟩
    exact hadj
  · rcases hcase with ⟨hu, hv⟩
    subst hu
    subst hv
    exact Gs.symm hadj

private lemma bichromSubgraph_le (Gs : SimpleGraph V) (f : V → Bool) :
    bichromSubgraph Gs f ≤ Gs := by
  intro u v h
  rw [bichromSubgraph] at h
  exact h.1

private lemma bichrom_adj_iff (Gs : SimpleGraph V) (f : V → Bool) {u v : V} :
    (bichromSubgraph Gs f).Adj u v ↔ Gs.Adj u v ∧ f u ≠ f v := by
  constructor
  · intro h
    rw [bichromSubgraph] at h
    rcases h with ⟨hG, hnotMono⟩
    refine ⟨hG, ?_⟩
    intro hsame
    apply hnotMono
    rw [monoGraph, SimpleGraph.fromEdgeSet_adj]
    refine ⟨?_, Gs.ne_of_adj hG⟩
    exact ⟨u, v, rfl, hG, hsame⟩
  · intro h
    rcases h with ⟨hG, hdiff⟩
    rw [bichromSubgraph]
    refine ⟨hG, ?_⟩
    intro hmono
    rw [monoGraph, SimpleGraph.fromEdgeSet_adj] at hmono
    rcases hmono with ⟨hmem, hne⟩
    rcases hmem with ⟨a, b, hsym, hadj, hsame⟩
    have hs : s(u, v) = s(a, b) := by simpa using hsym.symm
    rcases (Sym2.mk_eq_mk_iff.mp hs) with hcase | hcase
    · rcases hcase with ⟨rfl, rfl⟩
      exact hdiff hsame
    · rcases hcase with ⟨hu, hv⟩
      subst hu
      subst hv
      exact hdiff hsame.symm

private theorem bichromSubgraph_bipartite (Gs : SimpleGraph V) (f : V → Bool) :
    (bichromSubgraph Gs f).IsBipartite := by
  dsimp [SimpleGraph.IsBipartite]
  refine ⟨⟨fun v : V => if f v then (1 : Fin 2) else 0, ?_⟩⟩
  intro u v huv
  have hdiff : f u ≠ f v := (bichrom_adj_iff Gs f).mp huv |>.2
  by_cases hu : f u = true
  · have hv : f v = false := by
      cases hvv : f v <;> simp_all
    simp [hu, hv]
  · have huF : f u = false := by
      cases huu : f u <;> simp_all
    have hvT : f v = true := by
      cases hvv : f v <;> simp_all
    simp [huF, hvT]

/-- Oriented-to-unoriented map used in the counting bridge. -/
def orderedToSym2 : V × V → Sym2 V :=
  fun p => s(p.1, p.2)

private lemma orderedToSym2_inj_on_ordered
    {p q : V × V}
    (hp : vEquivFin V p.1 < vEquivFin V p.2)
    (hq : vEquivFin V q.1 < vEquivFin V q.2)
    (h : orderedToSym2 p = orderedToSym2 q) :
    p = q := by
  rcases p with ⟨p1, p2⟩
  rcases q with ⟨q1, q2⟩
  unfold orderedToSym2 at h
  rcases (Sym2.mk_eq_mk_iff.mp h) with hcase | hcase
  · rcases hcase with ⟨h1, h2⟩
    simp [h1, h2]
  · rcases hcase with ⟨h1, h2⟩
    subst h1
    subst h2
    have : ¬ vEquivFin V q2 < vEquivFin V q1 := not_lt_of_ge (le_of_lt hq)
    exact False.elim (this hp)

/-- Counting bridge: the number of monochromatic unordered edges equals the
`simpleMonoCount` defined using the canonical ordered orientation. -/
private theorem monoGraph_edgeFinset_card_eq_simpleMonoCount
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj] (f : V → Bool) :
    (monoGraph Gs f).edgeFinset.card = simpleMonoCount Gs f := by
  classical
  let M : Finset (V × V) :=
    (orderedEdgeFinset Gs).filter (fun p : V × V => f p.1 = f p.2)
  have hcard :
      M.card = (monoGraph Gs f).edgeFinset.card := by
    refine Finset.card_congr
      (fun p _hp => orderedToSym2 p)
      ?hmem ?hinj ?hsurj
    · intro p hp
      have hpM : p ∈ M := hp
      have hpOrd : p ∈ orderedEdgeFinset Gs := (Finset.mem_filter.mp hpM).1
      have hsame : f p.1 = f p.2 := (Finset.mem_filter.mp hpM).2
      have hAdj : Gs.Adj p.1 p.2 :=
        (mem_orderedEdgeFinset_iff (Gs := Gs) p).mp hpOrd |>.2
      rw [SimpleGraph.mem_edgeFinset]
      rw [monoGraph, SimpleGraph.edgeSet_fromEdgeSet]
      simp [monoEdgeSet, orderedToSym2, hAdj, hsame]
    · intro p hp q hq h
      have hpOrd : p ∈ orderedEdgeFinset Gs := (Finset.mem_filter.mp hp).1
      have hqOrd : q ∈ orderedEdgeFinset Gs := (Finset.mem_filter.mp hq).1
      have hpLt : vEquivFin V p.1 < vEquivFin V p.2 :=
        (mem_orderedEdgeFinset_iff (Gs := Gs) p).mp hpOrd |>.1
      have hqLt : vEquivFin V q.1 < vEquivFin V q.2 :=
        (mem_orderedEdgeFinset_iff (Gs := Gs) q).mp hqOrd |>.1
      exact orderedToSym2_inj_on_ordered hpLt hqLt h
    · intro e he
      rw [SimpleGraph.mem_edgeFinset] at he
      rw [monoGraph, SimpleGraph.edgeSet_fromEdgeSet] at he
      rcases he with ⟨hmono, _hnotDiag⟩
      rcases hmono with ⟨u, v, heq, hAdj, hsame⟩
      have hne : u ≠ v := Gs.ne_of_adj hAdj
      by_cases huv : vEquivFin V u < vEquivFin V v
      · refine ⟨(u, v), ?_, ?_⟩
        · rw [Finset.mem_filter]
          constructor
          · exact (mem_orderedEdgeFinset_iff (Gs := Gs) (u, v)).mpr ⟨huv, hAdj⟩
          · exact hsame
        · simp [orderedToSym2, heq]
      · have hvu : vEquivFin V v < vEquivFin V u := by
          have hneq : vEquivFin V u ≠ vEquivFin V v := by
            intro hfin
            exact hne ((vEquivFin V).injective hfin)
          exact lt_of_le_of_ne (le_of_not_gt huv) hneq.symm
        refine ⟨(v, u), ?_, ?_⟩
        · rw [Finset.mem_filter]
          constructor
          · exact (mem_orderedEdgeFinset_iff (Gs := Gs) (v, u)).mpr
              ⟨hvu, Gs.symm hAdj⟩
          · exact hsame.symm
        · simp [orderedToSym2, heq, Sym2.eq_swap]
  unfold simpleMonoCount
  rw [← hcard]
  rfl

private theorem edgeFinset_sdiff_bichrom_card
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj] (f : V → Bool) :
    (Gs.edgeFinset \ (bichromSubgraph Gs f).edgeFinset).card =
      simpleMonoCount Gs f := by
  classical
  have hMle : monoGraph Gs f ≤ Gs := monoGraph_le Gs f
  have hsdiff :
      Gs.edgeFinset \ (bichromSubgraph Gs f).edgeFinset =
        (monoGraph Gs f).edgeFinset := by
    rw [← SimpleGraph.edgeFinset_sdiff]
    apply (SimpleGraph.edgeFinset_inj).mpr
    ext u v
    constructor
    · intro h
      rw [bichromSubgraph] at h
      rcases h with ⟨hG, hnotH⟩
      rw [monoGraph, SimpleGraph.fromEdgeSet_adj]
      refine ⟨?_, Gs.ne_of_adj hG⟩
      by_cases hsame : f u = f v
      · exact ⟨u, v, rfl, hG, hsame⟩
      · apply False.elim
        apply hnotH
        rw [bichromSubgraph]
        exact ⟨hG, by
          intro hm
          rw [monoGraph, SimpleGraph.fromEdgeSet_adj] at hm
          rcases hm with ⟨hmem, _⟩
          rcases hmem with ⟨a, b, hsym, hadj, habsame⟩
          have hs : s(u, v) = s(a, b) := by simpa using hsym.symm
          rcases (Sym2.mk_eq_mk_iff.mp hs) with hcase | hcase
          · rcases hcase with ⟨rfl, rfl⟩
            exact hsame habsame
          · rcases hcase with ⟨hu, hv⟩
            subst hu
            subst hv
            exact hsame habsame.symm⟩
    · intro h
      have hG : Gs.Adj u v := hMle h
      rw [bichromSubgraph]
      refine ⟨hG, ?_⟩
      intro hH
      have hdiff : f u ≠ f v := (bichrom_adj_iff Gs f).mp hH |>.2
      rw [monoGraph, SimpleGraph.fromEdgeSet_adj] at h
      rcases h with ⟨hmem, _⟩
      rcases hmem with ⟨a, b, hsym, hadj, hsame⟩
      have hs : s(u, v) = s(a, b) := by simpa using hsym.symm
      rcases (Sym2.mk_eq_mk_iff.mp hs) with hcase | hcase
      · rcases hcase with ⟨rfl, rfl⟩
        exact hdiff hsame
      · rcases hcase with ⟨hu, hv⟩
        subst hu
        subst hv
        exact hdiff hsame.symm
  rw [hsdiff]
  exact monoGraph_edgeFinset_card_eq_simpleMonoCount Gs f

/-- Main bridge lemma required by formal-conjectures. -/
theorem beta_bipartization
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj] (K : Nat)
    (h : betaSimple Gs ≤ K) :
    ∃ H : SimpleGraph V,
      H ≤ Gs ∧ H.IsBipartite ∧
        (Gs.edgeFinset \ H.edgeFinset).card ≤ K := by
  classical
  let vals : Finset Nat := Finset.univ.image (simpleMonoCount Gs)
  have hvals_nonempty : vals.Nonempty :=
    Finset.image_nonempty.mpr Finset.univ_nonempty
  have hmin_mem : betaSimple Gs ∈ vals := by
    unfold betaSimple
    exact Finset.min'_mem vals hvals_nonempty
  rcases Finset.mem_image.mp hmin_mem with ⟨f, _hf, hf⟩
  let H : SimpleGraph V := bichromSubgraph Gs f
  refine ⟨H, ?_, ?_, ?_⟩
  · exact bichromSubgraph_le Gs f
  · exact bichromSubgraph_bipartite Gs f
  · have hcard :
        (Gs.edgeFinset \ H.edgeFinset).card = simpleMonoCount Gs f := by
      simpa [H] using edgeFinset_sdiff_bichrom_card Gs f
    have hf_le : simpleMonoCount Gs f ≤ K := by
      rw [← hf]
      exact h
    rw [hcard]
    exact hf_le

end

end SimpleGraphBridge
