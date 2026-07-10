import Erdos23Delta0.Ell5SingletonVertexSlack

/-!
# Endpoint-half relaxed cut covers

The universal half-singleton family uses every vertex of `C` as a cut, with
weight `1 / 2`.  It covers every bad edge internal to `C` exactly once and
places load at most one on every cut edge.

`EndpointHalfBoundaryPartition` records only an exact finite classification
of the resulting off-support boundary contributions.  It contains no Door or
graph-existence assertion.
-/

namespace Erdos23Delta0
namespace EndpointHalfRelaxedCutCover

open Finset MaxCutVertexIneq
open RelaxedCutCover RelaxedCoverGraphBridge
open Ell5SingletonVertexSlack

variable {V : Type*} [DecidableEq V]

section Graph

variable (G : SimpleGraph V) [Fintype G.edgeSet]

/-- The half-singleton family, in the argument order expected by
`graph_defect_bound`.  Row coverage is retained as an equality. -/
theorem endpointHalf_is_relaxedCutCover
    (s : V → Bool) (C : Finset V) (S F : Finset (Sym2 V))
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2)
    (hF : F ⊆ cutEdges G s) :
    (∀ x ∈ C, 0 ≤ halfWeight x) ∧
      (∀ e ∈ S,
        (∑ x ∈ C,
          if e ∈ deltaM G s ({x} : Finset V) then halfWeight x else 0) = 1) ∧
      (∀ c ∈ F,
        (∑ x ∈ C,
          if c ∈ deltaB G s ({x} : Finset V) then halfWeight x else 0) ≤ 1) := by
  refine ⟨?_, ?_, ?_⟩
  · intro x hx
    norm_num [halfWeight]
  · intro e he
    obtain ⟨heG, hbad, hcore⟩ := hS e he
    simpa [halfWeight] using singleton_bad_coverage G s C heG hbad hcore
  · intro c hc
    have hcdata : c ∈ G.edgeFinset ∧ edgeCut s c = true := by
      simpa [cutEdges] using hF hc
    simpa [RelaxedCutCover.load] using
      singleton_cut_load_le_one G s C hcdata.1 hcdata.2

/-- An exact finite partition of all endpoint-half contributions on
`cutEdges G s \ F`.  The total function `port` assigns each contribution to
one concrete port, and `aggregate_eq` states that a port load is exactly the
sum of its assigned contributions. -/
structure EndpointHalfBoundaryPartition
    (s : V → Bool) (C : Finset V) (F : Finset (Sym2 V))
    (Port : Type*) [Fintype Port] [DecidableEq Port] where
  port : Sym2 V → V → Port
  portLoad : Port → ℚ
  aggregate_eq : ∀ p,
    portLoad p =
      ∑ c ∈ cutEdges G s \ F, ∑ x ∈ C,
        if c ∈ deltaB G s ({x} : Finset V) then
          if port c x = p then halfWeight x else 0
        else 0

/-- Summing the exact per-port aggregation neither loses nor duplicates any
off-support endpoint-half contribution. -/
theorem EndpointHalfBoundaryPartition.total_portLoad_eq
    {s : V → Bool} {C : Finset V} {F : Finset (Sym2 V)}
    {Port : Type*} [Fintype Port] [DecidableEq Port]
    (P : EndpointHalfBoundaryPartition G s C F Port) :
    (∑ p : Port, P.portLoad p) =
      ∑ c ∈ cutEdges G s \ F,
        load C halfWeight (fun x => deltaB G s ({x} : Finset V)) c := by
  calc
    (∑ p : Port, P.portLoad p) =
        ∑ p : Port, ∑ c ∈ cutEdges G s \ F, ∑ x ∈ C,
          if c ∈ deltaB G s ({x} : Finset V) then
            if P.port c x = p then halfWeight x else 0
          else 0 := by
            apply Finset.sum_congr rfl
            intro p hp
            exact P.aggregate_eq p
    _ = ∑ c ∈ cutEdges G s \ F, ∑ p : Port, ∑ x ∈ C,
          if c ∈ deltaB G s ({x} : Finset V) then
            if P.port c x = p then halfWeight x else 0
          else 0 := by
            rw [Finset.sum_comm]
    _ = ∑ c ∈ cutEdges G s \ F, ∑ x ∈ C, ∑ p : Port,
          if c ∈ deltaB G s ({x} : Finset V) then
            if P.port c x = p then halfWeight x else 0
          else 0 := by
            apply Finset.sum_congr rfl
            intro c hc
            rw [Finset.sum_comm]
    _ = ∑ c ∈ cutEdges G s \ F, ∑ x ∈ C,
          if c ∈ deltaB G s ({x} : Finset V) then halfWeight x else 0 := by
            apply Finset.sum_congr rfl
            intro c hc
            apply Finset.sum_congr rfl
            intro x hx
            by_cases hcx : c ∈ deltaB G s ({x} : Finset V)
            · simp [hcx]
            · simp [hcx]
    _ = ∑ c ∈ cutEdges G s \ F,
          load C halfWeight (fun x => deltaB G s ({x} : Finset V)) c := rfl

/-- A defect-one row family forces at least one unit of concrete port load.
The only port-side input is the exact boundary partition above. -/
theorem endpointHalf_offSupportLoad_ge_one
    [Fintype V]
    {Port : Type*} [Fintype Port] [DecidableEq Port]
    (s : V → Bool) (hmax : IsMaxCut G s)
    (C : Finset V) (S F : Finset (Sym2 V))
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2)
    (hF : F ⊆ cutEdges G s)
    (hdefect : S.card = F.card + 1)
    (P : EndpointHalfBoundaryPartition G s C F Port) :
    (1 : ℚ) ≤ ∑ p : Port, P.portLoad p := by
  obtain ⟨hlam, hcoverage, hcongestion⟩ :=
    endpointHalf_is_relaxedCutCover G s C S F hS hF
  have hbound := graph_defect_bound G s hmax S F hF C
    (fun x => ({x} : Finset V)) halfWeight hlam
    (fun e he => le_of_eq (hcoverage e he).symm) hcongestion
  have hcard : (S.card : ℚ) = (F.card : ℚ) + 1 := by
    exact_mod_cast hdefect
  rw [P.total_portLoad_eq]
  linarith

end Graph


end EndpointHalfRelaxedCutCover
end Erdos23Delta0
