# General KTT Proof Workflow — Direct Route Registry V8

Selected: 2026-07-22

Status: ACTIVE; supersedes the dead V7 transportation route.

Language: English for internal plans, prompts, code, checkers, and artifacts.
User-facing discussion may be Turkish.

## Exact target

Prove full KTT in every rank, or produce one exact stretched LR polynomial
with a negative ordinary monomial coefficient and two independent replays.

## DIRECT ROUTE — RESOLVE THE EIGHT DEGREE-ANOMALY LR TRIPLES

### 1. Exact final deliverable

Resolve the only eight triples in the prior campaign for which a held-out
degree mismatch was observed but the exact stretching polynomial remained
unknown (`CLOSURE_REPORT.md`, Section 4.3). For each triple, produce its exact
degree, exact `h*` vector, ordinary monomial coefficients over `Q`, and exact
counts through an ambient degree bound plus two held-out positive dilations.

If any coefficient is negative, produce the full two-engine KTT
counterexample certificate immediately. Otherwise close this finite gap with
an independently replayable null certificate making no claim about general
KTT.

### 2. Current frontier lemma or finite certificate

The eight records are the seven side-seven indices

```text
3962, 1907, 1919, 1769, 3997, 4494, 5167
```

and the side-six index `142`, with the exact partition triples printed in
`CLOSURE_REPORT.md` Section 4.3. Their earlier low-degree fits failed held-out
checks and then exceeded the old counting cap. Thus no sign conclusion from
those fits is valid.

The finite certificate is one frozen record per triple containing counts,
degree, `h*`, monomial coefficients, held-outs, engine provenance, and hashes.
The first preflight record, index 3962, has already returned exact dimension
five and `h*=(1,3,0,0,0,0)` from the current pinned LR counter; it is not a
counterexample and still requires the uniform replay below.

### 3. Explicit logical bridge

For a triple of maximum partition length `r`, the hive dimension gives the
rigorous ambient degree bound

```text
D=(r-1)(r-2)/2.
```

Exact LR counts at `n=0,...,D` determine the stretching polynomial, and exact
agreement at `D+1,D+2` certifies the interpolation independently of any
smaller dimension oracle. Equivalently, an exact `h*` computation with the
same positive held-outs determines the same Ehrhart polynomial. A strictly
negative monomial coefficient in any resulting polynomial is literally a
counterexample to KTT.

### 4. Next falsifiable action

Run the current pinned `lrcalc-rs` Buch-style and GT/interior paths on all
eight triples with outer partition equal to the report's `nu`. Reconstruct
the polynomials over exact rationals and verify two positive dilations beyond
the inferred degree and, where feasible, beyond the ambient interpolation
set. Cross-check every base value and at least two further positive values
with the independent hive or LR-tableau engine. On any negative sign, stop
the batch and invoke the full two-engine counterexample contract.

### 5. Exit condition

Success:

```text
one exact negative coefficient, with the full sample table, two held-outs,
two independent counting engines, and a frozen certificate hash.
```

Failure:

```text
DEAD: all eight unresolved degree-anomaly triples have exact nonnegative
stretching polynomials -- <frozen record and independent replay hashes>.
```

Do not enlarge this into another LR census. A null result resolves only the
eight named anomalies and returns the main proof route to GHTE. The separate
bounded skew-Kostka gate continues under its own fixed exit condition.

## Scope guard

This finite route can disprove KTT but cannot prove it. A smaller inferred
degree is never used as an interpolation bound unless the two ambient
held-outs also agree. General KTT remains open after any null result.
