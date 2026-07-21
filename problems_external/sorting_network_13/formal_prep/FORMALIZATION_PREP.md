# SN13 formalization and Formal Conjectures PR preparation

Date: 2026-07-18 (Europe/Istanbul)

## Verdict

**Infrastructure GO; exact-theorem PR NO-GO unless two independent missing
certificates are supplied.**

If a 44-comparator network is found, its explicit upper bound can be made into
a short Lean theorem.  A no-`sorry` theorem asserting the exact equality
`S(13) = 44` additionally needs a Lean lower-bound proof.  That lower-bound
proof is not in Formal Conjectures or Mathlib and was not produced here.

No 44-comparator network is asserted anywhere in this directory.

## Repository and toolchain audit

- Locally fetched upstream reference:
  `google-deepmind/formal-conjectures` main at
  `c252a41054125b5fd9c8356e2137cd9b55337657` (2026-07-16).
- Toolchain and Mathlib release: Lean `v4.27.0`, Mathlib `v4.27.0`.
- Current problem-file import on that upstream revision:
  `import FormalConjecturesUtil`.
- The existing `formal-conjectures/` checkout is a dirty research branch and
  is unsuitable for a PR.  A fresh worktree from the then-current upstream
  main is required after a certificate exists.
- The upstream contribution workflow asks for an issue before a PR, a 2026
  copyright header, a referenced module docstring, one namespace, one
  `category`, at least one `AMS` tag, and a passing build.  The agent-specific
  requirement is the stricter `lake --wfail build`.
- Proofs longer than roughly 25--50 lines belong in an external repository and
  should be linked with `formal_proof`; this length limit does not apply to
  `FormalConjecturesForMathlib` API code.

Recommended classifications are `AMS 05 68 94` (combinatorics, computer
science, and circuits/information), subject to reviewer preference.

## Collision audit

The exact full-tree scan recorded in
`../audit/FORMAL_CONJECTURES_SCAN.txt` and `../audit/LOWER44_AUDIT.md` found no
sorting-network, comparator-network, Bose--Nelson, Van Voorhis, compare-exchange,
zero--one-principle, or `S(13)` formalization at upstream commit `c252a410`.

This is only a dated local collision result.  Immediately after any L44 hit,
refresh upstream and search current files, issues, and pull requests again
before claiming priority or opening a PR.

## Compile-tested generic prototype

`KernelPrototype.lean` contains:

1. `Comparator n := Fin n × Fin n` and `Network n := List (Comparator n)`;
2. canonical compare-exchange semantics using lower and higher channel indices;
3. left-to-right network execution;
4. semantic binary sortedness using `List.Pairwise`;
5. a structurally executable enumeration of all `2^n` binary inputs;
6. `mem_allBinaryInputs`, proving enumeration completeness;
7. `verifyBinary_eq_true_iff`, connecting the executable check to the semantic
   universal property;
8. `HasSizeSorter` and `IsOptimalSize`;
9. the exact logical injection lemma
   `isOptimalSize_of_certificate_of_lowerBound`;
10. a no-`sorry`, no-`native_decide` two-channel kernel smoke test; and
11. the published Dobbelaere 13/45 fixture for shape and length testing only.

It compiled successfully with cached Lean/Mathlib v4.27.0 in 19.877 seconds:

```text
exit code: 0
SHA-256: 4E0704E6A26DD40E509EB492BB2016CE2DED88B6DDE5E0F20EAE71ED101B405A
```

The prototype deliberately imports `Mathlib` so it can compile outside the
upstream source tree.  A PR version must use `FormalConjecturesUtil` in the
problem file, or narrow Mathlib imports if the generic API is moved to
`FormalConjecturesForMathlib`.

### Performance boundary

The naive structural verifier did not finish the published 13/45 exhaustive
kernel check within 229 CPU-seconds and was terminated.  All Lean and Lake
processes were then confirmed stopped.  Consequently this particular
enumerator is a correctness prototype, not the production L44 checker.

Before an L44 theorem is submitted, replace its executable core with a compact
proof-producing route, preferably a `BitVec 13`/mask checker discharged by
kernel `decide` or `bv_decide`, and prove once that it is equivalent to
`SortsBinary`.  `native_decide` remains forbidden.  The production route must
first reproduce the published 13/45 fixture and then the new 13/44 fixture.

## Exact certificate injection point

Only after a verified hit, add the exact ordered 44-pair list as a definition
of type `Network 13`.  Then prove, in this order:

1. the list has length 44;
2. the certified verifier returns true;
3. verifier truth implies `SortsBinary`;
4. therefore `HasSizeSorter 13 44`.

The intended theorem shape is:

```lean
def candidate44 : Network 13 :=
  -- Insert only the exact normalized list emitted by the independently
  -- verified search artifact.

theorem candidate44_length : candidate44.length = 44 := by
  decide

theorem candidate44_sorts_binary : SortsBinary candidate44 := by
  apply (certifiedVerifier_eq_true_iff candidate44).mp
  -- kernel decide or bv_decide over the compact checker

theorem hasSizeSorter_13_44 : HasSizeSorter 13 44 :=
  ⟨candidate44, candidate44_length, candidate44_sorts_binary⟩
```

This is a shape specification, not executable Lean: no candidate body or proof
is invented before the search emits one.

The certificate definition must carry a comment with the source `.net` path,
its SHA-256 hash, and the two independent external verifier results.  Lean's
ordered list must be byte-for-byte regenerated from that normalized artifact,
not manually retyped.

## Zero--one bridge

The prototype's `SortsBinary` is precisely the finite zero--one property.  It
does **not** yet prove the generic zero--one principle saying that the same
network sorts inputs in every linear order.  There are two honest PR choices:

1. State optimality for binary comparator networks and cite the standard
   zero--one equivalence in the module documentation; or
2. Add a formal threshold-map proof showing that compare-exchange commutes with
   Boolean thresholding, then derive sorting over arbitrary linear orders.

Choice 2 is formally stronger and preferable for reusable API, but was not
started because there is no L44 certificate and target search has priority.
No generic-order claim should receive `formal_proof` until this bridge exists.

## Why exact `S(13) = 44` is not yet a Lean theorem

The mathematical lower-bound chain audited in `../audit/LOWER44_AUDIT.md` is

```text
S(13) >= S(11) + ceil(log2(F(13))) = 35 + ceil(log2(392)) = 44.
```

The audit is computationally and bibliographically sound, but three links are
not Lean theorems in the current environment:

1. Van Voorhis' two-channel deletion theorem;
2. the recurrence semantics plus the theorem `F(13) = 392`; and
3. Harder's lower bound `S(11) >= 35`, whose published formal certificate is
   checked in Isabelle/HOL, not Lean.

An Isabelle formal-proof citation is excellent evidence and can be recorded
with `formal_proof using other_system`; it cannot be imported as a Lean proof
term.  Adding any of these links as an axiom would violate the requested
no-placeholder standard.

Therefore:

- `HasSizeSorter 13 44` can become a complete no-`sorry` Lean theorem from an
  L44 certificate;
- `IsOptimalSize 13 44` cannot become a complete no-`sorry` Lean theorem from
  the present artifacts; and
- a paper may still establish the exact mathematical result by combining the
  new upper certificate with the published lower theorem, after expert and
  novelty review.

## Formal Conjectures scope decision

| Proposed item | Repository fit | No-`sorry` readiness after L44 | Decision |
|---|---|---:|---|
| `candidate44.length = 44` | test/supporting fact | immediate | include only as support |
| `HasSizeSorter 13 44` | solved research upper bound | after compact checker | **GO** |
| generic zero--one theorem | reusable API | not prepared | optional follow-up |
| `IsOptimalSize 13 44` | exact Bose--Nelson result | lower bridge missing | **NO-GO** |
| exact statement with benchmark `sorry` | standard FC statement style | conflicts with user rule | **do not submit** |

If reviewers require the exact numerical-answer statement rather than the
upper-bound theorem, do not weaken the claim or hide the lower-bound gap.  Host
the complete formal development externally or finish the lower bridge first.

## Proposed eventual file placement

For a minimal upper-certificate PR:

- `FormalConjectures/Other/OptimalSortingNetwork13.lean`.

For reusable definitions and a generic zero--one theorem:

- `FormalConjecturesForMathlib/Combinatorics/SortingNetwork.lean`;
- add its import to `FormalConjecturesForMathlib.lean`; and
- keep the concrete problem/certificate in
  `FormalConjectures/Other/OptimalSortingNetwork13.lean`.

The latter is cleaner but substantially larger.  It should not be started
during the target search.

## Post-hit runbook

1. Stop every search worker on the first apparent L44 output.
2. Normalize the 44 ordered pairs and hash the source artifact.
3. Re-run both independent exhaustive external verifiers over all 8192 inputs.
4. Refresh upstream and repeat the file/issue/PR collision search.
5. Create a fresh branch/worktree from current upstream main.
6. Inject the candidate into the compact Lean checker and reproduce 13/45
   before checking 13/44.
7. Run the focused Lean file, then `lake --wfail build`.
8. Submit only the theorem actually proved in Lean; describe the published
   lower-bound chain separately if exactness is not formalized.
9. Open/link the required GitHub issue, verify CLA status, and only then create
   the PR.  Add a stable `formal_proof` permalink once a commit URL exists.

No branch, commit, push, issue, or PR was created in this preparation step.
