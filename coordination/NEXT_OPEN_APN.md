# NEXT_OPEN_APN

generated_at: 2026-05-31T10:25:25+03:00
mode: OPEN_ERDOS_PROOF_TARGET

## Target

target_priority: 1
theorem: Erdos26.erdos_26.variants.tenenbaum
source_file: E:\Projects\ErdosProblems\formal-conjectures\FormalConjectures\ErdosProblems\26.lean
local_source_ref: formal-conjectures/FormalConjectures/ErdosProblems/26.lean:116
assignment_mode: proof-body replacement

## APN References

apn_output_path: E:\Projects\ErdosProblems\apn-gpt55-workbench\alphaproof-nexus-results\APNOutputs\ErdosProblems\erdos_26.variants.tenenbaum.lean
apn_output_ref: apn-gpt55-workbench/alphaproof-nexus-results/APNOutputs/ErdosProblems/erdos_26.variants.tenenbaum.lean:1053
natural_language_proof_path: E:\Projects\ErdosProblems\apn-gpt55-workbench\alphaproof-nexus-results\NaturalLanguageProofs\ErdosProblems\erdos26.pdf

## Preassignment Checks

exact_theorem_name_exists: yes
theorem_body_contains_sorry: yes
source_compile_precheck: lean exit 0
already_in_ledger: no
already_in_pushed_pr_batch: no
requires_unreviewed_statement_edit: no
source_contains_answer_sorry: no
statement_review_status: local theorem statement matches the APN target proposition after theorem-name normalization; final verifier must preserve the local source signature byte-for-byte.

## Scope

Do not count auxiliary, test, certificate, or helper theorems as solved open Erdos proofs.
Do not assign random finite certificates.
Do not continue Erdos307 or Erdos686 witness search in this mode.
Do not switch to another priority target unless this target fails a preassignment or verifier gate.

## Allowed Phases

Phase A: independent reconstruction from local source, no APN Lean.
Phase B: use APN natural-language proof only.
Phase C: if still blocked, use APN Lean proof as reference/port.

## Final Label

If Phase A or Phase B succeeds: OPEN_ERDOS_REPRODUCED
If Phase C uses APN Lean: OPEN_ERDOS_APN_PORTED

## Acceptance Gate

- source file or candidate theorem compiles
- exact #print axioms clean
- no sorryAx
- allowed axioms only:
  - propext
  - Classical.choice
  - Quot.sound
- no forbidden constructs
- statement byte-identical unless explicitly marked source-review candidate
- clean-room pass
- not duplicate

## Candidate Verification Output

When an Erdos26 candidate arrives, run the full gate above. If accepted, output exactly:

OPEN_ERDOS_PROOF_ACCEPTED
target: Erdos26.erdos_26.variants.tenenbaum
theorem: Erdos26.erdos_26.variants.tenenbaum
mode: OPEN_ERDOS_REPRODUCED or OPEN_ERDOS_APN_PORTED
owner_model:
statement unchanged: yes
lean exit: 0
clean-room: yes
axioms: [propext, Classical.choice, Quot.sound]
forbidden constructs: none
duplicate: no
ledger_count:
proof idea:
path:

## Duplicate Output

DUPLICATE_DO_NOT_COUNT

## Rejection Output

If rejected, output exactly:

REJECTED_CANDIDATE
target: Erdos26.erdos_26.variants.tenenbaum
failed_gate:
reason:
next_action:
