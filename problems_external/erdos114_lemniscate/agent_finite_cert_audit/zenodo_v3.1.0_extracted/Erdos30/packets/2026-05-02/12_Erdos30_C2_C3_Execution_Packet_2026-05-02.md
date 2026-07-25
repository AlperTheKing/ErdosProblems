# Erdos #30 C2/C3 Execution Packet

Date: 2026-05-02
Owner: Subagent C
Scope: planning packet only. No Lean or registry files edited.

## Executive Boundary

Erdos #30 is not solved.

The current local evidence supports this narrower status:

- The #30 Lean packet has a strong formalization surface.
- The open Sidon problem remains open.
- The C-axis push should upgrade automation/reusability only, not theorem-progress status.

Best local current status, using the May 2 local read-back packet:

```text
problem_id: 30
math_status: open
lean_status: COMPILED
alignment_status: ALIGNED
math_scope: PARTIAL_INTEGER
May 2 verified rows: 5
lake_build_status: pass for all 5 rows
sorry_count: 0
theorem_count: 47
lemma_count: 25
axiom_count: 3
```

Older local artifacts still report different theorem/axiom counts. Treat the May 2 D1 read-back packet as the freshest local summary, but do not treat this packet as a fresh D1 query or a fresh Lean build.

## Sources Used

Local artifacts consulted:

- `11_D1_Drain_Readback_Verification_2026-05-02.md`
- `/Users/kenbengoetxea/container-projects/apps/H2/Math/scoring/assessment_erdos30.json`
- `/Users/kenbengoetxea/container-projects/apps/H2/Math/ERDOS_PORTFOLIO_STATUS.md`
- `/Users/kenbengoetxea/container-projects/apps/H2/Math/Math-Problems/numberverse-proofs/Erdos30_Proof.md`
- `/Users/kenbengoetxea/container-projects/apps/H2/Math/scoring/erdos_scorer.py`
- `/Users/kenbengoetxea/container-projects/apps/H2/Math/export-packets/erdos30/ERDOS30_FULL_REVIEW.lean`
- `10_D1_Third_Party_Agent_Review_Prompt_2026-05-02.md`

Unknowns:

- I did not run a live D1 query in this packet pass.
- I did not run `lake build` in this packet pass.
- I did not check current web literature or erdosproblems.com.
- The exact local scoring rubric gives C-axis labels, not a detailed proof checklist. The C2/C3 criteria below are operational definitions derived from those labels and the current #30 artifact surface.

## Current A/B/C Position

The prior local score is:

```text
A0 / B5 / C1
```

Meaning:

- `A0`: no new mathematical progress on the open Sidon conjecture.
- `B5`: landmark formalization surface for classical Sidon results.
- `C1`: task-specific automation and scripts, not yet a reusable benchmark capability.

The execution target is therefore:

```text
A0 / B5 / C1  ->  A0 / B5 / C2  ->  A0 / B5 / C3
```

Do not move the A-axis unless a genuinely new mathematical theorem is proved relative to current literature. Do not move the public claim from "formalized classical infrastructure" to "solved" or "advanced the conjecture."

## C2 Definition

For Erdos #30, `C2 = Limited generalization` should mean:

```text
At least one proof/certificate component originally built for #30 is extracted
into a reusable theorem schema or reusable certificate pipeline, then
demonstrated on one adjacent Sidon-family or collision-channel target without
weakening the current proof-status discipline.
```

Minimum C2 gate:

1. A reusable theorem schema exists in Lean or in a generated Lean certificate architecture.
2. It is not hardcoded to one theorem name, one finite example, or one numerical range.
3. It specializes back to at least one current #30 result.
4. It specializes forward to at least one adjacent target, such as a B2[g], B_h[g], finite collision-channel, or constrained-state counting lemma.
5. All new Lean artifacts build with zero `sorry`.
6. Any axioms are explicit, citation-bound, and do not conceal the open problem.
7. The status remains "automation/reusability upgrade," not "Erdos #30 solved."

What does not count as C2:

- A new one-off script that only recomputes Singer excess.
- A renamed copy of an existing #30 proof.
- A benchmark table without reusable proof/certificate code.
- A theorem statement that smuggles the Sidon conjecture in as an axiom.

## Candidate C2 Theorem Schema

The safest C2 theorem target is a finite collision-channel counting lemma. This captures the reusable part of Sidon set arguments without claiming the conjectural asymptotic improvement.

Implementation schema (pseudo-Lean; adapt to local Mathlib syntax):

```text
theorem card_bound_from_injective_channel
    {alpha beta : Type*}
    [DecidableEq alpha] [DecidableEq beta]
    (P : Finset (Prod alpha alpha))
    (C : Finset beta)
    (phi : Prod alpha alpha -> beta)
    (h_image : P.image phi subset C)
    (h_inj : Set.InjOn phi P)
    (h_pair_count : P.card = pair_count_formula)
    :
    pair_count_formula <= C.card := by
  -- image-cardinality plus injectivity
```

The exact Lean syntax and pair quotient representation are implementation details. The theorem should avoid depending on a fragile `Sym2` API unless the local Mathlib version makes that route easy. A robust first pass can use ordered-pair `Finset` subsets plus an explicit pair-count hypothesis.

Specializations:

1. Existing #30 difference-counting bound:

   ```text
   Sidon A in [1, N]
   P = ordered unequal pairs from A
   phi(a, b) = a - b
   C = {1, ..., N}
   result: A.card * (A.card - 1) <= 2N
   ```

2. Adjacent bounded-multiplicity variant:

   ```text
   B2[g] or collision multiplicity <= g
   each channel output has at most g preimages
   result: pair_count_formula <= g * C.card
   ```

3. Optional finite witness checker:

   ```text
   Given an explicit finite set A, verify IsSidonSet A by channel injectivity.
   ```

C2 is achieved if the implementation proves the generic counting lemma and one real specialization beyond the currently hardcoded #30 result.

## C2 Deliverables

Expected implementation deliverables, not created by this packet:

1. `Erdos30_CollisionChannel.lean`

   Reusable finite image/injectivity counting lemma plus B2/B2[g]-ready interfaces.

2. `Erdos30_C2_Demo.lean`

   Demonstrates the generic lemma by recovering an existing #30 counting bound and proving one adjacent bounded-collision specialization.

3. `Erdos30_C2_PROOF_AUDIT.md`

   Lists theorem names, imports, axioms, `sorry` count, build command, and exact claim ceiling.

4. Fresh build receipt

   ```text
   lake build <target>
   sorry scan = 0
   axiom inventory = explicit and citation-bound
   ```

5. Registry update plan

   Draft only until user approves mutation. If accepted, C-axis can move from `C1` to `C2`; A-axis remains `A0`; public math status remains open.

## Proof-Risk Gates

Gate 0: scope lock

- Confirm the target is Erdos #30 Sidon sets, not a cousin problem.
- Confirm no one else has changed the active Lean files before editing.
- Do not overwrite existing #30 artifacts.

Gate 1: statement honesty

- The generic theorem must be a counting/certificate lemma.
- It must not assert `h(N) = sqrt(N) + O_epsilon(N^epsilon)`.
- It must not assume the conjecture under a different name.

Gate 2: import/build discipline

- Add new files rather than refactoring stable compiled files first.
- Build the new target alone, then build the #30 export chain.
- No `sorry`; no hidden `admit`; no untracked local theorem used as a black box.

Gate 3: axiom transparency

- Existing citation-backed axioms may remain if unchanged.
- Any new axiom blocks C2 unless it is clearly a quoted classical theorem with a closure path and does not imply the open conjecture.

Gate 4: specialization test

- The generic lemma must recover one current #30 result.
- The same generic lemma must support at least one adjacent bounded-collision target.

Gate 5: negative-control test

- Include a small example where injectivity fails and the bound is not claimed.
- If the certificate accepts a non-Sidon set as Sidon, stop.

Gate 6: status discipline

- If build passes: eligible for C2 only.
- If the adjacent target is only sketched: remain C1.
- If the theorem only restates existing #30 logic: remain C1.

## C3 Target Definition

For this push, `C3 = Benchmark-relevant capability` should mean:

```text
The reusable #30 collision/certificate machinery works across a small audited
benchmark family of related extremal-combinatorics problems, with repeatable
build/test commands and at least one negative control.
```

C3 is not "the Sidon problem is solved." It is "the automation pattern is now credible outside one local proof."

Minimum C3 gate:

1. At least three audited targets use the same core certificate theorem or generator.
2. At least two targets are not simply restatements of #30.
3. One negative-control target is rejected or marked unsupported.
4. The benchmark is reproducible from saved scripts or Lean targets.
5. The report separates formalized theorem content from computation and heuristic routing.

## C3 Candidates Ranked By Feasibility

| Rank | Candidate | Feasibility | Why it is plausible | Main blocker |
|---:|---|---|---|---|
| 1 | B2/B2[g] bounded-collision certificate family | High | Direct generalization of Sidon uniqueness to bounded multiplicity; closest to the C2 theorem schema. | Need clean multiplicity counting in Lean without overcomplicating the API. |
| 2 | Finite witness/counterexample checker for Sidon-family sets | High | Explicit finite sets can be certified by injectivity of pair-sum or difference channels; useful as a reusable benchmark harness. | Must avoid presenting finite checks as asymptotic theorem progress. |
| 3 | Lane B constrained-state geometry: #30 plus #755 B_h[g] plus #166 sum-free style extremal sets | Medium-high | The May 2 D1 review prompt already groups #30, #755, and #166 as constrained-state / transfer-style candidates. | Requires D1/local artifact audit before claiming the targets are aligned. |
| 4 | Transfer-matrix surface for Sidon and C4-free/hypercube-style targets | Medium | Could become benchmark-relevant if the same channel matrix interface handles Sidon and graph extremal examples. | Risk of becoming a numerical analogy rather than a Lean/proof certificate. |
| 5 | Singer/projective-plane construction verifier beyond current finite q examples | Medium-low | Strong mathematical relation to existing lower-bound formalization. | Finite-field/projective-plane infrastructure can become a large formalization project. |
| 6 | SKTC/operator/tensor bridge from EHP114 into #30 | Low for immediate C3 | Interesting as a research-program bridge; local prompt lists #30 as a transfer-matrix surface candidate. | Too speculative for C3 unless it produces a concrete reusable certificate and negative controls. |
| 7 | Direct asymptotic improvement toward `O_epsilon(N^epsilon)` | Not a C3 automation target | This is the actual open problem. | Would be theorem-progress, not merely automation; no local artifact supports claiming it. |

Recommended C3 path:

```text
C2 collision-channel theorem
-> bounded-collision B2[g] specialization
-> finite witness checker
-> one audited adjacent target from #755 or #166
-> negative control
-> C3 benchmark report
```

## Public Claim Boundary

Safe private working sentence:

```text
We are trying to move Erdos #30 from task-specific formalization scripts toward
reusable collision-channel certificate machinery.
```

Safe public sentence after C2, if the build and audit pass:

```text
We generalized part of the Lean Sidon formalization into reusable finite
collision-channel proof infrastructure, while the Erdos #30 asymptotic problem
remains open.
```

Safe public sentence after C3, if the benchmark passes:

```text
The Sidon formalization now supports a small reusable benchmark family for
collision-style extremal-combinatorics certificates; this is automation and
formalization progress, not a solution of Erdos #30.
```

Forbidden public claims:

- "We solved Erdos #30."
- "The Sidon conjecture is proved."
- "We improved the best known asymptotic bound."
- "The C2/C3 upgrade advances the mathematical state of the conjecture."
- "PARTIAL_INTEGER means solved."

## Exact Next Implementation Steps

1. Re-open the current #30 truth surface.

   ```text
   cd /Users/kenbengoetxea/container-projects/apps/H2/Math
   git status --short
   sed -n '1,140p' scoring/assessment_erdos30.json
   sed -n '1,140p' ERDOS_PORTFOLIO_STATUS.md
   ```

   If the worktree shows other active edits in #30 files, do not overwrite them.

2. Inspect current compiled #30 files before editing.

   ```text
   rg -n "theorem|axiom|sorry|IsSidonSet|sidon_difference_count|sidon_lower_bound" \
     src/Erdos/Erdos30_*.lean export-packets/erdos30/Erdos30_*.lean
   ```

3. Create an additive new Lean file rather than refactoring first.

   Proposed future file:

   ```text
   src/Erdos/Erdos30_CollisionChannel.lean
   ```

   Start with a generic finite image/injectivity counting theorem over ordered-pair finite sets.

4. Prove the generic C2 lemma using existing finite-set tools.

   Initial proof ingredients likely needed:

   ```text
   Finset.card_image_of_injOn
   Finset.card_le_card
   image subset codomain
   explicit pair-count hypothesis
   ```

   Avoid a dependent quotient or `Sym2` abstraction until the ordered-pair version builds.

5. Add one #30 specialization.

   Use the generic lemma to restate or recover the existing difference-channel bound:

   ```text
   A.card * (A.card - 1) <= 2 * N
   ```

   This proves the generic theorem is not decorative.

6. Add one adjacent bounded-collision specialization.

   Minimal target:

   ```text
   If every channel output has at most g preimages, then
   pair_count_formula <= g * C.card.
   ```

   Keep it finite and parametric. Do not connect it to the full open conjecture.

7. Run the build and scans.

   ```text
   lake build Erdos.Erdos30_CollisionChannel
   rg -n "sorry|admit|axiom" src/Erdos/Erdos30_CollisionChannel.lean
   ```

   Then build the existing #30 chain if imports were touched.

8. Write the C2 audit report.

   Required fields:

   ```text
   theorem names
   imports
   build command
   build result
   sorry count
   axiom inventory
   what generalized
   what did not change
   public claim boundary
   ```

9. Only then consider C2 status.

   If the generic theorem builds and the adjacent specialization exists:

   ```text
   A0 / B5 / C2 candidate
   ```

   If it only recovers an existing #30 theorem:

   ```text
   remain A0 / B5 / C1
   ```

10. For C3, do not start with SKTC.

    Start with the ranked high-feasibility path:

    ```text
    bounded-collision B2[g]
    finite witness checker
    #755 or #166 after D1/local status audit
    negative control
    benchmark report
    ```

11. Do not mutate D1 or publish without explicit approval.

    Draft any registry update as intent only:

    ```text
    proposed_automation_progress: C2
    theorem_progress: A0
    formalization_progress: B5
    math_status: open
    public_status: not solved
    ```

## Bottom Line

The narrow critical path is not another claim about the Sidon conjecture. It is a reusable collision-channel theorem/certificate layer that can be demonstrated on #30 and one adjacent finite extremal target. That is the honest C2 move. C3 becomes realistic only after the same layer runs across a small audited family with a negative control.
