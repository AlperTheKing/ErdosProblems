Unable to inspect or write the lane: the configured host `bin/codex-code-mode-host.exe` is missing, and the workspace is otherwise read-only. Therefore no file hash or source-compatible compile result can honestly be reported.

Assuming the existing objects have the effective shapes `RowChoice`, `scopedScore : RowChoice → ℕ`, and `Matching : RowChoice → Prop`, the honest hierarchy is:

```lean
def LowerReplacement (ω ω' : RowChoice) : Prop :=
  Matching ω' ∧ scopedScore ω' < scopedScore ω

def ReplacementStep (ω ω' : RowChoice) : Prop :=
  Matching ω' ∧ scopedScore ω' < scopedScore ω

def ReplacementReachable : RowChoice → RowChoice → Prop :=
  Relation.TransGen ReplacementStep
```

The minimum contradiction needs exactly an arbitrary lower-scoring matching:

```lean
theorem contradicts_global_minimum
    (ω ω' : RowChoice)
    (hmin : ∀ η : RowChoice, Matching η →
      scopedScore ω ≤ scopedScore η)
    (hrepl : LowerReplacement ω ω') :
    False := by
  exact Nat.not_lt_of_ge (hmin ω' hrepl.1) hrepl.2
```

If the project’s minimum hypothesis bundles feasibility of `ω`, a more complete definition is:

```lean
def IsGlobalMinimum (ω : RowChoice) : Prop :=
  Matching ω ∧
  ∀ η : RowChoice, Matching η →
    scopedScore ω ≤ scopedScore η
```

with:

```lean
theorem lowerReplacement_not_of_globalMinimum
    {ω ω' : RowChoice}
    (hmin : IsGlobalMinimum ω)
    (hrepl : LowerReplacement ω ω') :
    False := by
  exact Nat.not_lt_of_ge (hmin.2 ω' hrepl.1) hrepl.2
```

Comparison:

- `∃ ω', Matching ω' ∧ scopedScore ω' < scopedScore ω` is exactly sufficient.
- A named replacement relation is harmless only if it is definitionally that proposition.
- One replacement edge is sufficient if every edge guarantees feasibility and strict score decrease.
- Reachability/transitive closure is stronger and unnecessary for the contradiction.
- Claiming reachability after Hamming-one failure adds unjustified structure unless an independent theorem constructs a finite chain.
- Hamming-one failure alone does not imply that any lower-scoring global replacement exists.

A closure theorem, if genuinely needed elsewhere, should expose its assumptions:

```lean
theorem reachable_strictly_decreases
    {ω ω' : RowChoice}
    (h : Relation.TransGen ReplacementStep ω ω') :
    Matching ω' ∧ scopedScore ω' < scopedScore ω := by
  induction h with
  | single hstep =>
      exact hstep
  | tail hxy hyz ih =>
      exact ⟨hyz.1, lt_trans hyz.2 ih.2⟩
```

The final `lt_trans` orientation may need adjustment depending on the installed `TransGen` constructors.

Falsifiers and vacuity hazards:

- `ReplacementStep := fun _ _ => False` makes all universal preservation claims vacuous.
- Omitting `Matching ω'` permits an infeasible lower-score witness.
- Defining replacement as merely `scopedScore ω' < scopedScore ω` silently loses feasibility.
- `ReflTransGen` permits `ω' = ω`; strict decrease then cannot be derived without a nonempty-path premise.
- A relation with nondecreasing edges cannot support the closure lemma.
- If `RowChoice` itself encodes only row selections and not matching validity, quantifying over every `RowChoice` without `Matching` makes the “minimum” unnecessarily strong.
- If the score codomain is not `Nat`, replace `Nat.not_lt_of_ge` with `not_lt_of_ge`.
- Strict descent in `Nat` rules out cycles, but does not construct a replacement edge or path.

Hashes: unavailable—no file was readable or writable, so inventing hashes would violate the reporting protocol.

Proof gaps:

1. Exact signatures and namespaces of `RowChoice`, `scopedScore`, and `Matching` were inaccessible.
2. No Lean build was possible.
3. No implication from Hamming-one failure to `LowerReplacement` has been proved; in general it is false without an added global-existence argument.
4. The precise `Relation.TransGen` induction constructor orientation remains compile-unverified.