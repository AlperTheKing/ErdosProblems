import Erdos23Delta0.Ell5SingletonVertexSlack

/-!
# Half-weight block cuts

Partition a geodesic core into blocks and put weight `1/2` on the cut given by
each block. A bad edge whose endpoints lie in different blocks is covered
exactly once. Every blue edge has congestion at most one, while a blue edge
inside one block has zero congestion. Thus taking blocks to be components of
the internal off-support blue graph removes all internal bank demand; only
core-boundary edges retain load `1/2`.
-/

namespace Erdos23Delta0
namespace Ell5BlockSingleton

open Finset MaxCutVertexIneq
open Ell5FullBankInterface Ell5FullBankAssignedSink
open Ell5SingletonVertexSlack

variable {V Block : Type*} [DecidableEq V] [Fintype Block] [DecidableEq Block]

def blockSet (C : Finset V) (block : V → Block) (b : Block) : Finset V :=
  C.filter fun x => block x = b

def blockWeight (_b : Block) : ℚ := 1 / 2

def BlocksApart (block : V → Block) (e : Sym2 V) : Prop :=
  ∀ u v, e = s(u, v) → block u ≠ block v

def SameBlock (block : V → Block) (e : Sym2 V) : Prop :=
  ∀ u v, e = s(u, v) → block u = block v

theorem mem_blockSet_iff (C : Finset V) (block : V → Block) (b : Block) (x : V) :
    x ∈ blockSet C block b ↔ x ∈ C ∧ block x = b := by
  simp [blockSet]

theorem half_block_boundary_sum_distinct
    (C : Finset V) (block : V → Block) {u v : V}
    (hu : u ∈ C) (hv : v ∈ C) (hblock : block u ≠ block v) :
    (∑ b : Block,
      if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0) = 1 := by
  have hpoint : ∀ b : Block,
      (if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0) =
        (if block u = b then (1 / 2 : ℚ) else 0) +
          (if block v = b then (1 / 2 : ℚ) else 0) := by
    intro b
    by_cases hub : block u = b
    · have hvb : block v ≠ b := fun h => hblock (hub.trans h.symm)
      simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, blockSet, hu, hv, hub, hvb]
    · by_cases hvb : block v = b
      · simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, blockSet, hu, hv, hub, hvb]
      · simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, blockSet, hu, hv, hub, hvb]
  calc
    (∑ b : Block,
        if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0) =
        (∑ b : Block, if block u = b then (1 / 2 : ℚ) else 0) +
          ∑ b : Block, if block v = b then (1 / 2 : ℚ) else 0 := by
            rw [← Finset.sum_add_distrib]
            exact Finset.sum_congr rfl fun b _ => hpoint b
    _ = 1 := by norm_num

theorem half_block_boundary_sum_same
    (C : Finset V) (block : V → Block) {u v : V}
    (hu : u ∈ C) (hv : v ∈ C) (hblock : block u = block v) :
    (∑ b : Block,
      if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0) = 0 := by
  apply Finset.sum_eq_zero
  intro b hb
  by_cases hub : block u = b
  · have hvb : block v = b := hblock.symm.trans hub
    simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, blockSet, hu, hv, hub, hvb]
  · have hvb : block v ≠ b := fun h => hub (hblock.trans h)
    simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, blockSet, hu, hv, hub, hvb]

theorem half_block_boundary_sum_boundary
    (C : Finset V) (block : V → Block) {u v : V}
    (hu : u ∈ C) (hv : v ∉ C) :
    (∑ b : Block,
      if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0) = 1 / 2 := by
  have hpoint : ∀ b : Block,
      (if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0) =
        if block u = b then (1 / 2 : ℚ) else 0 := by
    intro b
    by_cases hub : block u = b <;>
      simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, blockSet, hu, hv, hub]
  calc
    (∑ b : Block,
        if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0) =
        ∑ b : Block, if block u = b then (1 / 2 : ℚ) else 0 :=
          Finset.sum_congr rfl fun b _ => hpoint b
    _ = 1 / 2 := by simp

theorem half_block_boundary_sum_le_one
    (C : Finset V) (block : V → Block) {u v : V} (hne : u ≠ v) :
    (∑ b : Block,
      if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0) ≤ 1 := by
  by_cases hu : u ∈ C
  · by_cases hv : v ∈ C
    · by_cases hblock : block u = block v
      · rw [half_block_boundary_sum_same C block hu hv hblock]
        norm_num
      · rw [half_block_boundary_sum_distinct C block hu hv hblock]
    · rw [half_block_boundary_sum_boundary C block hu hv]
      norm_num
  · by_cases hv : v ∈ C
    · rw [Sym2.eq_swap]
      rw [half_block_boundary_sum_boundary C block hv hu]
      norm_num
    · simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, blockSet, hu, hv]

theorem edgeBoundary_false_of_mem_sym2 (C : Finset V) {e : Sym2 V}
    (hcore : e ∈ C.sym2) : edgeBoundary C e = false := by
  revert hcore
  refine Sym2.inductionOn e ?_
  intro u v hcore
  rw [Finset.mk_mem_sym2_iff] at hcore
  simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, hcore.1, hcore.2]

section Graph

variable (G : SimpleGraph V) [Fintype G.edgeSet]

def blockLoad (s : V → Bool) (C : Finset V) (block : V → Block)
    (e : Sym2 V) : ℚ :=
  RelaxedCutCover.load Finset.univ blockWeight
    (fun b => deltaB G s (blockSet C block b)) e

def blockDoorQ (s : V → Bool) (C : Finset V) (block : V → Block)
    (c j : Sym2 V) : ℚ :=
  if edgeBoundary C c = true then
    if c = j then blockLoad G s C block c else 0
  else 0

theorem bad_mem_deltaM_iff (s : V → Bool) (U : Finset V) {u v : V}
    (hadj : G.Adj u v) (hmono : s u = s v) :
    s(u, v) ∈ deltaM G s U ↔ edgeBoundary U s(u, v) = true := by
  have hcut : edgeCut s s(u, v) = false := by
    simp [edgeCut, edgeBool, Sym2.lift_mk, hmono]
  have hedge : s(u, v) ∈ G.edgeFinset := by
    rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet]
    exact hadj
  simp [deltaM, hedge, hcut]

theorem cut_mem_deltaB_iff (s : V → Bool) (U : Finset V) {u v : V}
    (hadj : G.Adj u v) (hcutuv : s u ≠ s v) :
    s(u, v) ∈ deltaB G s U ↔ edgeBoundary U s(u, v) = true := by
  have hcut : edgeCut s s(u, v) = true := by
    simp [edgeCut, edgeBool, Sym2.lift_mk, hcutuv]
  have hedge : s(u, v) ∈ G.edgeFinset := by
    rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet]
    exact hadj
  simp [deltaB, hedge, hcut]

theorem block_bad_coverage_mk
    (s : V → Bool) (C : Finset V) (block : V → Block) {u v : V}
    (hadj : G.Adj u v) (hmono : s u = s v)
    (hu : u ∈ C) (hv : v ∈ C) (hblock : block u ≠ block v) :
    (∑ b : Block,
      if s(u, v) ∈ deltaM G s (blockSet C block b) then blockWeight b else 0) = 1 := by
  calc
    (∑ b : Block,
        if s(u, v) ∈ deltaM G s (blockSet C block b) then blockWeight b else 0) =
        ∑ b : Block,
          if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0 := by
            apply Finset.sum_congr rfl
            intro b hb
            have hiff := bad_mem_deltaM_iff G s (blockSet C block b) hadj hmono
            by_cases hm : s(u, v) ∈ deltaM G s (blockSet C block b)
            · have hboundary := hiff.mp hm
              simp [blockWeight, hm, hboundary]
            · have hboundary : edgeBoundary (blockSet C block b) s(u, v) ≠ true :=
                fun h => hm (hiff.mpr h)
              simp [blockWeight, hm, hboundary]
    _ = 1 := half_block_boundary_sum_distinct C block hu hv hblock

theorem block_cut_load_le_one_mk
    (s : V → Bool) (C : Finset V) (block : V → Block) {u v : V}
    (hadj : G.Adj u v) (hcutuv : s u ≠ s v) :
    (∑ b : Block,
      if s(u, v) ∈ deltaB G s (blockSet C block b) then blockWeight b else 0) ≤ 1 := by
  calc
    (∑ b : Block,
        if s(u, v) ∈ deltaB G s (blockSet C block b) then blockWeight b else 0) =
        ∑ b : Block,
          if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0 := by
            apply Finset.sum_congr rfl
            intro b hb
            have hiff := cut_mem_deltaB_iff G s (blockSet C block b) hadj hcutuv
            by_cases hm : s(u, v) ∈ deltaB G s (blockSet C block b)
            · have hboundary := hiff.mp hm
              simp [blockWeight, hm, hboundary]
            · have hboundary : edgeBoundary (blockSet C block b) s(u, v) ≠ true :=
                fun h => hm (hiff.mpr h)
              simp [blockWeight, hm, hboundary]
    _ ≤ 1 := half_block_boundary_sum_le_one C block (G.ne_of_adj hadj)

theorem block_cut_load_same_mk
    (s : V → Bool) (C : Finset V) (block : V → Block) {u v : V}
    (hadj : G.Adj u v) (hcutuv : s u ≠ s v)
    (hu : u ∈ C) (hv : v ∈ C) (hblock : block u = block v) :
    (∑ b : Block,
      if s(u, v) ∈ deltaB G s (blockSet C block b) then blockWeight b else 0) = 0 := by
  calc
    (∑ b : Block,
        if s(u, v) ∈ deltaB G s (blockSet C block b) then blockWeight b else 0) =
        ∑ b : Block,
          if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0 := by
            apply Finset.sum_congr rfl
            intro b hb
            have hiff := cut_mem_deltaB_iff G s (blockSet C block b) hadj hcutuv
            by_cases hm : s(u, v) ∈ deltaB G s (blockSet C block b)
            · have hboundary := hiff.mp hm
              simp [blockWeight, hm, hboundary]
            · have hboundary : edgeBoundary (blockSet C block b) s(u, v) ≠ true :=
                fun h => hm (hiff.mpr h)
              simp [blockWeight, hm, hboundary]
    _ = 0 := half_block_boundary_sum_same C block hu hv hblock

theorem block_cut_load_boundary_mk
    (s : V → Bool) (C : Finset V) (block : V → Block) {u v : V}
    (hadj : G.Adj u v) (hcutuv : s u ≠ s v)
    (hu : u ∈ C) (hv : v ∉ C) :
    (∑ b : Block,
      if s(u, v) ∈ deltaB G s (blockSet C block b) then blockWeight b else 0) = 1 / 2 := by
  calc
    (∑ b : Block,
        if s(u, v) ∈ deltaB G s (blockSet C block b) then blockWeight b else 0) =
        ∑ b : Block,
          if edgeBoundary (blockSet C block b) s(u, v) = true then (1 / 2 : ℚ) else 0 := by
            apply Finset.sum_congr rfl
            intro b hb
            have hiff := cut_mem_deltaB_iff G s (blockSet C block b) hadj hcutuv
            by_cases hm : s(u, v) ∈ deltaB G s (blockSet C block b)
            · have hboundary := hiff.mp hm
              simp [blockWeight, hm, hboundary]
            · have hboundary : edgeBoundary (blockSet C block b) s(u, v) ≠ true :=
                fun h => hm (hiff.mpr h)
              simp [blockWeight, hm, hboundary]
    _ = 1 / 2 := half_block_boundary_sum_boundary C block hu hv

theorem block_bad_coverage
    (s : V → Bool) (C : Finset V) (block : V → Block) {e : Sym2 V}
    (heG : e ∈ G.edgeFinset) (hbad : edgeCut s e = false)
    (hcore : e ∈ C.sym2) (hapart : BlocksApart block e) :
    (∑ b : Block,
      if e ∈ deltaM G s (blockSet C block b) then blockWeight b else 0) = 1 := by
  revert heG hbad hcore hapart
  refine Sym2.inductionOn e ?_
  intro u v heG hbad hcore hapart
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at heG
  rw [Finset.mk_mem_sym2_iff] at hcore
  have hmono : s u = s v := by
    simpa [edgeCut, edgeBool, Sym2.lift_mk] using hbad
  exact block_bad_coverage_mk G s C block heG hmono hcore.1 hcore.2
    (hapart u v rfl)

theorem block_cut_load_le_one
    (s : V → Bool) (C : Finset V) (block : V → Block) {e : Sym2 V}
    (heG : e ∈ G.edgeFinset) (hcut : edgeCut s e = true) :
    (∑ b : Block,
      if e ∈ deltaB G s (blockSet C block b) then blockWeight b else 0) ≤ 1 := by
  revert heG hcut
  refine Sym2.inductionOn e ?_
  intro u v heG hcut
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at heG
  have hcutuv : s u ≠ s v := by
    simpa [edgeCut, edgeBool, Sym2.lift_mk] using hcut
  exact block_cut_load_le_one_mk G s C block heG hcutuv

theorem block_cut_load_same
    (s : V → Bool) (C : Finset V) (block : V → Block) {e : Sym2 V}
    (heG : e ∈ G.edgeFinset) (hcut : edgeCut s e = true)
    (hcore : e ∈ C.sym2) (hsame : SameBlock block e) :
    (∑ b : Block,
      if e ∈ deltaB G s (blockSet C block b) then blockWeight b else 0) = 0 := by
  revert heG hcut hcore hsame
  refine Sym2.inductionOn e ?_
  intro u v heG hcut hcore hsame
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at heG
  rw [Finset.mk_mem_sym2_iff] at hcore
  have hcutuv : s u ≠ s v := by
    simpa [edgeCut, edgeBool, Sym2.lift_mk] using hcut
  exact block_cut_load_same_mk G s C block heG hcutuv hcore.1 hcore.2
    (hsame u v rfl)

theorem block_cut_load_boundary
    (s : V → Bool) (C : Finset V) (block : V → Block) {e : Sym2 V}
    (heG : e ∈ G.edgeFinset) (hcut : edgeCut s e = true)
    (hboundary : edgeBoundary C e = true) :
    (∑ b : Block,
      if e ∈ deltaB G s (blockSet C block b) then blockWeight b else 0) = 1 / 2 := by
  revert heG hcut hboundary
  refine Sym2.inductionOn e ?_
  intro u v heG hcut hboundary
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at heG
  have hcutuv : s u ≠ s v := by
    simpa [edgeCut, edgeBool, Sym2.lift_mk] using hcut
  by_cases hu : u ∈ C
  · by_cases hv : v ∈ C
    · simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, hu, hv] at hboundary
    · exact block_cut_load_boundary_mk G s C block heG hcutuv hu hv
  · by_cases hv : v ∈ C
    · rw [Sym2.eq_swap]
      exact block_cut_load_boundary_mk G s C block heG.symm (Ne.symm hcutuv) hv hu
    · simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, hu, hv] at hboundary

/-- Component-block singleton cover. When internal off-support blue edges stay
inside blocks and every selected bad edge joins two blocks, internal demand is
zero. Only core-boundary edges use their individual Door sink. -/
noncomputable def certificate_of_blockSingleton_boundaryDoors
    (s : V → Bool) (C : Finset V) (block : V → Block)
    (S F O : Finset (Sym2 V))
    (inc : Sym2 V → Sym2 V → Prop) (kap : Sym2 V → ℚ)
    (hkap : ∀ e ∈ O, 0 ≤ kap e)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2 ∧ BlocksApart block e)
    (hF : ∀ e ∈ F, e ∈ G.edgeFinset ∧ edgeCut s e = true)
    (hO : ∀ e ∈ O,
      e ∈ G.edgeFinset ∧ edgeCut s e = true ∧
        (edgeBoundary C e = true ∨ (e ∈ C.sym2 ∧ SameBlock block e)))
    (hinc : ∀ e ∈ O, edgeBoundary C e = true → inc e e)
    (hdoor : ∀ e ∈ O, edgeBoundary C e = true → (1 / 2 : ℚ) ≤ kap e) :
    FullBankRelaxedCoverCert S F O O Finset.univ
      (fun b => deltaM G s (blockSet C block b))
      (fun b => deltaB G s (blockSet C block b)) inc kap where
  lam := blockWeight
  q := blockDoorQ G s C block
  hlam := by intro b hb; norm_num [blockWeight]
  hq := by
    intro c hc j hj
    by_cases hboundary : edgeBoundary C c = true
    · by_cases hcj : c = j
      · subst j
        simpa [blockDoorQ, hboundary, blockLoad] using
          load_nonneg Finset.univ blockWeight
            (fun b => deltaB G s (blockSet C block b))
            (by intro b hb; norm_num [blockWeight]) c
      · simp [blockDoorQ, hboundary, hcj]
    · simp [blockDoorQ, hboundary]
  hkap := hkap
  hcov := by
    intro e he
    obtain ⟨heG, hbad, hcore, hapart⟩ := hS e he
    exact le_of_eq (block_bad_coverage G s C block heG hbad hcore hapart).symm
  hcong := by
    intro e he
    obtain ⟨heG, hcut⟩ := hF e he
    exact block_cut_load_le_one G s C block heG hcut
  hroute := by
    intro e he
    obtain ⟨heG, hcut, hclass⟩ := hO e he
    change blockLoad G s C block e ≤
      ∑ j ∈ O, blockDoorQ G s C block e j
    rcases hclass with hboundary | ⟨hcore, hsame⟩
    · have hsum :
          (∑ j ∈ O, blockDoorQ G s C block e j) = blockLoad G s C block e := by
            rw [Finset.sum_eq_single e]
            · simp [blockDoorQ, hboundary]
            · intro j hj hne
              have henj : e ≠ j := Ne.symm hne
              simp [blockDoorQ, hboundary, henj]
            · intro hnot
              exact False.elim (hnot he)
      rw [hsum]
    · have hboundary : edgeBoundary C e ≠ true := by
        rw [edgeBoundary_false_of_mem_sym2 C hcore]
        decide
      have hload : blockLoad G s C block e = 0 := by
        exact block_cut_load_same G s C block heG hcut hcore hsame
      rw [hload]
      simp [blockDoorQ, hboundary]
  hcap := by
    intro j hj
    by_cases hboundary : edgeBoundary C j = true
    · have hjdata := hO j hj
      calc
        (∑ c ∈ O, blockDoorQ G s C block c j) = blockLoad G s C block j := by
          rw [Finset.sum_eq_single j]
          · simp [blockDoorQ, hboundary]
          · intro c hc hne
            simp [blockDoorQ, hne]
          · intro hnot
            exact False.elim (hnot hj)
        _ = 1 / 2 := block_cut_load_boundary G s C block hjdata.1 hjdata.2.1 hboundary
        _ ≤ kap j := hdoor j hj hboundary
    · have hnonneg := hkap j hj
      calc
        (∑ c ∈ O, blockDoorQ G s C block c j) = 0 := by
          rw [Finset.sum_eq_single j]
          · simp [blockDoorQ, hboundary]
          · intro c hc hne
            simp [blockDoorQ, hne]
          · intro hnot
            exact False.elim (hnot hj)
        _ ≤ kap j := hnonneg
  hqinc := by
    intro c hc j hj hpos
    by_cases hboundary : edgeBoundary C c = true
    · by_cases hcj : c = j
      · simpa [hcj] using hinc c hc hboundary
      · simp [blockDoorQ, hboundary, hcj] at hpos
    · simp [blockDoorQ, hboundary] at hpos

end Graph

end Ell5BlockSingleton
end Erdos23Delta0
