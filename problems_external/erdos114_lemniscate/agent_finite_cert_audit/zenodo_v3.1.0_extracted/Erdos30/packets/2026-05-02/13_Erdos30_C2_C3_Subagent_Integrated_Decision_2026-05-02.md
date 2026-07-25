# Erdős #30 C2/C3 Subagent Integrated Decision

Date: 2026-05-02

## Status

Three subagents were sent:

```text
Boole    read-only map of the current #30 Lean package
Franklin read-only scan of Mathlib/local reusable infrastructure
Plato    planning packet writer
```

Plato wrote:

```text
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/12_Erdos30_C2_C3_Execution_Packet_2026-05-02.md
```

## Canonical Source Decision

Use this as the live source for C2 work:

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30
```

Do not start from:

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/export-packets/erdos30
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30-v427
/Users/kenbengoetxea/container-projects/apps/H2/Math/src/Erdos
```

Those are stale or secondary surfaces unless specifically auditing export drift.

The canonical package is:

```text
package: erdos30_sidon
toolchain: leanprover/lean4:v4.27.0
mathlib: v4.27.0
namespace: Erdos.Sidon
```

Likely build command:

```bash
cd /Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30
lake build Erdos30_Sidon_Defs Erdos30_Complete Erdos30_Lindstrom Erdos30_BFR Erdos30_Singer
```

## Current Proof Boundary

Do not use the unresolved analytic/classical axioms for C2.

Current core axioms:

```text
lindstrom_bound
bfr_core_bound
singer_sidon_exists
```

Closed reusable theorems include:

```text
IsSidonSet
sidon_diff_injective
sidon_difference_count
sidon_sharp_diff_bound
distinctSums
card_distinctSums_sidon
shifted
card_shifted
shifted_subset_range
shifted_inter_card_le_one
sidon_elem_bound
order_diff_counting
```

Important correction: older export copies still describe some now-closed facts as axioms. The current package has `sidon_elem_bound` and `order_diff_counting` closed.

## C2 Decision

The right C2 is not the full Lindström/BFR/Singer layer.

The right C2 is:

```text
general finite Sidon / collision-channel framework over closed finite combinatorics
```

Start with an additive new file, not a refactor:

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30/lean/Erdos30_CollisionChannel.lean
```

First implementation should prove a generic finite image/injectivity counting lemma, then instantiate it back to the existing #30 difference-counting result.

Conservative first theorem shape:

```text
image subset codomain
injective on finite pair set
therefore pair_count <= codomain.card
```

Then specialize to:

```text
A.card * (A.card - 1) <= 2 * N
```

This gives a real C2 framework without touching the conjectural asymptotic question.

## Upstream-Oriented C2+

Franklin identified a stronger Mathlib-facing route:

```lean
pairSum : Sym2 G -> G
IsSidon : Finset G -> Prop
sidon_pairSum_card
sidon_diff_image_card
sidon_card_mul_pred_le_fintype_card_sub_one
zmod_sidon_card_mul_pred_le
```

This is more elegant and potentially upstreamable, but it is a higher-risk first step because it requires resolving the `Sym2`/`Finset.sym2` API cleanly.

Recommended sequence:

```text
1. C2 conservative ordered-pair collision-channel theorem
2. Adapter back to current #30 package
3. Optional Sym2 generalization once the conservative theorem builds
4. Mathlib PR extraction only after API polish
```

## C3 Decision

C3 should not start with SKTC or tensor language.

Best C3 ladder:

```text
C2 collision-channel theorem
-> B2[g] bounded-collision specialization
-> finite witness checker
-> one audited adjacent target (#755 or #166)
-> negative control
-> benchmark report
```

This upgrades automation/reusability, not theorem progress on the open #30 problem.

Safe status after C2:

```text
A0 / B5 / C2 candidate
```

Only if the generic theorem builds and at least one adjacent specialization exists.

Safe status after C3:

```text
A0 / B5 / C3 candidate
```

Only if the same certificate layer runs across a small audited family and rejects a negative control.

## Public Claim Boundary

After C2, if build and audit pass:

```text
We generalized part of the Lean Sidon formalization into reusable finite collision-channel proof infrastructure, while Erdős #30 remains open.
```

Do not claim:

```text
Erdős #30 solved
best asymptotic improved
PARTIAL_INTEGER means solved
the tensor/SKTC method is validated by #30
```

## Next Move

Implement one additive file in the canonical package:

```text
lean/Erdos30_CollisionChannel.lean
```

Then run:

```bash
cd /Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30
lake build Erdos30_CollisionChannel
rg -n "sorry|admit|axiom" lean/Erdos30_CollisionChannel.lean
```

No D1 mutation until the new file builds, has zero `sorry`, and has a local proof-audit note.
