import Erdos23Delta0.ODLFull

/-!
# Chunk-friendly cone evaluation bridge for generated O14 payloads

`PolyCert.ConeCert` is the canonical proof object for polynomial cone leaves,
but the generated O14 chart payloads can be too large for a single monolithic
`checkEq target (comboNF base mults slacks) = true` proof by definitional
reduction.  This module supplies a small value-level bridge:

* check many small NF equalities with `checkEqPairs`;
* combine them into an evaluated equality of flattened chunks;
* use the same nonnegative-base/nonnegative-multiplier argument as
  `ConeCert.sound`;
* finish with `ODLFull.CoreODLGoal_of_defect_nonneg`.

The final generated modules may still build a `ConeCert` when cheap; this bridge
is the escape hatch for chunked chart payloads.
-/

namespace Erdos23Delta0
namespace O14
namespace ConeEvalBridge

open PolyCert
open ODLFull

/-- Boolean checker for a list of chunk equalities. -/
def checkEqPairs : List (NF × NF) → Bool
  | [] => true
  | p :: ps => checkEq p.1 p.2 && checkEqPairs ps

/-- Evaluation of a flattened list of NF chunks is the sum of chunk evaluations. -/
theorem NF_eval_flatten_chunks (env : Var → ℚ) :
    ∀ chunks : List NF,
      NF.eval env chunks.flatten = (chunks.map (fun f => NF.eval env f)).sum
  | [] => by
      simp [NF.eval]
  | c :: cs => by
      simp only [List.flatten_cons, List.map_cons, List.sum_cons]
      rw [NF.eval_append, NF_eval_flatten_chunks env cs]

/-- Soundness for chunk equality pairs, at the value level. -/
theorem eval_sum_eq_of_checkEqPairs (pairs : List (NF × NF))
    (h : checkEqPairs pairs = true) (env : Var → ℚ) :
    (pairs.map (fun p => NF.eval env p.1)).sum =
      (pairs.map (fun p => NF.eval env p.2)).sum := by
  induction pairs with
  | nil =>
      simp
  | cons p ps ih =>
      simp [checkEqPairs] at h
      have hp : NF.eval env p.1 = NF.eval env p.2 :=
        checkEq_sound p.1 p.2 h.1 env
      have hps := ih h.2
      simp [hp, hps]

/-- Flattened left/right chunk lists have equal evaluation when each pair checks. -/
theorem eval_flatten_fst_eq_snd_of_checkEqPairs (pairs : List (NF × NF))
    (h : checkEqPairs pairs = true) (env : Var → ℚ) :
    NF.eval env ((pairs.map Prod.fst).flatten) =
      NF.eval env ((pairs.map Prod.snd).flatten) := by
  rw [NF_eval_flatten_chunks, NF_eval_flatten_chunks]
  simpa using eval_sum_eq_of_checkEqPairs pairs h env

/-- Value-level cone nonnegativity.  This is `ConeCert.sound` with the Boolean
identity replaced by an evaluated identity, so generated chunks can provide the
identity without one giant `checkEq`. -/
theorem cone_eval_nonneg_of_eval_combo
    (target base : NF) (mults slacks : List NF) (env : Var → ℚ)
    (hvars : ∀ v, 0 ≤ env v)
    (hbase : base.allCoeffNonneg = true)
    (hmults : mults.all NF.allCoeffNonneg = true)
    (hslacks : ∀ s ∈ slacks, 0 ≤ NF.eval env s)
    (hidEval : NF.eval env target = NF.eval env (comboNF base mults slacks)) :
    0 ≤ NF.eval env target := by
  rw [hidEval]
  unfold comboNF
  rw [NF.eval_append, zip_nfmul_flatten_eval]
  have hbaseEval := NF.eval_nonneg env base hvars hbase
  have hzip := zip_nfmul_sum_nonneg env hvars mults slacks hmults hslacks
  linarith

/-- ODL core goal from a value-level cone identity. -/
theorem coreODLGoal_of_coneEval
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    (core : ODLCoreData G c rows Q)
    (target base : NF) (mults slacks : List NF) (env : Var → ℚ)
    (hvars : ∀ v, 0 ≤ env v)
    (hbase : base.allCoeffNonneg = true)
    (hmults : mults.all NF.allCoeffNonneg = true)
    (hslacks : ∀ s ∈ slacks, 0 ≤ NF.eval env s)
    (hidEval : NF.eval env target = NF.eval env (comboNF base mults slacks))
    (htarget : NF.eval env target = coreDefect core) :
    CoreODLGoal G c rows Q core := by
  have h0 := cone_eval_nonneg_of_eval_combo target base mults slacks env
    hvars hbase hmults hslacks hidEval
  rw [htarget] at h0
  exact CoreODLGoal_of_defect_nonneg core h0

/-- ODL core goal from chunked equality pairs.  The generator supplies:

* `pairs`, each checked by `checkEq`;
* an evaluated equality between the flattened right chunks and the cone
  combination;
* an evaluated equality between the flattened left chunks and the emitted core
  defect.
-/
theorem coreODLGoal_of_chunkedConeEval
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    (core : ODLCoreData G c rows Q)
    (pairs : List (NF × NF)) (base : NF) (mults slacks : List NF)
    (env : Var → ℚ)
    (hvars : ∀ v, 0 ≤ env v)
    (hbase : base.allCoeffNonneg = true)
    (hmults : mults.all NF.allCoeffNonneg = true)
    (hslacks : ∀ s ∈ slacks, 0 ≤ NF.eval env s)
    (hchunks : checkEqPairs pairs = true)
    (hcombo :
      NF.eval env ((pairs.map Prod.snd).flatten) =
        NF.eval env (comboNF base mults slacks))
    (htarget :
      NF.eval env ((pairs.map Prod.fst).flatten) = coreDefect core) :
    CoreODLGoal G c rows Q core := by
  have hpair := eval_flatten_fst_eq_snd_of_checkEqPairs pairs hchunks env
  have hidEval :
      NF.eval env ((pairs.map Prod.fst).flatten) =
        NF.eval env (comboNF base mults slacks) := by
    rw [hpair, hcombo]
  exact coreODLGoal_of_coneEval core ((pairs.map Prod.fst).flatten)
    base mults slacks env hvars hbase hmults hslacks hidEval htarget

#print axioms checkEqPairs
#print axioms NF_eval_flatten_chunks
#print axioms eval_sum_eq_of_checkEqPairs
#print axioms eval_flatten_fst_eq_snd_of_checkEqPairs
#print axioms cone_eval_nonneg_of_eval_combo
#print axioms coreODLGoal_of_coneEval
#print axioms coreODLGoal_of_chunkedConeEval

end ConeEvalBridge
end O14
end Erdos23Delta0
