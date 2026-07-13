import Erdos23Delta0.Ell5FullBankAssignedSink

/-!
# Bank-absorbed Hall obstruction for the layered family

This module is the abstract relaxed-cover matrix of the graph family (G_t).
It does not encode the ambient graph.  Its finite types record exactly:

* (t^2) bad-edge atoms (L_iR_j);
* (2t+2) shortest-support edges (L_i u,uw,wv,vR_j);
* (2t^2) terminal wide-channel ports;
* (2t+3) singleton cuts (L_i,R_j,u,w,v);
* (2t) endpoint vertex-slack sinks.

Every singleton cut has weight (1/2).  The (L_i)- and (R_j)-cuts
cover atom (L_iR_j); each support edge belongs to its two endpoint cuts;
and every terminal port has load (1/2), assigned to its terminal endpoint.
Each endpoint receives total load (t/2), below its graph-derived slack
capacity (2t+3=(7t+3)-5t).
-/

namespace Erdos23Delta0
namespace LayeredHallObstructionBankAbsorbed

open Finset
open Ell5FullBankInterface
open Ell5FullBankAssignedSink

abbrev Atom (t : Nat) := Fin t × Fin t
abbrev Short (t : Nat) := Fin t ⊕ (Fin 2 ⊕ Fin t)
abbrev Port (t : Nat) := (Fin t × Fin t) ⊕ (Fin t × Fin t)
abbrev Cut (t : Nat) := Fin t ⊕ (Fin t ⊕ Fin 3)
abbrev Sink (t : Nat) := Fin t ⊕ Fin t

inductive Edge (t : Nat) where
  | short : Short t → Edge t
  | port : Port t → Edge t
  deriving DecidableEq

@[simp] theorem card_atom (t : Nat) :
    Fintype.card (Atom t) = t * t := by
  simp [Atom]

@[simp] theorem card_short (t : Nat) :
    Fintype.card (Short t) = 2 * t + 2 := by
  simp [Short]
  omega

@[simp] theorem card_port (t : Nat) :
    Fintype.card (Port t) = 2 * t * t := by
  simp [Port]
  ring

@[simp] theorem card_cut (t : Nat) :
    Fintype.card (Cut t) = 2 * t + 3 := by
  simp [Cut]
  omega

@[simp] theorem card_sink (t : Nat) :
    Fintype.card (Sink t) = 2 * t := by
  simp [Sink]
  omega

def shortEmbedding {t : Nat} : Short t ↪ Edge t where
  toFun := Edge.short
  inj' := by
    intro a b h
    exact Edge.short.inj h

def portEmbedding {t : Nat} : Port t ↪ Edge t where
  toFun := Edge.port
  inj' := by
    intro a b h
    exact Edge.port.inj h

def rows (t : Nat) : Finset (Atom t) := Finset.univ
def support (t : Nat) : Finset (Edge t) := Finset.univ.map shortEmbedding
def outside (t : Nat) : Finset (Edge t) := Finset.univ.map portEmbedding
def sinks (t : Nat) : Finset (Sink t) := Finset.univ
def cuts (t : Nat) : Finset (Cut t) := Finset.univ

def leftCut {t : Nat} (i : Fin t) : Cut t := .inl i
def rightCut {t : Nat} (j : Fin t) : Cut t := .inr (.inl j)
def coreCut {t : Nat} (k : Fin 3) : Cut t := .inr (.inr k)

def coreLo (k : Fin 2) : Fin 3 := ⟨k.val, by omega⟩
def coreHi (k : Fin 2) : Fin 3 := ⟨k.val + 1, by omega⟩

def atomLeft {t : Nat} (a : Atom t) : Cut t := leftCut a.1
def atomRight {t : Nat} (a : Atom t) : Cut t := rightCut a.2

def shortLeft {t : Nat} : Short t → Cut t
  | .inl i => leftCut i
  | .inr (.inl k) => coreCut (coreLo k)
  | .inr (.inr _j) => coreCut 2

def shortRight {t : Nat} : Short t → Cut t
  | .inl _i => coreCut 0
  | .inr (.inl k) => coreCut (coreHi k)
  | .inr (.inr j) => rightCut j

def portInsideCut {t : Nat} : Port t → Cut t
  | .inl p => leftCut p.1
  | .inr p => rightCut p.1

def portInsideSink {t : Nat} : Port t → Sink t
  | .inl p => .inl p.1
  | .inr p => .inr p.1

def separated {t : Nat} (k : Cut t) : Finset (Atom t) :=
  rows t |>.filter fun a => k = atomLeft a ∨ k = atomRight a

def boundary {t : Nat} (k : Cut t) : Finset (Edge t) :=
  ((Finset.univ.filter fun f : Short t => k = shortLeft f ∨ k = shortRight f).map
      shortEmbedding) ∪
    ((Finset.univ.filter fun p : Port t => k = portInsideCut p).map portEmbedding)

def weight {t : Nat} (_k : Cut t) : ℚ := 1 / 2

def defaultFin {t : Nat} (ht : 0 < t) : Fin t := ⟨0, ht⟩

def assignedVertexSlack {t : Nat} (ht : 0 < t) : Edge t → Sink t
  | .short _ => .inl (defaultFin ht)
  | .port p => portInsideSink p

def legalVertexSlack {t : Nat} : Edge t → Sink t → Prop
  | .short _, _ => False
  | .port p, s => portInsideSink p = s

def vertexSlackCap (t : Nat) (_s : Sink t) : ℚ := 2 * t + 3

private theorem two_indicator_sum {α : Type*} [Fintype α] [DecidableEq α]
    (x y : α) (hne : x ≠ y) :
    (∑ k ∈ (Finset.univ : Finset α),
      if k = x ∨ k = y then (1 / 2 : ℚ) else 0) = 1 := by
  calc
    (∑ k ∈ (Finset.univ : Finset α),
        if k = x ∨ k = y then (1 / 2 : ℚ) else 0) =
        (∑ k ∈ (Finset.univ : Finset α), if k = x then (1 / 2 : ℚ) else 0) +
          ∑ k ∈ (Finset.univ : Finset α), if k = y then (1 / 2 : ℚ) else 0 := by
      rw [← Finset.sum_add_distrib]
      apply Finset.sum_congr rfl
      intro k _hk
      by_cases hkx : k = x
      · have hky : k ≠ y := by
          intro h
          exact hne (hkx.symm.trans h)
        simp [hkx, hne]
      · by_cases hky : k = y
        · simp [hky, Ne.symm hne]
        · simp [hkx, hky]
    _ = 1 := by norm_num

private theorem atom_ends_ne {t : Nat} (a : Atom t) :
    atomLeft a ≠ atomRight a := by
  simp [atomLeft, atomRight, leftCut, rightCut]

private theorem atom_coverage {t : Nat} (a : Atom t) :
    (∑ k ∈ cuts t, if a ∈ separated k then weight k else 0) = 1 := by
  simpa [cuts, separated, rows, weight] using
    two_indicator_sum (atomLeft a) (atomRight a) (atom_ends_ne a)

private theorem short_ends_ne {t : Nat} (f : Short t) :
    shortLeft f ≠ shortRight f := by
  rcases f with i | f
  · simp [shortLeft, shortRight, leftCut, coreCut]
  · rcases f with k | j
    · intro h
      have hv : k.val = k.val + 1 := by
        simpa [shortLeft, shortRight, coreCut, coreLo, coreHi] using h
      omega
    · simp [shortLeft, shortRight, coreCut, rightCut]

private theorem short_mem_boundary_iff {t : Nat} (k : Cut t) (f : Short t) :
    Edge.short f ∈ boundary k ↔ k = shortLeft f ∨ k = shortRight f := by
  simp [boundary, shortEmbedding, portEmbedding]

private theorem short_congestion {t : Nat} (f : Short t) :
    (∑ k ∈ cuts t, if Edge.short f ∈ boundary k then weight k else 0) = 1 := by
  simpa [cuts, short_mem_boundary_iff, weight] using
    two_indicator_sum (shortLeft f) (shortRight f) (short_ends_ne f)

private theorem port_mem_boundary_iff {t : Nat} (k : Cut t) (p : Port t) :
    Edge.port p ∈ boundary k ↔ k = portInsideCut p := by
  simp [boundary, shortEmbedding, portEmbedding]

private theorem port_load {t : Nat} (p : Port t) :
    (∑ k ∈ cuts t, if Edge.port p ∈ boundary k then weight k else 0) = 1 / 2 := by
  simp [cuts, port_mem_boundary_iff, weight]

@[simp] private theorem relaxed_load_port {t : Nat} (p : Port t) :
    RelaxedCutCover.load (cuts t) weight boundary (Edge.port p) = 1 / 2 :=
  port_load p

private theorem outside_eq_port {t : Nat} {e : Edge t} (he : e ∈ outside t) :
    ∃ p : Port t, e = Edge.port p := by
  obtain ⟨p, _hp, hpe⟩ := Finset.mem_map.mp he
  exact ⟨p, hpe.symm⟩

private theorem support_eq_short {t : Nat} {e : Edge t} (he : e ∈ support t) :
    ∃ f : Short t, e = Edge.short f := by
  obtain ⟨f, _hf, hfe⟩ := Finset.mem_map.mp he
  exact ⟨f, hfe.symm⟩

private theorem sink_count (t : Nat) (s : Sink t) :
    (∑ p : Port t, if portInsideSink p = s then (1 / 2 : ℚ) else 0) = (t : ℚ) / 2 := by
  have fiber_sum (i : Fin t) :
      (∑ x : Fin t, ∑ _y : Fin t, if x = i then (1 / 2 : ℚ) else 0) =
        (t : ℚ) / 2 := by
    classical
    calc
      (∑ x : Fin t, ∑ _y : Fin t, if x = i then (1 / 2 : ℚ) else 0) =
          ∑ x : Fin t, if x = i then (t : ℚ) / 2 else 0 := by
        apply Finset.sum_congr rfl
        intro x _hx
        by_cases h : x = i <;> simp [h, div_eq_mul_inv]
      _ = (t : ℚ) / 2 := by simp
  rcases s with i | i
  · simpa only [Port, portInsideSink, Fintype.sum_sum_type, Fintype.sum_prod_type,
      Sum.inl.injEq, Sum.inr.injEq, Sum.inr_ne_inl, Sum.inl_ne_inr, if_false,
      Finset.sum_const_zero, add_zero, zero_add] using fiber_sum i
  · simpa only [Port, portInsideSink, Fintype.sum_sum_type, Fintype.sum_prod_type,
      Sum.inl.injEq, Sum.inr.injEq, Sum.inr_ne_inl, Sum.inl_ne_inr, if_false,
      Finset.sum_const_zero, add_zero, zero_add] using fiber_sum i

theorem per_sink_load {t : Nat} (ht : 0 < t) (s : Sink t) :
    (∑ c ∈ outside t,
      assignedSinkQ (cuts t) weight boundary (assignedVertexSlack ht) c s) =
        (t : ℚ) / 2 := by
  calc
    (∑ c ∈ outside t,
      assignedSinkQ (cuts t) weight boundary (assignedVertexSlack ht) c s) =
        ∑ p : Port t,
          assignedSinkQ (cuts t) weight boundary (assignedVertexSlack ht)
            (Edge.port p) s := by
      simp [outside, portEmbedding]
    _ = ∑ p : Port t, if portInsideSink p = s then (1 / 2 : ℚ) else 0 := by
      apply Finset.sum_congr rfl
      intro p _hp
      by_cases h : portInsideSink p = s <;>
        simp [assignedSinkQ, assignedVertexSlack, h]
    _ = (t : ℚ) / 2 := sink_count t s

theorem per_sink_load_le_capacity {t : Nat} (ht : 0 < t) (s : Sink t) :
    (∑ c ∈ outside t,
      assignedSinkQ (cuts t) weight boundary (assignedVertexSlack ht) c s) ≤
        vertexSlackCap t s := by
  have htq : (0 : ℚ) ≤ (t : ℚ) := by positivity
  rw [per_sink_load ht s]
  norm_num [vertexSlackCap]
  linarith

/-- The exact bank-absorbed relaxed-cover certificate for every positive layer size. -/
noncomputable def certificate (t : Nat) (ht : 0 < t) :
    FullBankRelaxedCoverCert (rows t) (support t) (outside t) (sinks t) (cuts t)
      separated boundary legalVertexSlack (vertexSlackCap t) :=
  cert_of_assignedSink (rows t) (support t) (outside t) (sinks t) (cuts t)
    separated boundary legalVertexSlack (vertexSlackCap t) weight
    (assignedVertexSlack ht)
    (by intro k hk; norm_num [weight])
    (by intro s hs; simp [vertexSlackCap]; positivity)
    (by
      intro a ha
      rw [atom_coverage a])
    (by
      intro e he
      obtain ⟨f, rfl⟩ := support_eq_short he
      rw [short_congestion f])
    (by
      intro e he
      obtain ⟨p, rfl⟩ := outside_eq_port he
      simp [assignedVertexSlack, sinks])
    (by
      intro e he
      obtain ⟨p, rfl⟩ := outside_eq_port he
      simp [assignedVertexSlack, legalVertexSlack])
    (by
      intro s hs
      exact per_sink_load_le_capacity ht s)

/-- The bank-absorbed (G_t) fixture has no exact rational Farkas dual. -/
theorem no_dualCert (t : Nat) (ht : 0 < t) :
    ¬ ∃ alpha beta gam del,
      BankedCutDominationCore.IsDualCert
        (rows t) (support t) (outside t) (sinks t) (cuts t)
        separated boundary legalVertexSlack (vertexSlackCap t)
        alpha beta gam del :=
  no_dualCert_of_cert (rows t) (support t) (outside t) (sinks t) (cuts t)
    separated boundary legalVertexSlack (vertexSlackCap t) (certificate t ht)

end LayeredHallObstructionBankAbsorbed
end Erdos23Delta0


