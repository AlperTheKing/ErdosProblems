# Erdos #30 C2 Audit Template / Report Shell

Date: 2026-05-02
Prepared by: Subagent 2
Scope: audit template/report shell only
Ownership boundary: this file only. No Lean files edited. No D1 mutation.

## Executive Status

```text
audit_status: TEMPLATE_ONLY
c2_verdict: PENDING_MAIN_AGENT_VERIFICATION
local_build_verified_by_subagent_2: NO
sorry_admit_axiom_scan_verified_by_subagent_2: NO
d1_mutated_by_subagent_2: NO
public_math_status: Erdos #30 remains open
claim_ceiling: reusable finite collision-channel proof infrastructure only
```

This shell is for the new conservative C2 target:

```text
general finite Sidon / collision-channel framework over closed finite combinatorics
```

It must not be used to claim that Erdos #30 is solved, that the asymptotic bound
has improved, or that A-axis theorem progress has occurred. C2 is an
automation/reusability claim only, and only after the main agent verifies the
new Lean target, theorem names, zero executable `sorry`/`admit`, and axiom
status.

## Source Binding

Canonical package for this audit:

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30
```

Canonical package metadata to verify in-session:

```text
package: erdos30_sidon
namespace: Erdos.Sidon
toolchain: leanprover/lean4:v4.27.0
mathlib: v4.27.0
```

Do not base this audit on stale or secondary surfaces unless the task is
explicitly export-drift review:

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/export-packets/erdos30
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30-v427
/Users/kenbengoetxea/container-projects/apps/H2/Math/src/Erdos
```

Local planning sources behind this shell:

```text
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/12_Erdos30_C2_C3_Execution_Packet_2026-05-02.md
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/13_Erdos30_C2_C3_Subagent_Integrated_Decision_2026-05-02.md
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30/README.md
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30/AUDIT_2026-05-02.md
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30/AXIOM_INVENTORY.md
```

Baseline boundary:

```text
current_problem_status: open
current_public_math_scope: PARTIAL_INTEGER / formalized classical infrastructure
prior_local_score: A0 / B5 / C1
target_after_verified_C2: A0 / B5 / C2_candidate
```

## C2 Theorem Identity

Fill this section after the main agent creates or verifies the new Lean file.

| Field | Value |
|---|---|
| New Lean artifact | `lean/Erdos30_CollisionChannel.lean` |
| Optional demo artifact | `lean/Erdos30_C2_Demo.lean` |
| Actual namespace | PENDING |
| Actual main theorem name | PENDING |
| Actual adjacent-specialization theorem name | PENDING |
| Actual #30 specialization theorem name | PENDING |
| Imports used | PENDING |
| Theorem statement copied from Lean | PENDING |
| Main proof dependencies | PENDING |
| Uses unresolved `lindstrom_bound` / `bfr_core_bound` / `singer_sidon_exists`? | PENDING |
| New axioms introduced? | PENDING |

Proposed conservative theorem handles to check against actual Lean:

```text
card_bound_from_injective_channel
card_bound_from_bounded_collision_channel
sidon_difference_count_via_collision_channel
```

The exact names may differ. The audit must record the actual theorem handles
from the Lean source, not these placeholders.

## Required Theorem Shape

The C2 theorem should be a generic finite counting/certificate lemma, not a
new Sidon asymptotic theorem.

Minimum acceptable shape:

```text
Finite pair/channel domain P
Finite codomain C
Channel map phi : pair -> channel_output
P.image phi subset C
phi injective on P
pair_count_formula = P.card
therefore pair_count_formula <= C.card
```

Bounded-collision extension, if present:

```text
Every channel output has at most g preimages
therefore pair_count_formula <= g * C.card
```

Specialization back to #30:

```text
Sidon A in a finite interval
P = ordered unequal pairs from A
phi(a, b) = positive difference channel
C = finite difference codomain
recover: A.card * (A.card - 1) <= 2 * N
```

Adjacent target needed for C2:

```text
B2[g], B_h[g], finite bounded-collision channel, or another constrained-state
counting lemma that is not just a renamed copy of the #30 proof.
```

## Build Receipt

All fields in this section are PENDING until the main agent verifies them.

Canonical working directory:

```bash
cd /Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30
```

Primary build command:

```bash
lake build Erdos30_CollisionChannel
```

Secondary build command if a separate demo file exists:

```bash
lake build Erdos30_C2_Demo
```

Regression build command:

```bash
lake build Erdos30_Sidon_Defs Erdos30_Complete Erdos30_Lindstrom Erdos30_BFR Erdos30_Singer Erdos30_CollisionChannel
```

Receipt table:

| Field | Value |
|---|---|
| Build verifier | PENDING |
| Verification timestamp | PENDING |
| `lean-toolchain` content | PENDING |
| `lake-manifest.json` / Mathlib pin checked | PENDING |
| Primary command exit code | PENDING |
| Secondary command exit code | PENDING |
| Regression command exit code | PENDING |
| Job count / build summary | PENDING |
| Build stdout/stderr saved where | PENDING |
| Build warnings relevant to claim | PENDING |

## Sorry / Admit / Axiom Scan

All fields in this section are PENDING until the main agent verifies them.

Suggested scan targets:

```bash
rg -n "\b(sorry|admit|axiom)\b" lean/Erdos30_CollisionChannel.lean
rg -n "\b(sorry|admit|axiom)\b" lean/Erdos30_C2_Demo.lean
```

Scan receipt:

| File | executable `sorry` | executable `admit` | new `axiom` | comment-only hits | status |
|---|---:|---:|---:|---:|---|
| `lean/Erdos30_CollisionChannel.lean` | PENDING | PENDING | PENDING | PENDING | PENDING |
| `lean/Erdos30_C2_Demo.lean` | PENDING | PENDING | PENDING | PENDING | PENDING |

Blocking rule:

```text
Any executable sorry/admit blocks C2.
Any new axiom blocks C2 unless it is explicitly citation-bound, does not imply
the open Sidon conjecture, and has an accepted closure path. For this target,
the expected result is no new axioms.
```

Existing main-package axioms to keep separate from new C2 work:

```text
lindstrom_bound
bfr_core_bound
singer_sidon_exists
```

If the new C2 theorem depends on these, record that dependency explicitly. A
clean conservative C2 result should avoid relying on those unresolved analytic
or classical axioms.

## C2 Gate Checklist

| Gate | Requirement | Status | Evidence |
|---|---|---|---|
| 0 | Scope locked to Erdos #30 canonical package | PENDING | PENDING |
| 1 | Generic finite collision-channel theorem exists | PENDING | PENDING |
| 2 | Not hardcoded to one theorem name, finite example, or numeric range | PENDING | PENDING |
| 3 | Specializes back to an existing #30 finite counting result | PENDING | PENDING |
| 4 | Specializes forward to at least one adjacent bounded-collision target | PENDING | PENDING |
| 5 | New Lean target builds | PENDING | PENDING |
| 6 | Zero executable `sorry` / `admit` | PENDING | PENDING |
| 7 | No new hidden or uncited axioms | PENDING | PENDING |
| 8 | Negative-control behavior recorded, if checker/certificate code exists | PENDING | PENDING |
| 9 | Claim remains automation/reusability, not theorem progress on #30 | PENDING | PENDING |

Decision rule:

```text
If Gates 1-7 pass and Gate 4 has a real adjacent specialization:
  status = A0 / B5 / C2_candidate

If the generic theorem only recovers existing #30 logic:
  status = A0 / B5 / C1_retained

If build or scan fails:
  status = C2_not_attained
```

## Claim Ceiling

Allowed internal claim after build and audit pass:

```text
We generalized part of the Lean Sidon formalization into reusable finite
collision-channel proof infrastructure, while Erdos #30 remains open.
```

Allowed registry-level claim after approval:

```text
C-axis candidate upgrade from C1 to C2 based on reusable finite
collision-channel theorem/certificate infrastructure.
```

Disallowed claims:

```text
Erdos #30 is solved.
The Sidon asymptotic bound has improved.
The C2 theorem advances the open conjecture.
The tensor/SKTC/MDL method is validated by Erdos #30.
PARTIAL_INTEGER means solved.
```

## D1 Intent-Only Update

No D1 update is authorized or executed by this subagent.

Draft intent payload for later registry reconciliation, only after main-agent
verification and explicit approval:

```json
{
  "d1_action": "INTENT_ONLY",
  "database": "research-hub-auth",
  "problem_id": 30,
  "source_package": "/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30",
  "new_artifact": "lean/Erdos30_CollisionChannel.lean",
  "optional_demo_artifact": "lean/Erdos30_C2_Demo.lean",
  "proposed_c_axis": "C2_candidate",
  "theorem_progress_axis": "A0",
  "formalization_axis": "B5",
  "public_problem_status": "open",
  "build_status": "PENDING",
  "sorry_count_new_artifacts": "PENDING",
  "admit_count_new_artifacts": "PENDING",
  "new_axiom_count": "PENDING",
  "claim_ceiling": "Reusable finite collision-channel proof infrastructure only; no Sidon asymptotic improvement claimed.",
  "mutation_gate": "Do not execute until build, scan, theorem-name, and claim-ceiling fields are verified by the main agent and approved by the user."
}
```

Required D1 mutation gate:

```text
1. Main agent records actual theorem names.
2. Main agent records build receipt.
3. Main agent records comment-aware sorry/admit/axiom scan.
4. Main agent confirms adjacent specialization exists.
5. User approves registry mutation.
```

## Main Agent Fill-In Block

Use this block as the final report section after verification.

```text
actual_main_theorem:
actual_specialization_to_erdos30:
actual_adjacent_specialization:
actual_negative_control:
build_command_used:
build_result:
sorry_scan_result:
admit_scan_result:
axiom_scan_result:
new_axiom_justification_if_any:
claim_ceiling_verdict:
c2_verdict:
d1_intent_payload_ready:
registry_mutation_approved:
```

## Current Template Verdict

```text
C2 NOT YET ATTAINED BY THIS FILE.

This file is a clean audit shell for the main agent's verification pass. It
does not certify the new theorem, does not verify a build, and does not update
D1.
```
