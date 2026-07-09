import Erdos23Delta0.Ell5CSReduction
import Erdos23Delta0.Ell5SupportFinset

/-!
# Path-level bridge for T6

This module isolates the graph-walk content of `geodesics_union_ge_six`:
two distinct length-4 simple paths with the same endpoints have edge-union size
at least six.  The proof combines pure four-set counting with closed-walk
incidence parity.
-/

namespace Erdos23Delta0
namespace Ell5GeodesicUnion

open SimpleGraph Finset

variable {V : Type*} [DecidableEq V] {G : SimpleGraph V} {u v : V}

private theorem even_countP_edges_iff_walk {u v : V} {p : G.Walk u v} (x : V) :
    Even (p.edges.countP fun e => x ∈ e) ↔ u ≠ v → x ≠ u ∧ x ≠ v := by
  induction p with
  | nil => simp
  | cons huv p ih =>
    simp only [List.countP_cons, Ne, SimpleGraph.Walk.edges_cons, Sym2.mem_iff]
    split_ifs with h
    · rw [decide_eq_true_eq] at h
      obtain (rfl | rfl) := h
      · rw [Nat.even_add_one, ih]
        simp only [huv.ne, imp_false, Ne, not_false_iff, true_and, not_forall,
          Classical.not_not, exists_prop, not_true, false_and,
          and_iff_right_iff_imp]
        rintro rfl rfl
        exact G.loopless _ huv
      · have := huv.ne
        grind
    · grind

private theorem even_countP_edges_closed {u : V} (p : G.Walk u u) (x : V) :
    Even (p.edges.countP fun e => x ∈ e) := by
  rw [even_countP_edges_iff_walk]
  intro h
  exact False.elim (h rfl)

private theorem sym2_eq_of_even_two_nonloop {a b c d : V}
    (hab : a ≠ b)
    (hpar : ∀ x : V,
      Even ((if x ∈ s(a,b) then 1 else 0) + (if x ∈ s(c,d) then 1 else 0))) :
    s(a,b) = s(c,d) := by
  have ha : a ∈ s(c,d) := by
    by_contra ha
    have h := hpar a
    simp [Sym2.mem_iff, hab, ha] at h
  have hb : b ∈ s(c,d) := by
    by_contra hb
    have h := hpar b
    simp [Sym2.mem_iff, hab.symm, hb] at h
  rw [Sym2.eq_iff]
  rw [Sym2.mem_iff] at ha hb
  grind

private theorem countP_eq_sum_toFinset_of_nodup {α : Type*} [DecidableEq α]
    (l : List α) (P : α → Prop) [DecidablePred P] (hn : l.Nodup) :
    l.countP P = ∑ x ∈ l.toFinset, if P x then 1 else 0 := by
  induction l with
  | nil => simp
  | cons a t ih =>
    rw [List.nodup_cons] at hn
    have ht := hn.2
    have hnot : a ∉ t.toFinset := by simpa using hn.1
    rw [List.countP_cons, List.toFinset_cons, Finset.sum_insert hnot, ih ht]
    by_cases hP : P a <;> simp [hP] <;> omega

private theorem sdiff_card_one_of_four_inter_three {β : Type*} [DecidableEq β] {A B : Finset β}
    (hA : A.card = 4) (hI : (A ∩ B).card = 3) :
    (A \ B).card = 1 := by
  have hEq : A \ B = A \ (A ∩ B) := by
    ext x
    simp
  have hInter : (A ∩ B) ∩ A = A ∩ B := by
    ext x
    simp [and_comm]
  rw [hEq, Finset.card_sdiff, hInter]
  omega

private theorem even_singletons_of_even_sum {β : Type*} [DecidableEq β]
    {A B : Finset β} {eP eQ : β} (f : β → Nat)
    (hAp : A \ B = {eP}) (hBq : B \ A = {eQ})
    (hEven : Even ((∑ e ∈ A, f e) + (∑ e ∈ B, f e))) :
    Even (f eP + f eQ) := by
  let C : Nat := ∑ e ∈ A ∩ B, f e
  have hAminus : A \ (A ∩ B) = {eP} := by
    calc
      A \ (A ∩ B) = A \ B := by
        ext x
        by_cases hxA : x ∈ A <;> by_cases hxB : x ∈ B <;> simp [hxA, hxB]
      _ = {eP} := hAp
  have hBminus : B \ (A ∩ B) = {eQ} := by
    calc
      B \ (A ∩ B) = B \ A := by
        ext x
        by_cases hxA : x ∈ A <;> by_cases hxB : x ∈ B <;> simp [hxA, hxB]
      _ = {eQ} := hBq
  have hsumA0 := Finset.sum_sdiff (f := f) (Finset.inter_subset_left : A ∩ B ⊆ A)
  have hsumA : (∑ e ∈ A, f e) = f eP + C := by
    rw [hAminus] at hsumA0
    simp at hsumA0
    exact hsumA0.symm
  have hsumB0 := Finset.sum_sdiff (f := f) (Finset.inter_subset_right : A ∩ B ⊆ B)
  have hsumB : (∑ e ∈ B, f e) = f eQ + C := by
    rw [hBminus] at hsumB0
    simp at hsumB0
    exact hsumB0.symm
  rw [hsumA, hsumB] at hEven
  have hcalc : (f eP + C) + (f eQ + C) = (f eP + f eQ) + 2 * C := by omega
  rw [hcalc] at hEven
  rcases hEven with ⟨k, hk⟩
  use k - C
  omega

private theorem union_card_ge_six_of_inter_ne_three {β : Type*} [DecidableEq β]
    {A B : Finset β}
    (hA : A.card = 4) (hB : B.card = 4) (hne : A ≠ B)
    (hI : (A ∩ B).card ≠ 3) :
    6 ≤ (A ∪ B).card := by
  by_contra hnot
  have hU : (A ∪ B).card ≤ 5 := by omega
  have hsum := Finset.card_union_add_card_inter A B
  have hIle : (A ∩ B).card ≤ 4 := by
    calc (A ∩ B).card ≤ A.card := Finset.card_le_card Finset.inter_subset_left
      _ = 4 := hA
  have hIlt : (A ∩ B).card < 4 := by
    by_contra hnot4
    have hI4 : (A ∩ B).card = 4 := by omega
    have hIA : A ∩ B = A :=
      Finset.eq_of_subset_of_card_le Finset.inter_subset_left (by omega)
    have hIB : A ∩ B = B :=
      Finset.eq_of_subset_of_card_le Finset.inter_subset_right (by omega)
    exact hne (hIA.symm.trans hIB)
  have hIge : 3 ≤ (A ∩ B).card := by omega
  exact hI (by omega)

/-- Two length-4 simple paths with the same endpoints cannot share exactly three
unordered edges.  Appending one path to the reverse of the other gives a closed
walk; after canceling the three doubled common edges, closed-walk incidence
parity forces the two singleton difference edges to coincide. -/
theorem no_three_common_edges_len4_same_endpoints
    (p q : G.Walk u v) (hp : p.IsPath) (hq : q.IsPath)
    (hlp : p.length = 4) (hlq : q.length = 4) :
    (p.edges.toFinset ∩ q.edges.toFinset).card ≠ 3 := by
  intro h3
  let A : Finset (Sym2 V) := p.edges.toFinset
  let B : Finset (Sym2 V) := q.edges.toFinset
  have hA : A.card = 4 := Ell5CSReduction.geodesic_len4_card_edges p hp hlp
  have hB : B.card = 4 := Ell5CSReduction.geodesic_len4_card_edges q hq hlq
  have hApCard : (A \ B).card = 1 := sdiff_card_one_of_four_inter_three hA h3
  have hBqCard : (B \ A).card = 1 := by
    have h3' : (B ∩ A).card = 3 := by simpa [Finset.inter_comm] using h3
    exact sdiff_card_one_of_four_inter_three hB h3'
  obtain ⟨eP, hePsingle⟩ := Finset.card_eq_one.mp hApCard
  obtain ⟨eQ, heQsingle⟩ := Finset.card_eq_one.mp hBqCard
  have hePmemA : eP ∈ A := by
    have ht : eP ∈ A \ B := by rw [hePsingle]; simp
    rw [Finset.mem_sdiff] at ht
    exact ht.1
  have hePnotB : eP ∉ B := by
    have ht : eP ∈ A \ B := by rw [hePsingle]; simp
    rw [Finset.mem_sdiff] at ht
    exact ht.2
  have heQmemB : eQ ∈ B := by
    have ht : eQ ∈ B \ A := by rw [heQsingle]; simp
    rw [Finset.mem_sdiff] at ht
    exact ht.1
  have hEvenSums : ∀ x : V,
      Even ((∑ e ∈ A, if x ∈ e then 1 else 0) +
        (∑ e ∈ B, if x ∈ e then 1 else 0)) := by
    intro x
    have hclosed := even_countP_edges_closed (p.append q.reverse) x
    simp [SimpleGraph.Walk.edges_append, SimpleGraph.Walk.edges_reverse, List.countP_append] at hclosed
    rw [countP_eq_sum_toFinset_of_nodup p.edges (fun e => x ∈ e) hp.edges_nodup,
        countP_eq_sum_toFinset_of_nodup q.edges (fun e => x ∈ e) hq.edges_nodup] at hclosed
    simpa [A, B] using hclosed
  have hpar : ∀ x : V, Even ((if x ∈ eP then 1 else 0) + (if x ∈ eQ then 1 else 0)) := by
    intro x
    exact even_singletons_of_even_sum (fun e : Sym2 V => if x ∈ e then 1 else 0)
      hePsingle heQsingle (hEvenSums x)
  induction eP using Sym2.ind with
  | _ a b =>
    induction eQ using Sym2.ind with
    | _ c d =>
      have hab : a ≠ b := by
        intro hab
        subst hab
        have hePedge : s(a,a) ∈ p.edges := by simpa [A] using hePmemA
        have hnotdiag := G.not_isDiag_of_mem_edgeSet (SimpleGraph.Walk.edges_subset_edgeSet p hePedge)
        exact hnotdiag (by simp)
      have heq : s(a,b) = s(c,d) := sym2_eq_of_even_two_nonloop hab hpar
      rw [← heq] at heQmemB
      exact hePnotB heQmemB

/-- T6 bridge: two distinct length-4 path edge sets have union size at least
six once the exactly-three-common-edges case is excluded. -/
theorem geodesics_union_ge_six_of_inter_ne_three
    (p q : G.Walk u v) (hp : p.IsPath) (hq : q.IsPath)
    (hlp : p.length = 4) (hlq : q.length = 4)
    (hne : p.edges.toFinset ≠ q.edges.toFinset)
    (hI : (p.edges.toFinset ∩ q.edges.toFinset).card ≠ 3) :
    6 ≤ (p.edges.toFinset ∪ q.edges.toFinset).card := by
  have hP : p.edges.toFinset.card = 4 :=
    Ell5CSReduction.geodesic_len4_card_edges p hp hlp
  have hQ : q.edges.toFinset.card = 4 :=
    Ell5CSReduction.geodesic_len4_card_edges q hq hlq
  exact union_card_ge_six_of_inter_ne_three hP hQ hne hI

/-- T6: two distinct length-4 geodesic edge sets between the same endpoints have
edge-union size at least six. -/
theorem geodesics_union_ge_six
    (p q : G.Walk u v) (hp : p.IsPath) (hq : q.IsPath)
    (hlp : p.length = 4) (hlq : q.length = 4)
    (hne : p.edges.toFinset ≠ q.edges.toFinset) :
    6 ≤ (p.edges.toFinset ∪ q.edges.toFinset).card := by
  exact geodesics_union_ge_six_of_inter_ne_three p q hp hq hlp hlq hne
    (no_three_common_edges_len4_same_endpoints p q hp hq hlp hlq)

/-- A full support of shortest length-4 geodesics cannot have cardinality five.
If the full support had size five, one shortest geodesic would leave an extra
support edge.  That edge lies on another shortest geodesic, and T6 forces the
two geodesic edge sets to have union cardinality at least six inside a five-set. -/
theorem geodesicSupport_card_ne_five [Fintype V] {H : SimpleGraph V} {u v : V}
    (hr : H.Reachable u v) (hd : H.dist u v = 4) :
    (Ell5SupportFinset.geodesicSupport H u v).card ≠ 5 := by
  intro hcard5
  obtain ⟨p, hp, hplenDist⟩ := hr.exists_path_of_dist
  have hplen : p.length = 4 := hplenDist.trans hd
  have hpCard : p.edges.toFinset.card = 4 :=
    Ell5CSReduction.geodesic_len4_card_edges p hp hplen
  have hpsub : p.edges.toFinset ⊆ Ell5SupportFinset.geodesicSupport H u v :=
    Ell5SupportFinset.edges_toFinset_subset_geodesicSupport p hp hplenDist
  have hpne : p.edges.toFinset ≠ Ell5SupportFinset.geodesicSupport H u v := by
    intro heq
    have : p.edges.toFinset.card = 5 := by rw [heq, hcard5]
    omega
  have hproper : p.edges.toFinset ⊂ Ell5SupportFinset.geodesicSupport H u v :=
    (Finset.ssubset_iff_subset_ne).2 ⟨hpsub, hpne⟩
  obtain ⟨e, heSupp, heNotP⟩ := Finset.exists_of_ssubset hproper
  rw [Ell5SupportFinset.mem_geodesicSupport] at heSupp
  obtain ⟨q, hq, hqlenDist, heqEdge⟩ := heSupp
  have hqlen : q.length = 4 := hqlenDist.trans hd
  have hqnep : p.edges.toFinset ≠ q.edges.toFinset := by
    intro hEq
    have : e ∈ p.edges.toFinset := by
      rw [hEq]
      exact List.mem_toFinset.mpr heqEdge
    exact heNotP this
  have hUnionGe := geodesics_union_ge_six p q hp hq hplen hqlen hqnep
  have hqsub : q.edges.toFinset ⊆ Ell5SupportFinset.geodesicSupport H u v :=
    Ell5SupportFinset.edges_toFinset_subset_geodesicSupport q hq hqlenDist
  have hUnionSub : p.edges.toFinset ∪ q.edges.toFinset ⊆ Ell5SupportFinset.geodesicSupport H u v :=
    Finset.union_subset hpsub hqsub
  have hUnionLe : (p.edges.toFinset ∪ q.edges.toFinset).card ≤ 5 := by
    exact (Finset.card_le_card hUnionSub).trans_eq hcard5
  omega
/-- If two full shortest-geodesic supports of cardinality four are equal, then
their endpoint pairs are equal.  The cardinality-four assumption forces each
full support to be exactly the edge set of any chosen shortest length-4 path;
then `PathRigidity.edges_determine_badedge` applies. -/
theorem badEdge_eq_of_geodesicSupport_eq_card_four [Fintype V] {H : SimpleGraph V}
    {u v u' v' : V}
    (hr : H.Reachable u v) (hr' : H.Reachable u' v')
    (hd : H.dist u v = 4) (hd' : H.dist u' v' = 4)
    (hEq : Ell5SupportFinset.geodesicSupport H u v =
      Ell5SupportFinset.geodesicSupport H u' v')
    (hcard : (Ell5SupportFinset.geodesicSupport H u v).card = 4) :
    s(u, v) = s(u', v') := by
  obtain ⟨p, hp, hplenDist⟩ := hr.exists_path_of_dist
  obtain ⟨q, hq, hqlenDist⟩ := hr'.exists_path_of_dist
  have hplen : p.length = 4 := hplenDist.trans hd
  have hqlen : q.length = 4 := hqlenDist.trans hd'
  have hpCard : p.edges.toFinset.card = 4 :=
    Ell5CSReduction.geodesic_len4_card_edges p hp hplen
  have hqCard : q.edges.toFinset.card = 4 :=
    Ell5CSReduction.geodesic_len4_card_edges q hq hqlen
  have hpsub : p.edges.toFinset ⊆ Ell5SupportFinset.geodesicSupport H u v :=
    Ell5SupportFinset.edges_toFinset_subset_geodesicSupport p hp hplenDist
  have hqsub : q.edges.toFinset ⊆ Ell5SupportFinset.geodesicSupport H u' v' :=
    Ell5SupportFinset.edges_toFinset_subset_geodesicSupport q hq hqlenDist
  have hpEqSupport : p.edges.toFinset = Ell5SupportFinset.geodesicSupport H u v :=
    Finset.eq_of_subset_of_card_le hpsub (by rw [hpCard, hcard])
  have hcard' : (Ell5SupportFinset.geodesicSupport H u' v').card = 4 := by
    rw [← hEq, hcard]
  have hqEqSupport : q.edges.toFinset = Ell5SupportFinset.geodesicSupport H u' v' :=
    Finset.eq_of_subset_of_card_le hqsub (by rw [hqCard, hcard'])
  have hEdges : p.edges.toFinset = q.edges.toFinset := by
    rw [hpEqSupport, hEq, ← hqEqSupport]
  have hpn : ¬ p.Nil := by
    intro hnil
    rw [SimpleGraph.Walk.nil_iff_length_eq] at hnil
    omega
  have huv : u ≠ v := by
    intro huv
    subst huv
    simpa using hd
  exact PathRigidity.edges_determine_badedge hp hq hpn huv hEdges
/-- Actual T7 `m=6` wrapper for true full geodesic supports.  Six distinct
ell=5 atom endpoint pairs cannot form a minimal Hall obstruction when rows are
the full shortest-geodesic supports. -/
theorem no_minimal_violator_card_six_geodesicSupport [Fintype V]
    {ι : Type*} [DecidableEq ι] {H : SimpleGraph V}
    (x y : ι → V) (S : Finset ι)
    (hS : S.card = 6)
    (hReach : ∀ a ∈ S, H.Reachable (x a) (y a))
    (hdist : ∀ a ∈ S, H.dist (x a) (y a) = 4)
    (hbadInj : ∀ a ∈ S, ∀ b ∈ S, s(x a, y a) = s(x b, y b) → a = b)
    (hlt : (S.biUnion fun a => Ell5SupportFinset.geodesicSupport H (x a) (y a)).card < S.card)
    (hmin : ∀ T, T ⊂ S →
      T.card ≤ (T.biUnion fun a => Ell5SupportFinset.geodesicSupport H (x a) (y a)).card) :
    False := by
  let Erow : ι → Finset (Sym2 V) := fun a => Ell5SupportFinset.geodesicSupport H (x a) (y a)
  have hltE : (S.biUnion Erow).card < S.card := by simpa [Erow] using hlt
  have hminE : ∀ T, T ⊂ S → T.card ≤ (T.biUnion Erow).card := by
    intro T hT
    simpa [Erow] using hmin T hT
  obtain ⟨hcard, hnoPrivate⟩ :=
    Ell5CSReduction.minimal_hall_obstruction_no_private_edge Erow S hltE hminE
  let U : Finset (Sym2 V) := S.biUnion Erow
  have hU : U.card = 5 := by
    dsimp [U]
    omega
  have hsub : ∀ a ∈ S, Erow a ⊆ U := by
    intro a ha
    dsimp [U]
    have heraseSub : (S.erase a).biUnion Erow ⊆ S.biUnion Erow := by
      intro e he
      rw [Finset.mem_biUnion] at he ⊢
      obtain ⟨b, hb, hbe⟩ := he
      exact ⟨b, Finset.mem_of_mem_erase hb, hbe⟩
    exact subset_trans (hnoPrivate a ha) heraseSub
  have hrow4 : ∀ a ∈ S, (Erow a).card = 4 := by
    intro a ha
    have hle : (Erow a).card ≤ U.card := Finset.card_le_card (hsub a ha)
    have hge : 4 ≤ (Erow a).card := by
      obtain ⟨p, hp, hplenDist⟩ := (hReach a ha).exists_path_of_dist
      have hplen : p.length = 4 := hplenDist.trans (hdist a ha)
      have hpCard : p.edges.toFinset.card = 4 :=
        Ell5CSReduction.geodesic_len4_card_edges p hp hplen
      have hpsub : p.edges.toFinset ⊆ Erow a := by
        dsimp [Erow]
        exact Ell5SupportFinset.edges_toFinset_subset_geodesicSupport p hp hplenDist
      calc
        4 = p.edges.toFinset.card := hpCard.symm
        _ ≤ (Erow a).card := Finset.card_le_card hpsub
    have hne5 : (Erow a).card ≠ 5 := by
      dsimp [Erow]
      exact geodesicSupport_card_ne_five (hReach a ha) (hdist a ha)
    omega
  have hinj : Set.InjOn Erow S := by
    intro a ha b hb hEq
    have hEdge := badEdge_eq_of_geodesicSupport_eq_card_four
      (hReach a ha) (hReach b hb) (hdist a ha) (hdist b hb)
      (by simpa [Erow] using hEq) (by simpa [Erow] using hrow4 a ha)
    exact hbadInj a ha b hb hEdge
  have himage_subset : S.image Erow ⊆ U.powersetCard 4 := by
    intro A hA
    rw [Finset.mem_image] at hA
    obtain ⟨a, ha, rfl⟩ := hA
    rw [Finset.mem_powersetCard]
    exact ⟨hsub a ha, hrow4 a ha⟩
  have hle5 : S.card ≤ 5 := by
    calc
      S.card = (S.image Erow).card := (Finset.card_image_of_injOn hinj).symm
      _ ≤ (U.powersetCard 4).card := Finset.card_le_card himage_subset
      _ = Nat.choose U.card 4 := Finset.card_powersetCard 4 U
      _ = 5 := by rw [hU]; norm_num
  omega
end Ell5GeodesicUnion
end Erdos23Delta0
