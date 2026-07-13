# R28/R29 versus the compiled FullBank architecture

## Verdict

The canonical `N = 2943` tuple falsifies the following smallest proposition, for the **specific active-scoped owner source relation used by the R29 Hall checker** and the shore `A = {0,1,2}`:

\[
  \left|N_{\mathrm{active\mbox{-}scoped}}(A)\right| \ge D(A).
\]

The exact values are

\[
D(A)=19953,\qquad |N_{\mathrm{active\mbox{-}scoped}}(A)|=19925
=17325+2600,
\]

so `19925 < 19953`, equivalently `19953 - 19925 = 28`.  Interpreting the integers in `ℚ` changes nothing: `(19925 : ℚ) < (19953 : ℚ)` with difference `(28 : ℚ)`.

This does **not** falsify `FullBankRelaxedCoverCert`, and it does **not** falsify or contradict `FullBankGlobalPackage.Checked`.  No canonical artifact instantiates the parameters of either Lean structure, and the checked Hall relation omits the four full-bank capacity kinds and their rational, possibly fractional, routing/spend data.

## Exact artifact evidence

The independent owner-Hall result is `tmp/fanout/r29_gate/d05/retry2/result.json`.  Its asserted decomposition is:

```text
demand                  19953
same_first_only         17325
row_companion_only       2600
both_reasons                0
reach                    19925
gap                         28
shore                  [0,1,2]
```

The emitted cut certificate is `tmp/fanout/r29_gate/d05/retry2/cut_certificate.json`, whose actual SHA-256 is

```text
dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce
```

The global-minimum summary `tmp/fanout/global_min_proof/lead/r29_global_min_hall_falsifier.json` records exactly:

```text
globalScopedScore                 23115
phtLowerPerTupleFromGlobalMinimum 23115
phtUpperPerTuple                  23087
hallDemand                        19953
hallNeighborhood                  19925
hallDefect                           28
phtContradictionNumerator         28*680^676
```

Thus the tuple also falsifies the stronger auxiliary assertion that every Hall-failing tuple has a lower active-scoped score: the artifact asserts this tuple attains the global minimum `23115`.  It likewise falsifies the stated full-product heat-bath bound by the exact positive numerator `28*680^676`.  Those are consequences about the active-scoped selector score, not FullBank certificates.

The reconstruction in `tmp/fanout/r29_gate/lead/lead_result.json` records `N=2943`, `|B|=7039`, `|M|=1383`, `Gamma=34575`, and row-family histogram `707` of size `1` plus `676` of size `680`.  Its embedded canonical-payload SHA-256 is

```text
fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f
```

The all-anchor serialized tuple hash recorded by the falsifier is

```text
93d5d64c55338186603b718b5d6bb162d907c4fc868ce276808e01822c395901
```

These are hashes of canonical serializations computed by the scripts, not hashes of `lead_result.json` itself.  The current file SHA-256 of `lead_result.json` is `0fa2eb08696372b25b05429a692db9fa5ecabc173ce25dc66f59f68d3bf214f5`; the current file SHA-256 of `r29_global_min_hall_falsifier.json` is `bacfcf5364ad7765365d43045145b8cb3bc9db1a5a6e1da636dada154d161148`.  The writeup's advertised historical prefix `00186166...` is absent, so no conclusion should be attached to that unavailable object.

## Why this is not `FullBankRelaxedCoverCert`

`Ell5FullBankInterface.lean:27-40` defines `FullBankRelaxedCoverCert` by rational variables `lam : ι → ℚ` and `q : E → JT → ℚ` satisfying row cover, support congestion, off-support routing, sink capacity, and legal-incidence conditions.  In particular, its decisive conditions are weighted inequalities

```text
hroute : load(c) <= sum_j q(c,j)
hcap   : sum_c q(c,j) <= kap(j)
hqinc  : 0 < q(c,j) -> inc(c,j)
```

The R29 artifact instead counts distinct triples in one bespoke unweighted neighborhood.  It supplies no `S,F,O,J,K,sep,dB,inc,kap`, no rational `lam`, and no rational routing matrix `q`.  Therefore `19925 < 19953` proves only failure of the unit-capacity matching instance obtained by identifying those 19,925 triples with all available sinks.  It cannot prove

```text
¬ Nonempty (FullBankRelaxedCoverCert S F O J K sep dB inc kap)
```

for the real FullBank parameters.  Such a negation would require an exact rational dual certificate for those actual parameters; `Ell5FullBankInterface.lean:52-60` is the compiled separation theorem, and no R29 artifact provides its `alpha,beta,gam,del` witness.

## Why this is not `FullBankGlobalPackage.Checked`

`Gamma/FullBankToLengthSurplusCharge.lean:25-30` makes the full bank consist of four kinds: `door`, `vertexSlack`, `c5Base`, and `prune`.  Lines 33-45 give each local view four rational capacities and sum all four in `rhsQ`.  `Checked` at lines 177-227 assumes, among other things, every local view is checked, all four kind-spends agree with the local caps, token spends do not exceed token capacities, spends do not cross components, token keys are unique, and the component/global reserve identities hold.

The active-scoped count `17325+2600` is not shown to equal the sum of those four rational capacities.  It contains no Door, vertex-slack, c5-base, or prune token ledger, no `capQ/25` data, and no spend matrix.  Hence the missing `28` cannot be promoted to a deficit in `P.localCapTotal`, `P.tokenCapTotal`, or any field of `P.Checked`.

The architecture explicitly confirms this separation.  `Gamma/FullBankPortSinks.lean:41-49` defines Hall-scale token capacity as `capQ/25`, while lines 80-81 state that legal edge-to-token incidence is absent and that the finite sinks/capacities assert no Hall condition.  Conversely, `AggregateLedgerNoIncidenceCounterexample.lean:152-157` proves that a checked aggregate package alone does not create wall-port routing.  Thus neither direction needed to identify R29 owner-Hall failure with failure of `Checked` exists.

For scale only, the graph-level residual from the recorded integers is exact:

\[
N^2-25|M|=2943^2-25\cdot1383=8661249-34575=8626674,
\]

and therefore `etaQ = 8626674/25`.  This arithmetic is far larger than `28` but is not a capacity certificate: `Checked` requires the component reserve identities and legal token spends, not merely the global residual total.

## R28/R29 claim boundary

R28's `N=2928` writeup reports failure of its narrower scoped Hall / radius-three producer relation (`19950` demand versus `17235+2600=19835` reach, defect `115`) and explicitly leaves the one-row descent claim open.  R29 first supplies a local-minimum claim, and the later canonical all-anchor artifacts strengthen the selector-score conclusion to a global minimum with defect `28`.  Neither writeup constructs the real FullBank objects above.  The defensible statement is therefore:

> The canonical all-anchor `N=2943` tuple is an exact counterexample to the active-scoped same-first/row-companion owner-Hall condition, and consequently to the associated global-descent and heat-bath assertions.  It is not evidence for nonexistence of a real `FullBankRelaxedCoverCert` and is logically silent about existence or nonexistence of `FullBankGlobalPackage.Checked` until an exact adapter identifies the Hall sources with all four legal FullBank token families and capacities.
