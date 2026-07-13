I’m blocked from reading the R29 memo or Lean sources: the execution host is missing at

`E:\Projects\ErdosProblems\tmp\fanout\lean_bridge\bin\codex-code-mode-host.exe`

Both read-only commands failed before execution. Consequently I cannot honestly provide source hashes, confirm existing namespaces/APIs, or claim these terms compile against the chain.

The minimal purely logical replacement is nevertheless:

```lean
def IsGlobalMin {α β : Type*} [LE β] (score : α → β) (x : α) : Prop :=
  ∀ y, score x ≤ score y

def StrictGlobalDescent {α β : Type*} [LT β]
    (score : α → β) (HallFailure : α → Prop) : Prop :=
  ∀ x, HallFailure x → ∃ y, score y < score x
```

Here `y` is completely unrestricted: there is no active set, scope, exchange relation, or score-one condition.

The core implication is assumption-minimal:

```lean
theorem no_hallFailure_globalMin_of_strictGlobalDescent
    {α β : Type*} [Preorder β]
    (score : α → β) (HallFailure : α → Prop)
    (hdesc : StrictGlobalDescent score HallFailure) :
    ∀ x, IsGlobalMin score x → ¬ HallFailure x :=
  fun x hmin hfail =>
    let ⟨y, hy⟩ := hdesc x hfail
    (not_lt_of_ge (hmin y)) hy
```

“No Hall-failing global minimizer” implies every global minimizer has `Matching` only if Hall failure covers nonmatching objects:

```lean
theorem matching_of_no_hallFailure_globalMin
    {α β : Type*} [LE β]
    (score : α → β)
    (Matching HallFailure : α → Prop)
    (hall_of_not_matching : ∀ x, ¬ Matching x → HallFailure x)
    (hno : ∀ x, IsGlobalMin score x → ¬ HallFailure x) :
    ∀ x, IsGlobalMin score x → Matching x :=
  fun x hmin => by
    by_contra hn
    exact hno x hmin (hall_of_not_matching x hn)
```

Thus strict global descent gives the pointwise minimizer conclusion:

```lean
theorem globalMin_matching_of_strictGlobalDescent
    {α β : Type*} [Preorder β]
    (score : α → β)
    (Matching HallFailure : α → Prop)
    (hall_of_not_matching : ∀ x, ¬ Matching x → HallFailure x)
    (hdesc : StrictGlobalDescent score HallFailure) :
    ∀ x, IsGlobalMin score x → Matching x :=
  matching_of_no_hallFailure_globalMin score Matching HallFailure
    hall_of_not_matching
    (no_hallFailure_globalMin_of_strictGlobalDescent
      score HallFailure hdesc)
```

To conclude existence of a matching, global-minimum attainment is additionally required:

```lean
theorem exists_matching_of_strictGlobalDescent
    {α β : Type*} [Preorder β]
    (score : α → β)
    (Matching HallFailure : α → Prop)
    (hall_of_not_matching : ∀ x, ¬ Matching x → HallFailure x)
    (exists_globalMin : ∃ x, IsGlobalMin score x)
    (hdesc : StrictGlobalDescent score HallFailure) :
    ∃ x, Matching x := by
  obtain ⟨x, hx⟩ := exists_globalMin
  exact ⟨x,
    globalMin_matching_of_strictGlobalDescent
      score Matching HallFailure hall_of_not_matching hdesc x hx⟩
```

Over a linear order, the three pointwise forms become equivalent if `Matching` and `HallFailure` are incompatible and nonmatching implies Hall failure:

```lean
theorem strictGlobalDescent_of_globalMins_matching
    {α β : Type*} [LinearOrder β]
    (score : α → β)
    (Matching HallFailure : α → Prop)
    (incompatible : ∀ x, Matching x → HallFailure x → False)
    (hmins : ∀ x, IsGlobalMin score x → Matching x) :
    StrictGlobalDescent score HallFailure := by
  classical
  intro x hfail
  by_contra h
  have hmin : IsGlobalMin score x := by
    intro y
    exact le_of_not_gt (not_exists.mp h y)
  exact incompatible x (hmins x hmin) hfail
```

Assumption comparison:

- Strict descent ⇒ no Hall-failing global minimizer: only `Preorder β`.
- No failing minimizer ⇒ every minimizer matches: requires `¬ Matching x → HallFailure x`.
- Every minimizer matches ⇒ strict descent: requires `LinearOrder β` and incompatibility of `Matching` with `HallFailure`.
- Any pointwise statement ⇒ `∃ x, Matching x`: additionally requires `∃ x, IsGlobalMin score x`.
- For `score : α → ℕ`, minimum attainment follows from `Nonempty α`; for an arbitrary ordered codomain it must be supplied separately.
- “Every global minimizer matches” can be vacuous when no global minimizer exists.

Proof gaps: integration names, namespaces, implicit parameters, the chain’s exact `Matching`/Hall-failure complement lemma, and its minimum-attainment API remain unverified. Source hashes are unavailable because no source read could execute.