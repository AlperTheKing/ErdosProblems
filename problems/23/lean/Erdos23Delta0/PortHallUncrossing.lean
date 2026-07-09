import Mathlib
import Erdos23Delta0.BankedWallLP

/-!
# Port-Hall uncrossing algebra (2026-07-09)

The "fully proved part" of WALL ATTACK R2 (`WALL_ATTACK_R2_GPTPRO.md` §§1-2), compiled with FULL proofs and
exact-gated first (`_claude_porthall_uncross_gate.py`: falsifiers F1/F2 verified, 24000 identity checks,
692/692 minimal-deficient one-component). For a port load `L` on a banked wall LP, the Hall deficiency
`Def(P) = load(P) − cap(legalNbr(P))` satisfies:

* `deficiencyQ_supermodular` — Def(P) + Def(Q) ≤ Def(P∪Q) + Def(P∩Q);
* `deficiencyQ_union_of_disjoint_ports` — the EXACT overlap identity
  Def(P₁∪P₂) = Def(P₁) + Def(P₂) + cap(N(P₁) ∩ N(P₂)) for disjoint ports (overlap can hide positive
  deficiency — "independent root neighborhoods" MUST mean disjoint legal sink neighborhoods);
* `deficiencyQ_disjoint_neighbor_split` — additivity when the legal neighborhoods are disjoint;
* `minimal_deficient_has_one_legal_component` — an inclusion-minimal Hall-deficient port set has exactly ONE
  legal-incidence component (the precise uncrossing claim; the capacity side is safe because component sink
  blocks are disjoint, so no bank capacity is double-counted).

The closure-level versions (MinimalClosedDeficient etc.) attach at the EscapeQuotientData/extractor level —
deliberately not here. R2's falsifier 1 shows plain `InclusionMinimalDeficient` + closure is NOT enough; the
one-component theorem below is stated for the plain predicate, which is what its proof actually needs.
No `sorry`/`admit`/`native_decide`; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace Wall
namespace PortHall

open scoped BigOperators

variable {I : BankedWallLP}

@[local instance] noncomputable def portDecEq {I : BankedWallLP} : DecidableEq I.Port :=
  Classical.decEq _

@[local instance] noncomputable def sinkDecEq {I : BankedWallLP} : DecidableEq I.Sink :=
  Classical.decEq _

open Classical in
/-- Legal sink neighborhood of a port set. -/
noncomputable def legalNbr (I : BankedWallLP) (P : Finset I.Port) : Finset I.Sink :=
  Finset.univ.filter (fun s : I.Sink => ∃ p ∈ P, I.legal p s)

theorem mem_legalNbr {P : Finset I.Port} {s : I.Sink} :
    s ∈ legalNbr I P ↔ ∃ p ∈ P, I.legal p s := by
  simp [legalNbr]

theorem legalNbr_empty : legalNbr I (∅ : Finset I.Port) = ∅ := by
  ext s
  simp [mem_legalNbr]

/-- Total bank capacity of a sink set. -/
def capQ (I : BankedWallLP) (T : Finset I.Sink) : ℚ := ∑ s ∈ T, I.cap s

/-- Total port load of a port set. -/
def loadQ (I : BankedWallLP) (L : I.Port → ℚ) (P : Finset I.Port) : ℚ := ∑ p ∈ P, L p

/-- Hall deficiency of a port set against its legal sink neighborhood. -/
noncomputable def deficiencyQ (I : BankedWallLP) (L : I.Port → ℚ) (P : Finset I.Port) : ℚ :=
  loadQ I L P - capQ I (legalNbr I P)

def HallDeficient (I : BankedWallLP) (L : I.Port → ℚ) (P : Finset I.Port) : Prop :=
  0 < deficiencyQ I L P

def InclusionMinimalDeficient (I : BankedWallLP) (L : I.Port → ℚ) (P : Finset I.Port) : Prop :=
  HallDeficient I L P ∧ ∀ P' : Finset I.Port, P' ⊂ P → deficiencyQ I L P' ≤ 0

theorem legalNbr_union (P Q : Finset I.Port) :
    legalNbr I (P ∪ Q) = legalNbr I P ∪ legalNbr I Q := by
  ext s
  simp only [mem_legalNbr, Finset.mem_union]
  constructor
  · rintro ⟨p, hp | hp, hleg⟩
    · exact Or.inl ⟨p, hp, hleg⟩
    · exact Or.inr ⟨p, hp, hleg⟩
  · rintro (⟨p, hp, hleg⟩ | ⟨p, hp, hleg⟩)
    · exact ⟨p, Or.inl hp, hleg⟩
    · exact ⟨p, Or.inr hp, hleg⟩

theorem legalNbr_inter_subset (P Q : Finset I.Port) :
    legalNbr I (P ∩ Q) ⊆ legalNbr I P ∩ legalNbr I Q := by
  intro s hs
  simp only [mem_legalNbr, Finset.mem_inter] at hs ⊢
  rcases hs with ⟨p, hp, hleg⟩
  exact ⟨⟨p, hp.1, hleg⟩, ⟨p, hp.2, hleg⟩⟩

theorem capQ_mono (hcap : ∀ s : I.Sink, 0 ≤ I.cap s) {A B : Finset I.Sink} (hAB : A ⊆ B) :
    capQ I A ≤ capQ I B :=
  Finset.sum_le_sum_of_subset_of_nonneg hAB (fun s _ _ => hcap s)

theorem capQ_union_inter (A B : Finset I.Sink) :
    capQ I (A ∪ B) + capQ I (A ∩ B) = capQ I A + capQ I B :=
  Finset.sum_union_inter

theorem capQ_submodular_on_legalNbr (hcap : ∀ s : I.Sink, 0 ≤ I.cap s) (P Q : Finset I.Port) :
    capQ I (legalNbr I (P ∪ Q)) + capQ I (legalNbr I (P ∩ Q))
      ≤ capQ I (legalNbr I P) + capQ I (legalNbr I Q) := by
  have h1 : capQ I (legalNbr I (P ∪ Q)) = capQ I (legalNbr I P ∪ legalNbr I Q) := by
    rw [legalNbr_union]
  have h2 : capQ I (legalNbr I (P ∩ Q)) ≤ capQ I (legalNbr I P ∩ legalNbr I Q) :=
    capQ_mono hcap (legalNbr_inter_subset P Q)
  have h3 := capQ_union_inter (I := I) (legalNbr I P) (legalNbr I Q)
  linarith

theorem loadQ_union_inter (L : I.Port → ℚ) (P Q : Finset I.Port) :
    loadQ I L (P ∪ Q) + loadQ I L (P ∩ Q) = loadQ I L P + loadQ I L Q :=
  Finset.sum_union_inter

/-- **Supermodularity of the Hall deficiency** (load modular, capacity-neighborhood submodular). -/
theorem deficiencyQ_supermodular (hcap : ∀ s : I.Sink, 0 ≤ I.cap s) (L : I.Port → ℚ)
    (P Q : Finset I.Port) :
    deficiencyQ I L P + deficiencyQ I L Q
      ≤ deficiencyQ I L (P ∪ Q) + deficiencyQ I L (P ∩ Q) := by
  have hload := loadQ_union_inter (I := I) L P Q
  have hcapineq := capQ_submodular_on_legalNbr hcap P Q
  unfold deficiencyQ
  linarith

/-- **The exact overlap identity** for disjoint port sets: the neighborhood-intersection capacity is the
correction term — overlap can hide positive deficiency, so "independent root neighborhoods" must mean
DISJOINT legal sink neighborhoods. -/
theorem deficiencyQ_union_of_disjoint_ports (L : I.Port → ℚ) {P₁ P₂ : Finset I.Port}
    (hPdisj : Disjoint P₁ P₂) :
    deficiencyQ I L (P₁ ∪ P₂)
      = deficiencyQ I L P₁ + deficiencyQ I L P₂
        + capQ I (legalNbr I P₁ ∩ legalNbr I P₂) := by
  have hload : loadQ I L (P₁ ∪ P₂) = loadQ I L P₁ + loadQ I L P₂ :=
    Finset.sum_union hPdisj
  have hcapui := capQ_union_inter (I := I) (legalNbr I P₁) (legalNbr I P₂)
  unfold deficiencyQ
  rw [legalNbr_union, hload]
  linarith

/-- Additivity of deficiency on disjoint ports with disjoint legal neighborhoods. -/
theorem deficiencyQ_disjoint_neighbor_split (L : I.Port → ℚ) {P₁ P₂ : Finset I.Port}
    (hPdisj : Disjoint P₁ P₂)
    (hNdisj : Disjoint (legalNbr I P₁) (legalNbr I P₂)) :
    deficiencyQ I L (P₁ ∪ P₂) = deficiencyQ I L P₁ + deficiencyQ I L P₂ := by
  have h := deficiencyQ_union_of_disjoint_ports (I := I) L hPdisj
  have hzero : capQ I (legalNbr I P₁ ∩ legalNbr I P₂) = 0 := by
    rw [Finset.disjoint_iff_inter_eq_empty.mp hNdisj]
    simp [capQ]
  rw [h, hzero, add_zero]

/-- A deficient port set is nonempty (the empty set has zero load and zero legal capacity). -/
theorem nonempty_of_hallDeficient {L : I.Port → ℚ} {P : Finset I.Port}
    (h : HallDeficient I L P) : P.Nonempty := by
  rcases Finset.eq_empty_or_nonempty P with hP | hP
  · exfalso
    have : deficiencyQ I L P = 0 := by
      unfold deficiencyQ loadQ
      rw [hP, legalNbr_empty]
      simp [capQ]
    unfold HallDeficient at h
    rw [this] at h
    exact lt_irrefl 0 h
  · exact hP

/-- A partition of a port set into blocks with pairwise-disjoint ports AND pairwise-disjoint legal sink
neighborhoods (the sink block of each component is exactly its legal neighborhood). -/
structure LegalComponentPartition (I : BankedWallLP) (P : Finset I.Port) where
  K : Type
  kDecEq : DecidableEq K
  kFintype : Fintype K
  ports : K → Finset I.Port
  sinks : K → Finset I.Sink
  ports_subset : ∀ k, ports k ⊆ P
  ports_pairwise_disjoint : ∀ k l, k ≠ l → Disjoint (ports k) (ports l)
  sinks_pairwise_disjoint : ∀ k l, k ≠ l → Disjoint (sinks k) (sinks l)
  ports_cover : (Finset.univ.biUnion ports) = P
  sinks_cover : (Finset.univ.biUnion sinks) = legalNbr I P
  sinks_eq_nbr : ∀ k, sinks k = legalNbr I (ports k)
  nonempty_ports : ∀ k, (ports k).Nonempty

attribute [instance] LegalComponentPartition.kDecEq LegalComponentPartition.kFintype

theorem loadQ_eq_sum_components (L : I.Port → ℚ) {P : Finset I.Port}
    (D : LegalComponentPartition I P) :
    loadQ I L P = ∑ k : D.K, loadQ I L (D.ports k) := by
  have hdisj : Set.PairwiseDisjoint (↑(Finset.univ : Finset D.K)) D.ports :=
    fun k _ l _ hkl => D.ports_pairwise_disjoint k l hkl
  unfold loadQ
  conv_lhs => rw [← D.ports_cover]
  exact Finset.sum_biUnion hdisj

theorem capQ_nbr_eq_sum_components {P : Finset I.Port} (D : LegalComponentPartition I P) :
    capQ I (legalNbr I P) = ∑ k : D.K, capQ I (D.sinks k) := by
  have hdisj : Set.PairwiseDisjoint (↑(Finset.univ : Finset D.K)) D.sinks :=
    fun k _ l _ hkl => D.sinks_pairwise_disjoint k l hkl
  unfold capQ
  conv_lhs => rw [← D.sinks_cover]
  exact Finset.sum_biUnion hdisj

/-- Deficiency is ADDITIVE over a legal-component partition (no bank capacity is double-counted: the sink
blocks are disjoint and each equals its component's legal neighborhood). -/
theorem deficiencyQ_eq_sum_components (L : I.Port → ℚ) {P : Finset I.Port}
    (D : LegalComponentPartition I P) :
    deficiencyQ I L P = ∑ k : D.K, deficiencyQ I L (D.ports k) := by
  unfold deficiencyQ
  rw [loadQ_eq_sum_components L D, capQ_nbr_eq_sum_components D, ← Finset.sum_sub_distrib]
  refine Finset.sum_congr rfl fun k _ => ?_
  rw [D.sinks_eq_nbr k]

/-- **The precise uncrossing theorem**: an inclusion-minimal Hall-deficient port set has exactly one
legal-incidence component. -/
theorem minimal_deficient_has_one_legal_component (L : I.Port → ℚ) {P : Finset I.Port}
    (hmin : InclusionMinimalDeficient I L P)
    (D : LegalComponentPartition I P) :
    Fintype.card D.K = 1 := by
  obtain ⟨hdef, hproper⟩ := hmin
  have hdef' : 0 < deficiencyQ I L P := hdef
  have hsum : deficiencyQ I L P = ∑ k : D.K, deficiencyQ I L (D.ports k) :=
    deficiencyQ_eq_sum_components L D
  have hex : ∃ k : D.K, 0 < deficiencyQ I L (D.ports k) := by
    by_contra h
    push_neg at h
    have hle : deficiencyQ I L P ≤ 0 := by
      rw [hsum]
      exact Finset.sum_nonpos fun k _ => h k
    exact absurd hdef' (not_lt.mpr hle)
  obtain ⟨k, hk⟩ := hex
  have huniq : ∀ l : D.K, l = k := by
    intro l
    by_contra hlk
    have hsub : D.ports k ⊆ P := D.ports_subset k
    obtain ⟨x, hx⟩ := D.nonempty_ports l
    have hxP : x ∈ P := D.ports_subset l hx
    have hxk : x ∉ D.ports k := by
      have hdisj := D.ports_pairwise_disjoint l k hlk
      exact fun hxk => (Finset.disjoint_left.mp hdisj hx) hxk
    have hss : D.ports k ⊂ P := (Finset.ssubset_iff_of_subset hsub).mpr ⟨x, hxP, hxk⟩
    exact absurd hk (not_lt.mpr (hproper (D.ports k) hss))
  exact Fintype.card_eq_one_iff.mpr ⟨k, huniq⟩

#print axioms deficiencyQ_supermodular
#print axioms deficiencyQ_union_of_disjoint_ports
#print axioms deficiencyQ_disjoint_neighbor_split
#print axioms minimal_deficient_has_one_legal_component

end PortHall
end Wall
end Erdos23Delta0
