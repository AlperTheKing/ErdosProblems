# Erdős #30 C2 Verification Report

Date: 2026-05-02

## Verdict

```text
C2_LOCAL_VERDICT: ATTAINED_LOCALLY
D1_STATUS: NOT_MUTATED_IN_THIS_STEP
PUBLIC_MATH_STATUS: Erdős #30 remains open
CLAIM_CEILING: reusable finite collision-channel proof infrastructure
```

This is a C-axis upgrade candidate only:

```text
A0 / B5 / C1 -> A0 / B5 / C2 candidate
```

It is not A-axis theorem progress and does not solve Erdős #30.

## Canonical Package

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30
```

Package metadata:

```text
package: erdos30_sidon
toolchain: leanprover/lean4:v4.27.0
mathlib input: v4.27.0
mathlib resolved rev: a3a10db0e9d66acbebf76c5e6a135066525ac900
```

## New Lean Artifact

```text
lean/Erdos30_CollisionChannel.lean
```

SHA-256:

```text
f9114265831623042d0bad7a89dd33d77a73233deb1680df64a733039023257a
```

Lake target added:

```text
Erdos30_CollisionChannel
```

## Theorem Inventory

New reusable theorem/lemma surface:

```text
theorem card_le_of_injective_channel
theorem card_le_mul_of_fiber_card_bound
def     strictUpper
lemma   diff_injOn_strictUpper
lemma   strictUpper_card_double
lemma   strictUpper_diff_image_subset_Icc
theorem strictUpper_card_le_of_collision_channel
theorem sidon_collision_channel_bound
```

Interpretation:

- `card_le_of_injective_channel` is the reusable finite injective-channel pigeonhole lemma.
- `card_le_mul_of_fiber_card_bound` is the bounded-fiber extension point for B2[g] / bounded-collision variants.
- `strictUpper_card_le_of_collision_channel` specializes the generic channel lemma back to the Sidon strict-upper-triangle channel.
- `sidon_collision_channel_bound` recovers the standard #30 difference-count bound.

The file deliberately avoids the unresolved main-package axioms:

```text
lindstrom_bound
bfr_core_bound
singer_sidon_exists
```

## Build Receipt

Primary build:

```bash
cd /Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30
lake build Erdos30_CollisionChannel
```

Result:

```text
PASS
Build completed successfully (7888 jobs).
```

Regression build:

```bash
lake build Erdos30_Sidon_Defs Erdos30_Complete Erdos30_Lindstrom Erdos30_BFR Erdos30_Singer Erdos30_CollisionChannel
```

Result:

```text
PASS
Build completed successfully (7896 jobs).
```

Warnings:

```text
Pre-existing unused-variable warnings in Erdos30_Lindstrom.lean.
No C2-blocking warning from Erdos30_CollisionChannel.lean.
```

## Sorry / Admit / Axiom Scan

Command:

```bash
rg -n "\b(sorry|admit|axiom)\b" lean/Erdos30_CollisionChannel.lean
```

Result:

```text
No hits.
```

Scan verdict:

```text
executable_sorry: 0
executable_admit: 0
new_axiom: 0
```

## Worktree Note

The broader Math worktree was dirty before this work. This step intentionally touched only:

```text
modified: lakefile.lean
added:    lean/Erdos30_CollisionChannel.lean
```

The `lakefile.lean` already contained unrelated drift relative to the repository base, including v4.27 migration and additional targets. This session only added the `Erdos30_CollisionChannel` target to that existing local surface.

## D1 Intent-Only Payload

No D1 mutation was performed in this step.

Suggested registry update, if approved:

```json
{
  "problem_id": 30,
  "project_id": "erdos-30-sidon-lean",
  "artifact": "Erdos30_CollisionChannel.lean",
  "lake_build_status": "pass",
  "last_verified_date": "2026-05-02",
  "sorry_count": 0,
  "theorem_count": 4,
  "lemma_count": 3,
  "axiom_count": 0,
  "automation_progress": "C2_candidate",
  "theorem_progress": "A0",
  "formalization_progress": "B5",
  "math_status": "open",
  "claim_ceiling": "reusable finite collision-channel proof infrastructure; not a solution of Erdős #30"
}
```

The theorem count treats `def strictUpper` separately from theorem/lemma declarations.

## Safe Claim

```text
We have locally built a reusable Lean finite collision-channel layer for the Erdős #30 Sidon formalization. It proves generic injective-channel and bounded-fiber counting lemmas and recovers the standard Sidon difference-count bound. Erdős #30 remains open.
```

## Next Gate Toward C3

Use the new bounded-fiber lemma to build one adjacent target:

```text
B2[g] bounded-collision specialization
finite witness checker
negative control
then #755 or #166 after D1/local status audit
```
