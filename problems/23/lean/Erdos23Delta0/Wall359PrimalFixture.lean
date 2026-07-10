import Erdos23Delta0.Ell5FullBankAssignedSink

/-!
# Vertex-slack primal for the 359-vertex double-star regression fixture

This module checks the finite relaxed-cover matrix extracted by
`_codex_wall_r5_359_gate.py`.  It deliberately does not re-encode the 359
vertex graph: the exact Python gate verifies that graph-to-matrix extraction.

The matrix has nine K3,3 rows, eight double-star support edges, 140 external
ports, and nine singleton cuts.  Giving every singleton cut weight `1/2`
covers every row exactly once, saturates every support edge, and loads every
external port by `1/2`.  Each port is assigned to the vertex-slack sink at its
inside endpoint.  Every such sink has at least `359 - 45 = 314` capacity,
whereas the total load of all 140 ports is only 70.
-/

namespace Erdos23Delta0
namespace Wall359PrimalFixture

open Finset
open Ell5FullBankInterface
open Ell5FullBankAssignedSink

abbrev Atom := Fin 9
abbrev Short := Fin 8
abbrev Port := Fin 140
abbrev Cut := Fin 9
abbrev Sink := Fin 9

inductive Edge where
  | short : Short → Edge
  | port : Port → Edge
  deriving DecidableEq

def shortEmbedding : Short ↪ Edge where
  toFun := Edge.short
  inj' := by
    intro a b h
    exact Edge.short.inj h

def portEmbedding : Port ↪ Edge where
  toFun := Edge.port
  inj' := by
    intro a b h
    exact Edge.port.inj h

def rows : Finset Atom := Finset.univ
def support : Finset Edge := Finset.univ.map shortEmbedding
def outside : Finset Edge := Finset.univ.map portEmbedding
def sinks : Finset Sink := Finset.univ
def cuts : Finset Cut := Finset.univ

def atomLeft : Atom → Cut := ![0, 0, 0, 1, 1, 1, 2, 2, 2]
def atomRight : Atom → Cut := ![4, 5, 6, 4, 5, 6, 4, 5, 6]

def shortLeft : Short → Cut := ![0, 1, 2, 7, 3, 8, 8, 8]
def shortRight : Short → Cut := ![7, 7, 7, 3, 8, 4, 5, 6]

def portInside (p : Port) : Cut :=
  if p.val < 10 then 0
  else if p.val < 20 then 1
  else if p.val < 30 then 2
  else if p.val < 90 then 3
  else if p.val < 100 then 4
  else if p.val < 110 then 5
  else if p.val < 120 then 6
  else if p.val < 130 then 7
  else 8

def separated (k : Cut) : Finset Atom :=
  rows.filter fun a => k = atomLeft a ∨ k = atomRight a

def boundary (k : Cut) : Finset Edge :=
  ((Finset.univ.filter fun f : Short => k = shortLeft f ∨ k = shortRight f).map
      shortEmbedding) ∪
    ((Finset.univ.filter fun p : Port => k = portInside p).map portEmbedding)

def weight (_k : Cut) : ℚ := 1 / 2

def assignedVertexSlack : Edge → Sink
  | .short _ => 0
  | .port p => portInside p

def legalVertexSlack : Edge → Sink → Prop
  | .short _, _ => False
  | .port p, s => portInside p = s

def vertexSlackCap (_s : Sink) : ℚ := 314

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

private theorem atom_ends_ne (a : Atom) : atomLeft a ≠ atomRight a := by
  fin_cases a <;> decide

private theorem atom_coverage (a : Atom) :
    (∑ k ∈ cuts, if a ∈ separated k then weight k else 0) = 1 := by
  simpa [cuts, separated, rows, weight] using
    two_indicator_sum (atomLeft a) (atomRight a) (atom_ends_ne a)

private theorem short_mem_boundary_iff (k : Cut) (f : Short) :
    Edge.short f ∈ boundary k ↔ k = shortLeft f ∨ k = shortRight f := by
  simp [boundary, shortEmbedding, portEmbedding]

private theorem short_congestion (f : Short) :
    (∑ k ∈ cuts, if Edge.short f ∈ boundary k then weight k else 0) = 1 := by
  have hne : shortLeft f ≠ shortRight f := by
    fin_cases f <;> decide
  simpa [cuts, short_mem_boundary_iff, weight] using
    two_indicator_sum (shortLeft f) (shortRight f) hne

private theorem port_mem_boundary_iff (k : Cut) (p : Port) :
    Edge.port p ∈ boundary k ↔ k = portInside p := by
  simp [boundary, shortEmbedding, portEmbedding]

private theorem port_load (p : Port) :
    (∑ k ∈ cuts, if Edge.port p ∈ boundary k then weight k else 0) = 1 / 2 := by
  simp [cuts, port_mem_boundary_iff, weight]

@[simp] private theorem relaxed_load_port (p : Port) :
    RelaxedCutCover.load cuts weight boundary (Edge.port p) = 1 / 2 := by
  exact port_load p

private theorem outside_eq_port {e : Edge} (he : e ∈ outside) :
    ∃ p : Port, e = Edge.port p := by
  obtain ⟨p, _hp, hpe⟩ := Finset.mem_map.mp he
  exact ⟨p, hpe.symm⟩

private theorem support_eq_short {e : Edge} (he : e ∈ support) :
    ∃ f : Short, e = Edge.short f := by
  obtain ⟨f, _hf, hfe⟩ := Finset.mem_map.mp he
  exact ⟨f, hfe.symm⟩

/-- The exact vertex-slack relaxed-cover certificate for the finite fixture. -/
noncomputable def certificate :
    FullBankRelaxedCoverCert rows support outside sinks cuts
      separated boundary legalVertexSlack vertexSlackCap :=
  cert_of_assignedSink rows support outside sinks cuts
    separated boundary legalVertexSlack vertexSlackCap weight assignedVertexSlack
    (by intro k hk; norm_num [weight])
    (by intro s hs; norm_num [vertexSlackCap])
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
      calc
        (∑ c ∈ outside,
            assignedSinkQ cuts weight boundary assignedVertexSlack c s) ≤
            ∑ _c ∈ outside, (1 / 2 : ℚ) := by
          apply Finset.sum_le_sum
          intro e he
          obtain ⟨p, rfl⟩ := outside_eq_port he
          by_cases h : portInside p = s <;>
            simp [assignedSinkQ, assignedVertexSlack, h]
        _ = 70 := by norm_num [outside, portEmbedding]
        _ ≤ vertexSlackCap s := by norm_num [vertexSlackCap])

/-- Consequently the fixture has no exact rational Farkas dual. -/
theorem no_dualCert :
    ¬ ∃ alpha beta gam del,
      BankedCutDominationCore.IsDualCert rows support outside sinks cuts
        separated boundary legalVertexSlack vertexSlackCap alpha beta gam del :=
  no_dualCert_of_cert rows support outside sinks cuts separated boundary
    legalVertexSlack vertexSlackCap certificate

end Wall359PrimalFixture
end Erdos23Delta0
